"""
Autenticación y búsqueda de usuarios para el flujo de login.
"""
import secrets
from src.core.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from src.web import exceptions as exc
from src.web.extensions import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from src.core.models.rol_user import RolUser
from src.core.models.rol_user_user import RolUserUser

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


    # --- Método para "buscar o crear" al usuario en tu base de datos ---
    def find_or_create_google_user(self, user_info):
        """
        Busca un usuario por su email. Si no existe, lo crea.
        """
        mail = user_info.get('email')
        if not mail :
            raise exc.ValidationError("No se pudo obtener el mail de Google")
        # 1. Busca al usuario en tu base de datos
        new_name = user_info.get('given_name')
        new_last_name = user_info.get('family_name')
        new_avatar_url = user_info.get('picture')
        user = User.query.filter_by(mail=mail, deleted=False).first()
        
        if user:
            # 2. Si existe (LOGIN), actualiza sus datos por si cambiaron
            if user.name != new_name:
                user.name = new_name
            if user.last_name != new_last_name:
                user.last_name = new_last_name
            if user.avatar_url != new_avatar_url:
                user.avatar_url = new_avatar_url
        else:
            # 3. Si no existe (REGISTRO), crea uno nuevo
            user = User(
                mail=mail,
                name=new_name,
                last_name=new_last_name,
                avatar_url=new_avatar_url,
            )
            default_rol = RolUser.query.filter_by(name='Comun').first()
            if default_rol:
                # Forma correcta
                user.user_roles.append(RolUserUser(User_id=user.id, Rol_User_id=default_rol.id))
            db.session.add(user)
        # 4. Guarda los cambios (sea un update o un create)
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al crear el usuario: {e}")
        return user

auth_service = AuthService()