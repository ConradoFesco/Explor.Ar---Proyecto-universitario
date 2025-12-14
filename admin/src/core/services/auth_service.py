"""
Autenticación y búsqueda de usuarios para el flujo de login.
"""
import secrets
from src.core.models.user import User, PrivateUser, PublicUser
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
        Solo busca en usuarios privados ya que son los únicos con password.

        Args:
            mail (str): Email.
            password (str): Contraseña en texto plano.

        Returns:
            PrivateUser: Usuario autenticado.

        Raises:
            ValidationError: Credenciales inválidas o usuario bloqueado.
        """
        user = PrivateUser.query.filter_by(mail=mail, deleted=False).first()
        if not user or not user.check_password(password):
            raise exc.ValidationError("Credenciales inválidas")
        
        if user.blocked:
            raise exc.ValidationError("Usted ha sido bloqueado")
        
        return user
    
    def find_user_by_email(self, mail):
        """
        Devuelve el usuario por email (sin validar contraseña).
        Busca primero en usuarios privados, luego en públicos.
        Puede retornar cualquier tipo de usuario (público o privado).
        
        Nota: Si existe tanto un PrivateUser como un PublicUser con el mismo mail,
        retornará el PrivateUser (prioridad a usuarios privados).
        """
        user = PrivateUser.query.filter_by(mail=mail, deleted=False).first()
        if user:
            return user
        return PublicUser.query.filter_by(mail=mail, deleted=False).first()

    def find_or_create_google_user(self, user_info):
        """
        Busca un usuario público por su email. Si no existe, lo crea como PublicUser.
        Los usuarios de Google OAuth son siempre públicos.
        
        Nota: Puede existir un PrivateUser con el mismo mail, ya que el mail es único
        solo dentro de cada tipo de usuario (PrivateUser o PublicUser), no globalmente.
        """
        mail = user_info.get('email')
        if not mail:
            raise exc.ValidationError("No se pudo obtener el mail de Google")
        
        new_name = user_info.get('given_name') or user_info.get('name') or 'Usuario'
        new_last_name = user_info.get('family_name') or ''
        new_avatar_url = user_info.get('picture')
        
        user = PublicUser.query.filter_by(mail=mail, deleted=False).first()
        
        if user:
            if new_name and user.name != new_name:
                user.name = new_name
            if new_last_name and user.last_name != new_last_name:
                user.last_name = new_last_name
            if new_avatar_url and user.avatar_url != new_avatar_url:
                user.avatar_url = new_avatar_url
        else:
            user = PublicUser(
                mail=mail,
                name=new_name,
                last_name=new_last_name,
                avatar_url=new_avatar_url
            )
            db.session.add(user)
        
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al crear el usuario: {e}")
        return user

auth_service = AuthService()