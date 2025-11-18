# src/web/routes/login_routes.py
from datetime import datetime, timedelta
import jwt
from flask import Blueprint, request, redirect, url_for, session, jsonify, current_app
from src.web import exceptions as exc
from src.web.extensions import oauth
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


# --- RUTA 1: INICIA EL LOGIN CON GOOGLE ---
@login_bp.route("/google/login")
def google_login():
    """
    Redirige al usuario a la página de inicio de sesión de Google.
    """
    # 1. Define la URL a la que Google debe devolver al usuario.
    #    Debe coincidir EXACTAMENTE con la que pusiste en la Google Cloud Console.
    redirect_uri = url_for(
        'login_bp.google_callback',  # El nombre de tu blueprint y la función de callback
        _external=True               # Genera una URL completa (http://...)
    )
    
    # 2. Redirige al usuario a la página de Google
    return oauth.google.authorize_redirect(redirect_uri)


# --- RUTA 2: RECIBE LA RESPUESTA DE GOOGLE (EL CALLBACK) ---
@login_bp.route("/google/callback")
def google_callback():
    """
    Google redirige al usuario aquí después de que inicia sesión.
    """
    try:
        # 1. Authlib intercambia el código de Google por un token de acceso
        token = oauth.google.authorize_access_token()
        
        # 2. Obtener la información del usuario de Google
        #    Con authlib, después de authorize_access_token(), necesitamos hacer una petición adicional
        resp = oauth.google.get('userinfo', token=token)
        resp.raise_for_status()
        user_info = resp.json()
        
        if not user_info:
            raise exc.AuthenticationError("No se pudo obtener la información del usuario de Google.")
        
        # 3. Llama a tu servicio para "buscar o crear" al usuario en tu base de datos
        #    (Necesitarás crear este nuevo método en tu AuthService)
        user = auth_service.find_or_create_google_user(user_info)
        
        # 4. Inicia la sesión del usuario en TU aplicación
        session['user_id'] = user.id
        session.permanent = True
        
        # 5. Generar JWT para mantener consistencia con el endpoint /auth
        jwt_token, expires_in = _build_jwt_for_user(user)
        
        # 6. Redirige al usuario de vuelta a tu APLICACIÓN FRONTEND
        #    Usa una variable de entorno o configuración para hacerlo más flexible
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        redirect_url = f"{frontend_url}/dashboard?token={jwt_token}"
        
        return redirect(redirect_url)
        
    except exc.AuthenticationError as e:
        # Manejo de errores de autenticación
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        return redirect(f"{frontend_url}/login?error={str(e)}")
    except Exception as e:
        # Manejo de errores generales
        current_app.logger.error(f"Error en la autenticación con Google: {str(e)}", exc_info=True)
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        return redirect(f"{frontend_url}/login?error=Error en la autenticación con Google")

