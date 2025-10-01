from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import jsonify
from src.web.models import user as Usuario  

def permission_required(permission):
    """
    Decorador para validar si el usuario tiene un permiso específico.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()  # en el token guardamos el id del usuario
            user = Usuario.query.get(user_id)

            if not user:
                return jsonify({"error": "Usuario no encontrado"}), 404

            # Ejemplo simple: permisos basados en rol
            if not user.permissions.contain(permission):
                return jsonify({"error": "Acceso denegado, falta permiso"}), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper