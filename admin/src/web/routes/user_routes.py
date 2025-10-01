from flask import Blueprint, request, jsonify
from src.web.services.usuario_service import user_service
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError
from src.web.auth.decorators import permission_required

user_api = Blueprint('user_api', __name__)

@user_api.route('', methods=['POST'])
#@permission_required("user_new")
def create_user():
    try:
        json_content = request.get_json()
        data_user = json_content.get('data_user')
        data_new_user = json_content.get('data_new_user')
        if not data_user or not data_new_user:
            return jsonify({'error': 'Faltan datos de usuario'}), 400
        result = user_service.create_user(data_user, data_new_user)
        return jsonify(result), 201
    except (ValidationError, DatabaseError) as e:
        return jsonify({"error": str(e)}), 400

@user_api.route('', methods=['GET'])   
#@permission_required("user_index")
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
#@permission_required("user_show")
def get_user(user_id):
    try:
        result = user_service.get_user(user_id)
        return jsonify(result), 200
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404

@user_api.route('/<int:user_id>', methods=['PUT'])
#@permission_required("user_update")
def update_user(user_id):
    json_content = request.get_json()
    data_user = json_content.get('data_user')
    data_new = json_content.get('data_new')
    if not data_user or not data_new:
        return jsonify({'error': 'Faltan datos de usuario'}), 400
    try:
        result = user_service.update_user(user_id, data_user, data_new)
        return jsonify(result), 200
    except (DatabaseError, NotFoundError) as e:
        return jsonify({"error": str(e)}), 400

@user_api.route('/<int:user_id>', methods=['DELETE'])
#@permission_required("user_destroy")
def delete_user(user_id):
    json_content = request.get_json()
    data_user = json_content.get('data_user')
    if not data_user:
        return jsonify({'error': 'Faltan datos de usuario'}), 400
    try:
        result = user_service.delete_user(user_id,data_user)
        return jsonify(result), 200
    except (NotFoundError, DatabaseError) as e:
        return jsonify({"error": str(e)}), 404
