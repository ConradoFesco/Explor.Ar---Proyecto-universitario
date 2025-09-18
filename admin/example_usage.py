#!/usr/bin/env python3
"""
Ejemplo de uso de los modelos SQLAlchemy para el sistema de sitios históricos.
Este script demuestra cómo crear, consultar y relacionar datos usando los modelos.
"""

import os
from datetime import datetime
from src.web import create_app, db
from src.web.models import (
    User, CategorySite, Province, City, StateSite, 
    HistoricSite, Tag, Event, Permission, RolUser,
    PermissionRolUser, RolUserUser, TagHistoricSite
)

def setup_database():
    """Configurar la base de datos y crear tablas"""
    app = create_app()
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        print("✅ Base de datos configurada correctamente")
        return app

def create_sample_data(app):
    """Crear datos de ejemplo"""
    with app.app_context():
        print("\n📝 Creando datos de ejemplo...")
        
        # 1. Crear categorías de sitios
        categories = [
            CategorySite(name='Monumento Histórico'),
            CategorySite(name='Museo'),
            CategorySite(name='Iglesia'),
            CategorySite(name='Plaza'),
            CategorySite(name='Edificio Gubernamental')
        ]
        db.session.add_all(categories)
        db.session.commit()
        print(f"✅ Creadas {len(categories)} categorías")
        
        # 2. Crear provincias y ciudades
        provinces = [
            Province(name='Buenos Aires'),
            Province(name='Córdoba'),
            Province(name='Santa Fe')
        ]
        db.session.add_all(provinces)
        db.session.commit()
        
        cities = [
            City(name='La Plata', id_province=provinces[0].id),
            City(name='Mar del Plata', id_province=provinces[0].id),
            City(name='Córdoba Capital', id_province=provinces[1].id),
            City(name='Rosario', id_province=provinces[2].id)
        ]
        db.session.add_all(cities)
        db.session.commit()
        print(f"✅ Creadas {len(provinces)} provincias y {len(cities)} ciudades")
        
        # 3. Crear estados de sitios
        states = [
            StateSite(state='Excelente'),
            StateSite(state='Bueno'),
            StateSite(state='Regular'),
            StateSite(state='Malo')
        ]
        db.session.add_all(states)
        db.session.commit()
        print(f"✅ Creados {len(states)} estados de sitios")
        
        # 4. Crear usuarios
        users = [
            User(
                mail='admin@historicos.com',
                name='Admin',
                last_name='Sistema',
                password='admin123',
                active=True
            ),
            User(
                mail='editor@historicos.com',
                name='Editor',
                last_name='Contenido',
                password='editor123',
                active=True
            )
        ]
        db.session.add_all(users)
        db.session.commit()
        print(f"✅ Creados {len(users)} usuarios")
        
        # 5. Crear sitios históricos
        historic_sites = [
            HistoricSite(
                name='Casa Rosada',
                brief_description='Sede del Poder Ejecutivo de la República Argentina',
                complete_description='La Casa Rosada es la sede del Poder Ejecutivo de la República Argentina. Ubicada en la Plaza de Mayo, es uno de los edificios más emblemáticos del país.',
                id_ciudad=cities[0].id,  # La Plata
                latitude='-34.6083',
                longitude='-58.3712',
                id_estado=states[0].id,  # Excelente
                year_inauguration=1898,
                id_category=categories[4].id,  # Edificio Gubernamental
                visible=True
            ),
            HistoricSite(
                name='Teatro Colón',
                brief_description='Uno de los teatros de ópera más importantes del mundo',
                complete_description='El Teatro Colón es considerado uno de los teatros de ópera más importantes del mundo, junto con La Scala de Milán, la Ópera Garnier de París y la Ópera Estatal de Viena.',
                id_ciudad=cities[0].id,  # La Plata
                latitude='-34.6011',
                longitude='-58.3836',
                id_estado=states[0].id,  # Excelente
                year_inauguration=1908,
                id_category=categories[1].id,  # Museo
                visible=True
            ),
            HistoricSite(
                name='Catedral de Córdoba',
                brief_description='Principal templo católico de la ciudad de Córdoba',
                complete_description='La Catedral de Córdoba es el principal templo católico de la ciudad de Córdoba, Argentina. Fue construida entre 1577 y 1758.',
                id_ciudad=cities[2].id,  # Córdoba Capital
                latitude='-31.4201',
                longitude='-64.1888',
                id_estado=states[1].id,  # Bueno
                year_inauguration=1758,
                id_category=categories[2].id,  # Iglesia
                visible=True
            )
        ]
        db.session.add_all(historic_sites)
        db.session.commit()
        print(f"✅ Creados {len(historic_sites)} sitios históricos")
        
        # 6. Crear tags
        tags = [
            Tag(name='Patrimonio Mundial', slug='patrimonio-mundial'),
            Tag(name='Arquitectura Colonial', slug='arquitectura-colonial'),
            Tag(name='Cultura', slug='cultura'),
            Tag(name='Historia', slug='historia'),
            Tag(name='Turismo', slug='turismo')
        ]
        db.session.add_all(tags)
        db.session.commit()
        print(f"✅ Creados {len(tags)} tags")
        
        # 7. Asociar tags con sitios históricos
        tag_site_relations = [
            TagHistoricSite(Tag_id=tags[0].id, Historic_Site_id=historic_sites[0].id),  # Casa Rosada - Patrimonio Mundial
            TagHistoricSite(Tag_id=tags[3].id, Historic_Site_id=historic_sites[0].id),  # Casa Rosada - Historia
            TagHistoricSite(Tag_id=tags[4].id, Historic_Site_id=historic_sites[0].id),  # Casa Rosada - Turismo
            TagHistoricSite(Tag_id=tags[0].id, Historic_Site_id=historic_sites[1].id),  # Teatro Colón - Patrimonio Mundial
            TagHistoricSite(Tag_id=tags[2].id, Historic_Site_id=historic_sites[1].id),  # Teatro Colón - Cultura
            TagHistoricSite(Tag_id=tags[1].id, Historic_Site_id=historic_sites[2].id),  # Catedral - Arquitectura Colonial
            TagHistoricSite(Tag_id=tags[3].id, Historic_Site_id=historic_sites[2].id),  # Catedral - Historia
        ]
        db.session.add_all(tag_site_relations)
        db.session.commit()
        print(f"✅ Creadas {len(tag_site_relations)} relaciones tag-sitio")
        
        # 8. Crear eventos
        events = [
            Event(
                id_site=historic_sites[0].id,
                id_user=users[0].id,
                date_time=datetime.now(),
                type_Action='CREATE'
            ),
            Event(
                id_site=historic_sites[1].id,
                id_user=users[1].id,
                date_time=datetime.now(),
                type_Action='UPDATE'
            )
        ]
        db.session.add_all(events)
        db.session.commit()
        print(f"✅ Creados {len(events)} eventos")
        
        # 9. Crear roles y permisos
        roles = [
            RolUser(name='Administrador'),
            RolUser(name='Editor'),
            RolUser(name='Visitante')
        ]
        db.session.add_all(roles)
        db.session.commit()
        
        permissions = [
            Permission(name='create_site'),
            Permission(name='edit_site'),
            Permission(name='delete_site'),
            Permission(name='view_site')
        ]
        db.session.add_all(permissions)
        db.session.commit()
        
        # Asignar permisos a roles
        role_permissions = [
            PermissionRolUser(Permission_id=permissions[0].id, Rol_User_id=roles[0].id),  # Admin - create
            PermissionRolUser(Permission_id=permissions[1].id, Rol_User_id=roles[0].id),  # Admin - edit
            PermissionRolUser(Permission_id=permissions[2].id, Rol_User_id=roles[0].id),  # Admin - delete
            PermissionRolUser(Permission_id=permissions[3].id, Rol_User_id=roles[0].id),  # Admin - view
            PermissionRolUser(Permission_id=permissions[1].id, Rol_User_id=roles[1].id),  # Editor - edit
            PermissionRolUser(Permission_id=permissions[3].id, Rol_User_id=roles[1].id),  # Editor - view
            PermissionRolUser(Permission_id=permissions[3].id, Rol_User_id=roles[2].id),  # Visitante - view
        ]
        db.session.add_all(role_permissions)
        db.session.commit()
        
        # Asignar roles a usuarios
        user_roles = [
            RolUserUser(Rol_User_id=roles[0].id, User_id=users[0].id),  # Admin - Administrador
            RolUserUser(Rol_User_id=roles[1].id, User_id=users[1].id),  # Editor - Editor
        ]
        db.session.add_all(user_roles)
        db.session.commit()
        print(f"✅ Creados {len(roles)} roles, {len(permissions)} permisos y sus relaciones")

