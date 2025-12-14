"""
Ejemplo de uso de los modelos SQLAlchemy para el sistema de sitios históricos.
Este script demuestra cómo crear, consultar y relacionar datos usando los modelos.
"""

import os
from datetime import datetime
from src.web import create_app
from src.web.extensions import db
from werkzeug.security import generate_password_hash
from src.core.models.user import User
from src.core.models.category_site import CategorySite
from src.core.models.province import Province
from src.core.models.city import City
from src.core.models.state_site import StateSite
from src.core.models.historic_site import HistoricSite
from src.core.models.tag import Tag
from src.core.models.event import Event
from src.core.models.permission import Permission
from src.core.models.rol_user import RolUser
from src.core.models.permission_rol_user import PermissionRolUser
from src.core.models.rol_user_user import RolUserUser
from src.core.models.tag_historic_site import TagHistoricSite
from src.core.models.flag import Flag

def setup_database():
    """Configurar la base de datos y crear tablas"""
    app = create_app()
    
    with app.app_context():
        db.create_all()
        print("✅ Base de datos configurada correctamente")
        return app

def create_sample_data(app):
    """Crear datos de ejemplo de forma segura (verificando si ya existen)"""
    with app.app_context():
        print("\n📝 Creando datos de ejemplo...")
        
        db.session.commit()
        print("✅ Usuarios antiguos borrados")
        category_names = ['Monumento Histórico', 'Museo', 'Iglesia', 'Plaza', 'Edificio Gubernamental']
        created_categories = []
        for name in category_names:
            if not CategorySite.query.filter_by(name=name).first():
                new_cat = CategorySite(name=name)
                db.session.add(new_cat)
                created_categories.append(new_cat)
        if created_categories:
            db.session.commit()
        print(f"✅ Creadas {len(created_categories)} nuevas categorías. Total: {len(category_names)}")

        provinces_data = {'Buenos Aires': ['La Plata', 'Mar del Plata'], 'Córdoba': ['Córdoba Capital'], 'Santa Fe': ['Rosario']}
        created_provinces = 0
        created_cities = 0
        for province_name, city_list in provinces_data.items():
            province = Province.query.filter_by(name=province_name).first()
            if not province:
                province = Province(name=province_name)
                db.session.add(province)
                db.session.commit() 
                created_provinces += 1
            
            for city_name in city_list:
                if not City.query.filter_by(name=city_name, id_province=province.id).first():
                    city = City(name=city_name, id_province=province.id)
                    db.session.add(city)
                    created_cities += 1
        if created_cities > 0 or created_provinces > 0:
            db.session.commit()
        print(f"✅ Creadas {created_provinces} nuevas provincias y {created_cities} nuevas ciudades.")

        state_names = ['Excelente', 'Bueno', 'Regular', 'Malo']
        created_states = []
        for state_name in state_names:
            if not StateSite.query.filter_by(state=state_name).first():
                new_state = StateSite(state=state_name)
                db.session.add(new_state)
                created_states.append(new_state)
        if created_states:
            db.session.commit()
        print(f"✅ Creados {len(created_states)} nuevos estados de sitios.")
        
        print("✅ Datos de ejemplo creados/verificados correctamente.")


        flags_to_create = [
            {"key": 1, "name": "admin_maintenance_mode", "description": "Deshabilita temporalmente el sitio de administración", "enabled": False, "message": "El sitio está en mantenimiento", "last_modified_by": "System Admin", "last_modified_at": datetime.now()},
            {"key": 2, "name": "portal_maintenance_mode", "description": "Deshabilita temporalmente el portal público", "enabled": False, "message": "El portal está en mantenimiento", "last_modified_by": "System Admin", "last_modified_at": datetime.now()},
            {"key": 3, "name": "reviews_enabled", "description": "Permite o deshabilita la creación de reseñas", "enabled": True, "message": "Las reseñas están habilitadas", "last_modified_by": "System Admin", "last_modified_at": datetime.now()}
        ]

        created_flags = 0
        for f in flags_to_create:
            existing_flag = Flag.query.filter_by(name=f['name']).first()
            if not existing_flag:
                new_flag = Flag(
                    key=f['key'],
                    name=f['name'],
                    description=f['description'],
                    enabled=f['enabled'],
                    message=f['message'],
                    last_modified_at=f['last_modified_at'],
                    last_modified_by=f['last_modified_by']
                )
                db.session.add(new_flag)
                created_flags += 1
                print(f"✅ Flag creado: {f['name']}")
            else:
                print(f"- Flag ya existe: {f['name']}")
        
        if created_flags > 0:
            db.session.commit()
        print(f"✅ Total de flags creados: {created_flags}")
   


def query_examples(app):
    """Ejemplos de consultas a la base de datos"""
    with app.app_context():
        print("\n🔍 Ejemplos de consultas:")
        
        sites = HistoricSite.query.filter_by(visible=True).all()
        print(f"📍 Sitios históricos visibles: {len(sites)}")
        for site in sites:
            city_name = site.city.name if site.city else 'Sin ciudad'
            print(f"  - {site.name} ({city_name})")
        
        monuments_category = CategorySite.query.filter_by(name='Monumento Histórico').first()
        if monuments_category:
            monuments = HistoricSite.query.filter_by(id_category=monuments_category.id).all()
            print(f"🏛️  Monumentos históricos: {len(monuments)}")
        
        active_users = User.query.filter_by(active=True).all()
        print(f"👥 Usuarios activos: {len(active_users)}")
        for user in active_users:
            print(f"  - {user.name} {user.last_name} ({user.mail})")

def main():
    """Función principal"""
    print("🚀 Iniciando ejemplo de uso de modelos SQLAlchemy")
    print("=" * 50)
    
    app = setup_database()
    
    create_sample_data(app)
    
    query_examples(app)
    
    print("\n" + "=" * 50)
    print("✅ Ejemplo completado exitosamente!")
    print("\n💡 Próximos pasos:")
    print("  1. Ejecutar las migraciones (si usas Flask-Migrate): flask db upgrade")
    print("  2. Iniciar la aplicación: python main.py")

if __name__ == '__main__':
    main()