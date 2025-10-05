#!/usr/bin/env python3
"""
Script para asignar roles a usuarios existentes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.web import create_app
from src.web.extensions import db
from src.web.models.user import User
from src.web.models.rol_user import RolUser
from src.web.models.rol_user_user import RolUserUser

def list_users():
    """Listar todos los usuarios disponibles"""
    users = User.query.filter_by(deleted=False).all()
    print("\n👥 Usuarios disponibles:")
    print("-" * 50)
    for user in users:
        print(f"ID: {user.id} | Email: {user.mail} | Nombre: {user.name} {user.last_name}")
    return users

def list_roles():
    """Listar todos los roles disponibles"""
    roles = RolUser.query.filter_by(deleted=False).all()
    print("\n🎭 Roles disponibles:")
    print("-" * 30)
    for role in roles:
        print(f"ID: {role.id} | Nombre: {role.name}")
    return roles

def assign_role_to_user(user_id, role_name):
    """Asignar un rol a un usuario"""
    user = User.query.get(user_id)
    if not user:
        print(f"❌ Usuario con ID {user_id} no encontrado")
        return False
    
    role = RolUser.query.filter_by(name=role_name).first()
    if not role:
        print(f"❌ Rol '{role_name}' no encontrado")
        return False
    
    # Verificar si ya tiene ese rol
    existing = RolUserUser.query.filter_by(
        User_id=user_id,
        Rol_User_id=role.id
    ).first()
    
    if existing:
        print(f"⚠️  El usuario {user.mail} ya tiene el rol '{role_name}'")
        return False
    
    # Asignar el rol
    user_role = RolUserUser(
        User_id=user_id,
        Rol_User_id=role.id
    )
    db.session.add(user_role)
    
    print(f"✅ Rol '{role_name}' asignado al usuario {user.mail}")
    return True

def remove_role_from_user(user_id, role_name):
    """Remover un rol de un usuario"""
    user = User.query.get(user_id)
    if not user:
        print(f"❌ Usuario con ID {user_id} no encontrado")
        return False
    
    role = RolUser.query.filter_by(name=role_name).first()
    if not role:
        print(f"❌ Rol '{role_name}' no encontrado")
        return False
    
    # Buscar la relación
    existing = RolUserUser.query.filter_by(
        User_id=user_id,
        Rol_User_id=role.id
    ).first()
    
    if not existing:
        print(f"⚠️  El usuario {user.mail} no tiene el rol '{role_name}'")
        return False
    
    # Remover el rol
    db.session.delete(existing)
    print(f"✅ Rol '{role_name}' removido del usuario {user.mail}")
    return True

def show_user_roles(user_id):
    """Mostrar los roles de un usuario"""
    user = User.query.get(user_id)
    if not user:
        print(f"❌ Usuario con ID {user_id} no encontrado")
        return
    
    print(f"\n🎭 Roles del usuario {user.mail}:")
    print("-" * 40)
    
    if not user.user_roles:
        print("No tiene roles asignados")
        return
    
    for user_role in user.user_roles:
        role = user_role.rol_user
        print(f"- {role.name}")
        
        # Mostrar permisos del rol
        print("  Permisos:")
        for perm_rel in role.permission_rol_users:
            perm = perm_rel.permission
            print(f"    • {perm.name}")

def show_user_permissions(user_id):
    """Mostrar todos los permisos de un usuario"""
    user = User.query.get(user_id)
    if not user:
        print(f"❌ Usuario con ID {user_id} no encontrado")
        return
    
    permissions = user.permissions
    print(f"\n🔑 Permisos del usuario {user.mail}:")
    print("-" * 50)
    
    if not permissions:
        print("No tiene permisos asignados")
        return
    
    for perm in permissions:
        print(f"• {perm}")

def interactive_mode():
    """Modo interactivo para gestionar roles"""
    while True:
        print("\n" + "="*60)
        print("🔧 GESTOR DE ROLES DE USUARIOS")
        print("="*60)
        print("1. Listar usuarios")
        print("2. Listar roles")
        print("3. Ver roles de un usuario")
        print("4. Ver permisos de un usuario")
        print("5. Asignar rol a usuario")
        print("6. Remover rol de usuario")
        print("7. Salir")
        print("-"*60)
        
        choice = input("Selecciona una opción (1-7): ").strip()
        
        if choice == "1":
            list_users()
        
        elif choice == "2":
            list_roles()
        
        elif choice == "3":
            users = list_users()
            if users:
                try:
                    user_id = int(input("\nIngresa el ID del usuario: "))
                    show_user_roles(user_id)
                except ValueError:
                    print("❌ ID inválido")
        
        elif choice == "4":
            users = list_users()
            if users:
                try:
                    user_id = int(input("\nIngresa el ID del usuario: "))
                    show_user_permissions(user_id)
                except ValueError:
                    print("❌ ID inválido")
        
        elif choice == "5":
            users = list_users()
            roles = list_roles()
            if users and roles:
                try:
                    user_id = int(input("\nIngresa el ID del usuario: "))
                    role_name = input("Ingresa el nombre del rol: ").strip()
                    if assign_role_to_user(user_id, role_name):
                        db.session.commit()
                        print("✅ Cambios guardados")
                    else:
                        db.session.rollback()
                except ValueError:
                    print("❌ ID inválido")
        
        elif choice == "6":
            users = list_users()
            if users:
                try:
                    user_id = int(input("\nIngresa el ID del usuario: "))
                    role_name = input("Ingresa el nombre del rol a remover: ").strip()
                    if remove_role_from_user(user_id, role_name):
                        db.session.commit()
                        print("✅ Cambios guardados")
                    else:
                        db.session.rollback()
                except ValueError:
                    print("❌ ID inválido")
        
        elif choice == "7":
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción inválida")

def main():
    """Función principal"""
    print("🚀 Gestor de Roles de Usuarios")
    print("="*40)
    
    # Crear la aplicación Flask
    app = create_app()
    
    with app.app_context():
        try:
            interactive_mode()
        except KeyboardInterrupt:
            print("\n\n👋 Operación cancelada por el usuario")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    main()