def query_examples(app):
    """Ejemplos de consultas a la base de datos"""
    with app.app_context():
        print("\n🔍 Ejemplos de consultas:")
        
        # 1. Obtener todos los sitios históricos
        sites = HistoricSite.query.filter_by(visible=True).all()
        print(f"📍 Sitios históricos visibles: {len(sites)}")
        for site in sites:
            print(f"   - {site.name} ({site.city.name if site.city else 'Sin ciudad'})")
        
        # 2. Obtener sitios por categoría
        monuments = HistoricSite.query.join(CategorySite).filter(
            CategorySite.name == 'Monumento Histórico'
        ).all()
        print(f"🏛️ Monumentos históricos: {len(monuments)}")
        
        # 3. Obtener usuarios activos
        active_users = User.query.filter_by(active=True).all()
        print(f"👥 Usuarios activos: {len(active_users)}")
        for user in active_users:
            print(f"   - {user.name} {user.last_name} ({user.mail})")
        
        # 4. Obtener eventos recientes
        recent_events = Event.query.order_by(Event.date_time.desc()).limit(5).all()
        print(f"📅 Eventos recientes: {len(recent_events)}")
        for event in recent_events:
            print(f"   - {event.type_Action} en {event.historic_site.name} por {event.user.name}")
        
        # 5. Obtener sitios con tags específicos
        cultural_sites = HistoricSite.query.join(TagHistoricSite).join(Tag).filter(
            Tag.name == 'Cultura'
        ).all()
        print(f"🎭 Sitios culturales: {len(cultural_sites)}")
        for site in cultural_sites:
            print(f"   - {site.name}")

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
    print("   1. Ejecutar las migraciones: flask db upgrade")
    print("   2. Ejecutar las pruebas: python -m pytest tests/")
    print("   3. Iniciar la aplicación: python main.py")

if __name__ == '__main__':
    main()
