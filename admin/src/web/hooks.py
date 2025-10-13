"""
Hooks de la aplicación Flask.
Contiene before_request, context_processors y otros hooks.
"""
from flask import request, session, redirect, url_for, render_template
from src.core.models.user import User
from src.core.models.flag import Flag


def register_hooks(app):
    """
    Registra todos los hooks de la aplicación.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    
    @app.before_request
    def check_admin_maintenance():
        """
        Verifica antes de cada petición si el modo mantenimiento está activo.
        Solo los superAdmin pueden acceder cuando está activo.
        """
        # Ignorar rutas públicas (login, static, logout, archivos estáticos)
        public_endpoints = [
            'login_bp.login',      # POST /api/login
            'login_bp.logout',     # GET/POST /api/logout
            'main.index',          # GET /
            'static',              # Archivos estáticos
            None                   # Peticiones sin endpoint definido
        ]
        
        if request.endpoint in public_endpoints:
            return None
        
        # Ignorar todas las peticiones a /static/
        if request.path and request.path.startswith('/static/'):
            return None
        
        # Consultar el flag de mantenimiento
        try:
            admin_flag = Flag.query.filter_by(name="admin_maintenance_mode").first()
        except Exception as e:
            # Si hay error al consultar la BD, permitir acceso
            return None
        
        # Si el flag NO existe o está desactivado, continuar normalmente
        if not admin_flag or not admin_flag.enabled:
            return None
        
        # Flag activo: verificar si el usuario es superAdmin
        user_id = session.get("user_id")
        
        # Si no está logueado, permitir acceso (otras rutas lo redirigen)
        if not user_id:
            return None
        
        # Obtener el usuario completo
        try:
            user = User.query.get(user_id)
        except Exception as e:
            # Error en BD, limpiar sesión
            session.clear()
            return redirect(url_for('main.index'))
        
        # Si no se encuentra el usuario, cerrar sesión y redirigir
        if not user:
            session.clear()
            return redirect(url_for('main.index'))
        
        # Verificar si es superAdmin
        try:
            user_roles = user.get_user_roles()
            
            if 'superAdmin' in user_roles:
                # SuperAdmin puede acceder siempre
                return None
        except Exception as e:
            # Error al obtener roles, asumir no es superAdmin
            pass
        
        # Usuario normal: mostrar página de mantenimiento
        return render_template(
            "auth/mantenimiento.html",
            message=admin_flag.message or "El sitio de administración está temporalmente inactivo."
        )
    
    @app.context_processor
    def inject_user():
        """
        Inyecta el usuario actual en todos los templates.
        
        Returns:
            dict: Diccionario con información del usuario actual
        """
        user_id = session.get("user_id")
        if user_id:
            try:
                user = User.query.get(user_id)
                if user:
                    user_roles = user.get_user_roles()
                    user_initials = f"{user.name[0]}{user.last_name[0]}".upper() if user.name and user.last_name else "U"
                    return {
                        'current_user': user,
                        'user_roles': user_roles,
                        'user_initials': user_initials,
                        'is_admin': 'admin' in user_roles or 'superAdmin' in user_roles
                    }
            except Exception as e:
                pass
        return {
            'current_user': None,
            'user_roles': [],
            'user_initials': '',
            'is_admin': False
        }

