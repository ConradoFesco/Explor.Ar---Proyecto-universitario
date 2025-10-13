# src/web/routes/login_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.core.models.user import User
from ..extensions import db   # importa tu instancia SQLAlchemy
from .. import exceptions as exc
from src.core.services.auth_service import auth_service
from src.core.models.flag import Flag
login_bp = Blueprint("login_bp", __name__)

@login_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    mail = data.get("mail")
    password = data.get("password")
    
    if not mail or not password:
        return jsonify({"error": "Complete todos los campos"}), 400

    try:
        user = auth_service.login(mail, password)
        # Guardar el ID del usuario en la sesión
        session['user_id'] = user.id
        session.permanent = True

        return jsonify({"message": "Bienvenido!", "user":  user.to_dict()}), 200
    except exc.ValidationError as e:
        return jsonify({"error": str(e)}), 401 

    

# --- LOGOUT ---
@login_bp.route("/logout", methods=["GET","POST"])
def logout():
    session.pop("user_id", None)
    if request.is_json:
        return jsonify({"message": "Sesión cerrada correctamente"})
    return redirect(url_for("main.index"))