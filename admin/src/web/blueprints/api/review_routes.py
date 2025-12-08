from flask import Blueprint, request, current_app, jsonify
from src.core.services.review_service import review_service
from src.core.models.historic_site import HistoricSite
from src.web import exceptions as exc
from src.web.auth.decorators import token_or_session_required, get_current_user_id

review_api = Blueprint('review_api', __name__)



def _mask_email(email: str) -> str:
    """Enmascara un email mostrando solo los primeros 3 caracteres y el dominio."""
    if not email or '@' not in email:
        return email
    name, domain = email.split('@', 1)
    if len(name) <= 3:
        masked = name[0] + '•' * (len(name)-1)
    else:
        masked = name[:3] + '•' * (len(name)-3)
    return f"{masked}@{domain}"


@review_api.route('/public/sites/<int:site_id>/reviews', methods=['GET'])
def list_public_site_reviews(site_id: int):
    """Lista reseñas aprobadas de un sitio (API usada por el portal público)."""
    page = request.args.get('page') or 1
    per_page = request.args.get('per_page') or 10

    try:
        site = HistoricSite.query.filter_by(id=site_id, deleted=False).first()
        if not site:
            return jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": "Site not found",
                    }
                }
            ), 404
        result = review_service.list_reviews(
            site_id=site_id,
            page=page,
            per_page=per_page,
            only_approved=True,
        )
        items = result.get('items', [])
        pagination = result.get('pagination', {})
        for review in items:
            if 'user_mail' in review and review['user_mail']:
                review['user_mail'] = _mask_email(review['user_mail'])
            if 'user' in review and review['user'] and 'mail' in review['user']:
                review['user']['mail'] = _mask_email(review['user']['mail'])
        data = []
        for r in items:
            item = dict(r)
            item['comment'] = r.get('content')
            item['inserted_at'] = r.get('created_at')
            item.setdefault('updated_at', None)
            data.append(item)
        payload = {
            "data": data,
            "meta": {
                "page": pagination.get("page", 1),
                "per_page": pagination.get("per_page", per_page),
                "total": pagination.get("total", 0),
            },
        }
        response = jsonify(payload)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except exc.ValidationError as error:
        return jsonify(
            {
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": {
                        "_global": [str(error)],
                    },
                }
            }
        ), 400
    except exc.NotFoundError as error:
        return jsonify(
            {
                "error": {
                    "code": "not_found",
                    "message": str(error),
                }
            }
        ), 404
    except Exception as error:
        current_app.logger.exception("Error al listar reseñas públicas", exc_info=error)
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
        }
        response = jsonify(data)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 201
    except exc.ValidationError as error:
        return jsonify(
            {
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": {
                        "_global": [str(error)],
                    },
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
    user_id = get_current_user_id()
    try:
        data = review_service.get_review(site_id=site_id, review_id=review_id, current_user_id=user_id)
        response = jsonify(data)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except exc.ForbiddenError as error:
        return jsonify({'error': str(error)}), 403
    except exc.NotFoundError as error:
        return jsonify({'error': str(error)}), 404
    except Exception as error:
        current_app.logger.exception("Error al obtener reseña", exc_info=error)
        return jsonify({'error': 'Error interno al obtener reseña'}), 500


@review_api.route('/sites/<int:site_id>/reviews/<int:review_id>', methods=['PUT'])
@token_or_session_required
def update_site_review(site_id: int, review_id: int):
    """Actualiza una reseña existente."""
    payload = request.get_json(silent=True) or {}
    rating = payload.get('rating')
    # La API pública trabaja solo con `comment` como nombre de campo
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
        response = jsonify(review.to_dict())
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except exc.ValidationError as error:
        return jsonify({'error': str(error)}), 400
    except exc.ForbiddenError as error:
        return jsonify({'error': str(error)}), 403
    except exc.NotFoundError as error:
        return jsonify({'error': str(error)}), 404
    except exc.DatabaseError as error:
        return jsonify({'error': str(error)}), 500
    except Exception as error:
        current_app.logger.exception("Error al actualizar reseña", exc_info=error)
        return jsonify({'error': 'Error interno al actualizar reseña'}), 500


@review_api.route('/sites/<int:site_id>/reviews/me', methods=['GET'])
@token_or_session_required
def get_my_review(site_id: int):
    """Obtiene la reseña del usuario actual para un sitio."""
    user_id = get_current_user_id()
    try:
        review = review_service.get_user_review(site_id=site_id, user_id=user_id)
        response = jsonify({'review': review})
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except exc.ValidationError as error:
        return jsonify({'error': str(error)}), 400
    except Exception as error:
        current_app.logger.exception("Error al obtener reseña del usuario", exc_info=error)
        return jsonify({'error': 'Error interno al obtener reseña'}), 500


@review_api.route('/me/reviews', methods=['GET'])
@token_or_session_required
def list_my_reviews():
    """Lista todas las reseñas del usuario autenticado."""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Usuario no autenticado'}), 401

    page = request.args.get('page') or 1
    per_page = request.args.get('per_page') or 25
    sort = request.args.get('sort', 'desc')

    try:
        result = review_service.list_reviews(
            page=page,
            per_page=per_page,
            sort_by='created_at',
            sort_order=sort,
            user_id=user_id,
            only_approved=False,
        )
        response = jsonify(result)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except exc.ValidationError as error:
        return jsonify({'error': str(error)}), 400
    except Exception as error:
        current_app.logger.exception("Error al listar reseñas del usuario", exc_info=error)
        return jsonify({'error': 'Error interno al listar reseñas'}), 500


@review_api.route('/sites/<int:site_id>/reviews/<int:review_id>', methods=['DELETE'])
@token_or_session_required
def delete_site_review(site_id: int, review_id: int):
    user_id = get_current_user_id()
    try:
        review_service.delete_review(site_id=site_id, review_id=review_id, current_user_id=user_id)
        return '', 204
    except exc.ForbiddenError as error:
        return jsonify({'error': str(error)}), 403
    except exc.NotFoundError as error:
        return jsonify({'error': str(error)}), 404
    except exc.DatabaseError as error:
        return jsonify({'error': str(error)}), 500
    except Exception as error:
        current_app.logger.exception("Error al eliminar reseña", exc_info=error)
        return jsonify({'error': 'Error interno al eliminar reseña'}), 500