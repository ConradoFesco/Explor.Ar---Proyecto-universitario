from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from src.web.auth.decorators import permission_required
from flask import session
from src.web.services.flag_service import flag_service
from datetime import datetime
from src.web.models.user import User

flag_api = Blueprint("flag_api", __name__, url_prefix="/flags")

@flag_api.route("/<int:flag_id>/toggle", methods=["POST"])
#@permission_required('flag_admin')
def toggle_flag_route(flag_id):
    """
    Endpoint para cambiar el estado de un flag.
    """
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "Sesión o usuario inválido"}), 401

    flag = flag_service.toggle_flag(flag_id, user_id) # Pasamos el objeto User

    return redirect(url_for('flag_api.list_flags_page')) 

# === Página principal de administración de flags ===
@flag_api.route("/", methods=["GET"])
#@permission_required('flag_admin') # <--- Usamos el permiso requerido
def list_flags_page():
    """
    Muestra la página de Feature Flags en el panel de administración.
    """
    flags = flag_service.get_all_flags()
    return render_template("list_flags.html", flags=flags)

# === API: Actualizar mensaje de mantenimiento ===
@flag_api.route("/<int:flag_id>/message", methods=["POST"])
#@permission_required('flag_admin') # <--- Usamos el permiso requerido
def update_flag_message_route(flag_id):
    """
    Endpoint para actualizar el mensaje del flag (por ejemplo, modo mantenimiento).
    """
    data = request.get_json()
    message = data.get("message")

    if not message or len(message.strip()) == 0:
        return jsonify({"error": "El mensaje es obligatorio"}), 400

    if len(message) > 255:
        return jsonify({"error": "El mensaje no puede superar los 255 caracteres"}), 400

    user_id = session.get('user_id')
    current_user = User.query.get(user_id)

    if not current_user:
        return jsonify({"error": "Sesión o usuario inválido"}), 401 

    flag = flag_service.update_flag_message(flag_id, message, actor=current_user)

    return jsonify({
        "success": True,
        "message": flag.message,
        "last_modified_by": flag.last_modified_by,
        "last_modified_at": flag.last_modified_at.strftime("%Y-%m-%d %H:%M")
    })