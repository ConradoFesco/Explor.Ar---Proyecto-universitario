from src.core.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from src.web import exceptions as exc
from src.web.extensions import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError

class AuthService:
    def login(self, mail, password):
        user = User.query.filter_by(mail=mail, deleted=False).first()
        if not user or not  user.check_password(password):
            raise exc.ValidationError("Credenciales inválidas")
        
        # Verificar si el usuario está bloqueado
        if user.blocked:
            raise exc.ValidationError("Usted ha sido bloqueado")
        
        return user
    def find_user_by_email(self, mail):
        """
        Devuelve el usuario sin validar contraseña.
        """
        return User.query.filter_by(mail=mail, deleted=False).first()

auth_service = AuthService()