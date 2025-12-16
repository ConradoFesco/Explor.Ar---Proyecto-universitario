"""
Hooks de la aplicación Flask.
"""
from flask import request, session, render_template
from src.core.services.usuario_service import user_service
from src.core.services.flag_service import flag_service
from src.web.auth.decorators import get_current_user


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
        public_endpoints = [
            'login_bp.login',      
            'login_bp.logout',     
            'main.index',         
            'main.login_post',     
            'main.logout',        
            'static',              
            None                 
        ]
        
        if request.endpoint in public_endpoints:
            return None
        
        if request.path and request.path.startswith('/static/'):
            return None
        
        try:
            maintenance_flag = flag_service.get_flag_by_key("admin_maintenance_mode")
            maintenance_enabled = maintenance_flag.enabled if maintenance_flag else False
            maintenance_message = maintenance_flag.message if maintenance_flag else None
        except Exception:
            return None

        if not maintenance_enabled:
            return None
        
        user_id = session.get("user_id")
        
        if not user_id:
            return render_template(
                "auth/mantenimiento.html",
                message=maintenance_message or "El sitio de administración está temporalmente inactivo."
            )
        
        try:
            user_dict = user_service.get_user(user_id)
            if user_dict.get('is_super_admin'):
                return None
        except Exception:
            pass
        
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
        current_user = get_current_user()
        
        if current_user:
            try:
                user_id = current_user.id
                user_dict = user_service.get_user(user_id)
                roles = user_dict.get('current_roles', [])
                role_names = [r.get('name', '') for r in roles]
                perms = user_service.get_user_permissions(user_id)
                name = user_dict.get('name') or ''
                last_name = user_dict.get('last_name') or ''
                initials = (f"{name[:1]}{last_name[:1]}".upper()) if name and last_name else "U"
                is_super_admin = bool(user_dict.get('is_super_admin'))
                
                from src.core.models.user import PrivateUser
                if isinstance(current_user, PrivateUser):
                    user_service.hydrate_user_permissions(current_user)
                
                return {
                    'current_user': current_user,  # Pasar el objeto, no el diccionario
                    'user_roles': role_names,
                    'user_permissions': perms,
                    'user_initials': initials,
                    'is_super_admin': is_super_admin,
                }
            except Exception:
                pass
        
        return {
            'current_user': None,
            'user_roles': [],
            'user_initials': '',
            'is_super_admin': False
        }