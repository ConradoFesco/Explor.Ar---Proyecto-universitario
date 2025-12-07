#!/usr/bin/env python3
"""
Script para cargar permisos y roles en la base de datos
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.web import create_app
from src.web.extensions import db
from src.core.models.permission import Permission
from src.core.models.rol_user import RolUser
from src.core.models.permission_rol_user import PermissionRolUser
from src.core.models.rol_user_user import RolUserUser
from src.core.models.user import User

def create_permissions():
    """Crear los permisos necesarios para el sistema"""
    permissions = [
        # Permisos para sitios históricos
        "create_historic_site",
        "get_historic_site", 
        "get_all_historic_sites",
        "get_all_sites_for_map",
        "update_historic_site",
        "delete_historic_site",
        "add_tags",
        "update_tags",
        "get_filter_options",
        "export_historic_sites",
        
        # Permisos para usuarios
        "create_user",
        "get_user",
        "get_all_users", 
        "update_user",
        "delete_user",
        
        # Permisos para categorías
        "create_category",
        "get_category",
        "get_all_categories",
        "update_category", 
        "delete_category",
        
        # Permisos para tags
        "create_tag",
        "get_tag",
        "get_all_tags",
        "update_tag",
        "delete_tag",
        
        # Permisos para eventos
        "create_event",
        "get_event",
        "get_all_events",
        "update_event",
        "delete_event",
        
        # Permisos para estados
        "create_state",
        "get_state", 
        "get_all_states",
        "update_state",
        "delete_state",

        # Permisos para flags
        "flag_admin",
        
        # Permisos para exportación
        "export_historic_sites",
        
        # Permisos para perfil de usuario
        "view_profile",
        "update_password",
        # Permiso para moderar reseñas 
        "review_index","review_update","review_destroy"

    ]
    
    created_permissions = []
    for perm_name in permissions:
        existing = Permission.query.filter_by(name=perm_name).first()
        if not existing:
            perm = Permission(name=perm_name)
            db.session.add(perm)
            created_permissions.append(perm)
            print(f"✓ Permiso creado: {perm_name}")
        else:
            print(f"- Permiso ya existe: {perm_name}")
    
    return created_permissions

def create_roles():
    """Crear los roles del sistema"""
    roles = {
        "admin": "Administrador del sistema - acceso completo",
        "editor": "Editor - puede crear, editar y eliminar contenido",
        "moderator": "Moderador - puede revisar y moderar reseñas",
        
        "usuario": "Usuario autenticado - solo puede ver contenido"
    }
    
    created_roles = {}
    for role_name, description in roles.items():
        existing = RolUser.query.filter_by(name=role_name).first()
        if not existing:
            role = RolUser(name=role_name)
            db.session.add(role)
            created_roles[role_name] = role
            print(f"✓ Rol creado: {role_name} - {description}")
        else:
            created_roles[role_name] = existing
            print(f"- Rol ya existe: {role_name}")
    
    return created_roles

def assign_permissions_to_roles(roles):
    """Asignar permisos a los roles"""
    
    # Definir qué permisos tiene cada rol
    role_permissions = {
        "admin": [
            # Todos los permisos excepto gestión de flags
            "create_historic_site", "get_historic_site", "get_all_historic_sites", 
            "get_all_sites_for_map", "update_historic_site", "delete_historic_site",
            "add_tags", "update_tags", "get_filter_options", "export_historic_sites",
            "create_user", "get_user", "get_all_users", "update_user", "delete_user",
            "create_category", "get_category", "get_all_categories", "update_category", "delete_category",
            "create_tag", "get_tag", "get_all_tags", "update_tag", "delete_tag",
            "create_event", "get_event", "get_all_events", "update_event", "delete_event",
            "create_state", "get_state", "get_all_states", "update_state", "delete_state",
            "view_profile", "update_password", "review_index","review_update","review_destroy"
        ],
        "editor": [
            # Permisos para gestionar contenido
            "create_historic_site", "get_historic_site", "get_all_historic_sites",
            "get_all_sites_for_map", "update_historic_site", "delete_historic_site",
            "add_tags", "update_tags", "get_filter_options",
            "create_category", "get_category", "get_all_categories", "update_category", "delete_category",
            "create_tag", "get_tag", "get_all_tags", "update_tag", "delete_tag",
            "create_event", "get_event", "get_all_events", "update_event", "delete_event",
            "create_state", "get_state", "get_all_states", "update_state", "delete_state",
            "view_profile", "update_password", "review_index","review_update","review_destroy"
        ],
        "moderador": [
            # permisos limitados pero incluye moderación
            "get_historic_site", "get_all_historic_sites", "get_all_sites_for_map",
            "view_profile", "update_password", "review_index","review_update","review_destroy"
        ],
        "usuario": [
            # Permisos básicos para usuarios autenticados
            "get_historic_site", "get_all_historic_sites", "get_all_sites_for_map",
            "get_category", "get_all_categories", "get_tag", "get_all_tags",
            "get_state", "get_all_states", "get_event", "get_all_events",
            "view_profile", "update_password"
        ]

    }
    
    for role_name, permission_names in role_permissions.items():
        role = roles.get(role_name)
        if not role:
            continue
            
        for perm_name in permission_names:
            # Buscar el permiso
            permission = Permission.query.filter_by(name=perm_name).first()
            if not permission:
                print(f"⚠️  Permiso no encontrado: {perm_name}")
                continue
            
            # Verificar si ya existe la relación
            existing = PermissionRolUser.query.filter_by(
                Permission_id=permission.id,
                Rol_User_id=role.id
            ).first()
            
            if not existing:
                # Crear la relación
                perm_role = PermissionRolUser(
                    Permission_id=permission.id,
                    Rol_User_id=role.id
                )
                db.session.add(perm_role)
                print(f"✓ Asignado permiso '{perm_name}' al rol '{role_name}'")
            else:
                print(f"- Permiso '{perm_name}' ya asignado al rol '{role_name}'")

def create_default_admin_user():
    """Crear un usuario administrador por defecto"""
    admin_email = "admin@admin.com"
    
    # Verificar si ya existe
    existing_admin = User.query.filter_by(mail=admin_email).first()
    if existing_admin:
        print(f"- Usuario administrador ya existe: {admin_email}")
        return existing_admin
    
    # Crear el usuario administrador
    admin_user = User(
        mail=admin_email,
        name="Administrador",
        last_name="Sistema",
        active=True,
        blocked=False
    )
    admin_user.set_password("admin123")  # Cambiar por una contraseña segura
    
    db.session.add(admin_user)
    db.session.flush()  # Para obtener el ID
    
    # Asignar rol de administrador
    admin_role = RolUser.query.filter_by(name="admin").first()
    if admin_role:
        user_role = RolUserUser(
            User_id=admin_user.id,
            Rol_User_id=admin_role.id
        )
        db.session.add(user_role)
        print(f"✓ Usuario administrador creado: {admin_email}")
        print(f"✓ Rol 'admin' asignado al usuario")
    else:
        print("⚠️  No se pudo asignar el rol admin - rol no encontrado")
    
    return admin_user

def main():
    """Función principal"""
    print("🚀 Iniciando carga de permisos y roles...")
    print("=" * 50)
    
    # Crear la aplicación Flask
    app = create_app()
    
    with app.app_context():
        try:
            # Crear permisos
            print("\n📋 Creando permisos...")
            create_permissions()
            
            # Crear roles
            print("\n👥 Creando roles...")
            roles = create_roles()
            
            # Asignar permisos a roles
            print("\n🔗 Asignando permisos a roles...")
            assign_permissions_to_roles(roles)
            
            # Crear usuario administrador
            print("\n👤 Creando usuario administrador...")
            create_default_admin_user()
            
            # Confirmar cambios
            db.session.commit()
            print("\n✅ ¡Todos los cambios se guardaron exitosamente!")
            print("\n📝 Resumen:")
            print(f"- Permisos creados: {Permission.query.count()}")
            print(f"- Roles creados: {RolUser.query.count()}")
            print(f"- Relaciones permiso-rol: {PermissionRolUser.query.count()}")
            print(f"- Usuarios: {User.query.count()}")
            print(f"- Relaciones usuario-rol: {RolUserUser.query.count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {e}")
            return False
        
        return True

if __name__ == "__main__":
    main()
