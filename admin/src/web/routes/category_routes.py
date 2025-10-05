from flask import Blueprint, request, jsonify
from src.web.services.category_service import category_service
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError
from src.web.auth.decorators import permission_required

category_api = Blueprint('category_api', __name__)

@category_api.route('/category_routes', methods=['GET'])
@permission_required('get_all_categories')
def get_all_categories():
    try:
        categories = category_service.get_all_categories()
        return jsonify(categories), 200
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 409
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
