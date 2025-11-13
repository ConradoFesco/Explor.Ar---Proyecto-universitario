from functools import wraps
from flask import jsonify, session, redirect, url_for, flash
from src.core.models.user import User

def permission_required(permission_name):
    """
    Decorador para validar si el usuario tiene un permiso específico.
    
    Args:
        permission_name (str): Nombre del permiso requerido
    """
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            user_id = session.get('user_id')
            
            if not user_id:
                return jsonify({"error": "Usuario no autenticado"}), 401
                
            # Obtener el usuario de la base de datos
            current_user = User.query.get(user_id)
            
            if not current_user:
                return jsonify({"error": "Usuario no encontrado"}), 404
                
            if not current_user.user_roles:
                return jsonify({"error": "Usuario no tiene roles asignados"}), 403
                
            # Verificar si el usuario tiene el permiso requerido (método optimizado)
            if not current_user.has_permission(permission_name):
                return jsonify({"error": f"Acceso denegado. Se requiere el permiso: {permission_name}"}), 403
                
            return f(*args, **kwargs)
        return decorator
    return wrapper


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

            current_user = User.query.get(user_id)
            if not current_user:
                session.pop('user_id', None)
                flash('Usuario no encontrado.', 'error')
                return redirect(url_for('main.index'))

            if not current_user.user_roles:
                flash('Acceso denegado: sin roles asignados.', 'error')
                return redirect(url_for('main.home'))

            if not current_user.has_permission(permission_name):
                flash(f'Acceso denegado. Se requiere el permiso: {permission_name}', 'error')
                return redirect(url_for('main.home'))

            return f(*args, **kwargs)
        return decorator
    return wrapper