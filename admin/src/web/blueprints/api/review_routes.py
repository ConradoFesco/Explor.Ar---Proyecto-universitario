from flask import Blueprint, request, current_app, jsonify
from src.core.services.review_service import review_service
from src.core.services.historic_site_service import historic_site_service
from src.web import exceptions as exc
from src.web.auth.decorators import token_or_session_required, get_current_user_id
from src.core.validators.api_validator import (
    validate_api_pagination_params,
    validate_positive_int,
    format_validation_error_for_api
)

review_api = Blueprint('review_api', __name__)


@review_api.route('/sites/<int:site_id>/reviews', methods=['GET'])
@token_or_session_required
def list_site_reviews(site_id: int):
    """
    Obtiene una lista paginada de reseñas para un sitio histórico específico.
    Muestra reseñas aprobadas + la reseña pendiente del usuario (si existe).
    
    Información adicional no especificada en la API:
    - author_name: Nombre del autor de la reseña (string, opcional)
    - status: Estado de la reseña (string, opcional): 'pending', 'approved', o 'rejected'
    - user_id: ID del usuario autor de la reseña (number, opcional)
    """
    try:
        historic_site_service.get_historic_site(site_id)
    except exc.NotFoundError:
        return jsonify(
            {
                "error": {
                    "code": "not_found",
                    "message": "Site not found",
                }
            }
        ), 404
    
    try:
        page, per_page = validate_api_pagination_params(
            page=request.args.get('page'),
            per_page=request.args.get('per_page'),
            default_page=1,
            default_per_page=10,
            max_per_page=100
        )
    except exc.ValidationError as error:
        error_details = format_validation_error_for_api(error)
        return jsonify(
            {
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": error_details,
                }
            }
        ), 400
    
    user_id = get_current_user_id()
    
    try:
        result = review_service.list_reviews(
            site_id=site_id,
            page=page,
            per_page=per_page,
            only_approved=True,
            include_user_pending=user_id,
        )
        items = result.get('items', [])
        pagination = result.get('pagination', {})
        
        data = []
        for r in items:
            user_info = r.get('user', {})
            data.append({
                "id": r.get('id'),
                "site_id": r.get('site_id'),
                "rating": r.get('rating'),
                "comment": r.get('content'),
                "inserted_at": r.get('created_at'),
                "updated_at": r.get('updated_at') or r.get('created_at'),
                "author_name": user_info.get('name') if user_info else None,
                "status": r.get('status'),
                "user_id": user_info.get('id') if user_info else None,
            })
        
        payload = {
            "data": data,
            "meta": {
                "page": pagination.get("page", page),
                "per_page": pagination.get("per_page", per_page),
                "total": pagination.get("total", 0),
            },
        }
        response = jsonify(payload)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except Exception as error:
        current_app.logger.exception("Error al listar reseñas", exc_info=error)
        return jsonify(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            }
        ), 500


@review_api.route('/sites/<int:site_id>/reviews', methods=['POST'])
@token_or_session_required
def create_site_review(site_id: int):
    """Crea una nueva reseña para un sitio histórico específico."""
    payload = request.get_json(silent=True) or {}
    rating = payload.get('rating')
    content = payload.get('comment')
    user_id = get_current_user_id()

    try:
        review = review_service.create_review(
            site_id=site_id,
            user_id=user_id,
            rating=rating,
            content=content,
        )
        data = {
            "id": review.id,
            "site_id": review.site_id,
            "rating": review.rating,
            "comment": review.content,
            "inserted_at": review.created_at.isoformat() if review.created_at else None,
            "updated_at": (
                review.updated_at.isoformat() if review.updated_at else
                (review.created_at.isoformat() if review.created_at else None)
            ),
        }
        response = jsonify(data)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 201
    except exc.ValidationError as error:
        error_details = format_validation_error_for_api(error)
        return jsonify(
            {
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": error_details,
                }
            }
        ), 400
    except exc.NotFoundError:
        return jsonify(
            {
                "error": {
                    "code": "not_found",
                    "message": "Site not found",
                }
            }
        ), 404
    except exc.DatabaseError as error:
        current_app.logger.exception("Database error al crear reseña", exc_info=error)
        return jsonify(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            }
        ), 500
    except Exception as error:
        current_app.logger.exception("Error al crear reseña", exc_info=error)
        return jsonify(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            }
        ), 500


@review_api.route('/sites/<int:site_id>/reviews/<int:review_id>', methods=['GET'])
@token_or_session_required
def get_site_review(site_id: int, review_id: int):
    """
    Obtiene una reseña existente por su ID.
    Los parámetros site_id y review_id son validados por Flask como enteros.
    """
    user_id = get_current_user_id()
    
    # TO-DO: validar review_id en validators para que sea positivo
    if review_id <= 0:
        return jsonify(
            {
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": {
                        "review_id": ["Must be a positive integer"],
                    },
                }
            }
        ), 400
    
    try:
        data = review_service.get_review(site_id=site_id, review_id=review_id, current_user_id=user_id)
        
        response_data = {
            "id": data.get('id'),
            "site_id": data.get('site_id'),
            "rating": data.get('rating'),
            "comment": data.get('content'),
            "inserted_at": data.get('created_at'),
            "updated_at": data.get('updated_at') or data.get('created_at'),
        }
        
        response = jsonify(response_data)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except exc.ForbiddenError as error:
        return jsonify(
            {
                "error": {
                    "code": "forbidden",
                    "message": "You do not have permission to access this review",
                }
            }
        ), 403
    except exc.NotFoundError as error:
        error_msg = str(error).lower()
        if 'sitio' in error_msg or 'site' in error_msg:
            return jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": "Site not found",
                    }
                }
            ), 404
        else:
            return jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": "Review not found",
                    }
                }
            ), 404
    except exc.ValidationError as error:
        error_details = format_validation_error_for_api(error)
        return jsonify(
            {
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": error_details,
                }
            }
        ), 400
    except Exception as error:
        current_app.logger.exception("Error al obtener reseña", exc_info=error)
        return jsonify(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            }
        ), 500


@review_api.route('/sites/<int:site_id>/reviews/<int:review_id>', methods=['PUT'])
@token_or_session_required
def update_site_review(site_id: int, review_id: int):
    """Actualiza una reseña existente."""
    payload = request.get_json(silent=True) or {}
    rating = payload.get('rating')
    content = payload.get('comment')
    user_id = get_current_user_id()

    try:
        review = review_service.update_review(
            site_id=site_id,
            review_id=review_id,
            user_id=user_id,
            rating=rating,
            content=content,
        )
        data = {
            "id": review.id,
            "site_id": review.site_id,
            "rating": review.rating,
            "comment": review.content,
            "inserted_at": review.created_at.isoformat() if review.created_at else None,
            "updated_at": (
                review.updated_at.isoformat() if review.updated_at else
                (review.created_at.isoformat() if review.created_at else None)
            ),
        }
        response = jsonify(data)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except exc.ValidationError as error:
        error_details = format_validation_error_for_api(error)
        return jsonify(
            {
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": error_details,
                }
            }
        ), 400
    except exc.ForbiddenError as error:
        return jsonify(
            {
                "error": {
                    "code": "forbidden",
                    "message": "You do not have permission to access this review",
                }
            }
        ), 403
    except exc.NotFoundError as error:
        error_msg = str(error).lower()
        if 'sitio' in error_msg or 'site' in error_msg:
            return jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": "Site not found",
                    }
                }
            ), 404
        else:
            return jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": "Review not found",
                    }
                }
            ), 404
    except exc.DatabaseError as error:
        current_app.logger.exception("Database error al actualizar reseña", exc_info=error)
        return jsonify(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            }
        ), 500
    except Exception as error:
        current_app.logger.exception("Error al actualizar reseña", exc_info=error)
        return jsonify(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            }
        ), 500


@review_api.route('/me/reviews', methods=['GET'])
@token_or_session_required
def list_my_reviews():
    """
    Lista todas las reseñas del usuario autenticado.
    
    Información adicional no especificada en la API:
    - status: Estado de la reseña (string, opcional): 'pending', 'approved', o 'rejected'
    - site_name: Nombre del sitio histórico (string, opcional)
    """
    user_id = get_current_user_id()

    try:
        from src.core.validators.api_validator import validate_api_pagination_params
        page, per_page = validate_api_pagination_params(
            page=request.args.get('page'),
            per_page=request.args.get('per_page'),
            default_page=1,
            default_per_page=25,
            max_per_page=100
        )
    except exc.ValidationError as error:
        from src.core.validators.api_validator import format_validation_error_for_api
        error_details = format_validation_error_for_api(error)
        return jsonify(
            {
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": error_details,
                }
            }
        ), 400
    
    from src.core.validators.reviews_validator import validate_review_sort
    try:
        sort_order = validate_review_sort(request.args.get('sort'))
    except exc.ValidationError as error:
        error_details = format_validation_error_for_api(error)
        return jsonify(
            {
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": error_details,
                }
            }
        ), 400

    try:
        result = review_service.list_reviews(
            page=page,
            per_page=per_page,
            sort_by='created_at',
            sort_order=sort_order,
            user_id=user_id,
            only_approved=False,
        )
        items = result.get('items', [])
        transformed_items = []
        for item in items:
            transformed_item = {
                'id': item.get('id'),
                'site_id': item.get('site_id'),
                'rating': item.get('rating'),
                'comment': item.get('content'),
                'inserted_at': item.get('created_at'),
                'updated_at': item.get('updated_at') or item.get('created_at'),
                'status': item.get('status'),
                'site_name': item.get('site_name'),
            }
            transformed_items.append(transformed_item)
        
        response_data = {
            'items': transformed_items,
            'pagination': result.get('pagination', {})
        }
        response = jsonify(response_data)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except exc.ValidationError as error:
        error_details = format_validation_error_for_api(error)
        return jsonify(
            {
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": error_details,
                }
            }
        ), 400
    except Exception as error:
        current_app.logger.exception("Error al listar reseñas del usuario", exc_info=error)
        return jsonify(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            }
        ), 500


@review_api.route('/sites/<int:site_id>/reviews/<int:review_id>', methods=['DELETE'])
@token_or_session_required
def delete_site_review(site_id: int, review_id: int):
    user_id = get_current_user_id()
    try:
        review_service.delete_review(site_id=site_id, review_id=review_id, current_user_id=user_id)
        return '', 204
    except exc.ForbiddenError as error:
        return jsonify(
            {
                "error": {
                    "code": "forbidden",
                    "message": "You do not have permission to delete this review",
                }
            }
        ), 403
    except exc.NotFoundError as error:
        error_msg = str(error).lower()
        if 'sitio' in error_msg or 'site' in error_msg:
            return jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": "Site not found",
                    }
                }
            ), 404
        else:
            return jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": "Review not found",
                    }
                }
            ), 404
    except exc.DatabaseError as error:
        current_app.logger.exception("Database error al eliminar reseña", exc_info=error)
        return jsonify(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            }
        ), 500
    except Exception as error:
        current_app.logger.exception("Error al eliminar reseña", exc_info=error)
        return jsonify(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            }
        ), 500