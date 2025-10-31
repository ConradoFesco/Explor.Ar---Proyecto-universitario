from flask import Blueprint, request, jsonify, render_template
from src.core.services.usuario_service import user_service
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError
from src.web.auth.decorators import permission_required
from flask import session

user_api = Blueprint('user_api', __name__)

@user_api.route('', methods=['POST'])
@permission_required("create_user")
def create_user():
    try:
        # Obtener datos del usuario desde la sesión
        user_data = session.get('user_id')
        if not user_data:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        # Obtener datos del JSON
        json_content = request.get_json()
        if not json_content:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        data_new_user = json_content.get('data_new_user')
        if not data_new_user:
            return jsonify({'error': 'Faltan datos del nuevo usuario'}), 400
        
        result = user_service.create_user(user_data, data_new_user)
        return jsonify(result), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api.route('', methods=['GET'])
@permission_required("get_all_users")
def list_users():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 25))

    if page < 1:
        page = 1
    if per_page < 1 or per_page > 25:  # Límite máximo de 25 por página
        per_page = 25

    filters = {
        "email": request.args.get('email') or request.args.get('search'),
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
        result = user_service.list_users(filters=filters, page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order)
        
        # Me aseguro que siempre tenga formato JSON con users + pagination
        return jsonify({
            "users": result.get("users", []),
            "pagination": {
                "page": result.get("page", page),
                "per_page": result.get("per_page", per_page),
                "total": result.get("total", 0),
                "pages": result.get("pages", 1),
                "has_prev": result.get("has_prev", False),
                "has_next": result.get("has_next", False),
                "prev_num": result.get("prev_num"),
                "next_num": result.get("next_num"),
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

from datetime import datetime

@user_api.route('/<int:user_id>', methods=['GET'])
@permission_required("get_user")
def get_user(user_id):
    try:
        result = user_service.get_user(user_id)

        # Convertir created_at de string a datetime si existe
        if result and 'created_at' in result and isinstance(result['created_at'], str):
            try:
                result['created_at'] = datetime.fromisoformat(result['created_at'].replace('Z', '+00:00'))
            except:
                pass  # Si falla la conversión, dejamos el string original

        # Agregar información adicional que pueda necesitar el formulario de edición
        # como roles disponibles, etc.
        try:
            available_roles = user_service.get_available_roles()
            result['available_roles'] = available_roles
        except:
            result['available_roles'] = []
        
        return jsonify(result), 200
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404

@user_api.route('/<int:user_id>', methods=['PUT'])
@permission_required("update_user")
def update_user(user_id):
    try:
        # Obtener datos del usuario desde la sesión
        admin_user_id = session.get('user_id')
        if not admin_user_id:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        # Obtener datos del JSON
        json_content = request.get_json()
        if not json_content:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Contiene SOLO los campos que el usuario quiere modificar
        changed_fields = json_content.get('data_new', {})
        if not changed_fields:
            return jsonify({'error': 'No se proporcionaron campos para actualizar'}), 400
        
        # Llamar al servicio para actualizar el usuario
        result = user_service.update_user(user_id, changed_fields, admin_user_id)
        
        return jsonify({
            "message": "Usuario actualizado correctamente",
            "user": result
        }), 200
        
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api.route('/<int:user_id>', methods=['DELETE'])
@permission_required("delete_user")
def delete_user(user_id):
    try:
        # Obtener datos del usuario desde la sesión
        user_data = session.get('user_id')
        if not user_data:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        # Obtener datos del JSON
        json_content = request.get_json()
        if not json_content:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Obtener el motivo de eliminación
        reason = json_content.get('reason', 'Sin motivo especificado.')
        
        # Llamar al servicio para eliminar el usuario
        result = user_service.delete_user_with_reason(user_id, reason, user_data)
        
        return jsonify({"message": result}), 200
        
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Ocurrió un error interno al procesar la solicitud."}), 500

# --- RUTAS PARA GESTIÓN DE BLOQUEO DE USUARIOS ---

@user_api.route('/<int:user_id>/block', methods=['POST'])
@permission_required("update_user")
def block_user(user_id):
    """Bloquea un usuario"""
    try:
        json_content = request.get_json()
        if not json_content:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        data_user = json_content.get('data_user')
        if not data_user:
            return jsonify({'error': 'Faltan datos de usuario administrador'}), 400
        
        admin_user_id = data_user.get('id')
        if not admin_user_id:
            return jsonify({'error': 'Es necesario especificar el ID del usuario administrador'}), 400
        
        result = user_service.block_user(user_id, admin_user_id)
        return jsonify(result), 200
    except (ValidationError, NotFoundError) as e:
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api.route('/<int:user_id>/unblock', methods=['POST'])
@permission_required("update_user")
def unblock_user(user_id):
    """Desbloquea un usuario"""
    try:
        json_content = request.get_json()
        if not json_content:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        data_user = json_content.get('data_user')
        if not data_user:
            return jsonify({'error': 'Faltan datos de usuario administrador'}), 400
        
        admin_user_id = data_user.get('id')
        if not admin_user_id:
            return jsonify({'error': 'Es necesario especificar el ID del usuario administrador'}), 400
        
        result = user_service.unblock_user(user_id, admin_user_id)
        return jsonify(result), 200
    except (ValidationError, NotFoundError) as e:
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- RUTAS PARA GESTIÓN DE ROLES ---

@user_api.route('/<int:user_id>/roles', methods=['GET'])
@permission_required("get_user")
def get_user_roles(user_id):
    """Obtiene los roles asignados a un usuario"""
    try:
        result = user_service.get_user_roles(user_id)
        return jsonify({'roles': result}), 200
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api.route('/roles', methods=['GET'])
#@permission_required("get_all_users")
def get_available_roles():
    """Obtiene todos los roles disponibles en el sistema"""
    try:
        result = user_service.get_available_roles()
        return jsonify({'roles': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api.route('/<int:user_id>/roles/<int:role_id>', methods=['POST'])
@permission_required("update_user")
def assign_role_to_user(user_id, role_id):
    """Asigna un rol a un usuario"""
    try:
        json_content = request.get_json()
        if not json_content:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        data_user = json_content.get('data_user')
        if not data_user:
            return jsonify({'error': 'Faltan datos de usuario administrador'}), 400
        
        admin_user_id = data_user.get('id')
        if not admin_user_id:
            return jsonify({'error': 'Es necesario especificar el ID del usuario administrador'}), 400
        
        result = user_service.assign_role_to_user(user_id, role_id, admin_user_id)
        return jsonify(result), 200
    except (ValidationError, NotFoundError) as e:
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api.route('/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
@permission_required("update_user")
def revoke_role_from_user(user_id, role_id):
    """Revoca un rol de un usuario"""
    try:
        json_content = request.get_json()
        if not json_content:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        data_user = json_content.get('data_user')
        if not data_user:
            return jsonify({'error': 'Faltan datos de usuario administrador'}), 400
        
        admin_user_id = data_user.get('id')
        if not admin_user_id:
            return jsonify({'error': 'Es necesario especificar el ID del usuario administrador'}), 400
        
        result = user_service.revoke_role_from_user(user_id, role_id, admin_user_id)
        return jsonify(result), 200
    except (ValidationError, NotFoundError) as e:
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api.route('/<int:user_id>/roles', methods=['PUT'])
@permission_required("update_user")
def update_user_roles(user_id):
    """Actualiza los roles de un usuario (reemplaza todos los roles existentes)"""
    try:
        json_content = request.get_json()
        if not json_content:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        data_user = json_content.get('data_user')
        if not data_user:
            return jsonify({'error': 'Faltan datos de usuario administrador'}), 400
        
        admin_user_id = data_user.get('id')
        if not admin_user_id:
            return jsonify({'error': 'Es necesario especificar el ID del usuario administrador'}), 400
        
        role_ids = json_content.get('role_ids', [])
        if not isinstance(role_ids, list):
            return jsonify({'error': 'role_ids debe ser una lista'}), 400
        
        result = user_service.update_user_roles(user_id, role_ids, admin_user_id)
        return jsonify(result), 200
    except (ValidationError, NotFoundError) as e:
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api.route('/page', methods=['GET'])
def list_users_page():
    return render_template("users/list_users.html")


