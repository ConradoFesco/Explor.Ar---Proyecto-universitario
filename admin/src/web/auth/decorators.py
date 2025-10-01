from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import jsonify
from src.web.models import user as Usuario  

ADMIN_PERMISSIONS = ["user_new", "user_index", "user_show", "user_update", "user_destroy"]
def permission_required(f):
    """
    Decorador para validar si el usuario tiene un permiso específico.
    """
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()  # en el token guardamos el id del usuario
            user = Usuario.query.get(user_id)

            if not user:
                return jsonify({"error": "Usuario no encontrado"}), 404

            # Ejemplo simple: permisos basados en rol
            if not all(user.permissions for perm in ADMIN_PERMISSIONS):
                return jsonify({"error": "Acceso denegado, solo el admin puede acceder"}), 403

            return f(*args, **kwargs)
        return decorator
    return wrapper