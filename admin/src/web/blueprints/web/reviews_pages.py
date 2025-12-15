"""
Rutas Web para gestión de reseñas (renderizado HTML/Jinja).
Requieren permisos equivalentes a los endpoints API.
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app
from src.web.auth.decorators import web_permission_required, get_current_user_id
from src.core.services.review_service import review_service
from src.core.services.historic_site_service import historic_site_service
from src.core.validators.reviews_validator import validate_review_detail_params, validate_rejection_reason
from src.web import exceptions as exc

reviews_web = Blueprint('reviews_web', __name__)


def _get_review_list_params():
    """Extrae y retorna los parámetros de filtros de la request."""
    return {
        'page': request.args.get('page'),
        'per_page': request.args.get('per_page'),
        'sort_by': request.args.get('sort_by'),
        'sort_order': request.args.get('sort_order'),
        'status': request.args.get('status'),
        'site_id': request.args.get('site_id'),
        'user': request.args.get('user'),
        'rating_from': request.args.get('rating_from'),
        'rating_to': request.args.get('rating_to'),
        'date_from': request.args.get('date_from'),
        'date_to': request.args.get('date_to'),
    }


def _handle_review_action(action_name: str, action_func, success_message: str):
    """
    Maneja acciones de reseñas (aprobar, rechazar, eliminar) con manejo de errores común.
    
    Args:
        action_name: Nombre de la acción para logging
        action_func: Función que ejecuta la acción (debe recibir review_id)
        success_message: Mensaje de éxito a mostrar
    """
    try:
        action_func()
        flash(success_message, 'success')
    except (exc.ValidationError, exc.NotFoundError, exc.DatabaseError) as e:
        flash(f'Error al {action_name}: {str(e)}', 'error')
    except Exception as e:
        flash(f'Error inesperado: {str(e)}', 'error')
    
    return redirect(url_for('reviews_web.list_reviews_page'))


@reviews_web.route("/reviews")
@web_permission_required("review_index")
def list_reviews_page():
    """Listado SSR de reseñas con filtros."""
    items = []
    pagination = {'page': 1, 'pages': 1, 'per_page': 25, 'total': 0, 'has_next': False, 'has_prev': False}
    show_rejection_reason_column = False
    site_options = []

    try:
        sites = historic_site_service.get_sites_for_filter()
        site_options = [{'value': str(s.get('id')), 'label': s.get('name')} for s in sites if s.get('id')]
    except Exception as e:
        current_app.logger.exception("Error al cargar sitios para filtro", exc_info=e)

    try:
        params = _get_review_list_params()
        result = review_service.list_reviews(**params)
        items = result.get('items', [])
        pagination = result.get('pagination', {})
        show_rejection_reason_column = any(item.get('status') == 'rejected' for item in items)

    except exc.ValidationError as e:
        flash(f"Error en los filtros: {str(e)}", "error")
    except (exc.NotFoundError, exc.DatabaseError) as e:
        flash(f"Error al cargar datos: {str(e)}", "error")
    except Exception as e:
        current_app.logger.error(f"Error inesperado listando reseñas: {e}")
        flash("Ocurrió un error inesperado al cargar las reseñas.", "error")
    
    return render_template(
        'features/reviews/reviews.html.jinja',
        site_options=site_options,
        items=items,
        pagination=pagination,
        show_rejection_reason_column=show_rejection_reason_column
    )


@reviews_web.route("/reviews/fragment")
@web_permission_required("review_index")
def list_reviews_fragment():
    """Fragmento HTML para refrescar el listado de reseñas."""
    items = []
    pagination = {'page': 1, 'pages': 1, 'per_page': 25, 'total': 0, 'has_next': False, 'has_prev': False}
    show_rejection_reason_column = False
    
    try:
        params = _get_review_list_params()
        result = review_service.list_reviews(**params)
        items = result.get('items', [])
        pagination = result.get('pagination', {})
        show_rejection_reason_column = any(item.get('status') == 'rejected' for item in items)

    except exc.ValidationError as e:
        current_app.logger.warning(f"Error de validación en fragmento de reseñas: {e}")
    except Exception as e:
        current_app.logger.error(f"Error en fragmento de reseñas: {e}")
    
    return render_template(
        'features/reviews/_list_fragment.html.jinja',
        items=items,
        pagination=pagination,
        show_rejection_reason_column=show_rejection_reason_column
    )


@reviews_web.route("/reviews/<int:review_id>/fragment")
@web_permission_required("review_show")
def review_detail_fragment(review_id):
    """Fragmento HTML con detalle de reseña."""
    try:
        params = validate_review_detail_params(
            site_id=request.args.get('site_id'),
            review_id=review_id
        )
        
        review_data = review_service.get_review(
            site_id=params['site_id'],
            review_id=params['review_id'],
            current_user_id=get_current_user_id(),
            skip_ownership_validation=True
        )
        return render_template('features/reviews/_detail_fragment.html.jinja', review=review_data)
    
    except exc.ValidationError as e:
        return f'<div class="text-red-600 p-4">Error: {str(e)}</div>', 400
    except (exc.NotFoundError, exc.ForbiddenError) as e:
        return f'<div class="text-red-600 p-4">Error: {str(e)}</div>', 400
    except Exception as e:
        return f'<div class="text-red-600 p-4">Error inesperado: {str(e)}</div>', 500


@reviews_web.route("/reviews/<int:review_id>/aprobar", methods=["POST"])
@web_permission_required("review_update")
def aprobar_review(review_id):
    """Aprueba una reseña."""
    return _handle_review_action(
        'aprobar',
        lambda: review_service.approve_review(review_id=review_id),
        'Reseña aprobada correctamente'
    )


@reviews_web.route("/reviews/<int:review_id>/rechazar", methods=["POST"])
@web_permission_required("review_update")
def rechazar_review(review_id):
    """Rechaza una reseña con motivo."""
    try:
        reason = validate_rejection_reason(request.form.get('reason'))
    except exc.ValidationError as e:
        flash(str(e), 'error')
        return redirect(url_for('reviews_web.list_reviews_page'))
    
    return _handle_review_action(
        'rechazar',
        lambda: review_service.reject_review(review_id=review_id, reason=reason),
        'Reseña rechazada correctamente'
    )


@reviews_web.route("/reviews/<int:review_id>/eliminar", methods=["POST"])
@web_permission_required("review_destroy")
def eliminar_review(review_id):
    """Elimina físicamente una reseña (acción administrativa)."""
    return _handle_review_action(
        'eliminar',
        lambda: review_service.delete_review_admin(review_id=review_id),
        'Reseña eliminada correctamente'
    )