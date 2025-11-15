# src/web/routes/login_routes.py
from datetime import datetime, timedelta
import jwt
from flask import Blueprint, request, redirect, url_for, session, jsonify, current_app
from src.web import exceptions as exc
from src.core.services.auth_service import auth_service

login_bp = Blueprint("login_bp", __name__)


def _build_jwt_for_user(user):
    secret = current_app.config.get("JWT_SECRET_KEY") or current_app.config.get("SECRET_KEY")
    expires_in = current_app.config.get("JWT_EXPIRATION_SECONDS", 3600)
    now = datetime.utcnow()
    payload = {
        "sub": user.id,
        "mail": user.mail,
        "exp": now + timedelta(seconds=expires_in),
        "iat": now,
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token, expires_in


@login_bp.route("/auth", methods=["POST"])
def auth():
    data = request.get_json() or {}
    mail = (data.get("mail") or "").strip()
    password = data.get("password")
    
    if not mail or not password:
        return jsonify({"error": "Complete todos los campos"}), 400

    try:
        user = auth_service.login(mail, password)
        # Mantener compatibilidad con sesión existente (panel web/admin)
        session['user_id'] = user.id
        session.permanent = True

        token, expires_in = _build_jwt_for_user(user)
        return jsonify({
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "user": user.to_dict()
        }), 200
    except exc.ValidationError as e:
        return jsonify({"error": str(e)}), 401 


@login_bp.route("/logout", methods=["GET","POST"])
def logout():
    session.pop("user_id", None)
    if request.is_json:
        return jsonify({"message": "Sesión cerrada correctamente"})
    return redirect(url_for("main.index"))
