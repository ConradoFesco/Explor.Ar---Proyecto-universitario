from datetime import datetime
from src.web.models.flag import Flag
from src.web.models.user import User
from src.web.extensions import db

class FlagService:
    def get_all_flags(self):
        """
        Devuelve todos los flags del sistema ordenados por id.
        """
        return Flag.query.order_by(Flag.id).all()

    def toggle_flag(self, flag_id, actor): # Recibe el actor y lo pasa al modelo
        flag = Flag.query.get_or_404(flag_id)
        new_state = not flag.enabled 
        flag.set_enabled(new_state, actor=actor)
        db.session.commit()
        return flag

    def update_flag_message(self, flag_id, message, actor): # Recibe el actor y lo pasa al modelo
        flag = Flag.query.get_or_404(flag_id)
        flag.set_enabled(flag.enabled, actor=actor, msg=message)
        db.session.commit()
        return flag

flag_service = FlagService()