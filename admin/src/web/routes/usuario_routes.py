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
    
    # Validar parámetros de paginación
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 25:  # Límite máximo de 25 por página
        per_page = 25
    
    # Construir filtros
    filters = {
        "email": request.args.get('email'),
        "activo": request.args.get('activo'),
        "rol": request.args.get('rol')
    }
    filters = {k: v for k, v in filters.items() if v}
    
    # Parámetros de ordenamiento
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Validar parámetros de ordenamiento
    valid_sort_fields = ['created_at', 'name']
    valid_sort_orders = ['asc', 'desc']
    
    if sort_by not in valid_sort_fields:
        sort_by = 'created_at'
    if sort_order not in valid_sort_orders:
        sort_order = 'desc'
    
    try:
        result = user_service.list_users(
            filters=filters, 
            page=page, 
            per_page=per_page, 
            sort_by=sort_by, 
            sort_order=sort_order
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
