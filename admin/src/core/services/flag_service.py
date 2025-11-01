from datetime import datetime
from src.core.models.flag import Flag
from src.core.models.user import User
from src.web.extensions import db

class FlagService:
    
    def get_all_flags(self):
        """
        Devuelve todos los flags del sistema ordenados por id.
        """
        return Flag.query.order_by(Flag.id).all()


    def toggle_flag(self, flag_id, data_user): # Recibe el id del User
        flag = Flag.query.get_or_404(flag_id)
        new_state = not flag.enabled 
        user = User.query.get(data_user)
        flag.set_enabled(new_state, actor=user)
        db.session.commit()
        return flag

    def update_flag_message(self, flag_id, message, data_user):
        """
        Actualiza el mensaje de un flag sin cambiar su estado.
        
        Args:
            flag_id (int): ID del flag a actualizar
            message (str): Nuevo mensaje del flag
            actor (User): Objeto User que realiza la actualización
            
        Returns:
            Flag: El flag actualizado
        """
        flag = Flag.query.get_or_404(flag_id)
        # Mantiene el estado actual, solo actualiza el mensaje
        actor = User.query.get(data_user)
        flag.set_enabled(flag.enabled, actor=actor, msg=message)
        db.session.commit()
        return flag

    def is_maintenance_mode(self):
        """Devuelve True si el modo mantenimiento está activado."""
        flag = Flag.query.filter_by(key="admin_maintenance_mode").first()
        return flag.enabled if flag else False

    # 🔹 NUEVA FUNCIÓN: obtener el mensaje de mantenimiento
    def get_maintenance_message(self):
        """Devuelve el mensaje del modo mantenimiento, si existe."""
        flag = Flag.query.filter_by(key="admin_maintenance_mode").first()
        return flag.message if flag else None

flag_service = FlagService()