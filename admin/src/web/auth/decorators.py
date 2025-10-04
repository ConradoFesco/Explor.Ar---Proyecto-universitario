from functools import wraps
from flask import jsonify, session
from src.web.models.user import User

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
                
            # Verificar si el usuario tiene el permiso requerido
            user_permissions = current_user.permissions  # Usa la propiedad que ya tienes definida
            
            if permission_name not in user_permissions:
                return jsonify({"error": f"Acceso denegado. Se requiere el permiso: {permission_name}"}), 403
                
            return f(*args, **kwargs)
        return decorator
    return wrapper