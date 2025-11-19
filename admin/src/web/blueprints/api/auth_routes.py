# src/web/routes/login_routes.py
from datetime import datetime, timedelta, timezone
import jwt
from flask import Blueprint, request, redirect, url_for, session, jsonify, current_app, make_response
from src.web import exceptions as exc
from src.web.extensions import oauth
from src.core.services.auth_service import auth_service

login_bp = Blueprint("login_bp", __name__)


def _build_jwt_for_user(user):
    """
    Genera un JWT para el usuario autenticado.
    
    Args:
        user: Instancia del modelo User
        
    Returns:
        tuple: (token, expires_in) donde token es el JWT y expires_in son los segundos de expiración
    """
    secret = current_app.config.get("JWT_SECRET_KEY") or current_app.config.get("SECRET_KEY")
    expires_in = current_app.config.get("JWT_EXPIRATION_SECONDS", 3600)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.id,
        "mail": user.mail,
        "exp": now + timedelta(seconds=expires_in),
        "iat": now,
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token, expires_in


def _authenticate_user(user):
    """
    Autentica un usuario estableciendo la sesión y generando el JWT.
    Lógica común para autenticación con Google OAuth.
    
    Args:
        user: Instancia del modelo User
        
    Returns:
        tuple: (jwt_token, expires_in)
    """
    # Mantener compatibilidad con sesión existente (panel web/admin)
    session['user_id'] = user.id
    session.permanent = True
    
    # Generar JWT para la autenticación
    jwt_token, expires_in = _build_jwt_for_user(user)
    return jwt_token, expires_in


def _get_frontend_url():
    """
    Obtiene la URL del frontend desde la configuración.
    
    Returns:
        str: URL del frontend
    """
    return current_app.config.get('FRONTEND_URL', 'http://localhost:5173')


def _set_jwt_cookie(response, jwt_token, expires_in):
    """
    Establece el JWT como una cookie HTTP-only segura.
    
    Args:
        response: Objeto Response de Flask (creado con make_response)
        jwt_token: Token JWT a guardar
        expires_in: Segundos hasta la expiración
    """
    # Calcular la fecha de expiración usando timezone.utc (no deprecated)
    expires = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    
    # Determinar si estamos en producción (HTTPS)
    # En desarrollo puede ser False, en producción True
    is_secure = current_app.config.get('SESSION_COOKIE_SECURE', False)
    
    # Setear la cookie con opciones de seguridad
    response.set_cookie(
        'access_token',           # Nombre de la cookie
        jwt_token,                # Valor (el JWT)
        max_age=expires_in,       # Tiempo de vida en segundos
        expires=expires,           # Fecha de expiración
        httponly=True,            # ⚠️ CRÍTICO: No accesible desde JavaScript (protección XSS)
        secure=is_secure,         # Solo se envía por HTTPS en producción
        samesite='Lax',           # Protección CSRF (permite navegación normal)
        path='/'                  # Disponible en todo el sitio
    )


def _clear_jwt_cookie(response):
    """
    Elimina la cookie del JWT (para logout).
    
    Args:
        response: Objeto Response de Flask
    """
    response.set_cookie(
        'access_token',
        '',                       # Valor vacío
        max_age=0,                # Expira inmediatamente
        expires=0,                # Fecha pasada
        httponly=True,
        secure=current_app.config.get('SESSION_COOKIE_SECURE', False),
        samesite='Lax',
        path='/'
    )


def _error_response(code, message, status_code=400):
    """
    Genera una respuesta de error estructurada según el estándar de la API.
    
    Args:
        code: Código del error (ej: "invalid_credentials", "missing_fields")
        message: Mensaje descriptivo del error
        status_code: Código HTTP de estado (default: 400)
        
    Returns:
        tuple: (Response, status_code) para retornar en Flask
    """
    return jsonify({
        "error": {
            "code": code,
            "message": message
        }
    }), status_code

"""
@login_bp.route("/auth", methods=["POST"])
def auth():
    """
    """
    Endpoint para autenticación con email y contraseña.
    Retorna un JWT en formato JSON.
    """
    """
    data = request.get_json() or {}
    mail = (data.get("mail") or "").strip()
    password = data.get("password")
    
    if not mail or not password:
        return _error_response(
            code="missing_fields",
            message="Complete todos los campos",
            status_code=400
        )

    try:
        user = auth_service.login(mail, password)
        jwt_token, expires_in = _authenticate_user(user)
        
        return jsonify({
            "access_token": jwt_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "user": user.to_dict()
        }), 200
    except exc.ValidationError as e:
        return _error_response(
            code="invalid_credentials",
            message="Credenciales inválidas.",
            status_code=401
        ) 
"""

@login_bp.route("/logout", methods=["GET", "POST"])
def logout():
    """
    Cierra la sesión del usuario y elimina la cookie del JWT.
    Retorna JSON con el estado de la operación.
    """
    session.pop("user_id", None)
    
    response = jsonify({
        "message": "Sesión cerrada correctamente",
        "status": "success"
    })
    _clear_jwt_cookie(response)
    return response


@login_bp.route("/google/login")
def google_login():
    """
    Inicia el flujo de autenticación con Google OAuth.
    Redirige al usuario a la página de inicio de sesión de Google.
    """
    redirect_uri = url_for('login_bp.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@login_bp.route("/google/callback")
def google_callback():
    """
    Callback de Google OAuth.
    Recibe la respuesta de Google después de que el usuario inicia sesión,
    autentica o crea el usuario en la base de datos, y retorna JSON con el estado.
    La cookie HTTP-only se establece automáticamente en la respuesta.
    """
    try:
        # 1. Intercambiar código de autorización por token de acceso
        token = oauth.google.authorize_access_token()
        
        # 2. Obtener información del usuario de Google
        resp = oauth.google.get('userinfo', token=token)
        resp.raise_for_status()
        user_info = resp.json()
        
        if not user_info:
            return _error_response(
                code="google_auth_failed",
                message="No se pudo obtener la información del usuario de Google.",
                status_code=401
            )
        
        # 3. Buscar o crear el usuario en la base de datos
        user = auth_service.find_or_create_google_user(user_info)
        
        # 4. Autenticar al usuario (establecer sesión y generar JWT)
        jwt_token, expires_in = _authenticate_user(user)
        
        # 5. Crear respuesta JSON y establecer cookie HTTP-only
        response = make_response(jsonify({
            "status": "success",
            "message": "Autenticación exitosa",
            "user": user.to_dict(),
            "expires_in": expires_in
        }))
        _set_jwt_cookie(response, jwt_token, expires_in)
        
        return response
        
    except exc.AuthenticationError as e:
        return _error_response(
            code="google_auth_failed",
            message=str(e) if str(e) else "Error en la autenticación con Google.",
            status_code=401
        )
    except Exception as e:
        current_app.logger.error(f"Error en la autenticación con Google: {str(e)}", exc_info=True)
        return _error_response(
            code="internal_server_error",
            message="Error interno del servidor durante la autenticación con Google.",
            status_code=500
        )

