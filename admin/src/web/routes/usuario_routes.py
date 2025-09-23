from flask import Blueprint, request, jsonify
from src.web.services.usuario_service import user_service
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError
from src.web.auth.decorators import permission_required

user_api = Blueprint('user_api', __name__)

@user_api.route('', methods=['POST'])
@permission_required("user_new")
def create_user():
    try:
        data = request.get_json()
        result = user_service.create_user(data)
        return jsonify(result), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

@user_api.route('', methods=['GET'])
@permission_required("user_index")
def list_users():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 25))
    filters = {
        "email": request.args.get('email'),
        "activo": request.args.get('activo')
    }
    filters = {k: v for k, v in filters.items() if v}
    result = user_service.list_users(filters=filters, page=page, per_page=per_page)
    return jsonify(result), 200

@user_api.route('/<int:user_id>', methods=['GET'])
@permission_required("user_show")
def get_user(user_id):
    try:
        result = user_service.get_user(user_id)
        return jsonify(result), 200
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404

@user_api.route('/<int:user_id>', methods=['PUT'])
@permission_required("user_update")
def update_user(user_id):
    try:
        data = request.get_json()
        result = user_service.update_user(user_id, data)
        return jsonify(result), 200
    except (ValidationError, NotFoundError) as e:
        return jsonify({"error": str(e)}), 400

@user_api.route('/<int:user_id>', methods=['DELETE'])
@permission_required("user_destroy")
def delete_user(user_id):
    try:
        result = user_service.delete_user(user_id)
        return jsonify(result), 200
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
