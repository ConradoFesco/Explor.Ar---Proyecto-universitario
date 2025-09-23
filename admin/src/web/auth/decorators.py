from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import jsonify

def permission_required(permission):
    """
    Decorador para validar si el usuario tiene un permiso específico.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()

            user_permissions = identity.get("permissions", [])

            if permission not in user_permissions:
                return jsonify({"error": "Acceso denegado, falta permiso"}), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper
