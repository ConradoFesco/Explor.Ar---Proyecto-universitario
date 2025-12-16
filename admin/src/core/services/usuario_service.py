"""
Servicios de dominio para gestión de usuarios y roles.
Provee operaciones CRUD, roles y seguridad para ambos brazos (Web/API).
Gestiona únicamente usuarios privados (PrivateUser) ya que los públicos no tienen roles ni permisos.
"""
from src.core.models.user import User, PrivateUser
from src.core.models.rol_user import RolUser
from src.core.models.rol_user_user import RolUserUser
from src.core.models.permission import Permission
from src.web.extensions import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Set
from src.core.validators.user_validator import (
    validate_create_user,
    validate_update_user,
    validate_role_ids,
)
from src.core.validators.listing_validator import validate_user_list_params
from src.core.validators.profile_validator import validate_new_password

class UserService:
    """Casos de uso relacionados a usuarios privados (crear, listar, actualizar, roles, bloqueo)."""

    @staticmethod
    def _require_super_admin(actor_id: int, action: str = "realizar esta acción") -> PrivateUser:
        """
        Valida que el actor es un SuperAdmin.
        
        Args:
            actor_id: ID del usuario que intenta realizar la acción
            action: Descripción de la acción (para mensaje de error)
        
        Returns:
            PrivateUser: Usuario SuperAdmin validado
        
        Raises:
            ValidationError: Si el usuario no es SuperAdmin
        """
        from src.core.validators.api_validator import validate_positive_int
        
        actor_id = validate_positive_int(actor_id, "actor_id")
        actor = PrivateUser.query.filter_by(id=actor_id, deleted=False).first()
        if not actor or not actor.is_super_admin:
            raise ValidationError(f"Solo un SuperAdmin puede {action}")
        return actor
    
    @staticmethod
    def fetch_user_permissions(user_id: int) -> Set[str]:
        """
        Obtiene todos los permisos de un usuario mediante una consulta SQL optimizada.
        Usa JOINs para evitar N+1 queries.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            Set[str]: Conjunto de nombres de permisos del usuario
        """
        from src.core.models.permission_rol_user import PermissionRolUser
        from src.core.models.rol_user_user import RolUserUser
        
        permission_names = (
            db.session.query(Permission.name)
            .join(PermissionRolUser, Permission.id == PermissionRolUser.Permission_id)
            .join(RolUser, PermissionRolUser.Rol_User_id == RolUser.id)
            .join(RolUserUser, RolUser.id == RolUserUser.Rol_User_id)
            .filter(RolUserUser.User_id == user_id)
            .filter(Permission.deleted == False)
            .distinct()
            .all()
        )
        
        return {name for name, in permission_names}
    
    @staticmethod
    def hydrate_user_permissions(user: PrivateUser) -> None:
        """
        Busca los permisos del usuario y se los inyecta in-place.
        Encapsula la lógica de hidratación para mantener el código más declarativo.
        
        Args:
            user (PrivateUser): Usuario a hidratar con permisos
        """
        permissions = UserService.fetch_user_permissions(user.id)
        user.set_permissions(permissions)
    
    def create_user(self, data_user, data_new_user, commit=True):
        """
        Crea un usuario con roles iniciales.

        Args:
            data_user (int): ID del admin que realiza la acción.
            data_new_user (dict): Campos del nuevo usuario (mail, name, last_name, password, roles?).
            commit (bool): Confirmar transacción.

        Returns:
            dict: Usuario creado.

        Raises:
            ValidationError/DatabaseError según corresponda.
        """
        cleaned = validate_create_user(data_new_user)
        hashed_password = generate_password_hash(cleaned['password'])

        mail = cleaned['mail']
        name = cleaned['name']
        last_name = cleaned['last_name']
        active = data_new_user.get('active', True)
        blocked = data_new_user.get('blocked', False)
        role_ids = data_new_user.get('roles', [])
        role_ids = validate_role_ids(role_ids) if role_ids else []
        if not role_ids:
            raise ValidationError("Debe seleccionar al menos un rol para el usuario")
        deleted = False
        created_at = datetime.now()
        is_super_admin = bool(data_new_user.get('is_super_admin'))
        if is_super_admin:
            self._require_super_admin(data_user, "crear otro SuperAdmin")

        user = PrivateUser(
            mail=mail,
            name=name,
            last_name=last_name,
            password=hashed_password,
            active=active,
            blocked=blocked,
            deleted=deleted,
            created_at=created_at,
            is_super_admin=is_super_admin,
        )

        for role_id in role_ids:
            role = RolUser.query.get(role_id)
            if not role:
                raise ValidationError(f"Rol con ID {role_id} no encontrado")
            user.user_roles.append(RolUserUser(Rol_User_id=role_id))
        
        try:
            db.session.add(user)
            if commit:
                db.session.commit()
            return user.to_dict()
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al crear el usuario: {e}")

    def get_user(self, user_id):
        """
        Obtiene un usuario privado no eliminado con roles actuales.
        Hidrata los permisos del usuario antes de retornarlo.

        Args:
            user_id (int): ID del usuario.

        Returns:
            dict: Usuario con 'current_roles'.

        Raises:
            NotFoundError: Si no existe.
        """
        user = PrivateUser.query.filter_by(id=user_id, deleted=False).first()
        if not user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")
        
        # Hidratar permisos del usuario
        self.hydrate_user_permissions(user)
        
        user_dict = user.to_dict()
        user_dict['current_roles'] = self.get_user_roles(user_id)
        return user_dict

    def update_user(self, user_id, changed_fields, admin_user_id=None, commit=True):
        """
        Actualiza campos de un usuario.

        Args:
            user_id (int): ID del usuario.
            changed_fields (dict): Campos a modificar.
            admin_user_id (int|None): Actor para validaciones de superAdmin.
            commit (bool): Confirmar transacción.

        Returns:
            dict: Usuario actualizado.

        Raises:
            NotFoundError/ValidationError/DatabaseError.
        """
        user = PrivateUser.query.get(user_id)
        if user is None:
            raise NotFoundError(f"Usuario no encontrado")
        
        if user and user.is_super_admin:
            if admin_user_id and user_id != admin_user_id:
                raise ValidationError("No se puede editar un usuario administrador desde el listado de usuarios")

        cleaned = validate_update_user(changed_fields or {})

        if 'mail' in cleaned and cleaned['mail'] != user.mail:
            existing_user = PrivateUser.query.filter_by(mail=cleaned['mail'], deleted=False).first()
            if existing_user and existing_user.id != user_id:
                raise ValidationError("Ya existe un usuario privado con ese mail")

        if "name" in cleaned:
            user.name = cleaned["name"]

        if "last_name" in cleaned:
            user.last_name = cleaned["last_name"]

        if "mail" in cleaned:
            user.mail = cleaned["mail"]

        if "active" in cleaned:
            user.active = cleaned["active"]
        
        if "blocked" in cleaned:
            if cleaned["blocked"] and user and user.is_super_admin:
                raise ValidationError("No se pueden bloquear usuarios administradores")
            user.blocked = cleaned["blocked"]
        
        if "is_super_admin" in cleaned:
            if not admin_user_id:
                raise ValidationError("Se requiere un usuario administrador para esta acción")
            self._require_super_admin(admin_user_id, "modificar este atributo")
            user.is_super_admin = cleaned["is_super_admin"]
        
        if "password" in cleaned:
            user.password = generate_password_hash(cleaned["password"])

        try:
            if commit:
                db.session.commit()
            return user.to_dict()
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al actualizar el usuario: {e}")

    def delete_user(self, user_id, admin_user_id, commit=True):
        """
        Baja lógica de un usuario privado, registrando actor.
        Solo gestiona usuarios privados de la aplicación.

        Regla de negocio:
        - Un usuario no puede eliminarse a sí mismo.
        - Solo un SuperAdmin puede eliminar a otro SuperAdmin.

        Args:
            user_id (int): ID del usuario privado a eliminar.
            admin_user_id (int): ID del administrador que ejecuta la acción.
            commit (bool): Confirmar transacción.

        Returns:
            dict: Mensaje de resultado.

        Raises:
            NotFoundError/ValidationError/DatabaseError.
        """
        user = PrivateUser.query.filter_by(id=user_id, deleted=False).first()
        if not user:
            raise NotFoundError(f"Usuario privado con id {user_id} no encontrado")

        if user_id == admin_user_id:
            raise ValidationError("No puedes eliminarte a ti mismo")

        admin_user = PrivateUser.query.get(admin_user_id)

        if user.is_super_admin:
            if not admin_user or not admin_user.is_super_admin:
                raise ValidationError("Solo usuarios SuperAdmin pueden eliminar a un SuperAdmin")

        user.active = False
        user.deleted = True
        user.deleted_at = datetime.utcnow()
        user.deleted_by_id = admin_user_id

        try:
            if commit:
                db.session.commit()
            return {"message": f"El usuario '{user.mail}' ha sido eliminado correctamente."}
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al eliminar el usuario: {e}")

    def update_password(self, user_id, new_password, commit=True):
        """
        Actualiza la contraseña del usuario, validando que cambie.

        Args:
            user_id (int): ID del usuario.
            new_password (str): Nueva contraseña en texto plano.
            commit (bool): Confirmar transacción.

        Returns:
            dict: Mensaje de éxito.

        Raises:
            NotFoundError/ValidationError/DatabaseError.
        """
        user = PrivateUser.query.get(user_id)
        if user is None:
            raise NotFoundError("Usuario no encontrado")

        new_password = validate_new_password(new_password)

        if not user.password or check_password_hash(user.password, new_password):
            raise ValidationError("La nueva contraseña no puede ser igual a la actual")

        user.password = generate_password_hash(new_password)

        try:
            if commit:
                db.session.commit()
            return {"message": "Contraseña actualizada correctamente"}
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al actualizar contraseña: {e}")

    def list_users(self, filters=None, page=1, per_page=25, sort_by='created_at', sort_order='desc'):
        """
        Lista usuarios con filtros, orden y paginación.

        Returns:
            dict: {'users': [...], 'pagination': {...}}
        """
        filters = filters or {}
        v = validate_user_list_params(
            page=page,
            per_page=per_page,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        page = v['page']
        per_page = v['per_page']
        filters = v['filters']
        sort_by = v['sort_by']
        sort_order = v['sort_order']

        query = PrivateUser.query.filter_by(deleted=False)
        
        if filters:
            if filters.get('email'):
                query = query.filter(User.mail.ilike(f"{filters['email']}%"))
            if filters.get('activo') is not None:
                query = query.filter_by(active=filters['activo'])
            if filters.get('blocked') is not None:
                query = query.filter_by(blocked=filters['blocked'])
            if filters.get('rol'):
                from src.core.models.rol_user_user import RolUserUser
                from src.core.models.rol_user import RolUser
                query = query.join(RolUserUser).join(RolUser).filter(RolUser.name.ilike(f"%{filters['rol']}%"))

        if sort_by == 'created_at':
            if sort_order == 'desc':
                query = query.order_by(User.created_at.desc())
            else:
                query = query.order_by(User.created_at.asc())
        elif sort_by == 'name':
            if sort_order == 'desc':
                query = query.order_by(User.name.desc(), User.last_name.desc())
            else:
                query = query.order_by(User.name.asc(), User.last_name.asc())

        try:
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        except Exception as e:
            raise DatabaseError(f"Error al listar usuarios: {e}")
        users = pagination.items

        users_with_roles = []
        for user in users:
            user_dict = user.to_dict()
            if isinstance(user, PrivateUser):
                user_dict['roles'] = user.get_user_roles()
            else:
                user_dict['roles'] = []
            users_with_roles.append(user_dict)

        return {
            'users': users_with_roles,
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
        """
        Asigna un rol a un usuario.

        Raises:
            NotFoundError/ValidationError/DatabaseError.
        """
        admin_user = PrivateUser.query.get(admin_user_id)
        if not admin_user:
            raise NotFoundError("Usuario administrador no encontrado")
        
        target_user = PrivateUser.query.get(user_id)
        if not target_user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")

        role = RolUser.query.get(role_id)
        if not role:
            raise NotFoundError(f"Rol con id {role_id} no encontrado")
        
        if target_user and target_user.is_super_admin:
            self._require_super_admin(admin_user_id, "asignar roles a otros administradores")

        existing_assignment = RolUserUser.query.filter_by(
            User_id=user_id, 
            Rol_User_id=role_id
        ).first()

        if existing_assignment:
            raise ValidationError("El usuario ya tiene asignado este rol")

        role_assignment = RolUserUser(
            User_id=user_id,
            Rol_User_id=role_id
        )

        try:
            db.session.add(role_assignment)
            if commit:
                db.session.commit()
            
            # Invalidar cache y recargar permisos del usuario
            target_user.invalidate_permissions_cache()
            self.hydrate_user_permissions(target_user)
            
            return {"message": f"Rol '{role.name}' asignado correctamente al usuario"}
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al asignar el rol: {e}")

    def revoke_role_from_user(self, user_id, role_id, admin_user_id, commit=True):
        """
        Revoca un rol de un usuario.

        Raises:
            NotFoundError/ValidationError/DatabaseError.
        """
        admin_user = PrivateUser.query.get(admin_user_id)
        if not admin_user:
            raise NotFoundError("Usuario administrador no encontrado")

        target_user = PrivateUser.query.get(user_id)
        if not target_user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")

        role = RolUser.query.get(role_id)
        if not role:
            raise NotFoundError(f"Rol con id {role_id} no encontrado")
        
        if target_user and target_user.is_super_admin:
            self._require_super_admin(admin_user_id, "revocar roles de otros administradores")

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
            
            # Invalidar cache y recargar permisos del usuario
            target_user.invalidate_permissions_cache()
            self.hydrate_user_permissions(target_user)
            
            return {"message": f"Rol '{role.name}' revocado correctamente del usuario"}
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al revocar el rol: {e}")

    def get_user_roles(self, user_id):
        """
        Devuelve roles asignados a un usuario.

        Returns:
            list[dict]: [{'id', 'name', 'assigned_at'}]
        """
        user = PrivateUser.query.get(user_id)
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

    def get_user_permissions(self, user_id):
        """Devuelve la lista de nombres de permisos asignados al usuario (vía sus roles)."""
        user = PrivateUser.query.get(user_id)
        if not user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")
        if user.is_super_admin:
            return [perm.name for perm in Permission.query.all()]
        permissions = set()
        for role_rel in user.user_roles:
            role = role_rel.rol_user
            for perm_rel in getattr(role, 'permission_rol_users', []):
                perm = getattr(perm_rel, 'permission', None)
                if perm and getattr(perm, 'name', None):
                    permissions.add(perm.name)
        return list(permissions)

    def get_available_roles(self):
        """Lista roles disponibles"""
        roles = RolUser.query.filter_by(deleted=False).all()
        return [role.to_dict() for role in roles]

    def update_user_roles(self, user_id, role_ids, admin_user_id, commit=True):
        """
        Reemplaza los roles del usuario.

        Raises:
            NotFoundError/ValidationError/DatabaseError.
        """
        admin_user = PrivateUser.query.get(admin_user_id)
        if not admin_user:
            raise NotFoundError("Usuario administrador no encontrado")

        target_user = PrivateUser.query.get(user_id)
        if not target_user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")
        
        if target_user and target_user.is_super_admin:
            if user_id != admin_user_id:
                raise ValidationError("No se pueden modificar los roles de un usuario administrador")
                self._require_super_admin(admin_user_id, "modificar los roles de un usuario administrador")

        try:
            RolUserUser.query.filter_by(User_id=user_id).delete()

            for role_id in role_ids:
                role = RolUser.query.get(role_id)
                if not role:
                    raise ValidationError(f"Rol con id {role_id} no encontrado")

                role_assignment = RolUserUser(
                    User_id=user_id,
                    Rol_User_id=role_id
                )
                db.session.add(role_assignment)
            
            if commit:
                db.session.commit()
            
            # Invalidar cache y recargar permisos del usuario
            target_user.invalidate_permissions_cache()
            self.hydrate_user_permissions(target_user)
            
            return {"message": "Roles actualizados correctamente"}
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al actualizar roles: {e}")

    def block_user(self, user_id, admin_user_id, commit=True):
        """
        Bloquea un usuario privado no administrador.
        """
        admin_user = PrivateUser.query.get(admin_user_id)
        if not admin_user:
            raise NotFoundError("Usuario administrador no encontrado")

        target_user = PrivateUser.query.get(user_id)
        if not target_user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")
        
        if target_user and target_user.is_super_admin:
            raise ValidationError("No se pueden bloquear usuarios administradores")

        if target_user.blocked:
            raise ValidationError("El usuario ya está bloqueado")

        target_user.blocked = True

        try:
            if commit:
                db.session.commit()
            return {"message": f"Usuario bloqueado correctamente"}
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al bloquear el usuario: {e}")

    def unblock_user(self, user_id, admin_user_id, commit=True):
        """
        Desbloquea un usuario privado bloqueado que no sea administrador.
        """
        admin_user = PrivateUser.query.get(admin_user_id)
        if not admin_user:
            raise NotFoundError("Usuario administrador no encontrado")

        target_user = PrivateUser.query.get(user_id)
        if not target_user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")
        
        if target_user and target_user.is_super_admin:
            raise ValidationError("No se pueden desbloquear usuarios administradores")

        if not target_user.blocked:
            raise ValidationError("El usuario ya está desbloqueado")

        target_user.blocked = False

        try:
            if commit:
                db.session.commit()
            return {"message": f"Usuario desbloqueado correctamente"}
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al desbloquear el usuario: {e}")


user_service = UserService()