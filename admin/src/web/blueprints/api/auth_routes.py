from datetime import datetime, timedelta, timezone
import jwt
import secrets
import requests
from urllib.parse import urlencode
from flask import Blueprint, request, redirect, url_for, session, jsonify, current_app, make_response
from src.web import exceptions as exc
from src.web.extensions import oauth
from src.core.services.auth_service import auth_service
from src.web.auth.decorators import get_current_user, token_or_session_required

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
    session['user_id'] = user.id
    session.permanent = True
    
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
    expires = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    is_production = current_app.config.get('ENV') == 'production' or not current_app.debug
    
    if is_production:
        samesite_value = 'Lax'
        secure_value = True
        domain_value = None
    else:
        samesite_value = 'Lax'
        secure_value = False
        domain_value = None
    
    cookie_kwargs = {
        'key': 'access_token',
        'value': jwt_token,
        'max_age': expires_in,
        'expires': expires,
        'httponly': True,
        'secure': secure_value,
        'samesite': samesite_value,
        'path': '/'
    }
    
    if domain_value:
        cookie_kwargs['domain'] = domain_value
    
    response.set_cookie(**cookie_kwargs)


def _clear_jwt_cookie(response):
    """
    Elimina la cookie del JWT (para logout).
    
    Args:
        response: Objeto Response de Flask
    """
    response.set_cookie(
        'access_token',
        '',                   
        max_age=0,              
        expires=0,               
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

@login_bp.route("/me", methods=["GET"])
def get_current_user_info():
    """
    Endpoint ligero para verificar autenticación y obtener datos del usuario actual.
    Siempre retorna 200, con 'authenticated: false' si no está autenticado.
    Esto evita errores 401 en la consola del navegador.
    """
    user = get_current_user()
    if not user:
        return jsonify({
            "status": "success",
            "authenticated": False,
            "user": None
        }), 200
    
    return jsonify({
        "status": "success",
        "authenticated": True,
        "user": user.to_dict()
    }), 200


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
    Retorna la URL de Google OAuth para que el frontend redirija al usuario.
    El redirect_uri apunta al frontend, no al backend.
    """
    frontend_url = _get_frontend_url()
    
    redirect_uri = f"{frontend_url.rstrip('/')}/auth/callback"
    session['oauth_redirect_uri'] = redirect_uri
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    if not client_id:
        return _error_response(
            code="configuration_error",
            message="GOOGLE_CLIENT_ID no está configurado.",
            status_code=500
        )
    
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'prompt': 'select_account',
        'access_type': 'offline'
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    return jsonify({
        "status": "success",
        "auth_url": auth_url,
        "redirect_uri": redirect_uri
    }), 200


@login_bp.route("/google/exchange", methods=["POST"])
def google_exchange():
    """
    Intercambia el código de autorización de Google por tokens y autentica al usuario.
    Recibe el 'code' del frontend (que lo obtuvo de Google) y retorna JSON con el estado.
    La cookie HTTP-only se establece automáticamente en la respuesta.
    """
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return _error_response(
                code="missing_code",
                message="El código de autorización es requerido.",
                status_code=400
            )
        
        code = data.get('code')
        state = data.get('state')
        frontend_url = _get_frontend_url()
        redirect_uri = f"{frontend_url.rstrip('/')}/auth/callback"
        
        saved_redirect_uri = session.get('oauth_redirect_uri')
        if saved_redirect_uri and saved_redirect_uri != redirect_uri:
            redirect_uri = saved_redirect_uri
        
        saved_state = session.get('oauth_state')
        if not state or saved_state != state:
            return _error_response(
                code="invalid_state",
                message="Estado de OAuth inválido o faltante.",
                status_code=400
            )
        
        session.pop('oauth_state', None)
        
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            return _error_response(
                code="configuration_error",
                message="GOOGLE_CLIENT_ID o GOOGLE_CLIENT_SECRET no están configurados.",
                status_code=500
            )
        
        try:
            token_response = requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': redirect_uri
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            token_response.raise_for_status()
            token_data = token_response.json()
            
            token = {
                'access_token': token_data.get('access_token'),
                'token_type': token_data.get('token_type', 'Bearer'),
                'id_token': token_data.get('id_token'),
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('expires_in')
            }
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error al intercambiar code por token: {str(e)}")
            return _error_response(
                code="token_exchange_failed",
                message="No se pudo intercambiar el código de autorización por tokens.",
                status_code=401
            )
        
        resp = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo', token=token)
        resp.raise_for_status()
        user_info = resp.json()
        
        if not user_info:
            return _error_response(
                code="google_auth_failed",
                message="No se pudo obtener la información del usuario de Google.",
                status_code=401
            )
        
        user = auth_service.find_or_create_google_user(user_info)
        jwt_token, expires_in = _authenticate_user(user)
        
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
        import traceback
        error_trace = traceback.format_exc()
        current_app.logger.error(f"Error en la autenticación con Google: {str(e)}\n{error_trace}")
        return _error_response(
            code="internal_server_error",
            message=f"Error interno del servidor durante la autenticación con Google: {str(e)}",
            status_code=500
        )


@login_bp.route("/google/callback")
def google_callback():
    """
    Callback de Google OAuth (mantenido para compatibilidad, pero ya no se usa en el nuevo flujo).
    Este endpoint puede mantenerse para otros usos o eliminarse si no es necesario.
    """
    # Este endpoint ya no se usa en el nuevo flujo, pero lo mantenemos por compatibilidad
    return _error_response(
        code="deprecated_endpoint",
        message="Este endpoint está deprecado. Use /google/exchange en su lugar.",
        status_code=410
    )

