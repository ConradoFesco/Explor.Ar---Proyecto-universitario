# src/web/routes/login_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ..models.user import User
from ..extensions import db   # importa tu instancia SQLAlchemy

login_bp = Blueprint("login_bp", __name__)

# --- LOGIN ---
@login_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("mail")
    password = data.get("password")

    # --- prints de debug ---
    print("Email recibido:", email)
    print("Password recibido:", password)

    if not email or not password:
        return jsonify({"error": "Complete todos los campos"}), 400

    user = User.query.filter_by(mail=email).first()
    print("Usuario encontrado:", user)
    if user:
        print("Password hash en DB:", user.password_hash)
        print("Resultado check_password:", user.check_password(password))

    # --- validación normal ---
    if user and user.check_password(password):
        session["user_id"] = user.id
        return jsonify({"message": "Bienvenido!", "user":  user.to_dict()}), 200
    else:
        return jsonify({"error": "Credenciales inválidas"}), 401
# --- LOGOUT ---
@login_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Sesión cerrada"}), 200