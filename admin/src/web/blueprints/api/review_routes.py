from flask import Blueprint, request, current_app, jsonify
from src.core.services.review_service import review_service
from src.web import exceptions as exc
from src.web.auth.decorators import token_or_session_required, get_current_user_id

review_api = Blueprint('review_api', __name__)


@review_api.route('/sites/<int:site_id>/reviews', methods=['GET'])
@token_or_session_required
def list_site_reviews(site_id: int):
    """Lista reseñas aprobadas de un sitio. Requiere autenticación."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        result = review_service.list_reviews(
            site_id=site_id,
            page=page,
            per_page=per_page,
            only_approved=True  # Solo reseñas aprobadas
        )
        response = jsonify(result)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except exc.ValidationError as error:
        return jsonify({'error': str(error)}), 400
    except exc.NotFoundError as error:
        return jsonify({'error': str(error)}), 404
    except Exception as error:
        current_app.logger.exception("Error al listar reseñas", exc_info=error)
        return jsonify({'error': 'Error interno al listar reseñas'}), 500


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
    """Lista reseñas aprobadas de un sitio. No requiere autenticación."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        result = review_service.list_reviews(
            site_id=site_id,
            page=page,
            per_page=per_page,
            only_approved=True  
        )
        # Enmascarar emails antes de enviar al frontend
        for review in result.get('items', []):
            if 'user_mail' in review and review['user_mail']:
                review['user_mail'] = _mask_email(review['user_mail'])
            if 'user' in review and review['user'] and 'mail' in review['user']:
                review['user']['mail'] = _mask_email(review['user']['mail'])
        response_data = {
            'reviews': result.get('items', []),
            'pagination': result.get('pagination', {})
        }
        response = jsonify(response_data)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except exc.ValidationError as error:
        return jsonify({'error': str(error)}), 400
    except exc.NotFoundError as error:
        return jsonify({'error': str(error)}), 404
    except Exception as error:
        current_app.logger.exception("Error al listar reseñas públicas", exc_info=error)
        return jsonify({'error': 'Error interno al listar reseñas'}), 500


@review_api.route('/sites/<int:site_id>/reviews', methods=['POST'])
@token_or_session_required
def create_site_review(site_id: int):
    payload = request.get_json(silent=True) or {}
    rating = payload.get('rating')
    content = payload.get('content')
    user_id = get_current_user_id()

    try:
        review = review_service.create_review(
            site_id=site_id,
            user_id=user_id,
            rating=rating,
            content=content,
        )
        response = jsonify(review.to_dict())
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 201
    except exc.ValidationError as error:
        return jsonify({'error': str(error)}), 400
    except exc.NotFoundError as error:
        return jsonify({'error': str(error)}), 404
    except exc.DatabaseError as error:
        return jsonify({'error': str(error)}), 500
    except Exception as error:
        current_app.logger.exception("Error al crear reseña", exc_info=error)
        return jsonify({'error': 'Error interno al crear reseña'}), 500


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
    content = payload.get('content')
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

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    sort = request.args.get('sort', 'desc')  # 'asc' o 'desc'
    sort_order = 'asc' if sort == 'asc' else 'desc'

    try:
        result = review_service.list_reviews(
            filters={'user_id': user_id},
            page=page,
            per_page=per_page,
            sort_by='created_at',
            sort_order=sort_order,
            only_approved=False  # Mostrar todas las reseñas del usuario (pending, approved)
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