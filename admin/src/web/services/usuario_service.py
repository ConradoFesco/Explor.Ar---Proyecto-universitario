from src.web.models.user import User
from src.web.models.rol_user import RolUser
from src.web.models.rol_user_user import RolUserUser
from src.web.extensions import db
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

    def update_user(self, user_id, data, commit=True):
        """Actualiza un usuario existente"""
        user = User.query.get(user_id)
        if user is None:
            raise NotFoundError(f"Usuario no encontrado")
        
        # Campos que se pueden actualizar
        for field in ['mail', 'name', 'last_name', 'password']: #se puede actualizar el mail?
             if field == "password":
                setattr(user, field, generate_password_hash(data_new[field]))
             else:
                setattr(user, field, data_new[field])

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
            
    def update_password(self, user_id, new_password, commit=True):
        user = User.query.get(user_id)
        if user is None:
            raise NotFoundError("Usuario no encontrado")
        
        user.password = generate_password_hash(new_password)

        try:
            if commit:
                db.session.commit()
            return {"message": "Contraseña actualizada correctamente"}
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al actualizar contraseña: {e}")

    def list_users(self, filters=None, page=1, per_page=25, sort_by='created_at', sort_order='desc'):
        """Consultar usuarios no eliminados con filtros, paginación y ordenamiento"""
        
        # Construir query base
        query = User.query.filter_by(deleted=False)
        
        # Aplicar filtros
        if filters:
            if filters.get('email'):
                query = query.filter(User.mail.ilike(f"%{filters['email']}%"))
            if filters.get('activo'):
                active_value = filters['activo'].lower() in ['si', 'sí', 'true', '1']
                query = query.filter_by(active=active_value)
            # Filtro de rol deshabilitado - no se modifica el modelo de BDD
            # if filters.get('rol'):
            #     query = query.filter(User.role.ilike(f"%{filters['rol']}%"))
        
        # Aplicar ordenamiento
        if sort_by == 'created_at':
            if sort_order == 'desc':
                query = query.order_by(User.created_at.desc())
            else:  # asc
                query = query.order_by(User.created_at.asc())
        elif sort_by == 'name':
            if sort_order == 'desc':
                query = query.order_by(User.name.desc(), User.last_name.desc())
            else:  # asc
                query = query.order_by(User.name.asc(), User.last_name.asc())
        
        # Aplicar paginación
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        users = pagination.items
        
        return {
            'users': [user.to_dict() for user in users],
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'next_num': pagination.next_num,
                'prev_num': pagination.prev_num
            }
        }

    def assign_role_to_user(self, user_id, role_id, admin_user_id, commit=True):
        """Asigna un rol a un usuario (solo administradores pueden hacerlo)"""
        # Verificar que el usuario administrador existe y tiene permisos
        admin_user = User.query.get(admin_user_id)
        if not admin_user:
            raise NotFoundError("Usuario administrador no encontrado")
        
        # Verificar que el usuario objetivo existe
        target_user = User.query.get(user_id)
        if not target_user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")
        
        # Verificar que el rol existe
        role = RolUser.query.get(role_id)
        if not role:
            raise NotFoundError(f"Rol con id {role_id} no encontrado")
        
        # Verificar que el usuario objetivo no es administrador
        if self._is_admin_user(target_user):
            raise ValidationError("No se pueden asignar roles a otros administradores")
        
        # Verificar que el rol no está ya asignado
        existing_assignment = RolUserUser.query.filter_by(
            User_id=user_id, 
            Rol_User_id=role_id
        ).first()
        
        if existing_assignment:
            raise ValidationError("El usuario ya tiene asignado este rol")
        
        # Crear la asignación
        role_assignment = RolUserUser(
            User_id=user_id,
            Rol_User_id=role_id
        )
        
        try:
            db.session.add(role_assignment)
            if commit:
                db.session.commit()
            return {"message": f"Rol '{role.name}' asignado correctamente al usuario"}
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al asignar el rol: {e}")

    def revoke_role_from_user(self, user_id, role_id, admin_user_id, commit=True):
        """Revoca un rol de un usuario (solo administradores pueden hacerlo)"""
        # Verificar que el usuario administrador existe
        admin_user = User.query.get(admin_user_id)
        if not admin_user:
            raise NotFoundError("Usuario administrador no encontrado")
        
        # Verificar que el usuario objetivo existe
        target_user = User.query.get(user_id)
        if not target_user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")
        
        # Verificar que el rol existe
        role = RolUser.query.get(role_id)
        if not role:
            raise NotFoundError(f"Rol con id {role_id} no encontrado")
        
        # Verificar que el usuario objetivo no es administrador
        if self._is_admin_user(target_user):
            raise ValidationError("No se pueden revocar roles de otros administradores")
        
        # Buscar la asignación existente
        role_assignment = RolUserUser.query.filter_by(
            User_id=user_id, 
            Rol_User_id=role_id
        ).first()
        
        if not role_assignment:
            raise ValidationError("El usuario no tiene asignado este rol")
        
        try:
            db.session.delete(role_assignment)
            if commit:
                db.session.commit()
            return {"message": f"Rol '{role.name}' revocado correctamente del usuario"}
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al revocar el rol: {e}")

    def get_user_roles(self, user_id):
        """Obtiene todos los roles asignados a un usuario"""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")
        
        roles = []
        for role_rel in user.user_roles:
            role = role_rel.rol_user
            roles.append({
                'id': role.id,
                'name': role.name,
                'assigned_at': getattr(role_rel, 'created_at', None)
            })
        
        return roles

    def get_available_roles(self):
        """Obtiene todos los roles disponibles en el sistema"""
        roles = RolUser.query.filter_by(deleted=False).all()
        return [role.to_dict() for role in roles]

    def _is_admin_user(self, user):
        """Verifica si un usuario es administrador basándose en sus permisos"""
        # Verificar si tiene el rol de administrador
        for role_rel in user.user_roles:
            role = role_rel.rol_user
            if role.name.lower() in ['administrador', 'admin']:
                return True
        return False

    def block_user(self, user_id, admin_user_id, commit=True):
        """Bloquea un usuario (solo usuarios con permiso user_block pueden hacerlo)"""
        # Verificar que el usuario administrador existe
        admin_user = User.query.get(admin_user_id)
        if not admin_user:
            raise NotFoundError("Usuario administrador no encontrado")
        
        # Verificar que el usuario objetivo existe
        target_user = User.query.get(user_id)
        if not target_user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")
        
        # Verificar que el usuario objetivo no es administrador
        if self._is_admin_user(target_user):
            raise ValidationError("No se pueden bloquear usuarios administradores")
        
        # Verificar si el usuario ya está bloqueado
        if target_user.blocked:
            raise ValidationError("El usuario ya está bloqueado")
        
        # Bloquear usuario
        target_user.blocked = True
        
        try:
            if commit:
                db.session.commit()
            return {"message": f"Usuario bloqueado correctamente"}
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al bloquear el usuario: {e}")

    def unblock_user(self, user_id, admin_user_id, commit=True):
        """Desbloquea un usuario (solo usuarios con permiso user_block pueden hacerlo)"""
        # Verificar que el usuario administrador existe
        admin_user = User.query.get(admin_user_id)
        if not admin_user:
            raise NotFoundError("Usuario administrador no encontrado")
        
        # Verificar que el usuario objetivo existe
        target_user = User.query.get(user_id)
        if not target_user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")
        
        # Verificar que el usuario objetivo no es administrador
        if self._is_admin_user(target_user):
            raise ValidationError("No se pueden desbloquear usuarios administradores")
        
        # Verificar si el usuario ya está desbloqueado
        if not target_user.blocked:
            raise ValidationError("El usuario ya está desbloqueado")
        
        # Desbloquear usuario
        target_user.blocked = False
        
        try:
            if commit:
                db.session.commit()
            return {"message": f"Usuario desbloqueado correctamente"}
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al desbloquear el usuario: {e}")

# Instancia global para usar en la app
user_service = UserService()