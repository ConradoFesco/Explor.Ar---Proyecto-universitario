from flask import Blueprint, request, current_app, jsonify
from src.core.services.review_service import review_service
from src.web import exceptions as exc
from src.web.auth.decorators import token_or_session_required, get_current_user_id

review_api = Blueprint('review_api', __name__)


@review_api.route('/sites/<int:site_id>/reviews', methods=['GET'])
@token_or_session_required
def list_site_reviews(site_id: int):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        result = review_service.list_reviews(site_id=site_id, page=page, per_page=per_page)
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