from flask import Blueprint, request, jsonify, render_template
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

    if page < 1:
        page = 1
    if per_page < 1 or per_page > 25:  # Límite máximo de 25 por página
        per_page = 25

    filters = {
        "email": request.args.get('email') or request.args.get('search'),
        "activo": request.args.get('activo')
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
        result = user_service.list_users(page=page, per_page=per_page)
        
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
#@permission_required("user_show")
def get_user(user_id):
    try:
        result = user_service.get_user(user_id)

        # Convertir created_at de string a datetime si existe
        if result and 'created_at' in result and isinstance(result['created_at'], str):
            try:
                result['created_at'] = datetime.fromisoformat(result['created_at'].replace('Z', '+00:00'))
            except:
                pass  # Si falla la conversión, dejamos el string original

        return jsonify(result), 200
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404

@user_api.route('/<int:user_id>', methods=['PUT'])
#permission_required("user_update")
def update_user(user_id):
    from src.web.models import User
    from ..extensions import db
    from flask import request, jsonify

    # Obtengo el JSON del front
    data = request.get_json()
    user = User.query.get_or_404(user_id) # modificar y mandar al servicio!!!!

    # Contiene SOLO los campos que el usuario quiere modificar
    changed_fields = data.get('data_new', {})

    # Actualizar solo los campos que vienen en changed_fields
    if "name" in changed_fields:
        user.name = changed_fields["name"]

    if "last_name" in changed_fields:
        user.last_name = changed_fields["last_name"]

    if "mail" in changed_fields:
        user.mail = changed_fields["mail"]

    if "active" in changed_fields:
        user.active = changed_fields["active"]
    
    if "blocked" in changed_fields:
        user.blocked = changed_fields["blocked"]
    
    if "role" in changed_fields:
        # Aquí podrías manejar el cambio de rol si lo necesitas
        pass

    # Persistir los cambios en la base de datos
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al guardar en la base de datos", "details": str(e)}), 500

    # Respuesta JSON con el usuario actualizado
    return jsonify({
        "message": "Usuario actualizado correctamente",
        "user": user.to_dict()
    }), 200

    #if 'blocked' in changed_fields:
     #   new_blocked_status = changed_fields["blocked"]

        # Si el usuario a editar tiene permiso de 'admin' e intenta bloquearlo
        #if is_admin and new_blocked_status == True:
          #  return jsonify({
           #     "error": "Acción no permitida",
            #    "message": f"No se puede bloquear al usuario porque tiene permisos de Administrador."
           # }), 403 # 403 Forbidden

@user_api.route('/<int:user_id>', methods=['DELETE'])
#@permission_required("user_destroy")
def delete_user(user_id):
    from src.web.models import User
    from .. import db
    json_content = request.get_json()
    user_to_delete = User.query.get(user_id)
    if not user_to_delete:
        return jsonify({"error": f"Usuario con id {user_id} no encontrado"}), 404
    try:
        data = json_content.get('data_user')
        if not data:
            return jsonify({'error': 'No se proporcionaron datos en la petición'}), 400
        reason = data.get('reason', 'Sin motivo especificado.')
        #admin_data = data.get('data_user', {})
        admin_id = data.get('id')

        if not admin_id:
            #asigno temporalmente un id, ACORDARSE DE ELIMINARLO
            admin_id = 1
            #return jsonify({"error": "Es necesario especificar el ID del usuario que realiza la operación"}), 400

        user_to_delete.active = False  # ✅ Este es el campo correcto
        user_to_delete.deleted = True  # ✅ Marca como eliminado
        user_to_delete.deleted_at = datetime.utcnow() # Guarda la fecha y hora de la baja
        user_to_delete.deletion_reason = reason # Guarda el motivo
        user_to_delete.deleted_by_id = admin_id # Guarda quién lo eliminó

        db.session.commit()

        return jsonify({"message": f"El usuario '{user_to_delete.mail}' ha sido eliminado correctamente."}), 200

    except Exception as e:
        # Si algo sale mal, revertir los cambios y notificar el error
        db.session.rollback()
        print(f"Error en la operación: {e}") # Imprime el error en la consola del servidor
        return jsonify({"error": "Ocurrió un error interno al procesar la solicitud."}), 500

# --- RUTAS PARA GESTIÓN DE BLOQUEO DE USUARIOS ---

@user_api.route('/<int:user_id>/block', methods=['POST'])
#@permission_required("user_block")
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
#@permission_required("user_block")
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
#@permission_required("user_show")
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
#@permission_required("user_index")
def get_available_roles():
    """Obtiene todos los roles disponibles en el sistema"""
    try:
        result = user_service.get_available_roles()
        return jsonify({'roles': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api.route('/<int:user_id>/roles/<int:role_id>', methods=['POST'])
#@permission_required("user_update")
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
#@permission_required("user_update")
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

@user_api.route('/page', methods=['GET'])
def list_users_page():
    return render_template("list_users.html")

