#!/usr/bin/env python3
"""
Script para cargar datos iniciales necesarios para producción
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.web import create_app
from src.web.extensions import db
from src.core.models.permission import Permission
from src.core.models.rol_user import RolUser
from src.core.models.permission_rol_user import PermissionRolUser
from src.core.models.rol_user_user import RolUserUser
from src.core.models.user import User
from src.core.models.category_site import CategorySite
from src.core.models.state_site import StateSite
from src.core.models.flag import Flag

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
        # Permiso para moderar reseñas (panel privado)
        "moderate_reviews",
    ]
    
    created_count = 0
    for perm_name in permissions:
        existing = Permission.query.filter_by(name=perm_name).first()
        if not existing:
            perm = Permission(name=perm_name)
            db.session.add(perm)
            created_count += 1
    
    return created_count

def create_roles():
    """Crear los roles del sistema"""
    roles = {
        "admin": "Administrador del sistema - acceso completo",
        "editor": "Editor - puede crear, editar y eliminar contenido",
        "moderador": "Moderador - puede revisar y moderar reseñas",
        "usuario": "Usuario autenticado - solo puede ver contenido"
    }
    
    created_roles = {}
    created_count = 0
    for role_name, description in roles.items():
        existing = RolUser.query.filter_by(name=role_name).first()
        if not existing:
            role = RolUser(name=role_name)
            db.session.add(role)
            created_roles[role_name] = role
            created_count += 1
        else:
            created_roles[role_name] = existing
    
    return created_roles, created_count

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
            "view_profile", "update_password", "moderate_reviews"
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
            "view_profile", "update_password", "moderate_reviews"
        ],
        "moderador": [
            # Permisos limitados pero incluye moderación
            "get_historic_site", "get_all_historic_sites", "get_all_sites_for_map",
            "view_profile", "update_password", "moderate_reviews"
        ],
        "usuario": [
            # Permisos básicos para usuarios autenticados
            "get_historic_site", "get_all_historic_sites", "get_all_sites_for_map",
            "get_category", "get_all_categories", "get_tag", "get_all_tags",
            "get_state", "get_all_states", "get_event", "get_all_events",
            "view_profile", "update_password"
        ]
    }
    
    created_count = 0
    for role_name, permission_names in role_permissions.items():
        role = roles.get(role_name)
        if not role:
            continue
            
        for perm_name in permission_names:
            # Buscar el permiso
            permission = Permission.query.filter_by(name=perm_name).first()
            if not permission:
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
                created_count += 1
    
    return created_count

def create_categories():
    """Crear las categorías de sitios históricos"""
    categories = [
        "Arquitectura",
        "Infraestructura",
        "Sitio arqueologico"
    ]
    
    created_count = 0
    for category_name in categories:
        existing = CategorySite.query.filter_by(name=category_name).first()
        if not existing:
            category = CategorySite(name=category_name, deleted=False)
            db.session.add(category)
            created_count += 1
    
    return created_count

def create_states():
    """Crear los estados de conservación de sitios históricos"""
    states = [
        "Bueno",
        "Regular",
        "Malo"
    ]
    
    created_count = 0
    for state_name in states:
        existing = StateSite.query.filter_by(state=state_name).first()
        if not existing:
            state = StateSite(state=state_name, deleted=False)
            db.session.add(state)
            created_count += 1
    
    return created_count

def create_flags():
    """Crear los flags del sistema"""
    flags = [
        {
            "key": "admin_maintenance_mode",
            "name": "Modo Mantenimiento - Admin",
            "description": "Activa el modo mantenimiento para el panel de administración",
            "enabled": False,
            "message": "El sitio de administración está temporalmente inactivo por tareas de mantenimiento."
        },
        {
            "key": "portal_maintenance_mode",
            "name": "Modo Mantenimiento - Portal",
            "description": "Activa el modo mantenimiento para el portal público",
            "enabled": False,
            "message": "El portal está temporalmente inactivo por tareas de mantenimiento."
        },
        {
            "key": "reviews_enabled",
            "name": "Reviews Habilitadas",
            "description": "Permite a los usuarios dejar reseñas en sitios históricos",
            "enabled": True,
            "message": None
        }
    ]
    
    created_count = 0
    for flag_data in flags:
        existing = Flag.query.filter_by(key=flag_data["key"]).first()
        if not existing:
            flag = Flag(
                key=flag_data["key"],
                name=flag_data["name"],
                description=flag_data["description"],
                enabled=flag_data["enabled"],
                message=flag_data["message"]
            )
            db.session.add(flag)
            created_count += 1
    
    return created_count

def create_super_admin():
    """Crear usuario super administrador"""
    admin_email = "grupo06@gmail.com"
    
    # Verificar si ya existe
    existing_admin = User.query.filter_by(mail=admin_email).first()
    if existing_admin:
        return False
    
    # Crear el usuario super administrador
    admin_user = User(
        mail=admin_email,
        name="grupo",
        last_name="06",
        active=True,
        blocked=False,
        deleted=False,
        is_super_admin=True
    )
    admin_user.set_password("grupo06")
    
    db.session.add(admin_user)
    db.session.flush()  # Para obtener el ID
    
    return True
def create_dummy_users(existing_roles):
    """Crear 3 usuarios dummy y asignarles un rol distinto cada uno."""
    
    print("👥 Verificando usuarios dummy...")

    rol_admin = existing_roles["admin"]
    rol_editor = existing_roles["editor"]
    rol_moderador = existing_roles["moderador"]

    dummy_users = []

    # Datos de los usuarios y el rol a asignar
    user_data = [
        ("user1@example.com", "Usuario Prueba 1", rol_admin),
        ("user2@example.com", "Usuario Prueba 2", rol_editor),
        ("user3@example.com", "Usuario Prueba 3", rol_moderador),
    ]

    for mail, name, rol in user_data:
        existing_user = User.query.filter_by(mail=mail).first()
        if existing_user:
            print(f"   ⚠ Usuario {mail} ya existe, saltando...")
            continue

        u = User(
            mail=mail,
            name=name,
            last_name="Seed",
            active=True,
            blocked=False,
            deleted=False,
            is_super_admin=False,
        )
        u.set_password("password123")
        db.session.add(u)
        db.session.flush()  # para asegurar que u.id exista antes de asignar el rol

        # Crear la relación usuario-rol
        u.user_roles.append(RolUserUser(User_id=u.id, Rol_User_id=rol.id))

        dummy_users.append(u)

    db.session.commit()
    print(f"   ✓ Usuarios dummy creados: {len(dummy_users)}")
    return dummy_users


def ensure_category_and_state():
    """
    Asegura que exista al menos una CategorySite y un StateSite; devuelve sus ids.
    (Se adapta a los nombres de FK en HistoricSite: id_category e id_estado)
    """
    from src.core.models.category_site import CategorySite
    from src.core.models.state_site import StateSite
    from src.web.extensions import db

    category = CategorySite.query.filter_by(deleted=False).first()
    if not category:
        category = CategorySite(name="Categoria Dummy", deleted=False)
        db.session.add(category)
        db.session.commit()
        print("   ✓ Categoria dummy creada")

    state = StateSite.query.filter_by(deleted=False).first()
    if not state:
        state = StateSite(state="Bueno", deleted=False)
        db.session.add(state)
        db.session.commit()
        print("   ✓ Estado dummy creado")

    return category.id, state.id

def create_dummy_sites_if_needed(id_category, id_estado):
    """
    Crea algunos HistoricSite si no existe ninguno; devuelve la lista de sitios.
    Usa los campos del modelo: id_category, id_estado, brief_description, complete_description, visible.
    """
    

    sites = HistoricSite.query.filter_by(deleted=False).all()
    if sites:
        print(f"   ✓ Sitios existentes: {len(sites)}")
        return sites

    print("   ⚠️ No hay sitios históricos. Creando sitios dummy...")
    dummy_sites = []
    for i in range(3):
        s = HistoricSite(
            name=f"Sitio Histórico de Prueba {i+1}",
            brief_description="Breve descripción de prueba generada automáticamente.",
            complete_description="Texto completo de ejemplo para el sitio histórico de prueba.",
            # Asignamos campos FK según tu modelo
            id_category=id_category,
            id_estado=id_estado,
            # city id opcional, lo dejamos None
            id_ciudad=None,
            # latitude/longitude como strings
            latitude=str(-34.60 + random.uniform(-0.02, 0.02)),
            longitude=str(-58.38 + random.uniform(-0.02, 0.02)),
            year_inauguration=None,
            created_at=datetime.utcnow(),
            deleted=False,
            visible=True
        )
        db.session.add(s)
        dummy_sites.append(s)

    db.session.commit()
    print(f"   ✓ Sitios dummy creados: {len(dummy_sites)}")
    return dummy_sites

def create_test_reviews(users):
    """
    Crea reseñas de prueba. Asegura usuarios y sitios (crea dummy si hace falta).
    Usa strings para status ('pending','approved','rejected','deleted').
    """
  
    print("📝 Creando reseñas de prueba...")

   
    if not users:
        print("   ❌ No hay usuarios y no se pudieron crear.")
        return 0

    # 2) Asegurar category/state y sitios
    category_id, state_id = ensure_category_and_state()
    sites = create_dummy_sites_if_needed(category_id, state_id)
    if not sites:
        print("   ❌ No se pudieron crear sitios.")
        return 0

    # 3) Crear reseñas
    possible_statuses = ['pending', 'approved', 'rejected']
    created = 0
    examples = [
        "Excelente lugar, muy recomendado",
        "Me gustó pero podría estar más limpio",
        "No me pareció interesante",
        "Muy descuidado, no vale la pena",
        "La arquitectura es impresionante",
        "Buena experiencia general",
    ]

    for i, text in enumerate(examples):
        user = random.choice(users)
        site = random.choice(sites)
        review = HistoricSiteReview(
            site_id=site.id,
            user_id=user.id,
            rating=random.randint(1, 5),
            content=text,
            status=random.choice(possible_statuses),
            rejection_reason=None,
            created_at=datetime.utcnow()
        )
        db.session.add(review)
        created += 1

    db.session.commit()
    print(f"   ✓ Reseñas creadas: {created}")
    return created

def main():
    """Función principal para cargar todos los seeds"""
    print("🌱 Iniciando carga de datos iniciales (seeds)...")
    print("=" * 60)
    
    # Crear la aplicación Flask
    app = create_app()
    
    with app.app_context():
        try:
            # 1. Crear permisos
            print("\n📋 Creando permisos...")
            permisos_creados = create_permissions()
            print(f"   ✓ Permisos procesados: {permisos_creados} nuevos")
            
            # 2. Crear roles
            print("\n👥 Creando roles...")
            roles, roles_creados = create_roles()
            db.session.commit() 
            print(f"   ✓ Roles procesados: {roles_creados} nuevos")
            
            # 3. Asignar permisos a roles
            print("\n🔗 Asignando permisos a roles...")
            asignaciones = assign_permissions_to_roles(roles)
            db.session.commit()
            print(f"   ✓ Relaciones permiso-rol creadas: {asignaciones}")
            
            # 4. Crear usuarios dummy y reseñas
            print("\n📝 Creando usuarios dummy y reseñas de prueba...")
            users = create_dummy_users(roles)
            reviews = create_test_reviews(users)
            # 4. Crear categorías
            print("\n🏛️  Creando categorías...")
            categorias = create_categories()
            print(f"   ✓ Categorías creadas: {categorias}")
            
            # 5. Crear estados
            print("\n📊 Creando estados de conservación...")
            estados = create_states()
            print(f"   ✓ Estados creados: {estados}")
            
            # 6. Crear flags
            print("\n🚩 Creando flags del sistema...")
            flags = create_flags()
            print(f"   ✓ Flags creados: {flags}")
            
            # 7. Crear super administrador
            print("\n👤 Creando usuario super administrador...")
            super_admin_created = create_super_admin()
            if super_admin_created:
                print(f"   ✓ Super Admin creado: grupo06@gmail.com")
            else:
                print(f"   - Super Admin ya existe")
            db.session.commit()
            
            # Resumen final
            print("\n" + "=" * 60)
            print("✅ ¡Seeds cargados exitosamente!")
            print("\n📝 Resumen del sistema:")
            print(f"   - Permisos totales: {Permission.query.count()}")
            print(f"   - Roles totales: {RolUser.query.count()}")
            print(f"   - Relaciones permiso-rol: {PermissionRolUser.query.count()}")
            print(f"   - Categorías: {CategorySite.query.filter_by(deleted=False).count()}")
            print(f"   - Estados: {StateSite.query.filter_by(deleted=False).count()}")
            print(f"   - Flags: {Flag.query.count()}")
            print(f"   - Usuarios: {User.query.filter_by(deleted=False).count()}")
            print(f"   - Relaciones usuario-rol: {RolUserUser.query.count()}")
            
            print("\n🔐 Credenciales de acceso:")
            print(f"   Email: grupo06@gmail.com")
            print(f"   Contraseña: grupo06")
            print(f"   Super admin: Sí")
            print("\n⚠️  IMPORTANTE: Cambiar estas credenciales en producción")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al cargar seeds: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

