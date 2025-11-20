"""
Hooks de la aplicación Flask.
Contiene before_request, context_processors y otros hooks.
"""
from flask import request, session, redirect, url_for, render_template
from src.core.services.usuario_service import user_service
from src.core.services.flag_service import flag_service


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
        Solo los super administradores pueden acceder cuando está activo.
        """
        # Ignorar rutas públicas (login, static, logout, archivos estáticos)
        public_endpoints = [
            'login_bp.login',      # legacy API login
            'login_bp.logout',     # legacy API logout
            'main.index',          # GET /
            'main.login_post',     # POST /login (web)
            'main.logout',         # GET /logout (web)
            'static',              # Archivos estáticos
            None                   # Peticiones sin endpoint definido
        ]
        
        if request.endpoint in public_endpoints:
            return None
        
        # Ignorar todas las peticiones a /static/
        if request.path and request.path.startswith('/static/'):
            return None
        
        # Consultar el flag de mantenimiento mediante el servicio
        try:
            maintenance_enabled = flag_service.is_maintenance_mode()
            maintenance_message = flag_service.get_maintenance_message()
        except Exception:
            # Si hay error al consultar la BD, permitir acceso
            return None

        # Si el modo mantenimiento NO está activo, continuar normalmente
        if not maintenance_enabled:
            return None
        
        # Flag activo: verificar permiso en lugar de nombre de rol
        user_id = session.get("user_id")
        
        # Si no está logueado, mostrar mantenimiento para rutas no públicas
        if not user_id:
            return render_template(
                "auth/mantenimiento.html",
                message=maintenance_message or "El sitio de administración está temporalmente inactivo."
            )
        
        # Solo los super administradores pueden acceder cuando el flag está activo
        try:
            user_dict = user_service.get_user(user_id)
            if user_dict.get('is_super_admin'):
                return None
        except Exception:
            pass
        
        # Usuario normal: mostrar página de mantenimiento
        return render_template(
            "auth/mantenimiento.html",
            message=maintenance_message or "El sitio de administración está temporalmente inactivo."
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
                user_dict = user_service.get_user(user_id)
                roles = user_dict.get('current_roles', [])
                role_names = [r.get('name', '') for r in roles]
                perms = user_service.get_user_permissions(user_id)
                name = user_dict.get('name') or ''
                last_name = user_dict.get('last_name') or ''
                initials = (f"{name[:1]}{last_name[:1]}".upper()) if name and last_name else "U"
                is_super_admin = bool(user_dict.get('is_super_admin'))
                return {
                    'current_user': user_dict,
                    'user_roles': role_names,
                    'user_permissions': perms,
                    'user_initials': initials,
                    'is_super_admin': is_super_admin,
                    # Consideramos admin si es super admin o tiene algún permiso de administración
                    'is_admin': is_super_admin or any(p in perms for p in ['get_all_users','create_user','update_user','delete_user','flag_admin'])
                }
            except Exception:
                pass
        return {
            'current_user': None,
            'user_roles': [],
            'user_initials': '',
            'is_admin': False,
            'is_super_admin': False
        }

