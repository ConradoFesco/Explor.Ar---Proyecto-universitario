"""
Rutas Web para gestión de reseñas (renderizado HTML/Jinja).
Requieren permisos equivalentes a los endpoints API.
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from src.web.auth.decorators import web_permission_required
from src.core.services.review_service import review_service
from src.core.services.historic_site_service import historic_site_service
from src.core.validators.reviews_validator import validate_review_list_params
from src.core.validators.listing_validator import _validate_sort
from src.web import exceptions as exc
from src.core.models.historic_site import HistoricSite

reviews_web = Blueprint('reviews_web', __name__)


def _resolve_review_list_params():
    """Resuelve y valida parámetros de listado de reseñas desde request.args."""
    raw_args = {
        'page': request.args.get('page', 1, type=int),
        'per_page': request.args.get('per_page', 25, type=int),
        'status': request.args.get('status'),
        'site_id': request.args.get('site_id', type=int),
        'rating_from': request.args.get('rating_from', type=int),
        'rating_to': request.args.get('rating_to', type=int),
        'date_from': request.args.get('date_from'),
        'date_to': request.args.get('date_to'),
        'user': request.args.get('user'),
        'sort_by': request.args.get('sort_by', 'created_at'),
        'sort_order': request.args.get('sort_order', 'desc')
    }
    
    try:
        # Validar paginación
        pagination = validate_review_list_params(page=raw_args['page'], per_page=raw_args['per_page'])
        page = pagination['page']
        per_page = pagination['per_page']
        
        # Validar sort
        allowed_sort_fields = ['created_at', 'rating', 'user_mail', 'site_name']
        sort_by, sort_order = _validate_sort(raw_args['sort_by'], raw_args['sort_order'], allowed_fields=allowed_sort_fields)
        
        # Preparar filtros
        filters = {}
        
        # Status: solo filtrar si se especifica explícitamente
        status = raw_args['status']
        if status and status != '' and status != 'null':
            filters['status'] = status
        # Si no se especifica, no filtrar por status (mostrar todas)
        
        if raw_args['site_id']:
            filters['site_id'] = raw_args['site_id']
        if raw_args['rating_from']:
            filters['rating_from'] = raw_args['rating_from']
        if raw_args['rating_to']:
            filters['rating_to'] = raw_args['rating_to']
        if raw_args['date_from']:
            filters['date_from'] = raw_args['date_from']
        if raw_args['date_to']:
            filters['date_to'] = raw_args['date_to']
        if raw_args['user']:
            filters['user'] = raw_args['user']
        
        return {
            'filters': filters,
            'page': page,
            'per_page': per_page,
            'sort_by': sort_by,
            'sort_order': sort_order
        }
    except exc.ValidationError as error:
        flash('Parámetros inválidos en el listado: ' + str(error), 'error')
        # Retornar valores por defecto
        return {
            'filters': {},  # Sin filtros por defecto (mostrar todas)
            'page': 1,
            'per_page': 25,
            'sort_by': 'created_at',
            'sort_order': 'desc'
        }


@reviews_web.route("/reviews")
@web_permission_required("moderate_reviews")
def list_reviews_page():
    """Listado SSR de reseñas con filtros, orden y paginación."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    
    site_options = review_service.list_site_options()

    params = _resolve_review_list_params()
    
    
    
    # Obtener reseñas usando el servicio
    try:
        result = review_service.list_reviews(
            filters=params['filters'],
            page=params['page'],
            per_page=params['per_page'],
            sort_by=params['sort_by'],
            sort_order=params['sort_order']
        )
        items = result.get('items', [])
        pagination = result.get('pagination', {})
    except (exc.ValidationError, exc.NotFoundError, exc.DatabaseError) as e:
        flash('Error al cargar reseñas: ' + str(e), 'error')
        items = []
        pagination = {'page': 1, 'pages': 1, 'per_page': 25, 'total': 0}
    
    return render_template(
        'features/reviews/reviews.html.jinja',
        site_options=site_options,
        items=items,
        page=pagination.get('page', 1),
        per_page=pagination.get('per_page', 25),
        total=pagination.get('total', 0),
        pages=pagination.get('pages', 1)
    )


