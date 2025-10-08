#!/usr/bin/env python3
"""
Ejemplo de uso de los modelos SQLAlchemy para el sistema de sitios históricos.
Este script demuestra cómo crear, consultar y relacionar datos usando los modelos.
"""

import os
from datetime import datetime
from src.web import create_app, db
from werkzeug.security import generate_password_hash
from src.web.models import (
    User, CategorySite, Province, City, StateSite, 
    HistoricSite, Tag, Event, Permission, RolUser,
    PermissionRolUser, RolUserUser, TagHistoricSite, Flag
)

def setup_database():
    """Configurar la base de datos y crear tablas"""
    app = create_app()
    
    with app.app_context():
        # Crear todas las tablas si no existen
        db.create_all()
        print("✅ Base de datos configurada correctamente")
        return app

def create_sample_data(app):
    """Crear datos de ejemplo de forma segura (verificando si ya existen)"""
    with app.app_context():
        print("\n📝 Creando datos de ejemplo...")
        
        db.session.commit()
        print("✅ Usuarios antiguos borrados")
        # 1. Crear categorías de sitios
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

        # 2. Crear provincias y ciudades
        provinces_data = {'Buenos Aires': ['La Plata', 'Mar del Plata'], 'Córdoba': ['Córdoba Capital'], 'Santa Fe': ['Rosario']}
        created_provinces = 0
        created_cities = 0
        for province_name, city_list in provinces_data.items():
            province = Province.query.filter_by(name=province_name).first()
            if not province:
                province = Province(name=province_name)
                db.session.add(province)
                db.session.commit() # Commit para obtener el ID de la provincia
                created_provinces += 1
            
            for city_name in city_list:
                if not City.query.filter_by(name=city_name, id_province=province.id).first():
                    city = City(name=city_name, id_province=province.id)
                    db.session.add(city)
                    created_cities += 1
        if created_cities > 0 or created_provinces > 0:
            db.session.commit()
        print(f"✅ Creadas {created_provinces} nuevas provincias y {created_cities} nuevas ciudades.")

        # 3. Crear estados de sitios
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
        
        # 4. Crear usuarios
        #users_to_create = [
        #    {'mail': 'admin@historicos.com', 'name': 'Admin', 'last_name': 'Sistema', 'password': 'admin123', 'active': True},
        #    {'mail': 'editor@historicos.com', 'name': 'Editor', 'last_name': 'Contenido', 'password': 'editor123', 'active': True}
        #]

        #for user_data in users_to_create:
        #    if not User.query.filter_by(mail=user_data['mail']).first():
        #        new_user = User(
        #            mail=user_data['mail'],
        #            name=user_data['name'],
        #            last_name=user_data['last_name'],
        #            active=user_data['active']
        #       )
        #        new_user.set_password(user_data['password'])
        #        db.session.add(new_user)
        #db.session.commit()
        #print("✅ Usuarios recreados correctamente con contraseña hasheada")       
   
        # 5. Crear sitios históricos
        # Obtenemos los objetos necesarios para las relaciones
        #caba_city = City.query.filter_by(name='La Plata').first() # Asumiendo La Plata como CABA para el ejemplo
        #cordoba_city = City.query.filter_by(name='Córdoba Capital').first()
        #state_excelente = StateSite.query.filter_by(state='Excelente').first()
        #state_bueno = StateSite.query.filter_by(state='Bueno').first()
        #cat_gob = CategorySite.query.filter_by(name='Edificio Gubernamental').first()
        #cat_museo = CategorySite.query.filter_by(name='Museo').first()
        #cat_iglesia = CategorySite.query.filter_by(name='Iglesia').first()

        #historic_sites_data = [
        #    {'name': 'Casa Rosada', 'brief_description': 'Sede del Poder Ejecutivo', 'id_ciudad': caba_city.id, 'id_estado': state_excelente.id, 'id_category': cat_gob.id, 'latitude':'-34.6083', 'longitude':'-58.3712', 'year_inauguration': 1898, 'complete_description': '...'},
        #    {'name': 'Teatro Colón', 'brief_description': 'Uno de los teatros de ópera más importantes', 'id_ciudad': caba_city.id, 'id_estado': state_excelente.id, 'id_category': cat_museo.id, 'latitude':'-34.6011', 'longitude':'-58.3836', 'year_inauguration': 1908, 'complete_description': '...'},
        #    {'name': 'Catedral de Córdoba', 'brief_description': 'Principal templo católico de Córdoba', 'id_ciudad': cordoba_city.id, 'id_estado': state_bueno.id, 'id_category': cat_iglesia.id, 'latitude':'-31.4201', 'longitude':'-64.1888', 'year_inauguration': 1758, 'complete_description': '...'}
        #]
        #created_sites_count = 0
        #for site_data in historic_sites_data:
        #    if not HistoricSite.query.filter_by(name=site_data['name']).first():
        #        new_site = HistoricSite(**site_data, visible=True)
        #        db.session.add(new_site)
        #        created_sites_count += 1
        #if created_sites_count > 0:
        #    db.session.commit()
        #print(f"✅ Creados {created_sites_count} nuevos sitios históricos.")

        # El resto de las creaciones seguirían el mismo patrón de verificar antes de insertar...
        # Por simplicidad y para no alargar el código, los siguientes pasos se asumen en un
        # entorno limpio o se deberían implementar de la misma manera.
        
        print("✅ Datos de ejemplo creados/verificados correctamente.")


        #FLAG
        flags_to_create = [
            {"key": 1, "name": "admin_maintenance_mode", "description": "Deshabilita temporalmente el sitio de administración", "enabled": False, "message": "El sitio está en mantenimiento", "last_modified_by": "System Admin", "last_modified_at": datetime.now()},
            {"key": 2, "name": "portal_maintenance_mode", "description": "Deshabilita temporalmente el portal público", "enabled": False, "message": "El portal está en mantenimiento", "last_modified_by": "System Admin", "last_modified_at": datetime.now()},
            {"key": 3, "name": "reviews_enabled", "description": "Permite o deshabilita la creación de reseñas", "enabled": True, "message": "Las reseñas están habilitadas", "last_modified_by": "System Admin", "last_modified_at": datetime.now()}
        ]

        created_flags = 0
        for f in flags_to_create:
            # Verificar si el flag ya existe por su name
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
        
        # 1. Obtener todos los sitios históricos
        sites = HistoricSite.query.filter_by(visible=True).all()
        print(f"📍 Sitios históricos visibles: {len(sites)}")
        for site in sites:
            city_name = site.city.name if site.city else 'Sin ciudad'
            print(f"  - {site.name} ({city_name})")
        
        # 2. Obtener sitios por categoría
        monuments_category = CategorySite.query.filter_by(name='Monumento Histórico').first()
        if monuments_category:
            monuments = HistoricSite.query.filter_by(id_category=monuments_category.id).all()
            print(f"🏛️  Monumentos históricos: {len(monuments)}")
        
        # 3. Obtener usuarios activos
        active_users = User.query.filter_by(active=True).all()
        print(f"👥 Usuarios activos: {len(active_users)}")
        for user in active_users:
            print(f"  - {user.name} {user.last_name} ({user.mail})")

def main():
    """Función principal"""
    print("🚀 Iniciando ejemplo de uso de modelos SQLAlchemy")
    print("=" * 50)
    
    # Configurar base de datos
    app = setup_database()
    
    # Crear datos de ejemplo
    create_sample_data(app)
    
    # Mostrar ejemplos de consultas
    query_examples(app)
    
    print("\n" + "=" * 50)
    print("✅ Ejemplo completado exitosamente!")
    print("\n💡 Próximos pasos:")
    print("  1. Ejecutar las migraciones (si usas Flask-Migrate): flask db upgrade")
    print("  2. Iniciar la aplicación: python main.py")

if __name__ == '__main__':
    main()