"""
Servicios de dominio para gestión de usuarios y roles.
Provee operaciones CRUD, roles y seguridad para ambos brazos (Web/API).
"""
from src.core.models.user import User
from src.core.models.rol_user import RolUser
from src.core.models.rol_user_user import RolUserUser
from src.core.models.permission import Permission
from src.web.extensions import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError
from werkzeug.security import generate_password_hash, check_password_hash
from src.core.validators.user_validator import (
    validate_create_user,
    validate_update_user,
    validate_role_ids,
)
from src.core.validators.profile_validator import validate_new_password

class UserService:
    """Casos de uso relacionados a usuarios (crear, listar, actualizar, roles, bloqueo)."""
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
        # Validaciones de entrada
        cleaned = validate_create_user(data_new_user)
        hashed_password = generate_password_hash(cleaned['password'])

        mail = cleaned['mail']
        name = cleaned['name']
        last_name = cleaned['last_name']
        active = data_new_user.get('active', True)
        blocked = data_new_user.get('blocked', False)
        role_ids = data_new_user.get('roles', [])  # Lista de IDs de roles seleccionados
        role_ids = validate_role_ids(role_ids) if role_ids else []
        if not role_ids:
            raise ValidationError("Debe seleccionar al menos un rol para el usuario")
        deleted = False
        created_at = datetime.now()
        is_super_admin = bool(data_new_user.get('is_super_admin'))
        if is_super_admin:
            actor = User.query.filter_by(id=data_user, deleted=False).first()
            if not actor or not actor.is_super_admin:
                raise ValidationError("Solo un SuperAdmin puede crear otro SuperAdmin")

        user = User(
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
        
        # Asignar los roles seleccionados si se proporcionan
        if role_ids and len(role_ids) > 0:
            for role_id in role_ids:
                # Verificar que el rol existe
                role = RolUser.query.get(role_id)
                if not role:
                    raise ValidationError(f"Rol con ID {role_id} no encontrado")
                user.user_roles.append(RolUserUser(Rol_User_id=role_id))
        else:
            # Rol por defecto si no se especifica (usuario básico)
            default_role = RolUser.query.filter_by(name='usuario').first()
            if default_role:
                user.user_roles.append(RolUserUser(Rol_User_id=default_role.id))
        
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
        Obtiene un usuario no eliminado con roles actuales.

        Args:
            user_id (int): ID del usuario.

        Returns:
            dict: Usuario con 'current_roles'.

        Raises:
            NotFoundError: Si no existe.
        """
        user = User.query.filter_by(id=user_id, deleted=False).first()
        if not user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")
        
        user_dict = user.to_dict()
        # Agregar información de roles actuales
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
        user = User.query.get(user_id)
        if user is None:
            raise NotFoundError(f"Usuario no encontrado")
        
        # Verificar si el usuario a editar es Admin o SuperAdmin: solo puede auto-modificarse
        if self._is_admin_user(user):
            if admin_user_id and user_id != admin_user_id:
                raise ValidationError("No se puede editar un usuario administrador desde el listado de usuarios")
        
        # Validaciones de entrada
        cleaned = validate_update_user(changed_fields or {})

        # Unicidad de mail si se modifica
        if 'mail' in cleaned and cleaned['mail'] != user.mail:
            if User.query.filter_by(mail=cleaned['mail']).first():
                raise ValidationError("Ya existe un usuario con ese mail")

        # Actualizar solo los campos que vienen en cleaned
        if "name" in cleaned:
            user.name = cleaned["name"]

        if "last_name" in cleaned:
            user.last_name = cleaned["last_name"]

        if "mail" in cleaned:
            user.mail = cleaned["mail"]

        if "active" in cleaned:
            user.active = cleaned["active"]
        
        if "blocked" in cleaned:
            # Enforce: no se puede bloquear administradores/superadmins
            if cleaned["blocked"] and self._is_admin_user(user):
                raise ValidationError("No se pueden bloquear usuarios administradores")
            user.blocked = cleaned["blocked"]
        
        if "is_super_admin" in cleaned:
            if not admin_user_id:
                raise ValidationError("Se requiere un usuario administrador para esta acción")
            actor = User.query.get(admin_user_id)
            if not actor or not actor.is_super_admin:
                raise ValidationError("Solo un SuperAdmin puede modificar este atributo")
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

    def delete_user(self, user_id, commit=True):
        """
        Baja lógica del usuario.

        Args:
            user_id (int): ID del usuario.
            commit (bool): Confirmar transacción.

        Returns:
            dict: Mensaje de resultado.

        Raises:
            NotFoundError/DatabaseError.
        """
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

    def delete_user_with_reason(self, user_id, reason, admin_user_data, commit=True):
        """
        Elimina lógicamente un usuario, guardando motivo y actor.

        Args:
            user_id (int): ID del usuario a eliminar.
            reason (str): Motivo.
            admin_user_data (int|dict): ID o dict del admin actor.
            commit (bool): Confirmar transacción.

        Returns:
            str: Mensaje de éxito.

        Raises:
            NotFoundError/ValidationError/DatabaseError.
        """
        user = User.query.filter_by(id=user_id, deleted=False).first()
        if not user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")
        
        # Obtener el ID del administrador desde los datos de sesión
        admin_id = admin_user_data if isinstance(admin_user_data, int) else admin_user_data.get('id', 1)
        
        # Verificar que el administrador no intente eliminarse a sí mismo
        if user_id == admin_id:
            raise ValidationError("No puedes eliminarte a ti mismo")
        
        admin_user = User.query.get(admin_id)
        # Verificar si el usuario a eliminar es superAdmin
        if user.is_super_admin:
            if not admin_user or not admin_user.is_super_admin:
                raise ValidationError("Solo usuarios SuperAdmin pueden eliminar a un SuperAdmin")
        
        # Marcar como eliminado con información adicional
        user.active = False
        user.deleted = True
        user.deleted_at = datetime.utcnow()
        user.deletion_reason = reason
        user.deleted_by_id = admin_id
        
        try:
            if commit:
                db.session.commit()
            return f"El usuario '{user.mail}' ha sido eliminado correctamente."
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
        user = User.query.get(user_id)
        if user is None:
            raise NotFoundError("Usuario no encontrado")
        
        # Validación de formato/seguridad
        new_password = validate_new_password(new_password)
        # Verificar si la nueva contraseña es igual a la actual
        if check_password_hash(user.password, new_password):
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
        # Validaciones de entrada
        from src.core.validators.listing_validator import validate_user_list_params
        v = validate_user_list_params(page=int(page), per_page=int(per_page), filters=filters or {}, sort_by=sort_by, sort_order=sort_order)
        page = v['page']; per_page = v['per_page']; filters = v['filters']; sort_by = v['sort_by']; sort_order = v['sort_order']

        # Construir query base
        query = User.query.filter_by(deleted=False)
        
        # Aplicar filtros
        if filters:
            if filters.get('email'):
                query = query.filter(User.mail.ilike(f"{filters['email']}%"))
            if filters.get('activo') is not None:
                query = query.filter_by(active=bool(filters['activo']))
            if filters.get('blocked') is not None:
                query = query.filter_by(blocked=bool(filters['blocked']))
            if filters.get('rol'):
                from src.core.models.rol_user_user import RolUserUser
                from src.core.models.rol_user import RolUser
                query = query.join(RolUserUser).join(RolUser).filter(RolUser.name.ilike(f"%{filters['rol']}%"))
        
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
        
        # Agregar información de roles a cada usuario
        users_with_roles = []
        for user in users:
            user_dict = user.to_dict()
            user_dict['roles'] = user.get_user_roles()
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
        
        # Verificar que el administrador tiene permisos para asignar roles a administradores
        if self._is_admin_user(target_user) and not self._is_admin_user(admin_user):
            raise ValidationError("Solo los administradores pueden asignar roles a otros administradores")
        
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
        """
        Revoca un rol de un usuario.

        Raises:
            NotFoundError/ValidationError/DatabaseError.
        """
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
        
        # Verificar que el administrador tiene permisos para revocar roles de administradores
        if self._is_admin_user(target_user) and not self._is_admin_user(admin_user):
            raise ValidationError("Solo los administradores pueden revocar roles de otros administradores")
        
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
        """
        Devuelve roles asignados a un usuario.

        Returns:
            list[dict]: [{'id', 'name', 'assigned_at'}]
        """
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

    def get_user_permissions(self, user_id):
        """
        Devuelve la lista de nombres de permisos asignados al usuario (vía sus roles).
        """
        user = User.query.get(user_id)
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
        """
        Lista roles disponibles (respeta módulo de roles y permisos).
        """
        roles = RolUser.query.filter_by(deleted=False).all()
        return [role.to_dict() for role in roles]

    def _is_admin_user(self, user):
        """
        True si el usuario es superadmin o tiene rol admin.
        """
        if not user:
            return False
        if user.is_super_admin:
            return True
        for role_rel in user.user_roles:
            role = role_rel.rol_user
            if role.name.lower() == 'admin':
                return True
        return False
    
    def _is_super_admin(self, user):
        """
        True si el usuario tiene el atributo superadmin.
        """
        return bool(user and user.is_super_admin)

    def update_user_roles(self, user_id, role_ids, admin_user_id, commit=True):
        """
        Reemplaza los roles del usuario.

        Raises:
            NotFoundError/ValidationError/DatabaseError.
        """
        # Verificar que el usuario administrador existe
        admin_user = User.query.get(admin_user_id)
        if not admin_user:
            raise NotFoundError("Usuario administrador no encontrado")
        
        # Verificar que el usuario objetivo existe
        target_user = User.query.get(user_id)
        if not target_user:
            raise NotFoundError(f"Usuario con id {user_id} no encontrado")
        
        # Si el usuario objetivo es Admin o SuperAdmin, solo puede auto-modificar sus roles
        if self._is_admin_user(target_user) and user_id != admin_user_id:
            raise ValidationError("No se pueden modificar los roles de un usuario administrador")

        try:
            # Eliminar todos los roles actuales del usuario
            RolUserUser.query.filter_by(User_id=user_id).delete()
            
            # Agregar los nuevos roles
            for role_id in role_ids:
                # Verificar que el rol existe
                role = RolUser.query.get(role_id)
                if not role:
                    raise ValidationError(f"Rol con id {role_id} no encontrado")
                
                # Crear la nueva asignación
                role_assignment = RolUserUser(
                    User_id=user_id,
                    Rol_User_id=role_id
                )
                db.session.add(role_assignment)
            
            if commit:
                db.session.commit()
            return {"message": "Roles actualizados correctamente"}
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al actualizar roles: {e}")

    def block_user(self, user_id, admin_user_id, commit=True):
        """
        Bloquea un usuario no administrador.
        """
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
        """
        Desbloquea un usuario bloqueado que no sea administrador.
        """
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