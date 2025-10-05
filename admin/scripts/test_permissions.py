#!/usr/bin/env python3
"""
Script para probar el sistema de permisos y decoradores
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, session
from src.web.extensions import db
from src.web.models.user import User
from src.web.models.rol_user import RolUser
from src.web.models.permission import Permission
from src.web.auth.decorators import permission_required
from src.web import create_app

def test_user_permissions():
    """Probar los permisos de un usuario"""
    print("🔍 Probando permisos de usuarios...")
    print("="*50)
    
    # Listar usuarios
    users = User.query.filter_by(deleted=False).all()
    if not users:
        print("❌ No hay usuarios en la base de datos")
        return
    
    print("\n👥 Usuarios disponibles:")
    for user in users:
        print(f"ID: {user.id} | Email: {user.mail}")
    
    # Probar permisos de cada usuario
    for user in users:
        print(f"\n🔑 Permisos del usuario {user.mail} (ID: {user.id}):")
        print("-" * 40)
        
        permissions = user.permissions
        if permissions:
            for perm in permissions:
                print(f"  ✓ {perm}")
        else:
            print("  ⚠️  No tiene permisos asignados")
        
        # Mostrar roles
        print(f"\n🎭 Roles del usuario {user.mail}:")
        if user.user_roles:
            for user_role in user.user_roles:
                role = user_role.rol_user
                print(f"  • {role.name}")
        else:
            print("  ⚠️  No tiene roles asignados")

def test_decorator_simulation():
    """Simular el funcionamiento del decorador"""
    print("\n🧪 Simulando decorador de permisos...")
    print("="*50)
    
    # Crear una función de prueba
    @permission_required("create_historic_site")
    def test_function():
        return {"message": "Función ejecutada exitosamente"}
    
    # Obtener un usuario para probar
    admin_user = User.query.filter_by(mail="admin@admin.com").first()
    if not admin_user:
        print("❌ Usuario administrador no encontrado. Ejecuta primero load_permissions.py")
        return
    
    print(f"\n🔍 Probando con usuario: {admin_user.mail}")
    
    # Simular sesión de usuario
    with Flask(__name__).test_request_context():
        # Establecer la sesión
        session['user_id'] = admin_user.id
        
        print(f"📋 Permisos del usuario: {admin_user.permissions}")
        
        # Probar diferentes permisos
        test_permissions = [
            "create_historic_site",
            "get_historic_site", 
            "delete_user",
            "invalid_permission"
        ]
        
        for perm_name in test_permissions:
            print(f"\n🧪 Probando permiso: {perm_name}")
            
            # Crear decorador para este permiso
            @permission_required(perm_name)
            def test_func():
                return {"success": True}
            
            try:
                result = test_func()
                print(f"  ✅ Acceso permitido: {result}")
            except Exception as e:
                print(f"  ❌ Acceso denegado: {str(e)}")

def test_route_permissions():
    """Probar permisos en las rutas"""
    print("\n🛣️  Probando permisos en rutas...")
    print("="*50)
    
    # Definir las rutas que tienen permisos comentados
    routes_permissions = {
        "create_historic_site": "POST /HistoricSite_Routes",
        "get_historic_site": "GET /HistoricSite_Routes/<id>",
        "get_all_historic_sites": "GET /HistoricSite_Routes",
        "get_all_sites_for_map": "GET /HistoricSite_Routes/map",
        "update_historic_site": "PUT /HistoricSite_Routes/<id>",
        "delete_historic_site": "DELETE /HistoricSite_Routes/<id>",
        "add_tags": "POST /HistoricSite_Routes/<id>/tags",
        "update_tags": "PUT /HistoricSite_Routes/<id>/tags",
        "get_filter_options": "GET /HistoricSite_Routes/filter-options"
    }
    
    print("📋 Rutas con permisos definidos:")
    for perm, route in routes_permissions.items():
        # Verificar si el permiso existe en la base de datos
        permission = Permission.query.filter_by(name=perm).first()
        status = "✅" if permission else "❌"
        print(f"  {status} {route} -> {perm}")
    
    # Verificar qué usuarios tienen acceso a cada ruta
    users = User.query.filter_by(deleted=False).all()
    print(f"\n👥 Verificando acceso de usuarios ({len(users)} usuarios):")
    
    for user in users:
        user_permissions = user.permissions
        accessible_routes = []
        
        for perm, route in routes_permissions.items():
            if perm in user_permissions:
                accessible_routes.append(route)
        
        print(f"\n🔑 {user.mail}:")
        if accessible_routes:
            for route in accessible_routes:
                print(f"  ✅ {route}")
        else:
            print("  ⚠️  No tiene acceso a ninguna ruta")

def create_test_user():
    """Crear un usuario de prueba con permisos limitados"""
    print("\n👤 Creando usuario de prueba...")
    print("-" * 30)
    
    test_email = "test@test.com"
    
    # Verificar si ya existe
    existing = User.query.filter_by(mail=test_email).first()
    if existing:
        print(f"⚠️  Usuario de prueba ya existe: {test_email}")
        return existing
    
    # Crear usuario de prueba
    test_user = User(
        mail=test_email,
        name="Usuario",
        last_name="Prueba",
        active=True,
        blocked=False
    )
    test_user.set_password("test123")
    
    db.session.add(test_user)
    db.session.flush()
    
    # Asignar rol de viewer (solo lectura)
    viewer_role = RolUser.query.filter_by(name="viewer").first()
    if viewer_role:
        user_role = RolUserUser(
            User_id=test_user.id,
            Rol_User_id=viewer_role.id
        )
        db.session.add(user_role)
        print(f"✅ Usuario de prueba creado: {test_email}")
        print(f"✅ Rol 'viewer' asignado")
    else:
        print("⚠️  No se pudo asignar rol viewer - rol no encontrado")
    
    return test_user

def main():
    """Función principal"""
    print("🧪 PRUEBAS DEL SISTEMA DE PERMISOS")
    print("="*60)
    
    # Crear la app para tener el contexto
    app = create_app()
    
    with app.app_context():
        try:
            # Probar permisos de usuarios
            test_user_permissions()
            
            # Simular decorador
            test_decorator_simulation()
            
            # Probar rutas
            test_route_permissions()
            
            # Crear usuario de prueba
            create_test_user()
            
            # Confirmar cambios
            db.session.commit()
            
            print("\n" + "="*60)
            print("✅ PRUEBAS COMPLETADAS")
            print("="*60)
            print("\n📝 Para probar los decoradores en las rutas:")
            print("1. Ejecuta load_permissions.py para cargar permisos")
            print("2. Ejecuta assign_user_roles.py para asignar roles")
            print("3. Descomenta los decoradores en HistoricSite_Routes.py")
            print("4. Inicia sesión con un usuario que tenga permisos")
            print("5. Prueba las rutas protegidas")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    main()
