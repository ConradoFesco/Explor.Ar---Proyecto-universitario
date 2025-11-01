"""
Autenticación y búsqueda de usuarios para el flujo de login.
"""
from src.core.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from src.web import exceptions as exc
from src.web.extensions import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError

class AuthService:
    """Servicio de autenticación: login y utilidades relacionadas."""
    def login(self, mail, password):
        """
        Autentica un usuario por email/contraseña.

        Args:
            mail (str): Email.
            password (str): Contraseña en texto plano.

        Returns:
            User: Usuario autenticado.

        Raises:
            ValidationError: Credenciales inválidas o usuario bloqueado.
        """
        user = User.query.filter_by(mail=mail, deleted=False).first()
        if not user or not  user.check_password(password):
            raise exc.ValidationError("Credenciales inválidas")
        
        # Verificar si el usuario está bloqueado
        if user.blocked:
            raise exc.ValidationError("Usted ha sido bloqueado")
        
        return user
    def find_user_by_email(self, mail):
        """Devuelve el usuario por email (sin validar contraseña)."""
        return User.query.filter_by(mail=mail, deleted=False).first()

auth_service = AuthService()