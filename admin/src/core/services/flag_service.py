"""
Servicios para Feature Flags: obtención, toggle, actualización de mensaje y consultas de mantenimiento.
"""
from datetime import datetime
from src.core.models.flag import Flag
from src.core.models.user import User
from src.web.extensions import db
from src.core.validators.utils import ensure_max_length

class FlagService:
    """Opera sobre flags del sistema, incluyendo modo mantenimiento del admin."""
    
    def get_all_flags(self):
        """Devuelve todos los flags del sistema ordenados por id."""
        return Flag.query.order_by(Flag.id).all()


    def set_flag_state(self, flag_id: int, enabled: bool, data_user: int, message: str | None = None):
        """Establece explícitamente el estado del flag (idempotente) y opcionalmente el mensaje.

        Valida longitud máxima del mensaje (<= 255).
        """
        flag = Flag.query.get_or_404(flag_id)
        user = User.query.get(data_user)
        if message is not None and not ensure_max_length(message, 255):
            raise ValueError("El mensaje no puede superar los 255 caracteres")
        changed = False
        if bool(flag.enabled) != bool(enabled):
            flag.set_enabled(bool(enabled), actor=user, msg=message)
            changed = True
        elif message is not None and (flag.message or '') != message:
            # Actualiza solo el mensaje manteniendo estado
            flag.set_enabled(flag.enabled, actor=user, msg=message)
            changed = True
        if changed:
            db.session.commit()
        return flag

    def update_flag_message(self, flag_id: int, message: str, data_user: int):
        """Actualiza solamente el mensaje del flag con validación de longitud."""
        if not ensure_max_length(message, 255):
            raise ValueError("El mensaje no puede superar los 255 caracteres")
        flag = Flag.query.get_or_404(flag_id)
        actor = User.query.get(data_user)
        flag.set_enabled(flag.enabled, actor=actor, msg=message)
        db.session.commit()
        return flag

    # Métodos obsoletos removidos: toggle_flag, update_flag_message

    def is_maintenance_mode(self):
        """Devuelve True si el modo mantenimiento está activado."""
        flag = Flag.query.filter_by(key="admin_maintenance_mode").first()
        return flag.enabled if flag else False

    # 🔹 NUEVA FUNCIÓN: obtener el mensaje de mantenimiento
    def get_maintenance_message(self):
        """Devuelve el mensaje del modo mantenimiento, si existe."""
        flag = Flag.query.filter_by(key="admin_maintenance_mode").first()
        return flag.message if flag else None

    def get_flag_by_key(self, key: str):
        """Obtiene un flag por su key."""
        return Flag.query.filter_by(key=key).first()

    def set_flag_state_by_key(self, key: str, enabled: bool, data_user: int, message: str | None = None):
        """Establece explícitamente el estado del flag por key (idempotente) y opcionalmente el mensaje.
        
        Args:
            key: La key del flag
            enabled: Estado deseado
            data_user: ID del usuario que realiza el cambio
            message: Mensaje opcional
            
        Returns:
            El flag actualizado
        """
        flag = Flag.query.filter_by(key=key).first()
        if not flag:
            raise ValueError(f"Flag con key '{key}' no encontrado")
        
        user = User.query.get(data_user)
        if not user:
            raise ValueError(f"Usuario con ID {data_user} no encontrado")
        
        if message is not None and not ensure_max_length(message, 255):
            raise ValueError("El mensaje no puede superar los 255 caracteres")
        
        changed = False
        if bool(flag.enabled) != bool(enabled):
            flag.set_enabled(bool(enabled), actor=user, msg=message)
            changed = True
        elif message is not None and (flag.message or '') != message:
            # Actualiza solo el mensaje manteniendo estado
            flag.set_enabled(flag.enabled, actor=user, msg=message)
            changed = True
        
        if changed:
            db.session.commit()
        return flag

    # Métodos específicos para portal maintenance
    def is_portal_maintenance_mode(self):
        """Devuelve True si el modo mantenimiento del portal público está activado."""
        flag = Flag.query.filter_by(key="portal_maintenance_mode").first()
        return flag.enabled if flag else False

    def get_portal_maintenance_message(self):
        """Devuelve el mensaje del modo mantenimiento del portal público, si existe."""
        flag = Flag.query.filter_by(key="portal_maintenance_mode").first()
        return flag.message if flag else None

flag_service = FlagService()