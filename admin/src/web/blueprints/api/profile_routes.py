from flask import Blueprint, session, request, jsonify
from src.core.services.usuario_service import user_service

profile_bp = Blueprint("profile_bp", __name__)

@profile_bp.route("/profile/update_password", methods=["POST"])
def update_password():
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json()
    new_password = data.get("new_password")
    if not new_password or len(new_password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    try:
        result = user_service.update_password(session["user_id"], new_password)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


