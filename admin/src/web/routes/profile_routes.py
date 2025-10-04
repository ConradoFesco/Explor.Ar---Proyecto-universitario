from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from src.web.models.user import User
from src.web.extensions import db
from werkzeug.security import generate_password_hash,check_password_hash
from src.web.services.usuario_service import user_service

profile_bp = Blueprint("profile_bp", __name__)

@profile_bp.route("/profile", methods=["GET"])
def view_profile():
    if "user_id" not in session:
        return redirect(url_for("index"))
    
    try:
        user = user_service.get_user(session["user_id"])  # trae un dict
    except Exception:
        return redirect(url_for("index"))

    # Pasamos el diccionario completo al template
    return render_template("profile.html", user=user)

@profile_bp.route("/profile/update_password", methods=["POST"])
def update_password():
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json()
    new_password = data.get("new_password")
    if not new_password or len(new_password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    # Traer el usuario actual
    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Verificar si la nueva contraseña es igual a la actual
    if check_password_hash(user.password, new_password):
        return jsonify({"error": "La nueva contraseña no puede ser igual a la actual"}), 400

    # Actualizar la contraseña usando el método del service
    try:
        result = user_service.update_password(session["user_id"], new_password)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500