@reviews_web.route("/reviews/fragment")
@web_permission_required("moderate_reviews")
def list_reviews_fragment():
    """Fragmento HTML para refrescar el listado de reseñas (paginación/orden)."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    
    params = _resolve_review_list_params()
    
    try:
        result = review_service.list_reviews(
            filters=params['filters'],
            page=params['page'],
            per_page=params['per_page'],
            sort_by=params['sort_by'],
            sort_order=params['sort_order']
        )
        items = result.get('items', [])
        pagination = result.get('pagination', {})
    except (exc.ValidationError, exc.NotFoundError, exc.DatabaseError) as e:
        items = []
        pagination = {'page': 1, 'pages': 1, 'per_page': 25, 'total': 0}
    
    return render_template(
        'features/reviews/_list_fragment.html.jinja',
        items=items,
        page=pagination.get('page', 1),
        per_page=pagination.get('per_page', 25),
        total=pagination.get('total', 0),
        pages=pagination.get('pages', 1)
    )


@reviews_web.route("/reviews/<int:review_id>/fragment")
@web_permission_required("moderate_reviews")
def review_detail_fragment(review_id):
    """Fragmento HTML con detalle de reseña para uso en modales o vistas parciales."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    
    # Obtener site_id desde query parameter (el JavaScript lo pasa desde el item del listado)
    site_id = request.args.get('site_id', type=int)
    
    if not site_id:
        flash('Parámetro site_id requerido', 'error')
        return redirect(url_for('reviews_web.list_reviews_page'))
    
    try:
        review_data = review_service.get_review(
            site_id=site_id,
            review_id=review_id,
            current_user_id=session.get('user_id')
        )
        
        return render_template('features/reviews/_detail_fragment.html.jinja', review=review_data)
    except (exc.ValidationError, exc.NotFoundError, exc.ForbiddenError, exc.DatabaseError) as e:
        # Si es una petición AJAX/fetch, devolver HTML de error en lugar de redirect
        if request.headers.get('X-Requested-With') == 'fetch':
            return f'<div class="text-red-600 p-4">Error al cargar reseña: {str(e)}</div>', 400
        flash('Error al cargar reseña: ' + str(e), 'error')
        return redirect(url_for('reviews_web.list_reviews_page'))
    except Exception as e:
        # Si es una petición AJAX/fetch, devolver HTML de error en lugar de redirect
        if request.headers.get('X-Requested-With') == 'fetch':
            return f'<div class="text-red-600 p-4">Error inesperado: {str(e)}</div>', 500
        flash('Error inesperado: ' + str(e), 'error')
        return redirect(url_for('reviews_web.list_reviews_page'))




@reviews_web.route("/reviews/<int:review_id>/aprobar", methods=["POST"])
@web_permission_required("moderate_reviews")
def aprobar_review(review_id):
    """Aprueba una reseña."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    
    try:
        review_service.approve_review(review_id=review_id)
        flash('Reseña aprobada correctamente', 'success')
    except (exc.ValidationError, exc.NotFoundError, exc.DatabaseError) as e:
        flash('Error al aprobar reseña: ' + str(e), 'error')
    except Exception as e:
        flash('Error inesperado: ' + str(e), 'error')
    
    return redirect(url_for('reviews_web.list_reviews_page'))


@reviews_web.route("/reviews/<int:review_id>/rechazar", methods=["POST"])
@web_permission_required("moderate_reviews")
def rechazar_review(review_id):
    """Rechaza una reseña con motivo."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    
    reason = (request.form.get('reason') or "").strip()
    
    if not reason:
        flash('Motivo de rechazo requerido', 'error')
        return redirect(url_for('reviews_web.list_reviews_page'))
    
    try:
        review_service.reject_review(review_id=review_id, reason=reason)
        flash('Reseña rechazada correctamente', 'success')
    except (exc.ValidationError, exc.NotFoundError, exc.DatabaseError) as e:
        flash('Error al rechazar reseña: ' + str(e), 'error')
    except Exception as e:
        flash('Error inesperado: ' + str(e), 'error')
    
    return redirect(url_for('reviews_web.list_reviews_page'))


@reviews_web.route("/reviews/<int:review_id>/eliminar", methods=["POST"])
@web_permission_required("moderate_reviews")
def eliminar_review(review_id):
    """Elimina lógicamente una reseña (acción administrativa)."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    
    try:
        review_service.delete_review_admin(review_id=review_id)
        flash('Reseña eliminada correctamente', 'success')
    except (exc.ValidationError, exc.NotFoundError, exc.DatabaseError) as e:
        flash('Error al eliminar reseña: ' + str(e), 'error')
    except Exception as e:
        flash('Error inesperado: ' + str(e), 'error')
    
    return redirect(url_for('reviews_web.list_reviews_page'))



