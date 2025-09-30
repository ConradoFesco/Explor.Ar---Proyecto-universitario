from src.web.models.user import User
from src.web.extensions import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError
from werkzeug.security import generate_password_hash, check_password_hash

class UserService:
    def create_user(self, data, commit=True):
        required_fields = ['email', 'first_name', 'last_name', 'password']
        if not all(field in data for field in required_fields):
            raise ValidationError("Faltan campos obligatorios")
        
        if User.query.filter_by(email=data['email']).first():
            raise ValidationError("Ya existe un usuario con ese email")
        
        hashed_password = generate_password_hash(data['password'])

        email = data.get('email')
        first_name=data['first_name'],
        last_name=data['last_name'],
        password=hashed_password,
        active=data.get('active', True),
        role=data.get('role', 'Usuario público')
        deleted = False
        created_at = datetime.now()

        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            deleted=deleted,
            created_at=created_at,
            role=data.ger('role', 'Usuario publico')
        )
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

    def update_user(self, user_id, data, commit=True):
        """Actualiza un usuario existente"""
        user = User.query.get(user_id)
        if user is None:
            raise NotFoundError(f"Usuario no encontrado")
        
        # Campos que se pueden actualizar
        for field in ['username', 'email', 'password']:
            if field in data:
                setattr(user, field, data[field])
        
        try:
            if commit:
                db.session.commit()
            return user.to_dict()
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al actualizar el usuario: {e}")

    def delete_user(self, user_id, commit=True):
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