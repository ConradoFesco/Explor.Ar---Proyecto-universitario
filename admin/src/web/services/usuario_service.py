from src.web.models.user import User
from src.web.models.rol_user_user import RolUserUser
from ..extensions import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError
from werkzeug.security import generate_password_hash, check_password_hash

class UserService:
    def create_user(self, data_user, data_new_user, commit=True):
        required_fields = ['mail', 'name', 'last_name', 'password']
        if not all(field in data_new_user for field in required_fields):
            raise ValidationError("Faltan campos obligatorios")
        
        if User.query.filter_by(mail=data_new_user['mail']).first():
            raise ValidationError("Ya existe un usuario con ese mail")
        
        hashed_password = generate_password_hash(data_new_user['password'])

        mail = data_new_user.get('mail')
        name=data_new_user['name'],
        last_name=data_new_user['last_name'],
        active=data_new_user.get('active', True),
        deleted = False
        created_at = datetime.now()

        user = User(
            mail=mail,
            name=name,
            last_name=last_name,
            password=hashed_password,
            deleted=deleted,
            created_at=created_at,
        )
        user.user_roles.append(RolUserUser(Rol_User_id=1, User_id=user.id))
        try:
            db.session.add(user)
            if commit:
                db.session.commit()
            return user.to_dict()
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al crear el usuario: {e}")

    def get_user(self, user_id):
        user = User.query.filter_by(id=user_id, deleted=False).first()
        if not user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")
        return user.to_dict()

    def update_user(self, user_id, data_user, data_new, commit=True):
        """Actualiza un usuario existente"""
        user = User.query.get(user_id)
        if user is None:
            raise NotFoundError(f"Usuario no encontrado")
        
        # Campos que se pueden actualizar
        for field in ['mail', 'name', 'last_name', 'password']: #se puede actualizar el mail?
            if field in data_new: 
                setattr(user, field, data_new[field])
        
        try:
            if commit:
                db.session.commit()
            return user.to_dict()
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al actualizar el usuario: {e}")

    def delete_user(self, user_id, data_user, commit=True):
        """Baja lógica: marcar como eliminado"""
        user = User.query.filter_by(id=user_id, deleted=False).first()
        if not user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")
        
        user.deleted = True
        try:
            if commit:
                db.session.commit()
            return {"message": f"Usuario {user_id} eliminado correctamente"}
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al eliminar el usuario: {e}")

    def list_users(self):
        """Consultar todos los usuarios no eliminados"""
        users = User.query.filter_by(deleted=False).all()
        return [user.to_dict() for user in users]

# Instancia global para usar en la app
user_service = UserService()