from flask import Blueprint, request, jsonify, render_template
from src.web.services.usuario_service import usuario_service
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError
from src.web.auth.decorators import permission_required
from datetime import datetime


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
        result = usuario_service.create_user(data_user, data_new_user)
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
    result = usuario_service.list_users()
    return render_template('list_users.html', users=result), 200 

from datetime import datetime

@user_api.route('/<int:user_id>', methods=['GET'])
#@permission_required("user_show")
def get_user(user_id):
    try:
        result = usuario_service.get_user(user_id)

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
#@permission_required("user_update")
def update_user(user_id):
    from src.web.models import User
    from ..extensions import db
    from flask import request, jsonify

    # Obtengo el JSON del front
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    #is_admin = 'admin' in user.permissions

    # Contiene SOLO los campos que el usuario quiere modificar
    changed_fields = data.get('data_new', {})

    if "name" in changed_fields:
        user.name = changed_fields["name"]

    if "last_name" in changed_fields:
        user.last_name = changed_fields["last_name"]

    if "mail" in changed_fields:
        user.mail = changed_fields["mail"]

    if "active" in changed_fields:
        user.active = changed_fields["active"] # True o False

    #if 'blocked' in changed_fields:
     #   new_blocked_status = changed_fields["blocked"]

        # Si el usuario a editar tiene permiso de 'admin' e intenta bloquearlo
        #if is_admin and new_blocked_status == True:
          #  return jsonify({
           #     "error": "Acción no permitida",
            #    "message": f"No se puede bloquear al usuario porque tiene permisos de Administrador."
           # }), 403 # 403 Forbidden

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

        user_to_delete.is_active = False # O el campo que uses para marcarlo como inactivo
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