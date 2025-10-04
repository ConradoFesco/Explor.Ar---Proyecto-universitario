from src.web.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from .. import exceptions as exc
from ..extensions import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError

class AuthService:
    def login(self, mail, password):
        user = User.query.filter_by(mail=mail).first()
        if not user or not  user.check_password(password):
            raise exc.ValidationError("Credenciales inválidas")
        
        # Verificar si el usuario está bloqueado
        if user.blocked:
            raise exc.ValidationError("Usted ha sido bloqueado")
        
        return user
    

auth_service = AuthService()