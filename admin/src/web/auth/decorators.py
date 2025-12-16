from functools import wraps
from flask import jsonify, session, redirect, url_for, flash, request, g, current_app
from src.core.services.auth_service import auth_service
from src.core.services.usuario_service import user_service
from src.core.models.user import PrivateUser
import jwt


def permission_required(permission_name):
    """
    Decorador para validar si el usuario tiene un permiso específico.
    
    Args:
        permission_name (str): Nombre del permiso requerido
    """
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            current_user = _resolve_current_user()

            if not current_user:
                return jsonify({"error": "Usuario no autenticado"}), 401

            if isinstance(current_user, PrivateUser):
                user_service.hydrate_user_permissions(current_user)

            if not current_user.has_permission(permission_name):
                return jsonify({"error": f"Acceso denegado. Se requiere el permiso: {permission_name}"}), 403

            return f(*args, **kwargs)
        return decorator
    return wrapper


def token_or_session_required(f):
    """
    Permite acceder con sesión activa (panel admin) o con token Bearer emitido vía /api/auth.
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        current_user = _resolve_current_user()
        if current_user:
            return f(*args, **kwargs)

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.lower().startswith('bearer '):
            return jsonify({"error": "Autenticación requerida"}), 401

        token = auth_header.split(' ', 1)[1].strip()
        secret = current_app.config.get("JWT_SECRET_KEY") or current_app.config.get("SECRET_KEY")
        try:
            payload = jwt.decode(token, secret, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        user_id = payload.get('sub')
        user = auth_service.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 401

        g.current_user = user
        return f(*args, **kwargs)
    return decorator


def get_current_user():
    """Devuelve el usuario autenticado (o None)."""
    return _resolve_current_user()


def get_current_user_id():
    """Devuelve el ID del usuario autenticado (o None)."""
    user = _resolve_current_user()
    return user.id if user else None


def _resolve_current_user():
    current_user = getattr(g, 'current_user', None)
    if current_user:
        return current_user

    user_id = session.get('user_id')
    if not user_id:
        return None

    current_user = auth_service.get_user_by_id(user_id)
    if current_user:
        g.current_user = current_user
    return current_user


def web_permission_required(permission_name):
    """
    Decorador para validar permisos en endpoints Web.
    En caso de falla, redirige con flash en lugar de responder JSON.
    """
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            user_id = session.get('user_id')

            if not user_id:
                flash('Debe iniciar sesión.', 'error')
                return redirect(url_for('main.index'))

            current_user = auth_service.get_user_by_id(user_id)
            if not current_user:
                session.pop('user_id', None)
                flash('Usuario no encontrado.', 'error')
                return redirect(url_for('main.index'))

            if isinstance(current_user, PrivateUser):
                user_service.hydrate_user_permissions(current_user)

            if not current_user.has_permission(permission_name):
                flash(f'Acceso denegado. Se requiere el permiso: {permission_name}', 'error')
                return redirect(url_for('main.home'))

            return f(*args, **kwargs)
        return decorator
    return wrapper


def system_admin_required(f):
    """
    Decorador específico para Super Admins (API).
    Retorna JSON para endpoints de API.
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        """
        Usa el flag booleano `is_super_admin` del modelo User para determinar
        si el usuario es super administrador.
        """
        current_user = _resolve_current_user()

        if not current_user:
            return jsonify({"error": "Usuario no autenticado"}), 401

        if not getattr(current_user, "is_super_admin", False):
            return jsonify({"error": "Acceso denegado. Se requiere ser super administrador"}), 403

        return f(*args, **kwargs)
    return decorator


def web_system_admin_required(f):
    """
    Decorador específico para Super Admins (Web).
    En caso de falla, redirige con flash en lugar de responder JSON.
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        """
        Versión Web: se apoya únicamente en el flag booleano `is_super_admin`
        del modelo User. No depende de roles con nombre especial.
        """
        current_user = _resolve_current_user()

        if not current_user:
            flash('Debe iniciar sesión.', 'error')
            return redirect(url_for('main.index'))

        if not getattr(current_user, "is_super_admin", False):
            flash('Acceso denegado. Se requiere ser super administrador.', 'error')
            return redirect(url_for('main.home'))

        return f(*args, **kwargs)
    return decorator