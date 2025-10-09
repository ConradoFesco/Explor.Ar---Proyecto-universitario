import pytest
import os
from datetime import datetime
from src.web import create_app
from src.web.extensions import db
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

@pytest.fixture
def app():
    """Crear aplicación de prueba"""
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de prueba"""
    return app.test_client()

class TestUser:
    """Pruebas para el modelo User"""
    
    def test_create_user(self, app):
        with app.app_context():
            user = User(
                mail='test@example.com',
                name='Juan',
                last_name='Pérez',
                password='password123',
                active=True
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.mail == 'test@example.com'
            assert user.name == 'Juan'
            assert user.last_name == 'Pérez'
            assert user.active is True
            assert user.deleted is False
    
    def test_user_to_dict(self, app):
        with app.app_context():
            user = User(
                mail='test@example.com',
                name='Juan',
                last_name='Pérez',
                password='password123',
                active=True
            )
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            assert user_dict['mail'] == 'test@example.com'
            assert user_dict['name'] == 'Juan'
            assert 'password' not in user_dict  # Password no debe estar en el dict

class TestCategorySite:
    """Pruebas para el modelo CategorySite"""
    
    def test_create_category_site(self, app):
        with app.app_context():
            category = CategorySite(name='Monumento Histórico')
            db.session.add(category)
            db.session.commit()
            
            assert category.id is not None
            assert category.name == 'Monumento Histórico'
            assert category.deleted is False

class TestProvince:
    """Pruebas para el modelo Province"""
    
    def test_create_province(self, app):
        with app.app_context():
            province = Province(name='Buenos Aires')
            db.session.add(province)
            db.session.commit()
            
            assert province.id is not None
            assert province.name == 'Buenos Aires'

class TestCity:
    """Pruebas para el modelo City"""
    
    def test_create_city(self, app):
        with app.app_context():
            # Primero crear una provincia
            province = Province(name='Buenos Aires')
            db.session.add(province)
            db.session.commit()
            
            # Luego crear una ciudad
            city = City(name='La Plata', id_province=province.id)
            db.session.add(city)
            db.session.commit()
            
            assert city.id is not None
            assert city.name == 'La Plata'
            assert city.id_province == province.id

class TestHistoricSite:
    """Pruebas para el modelo HistoricSite"""
    
    def test_create_historic_site(self, app):
        with app.app_context():
            # Crear dependencias
            category = CategorySite(name='Monumento')
            city = City(name='Buenos Aires')
            state = StateSite(state='Bueno')
            
            db.session.add_all([category, city, state])
            db.session.commit()
            
            # Crear sitio histórico
            site = HistoricSite(
                name='Casa Rosada',
                brief_description='Sede del gobierno argentino',
                complete_description='La Casa Rosada es la sede del Poder Ejecutivo de la República Argentina',
                id_ciudad=city.id,
                latitude='-34.6083',
                longitude='-58.3712',
                id_estado=state.id,
                year_inauguration=1898,
                id_category=category.id,
                visible=True
            )
            db.session.add(site)
            db.session.commit()
            
            assert site.id is not None
            assert site.name == 'Casa Rosada'
            assert site.visible is True

class TestTag:
    """Pruebas para el modelo Tag"""
    
    def test_create_tag(self, app):
        with app.app_context():
            tag = Tag(name='Patrimonio Mundial', slug='patrimonio-mundial')
            db.session.add(tag)
            db.session.commit()
            
            assert tag.id is not None
            assert tag.name == 'Patrimonio Mundial'
            assert tag.slug == 'patrimonio-mundial'

class TestEvent:
    """Pruebas para el modelo Event"""
    
    def test_create_event(self, app):
        with app.app_context():
            # Crear dependencias
            user = User(
                mail='admin@example.com',
                name='Admin',
                last_name='User',
                password='password123'
            )
            site = HistoricSite(
                name='Test Site',
                brief_description='Test description',
                latitude='-34.6083',
                longitude='-58.3712',
                visible=True
            )
            
            db.session.add_all([user, site])
            db.session.commit()
            
            # Crear evento
            event = Event(
                id_site=site.id,
                id_user=user.id,
                date_time=datetime.now(),
                type_Action='CREATE'
            )
            db.session.add(event)
            db.session.commit()
            
            assert event.id is not None
            assert event.type_Action == 'CREATE'
            assert event.id_site == site.id
            assert event.id_user == user.id

class TestRelationships:
    """Pruebas para las relaciones entre modelos"""
    
    def test_user_events_relationship(self, app):
        with app.app_context():
            # Crear usuario
            user = User(
                mail='test@example.com',
                name='Test',
                last_name='User',
                password='password123'
            )
            db.session.add(user)
            db.session.commit()
            
            # Crear sitio histórico
            site = HistoricSite(
                name='Test Site',
                brief_description='Test description',
                latitude='-34.6083',
                longitude='-58.3712',
                visible=True
            )
            db.session.add(site)
            db.session.commit()
            
            # Crear evento
            event = Event(
                id_site=site.id,
                id_user=user.id,
                date_time=datetime.now(),
                type_Action='CREATE'
            )
            db.session.add(event)
            db.session.commit()
            
            # Verificar relación
            assert len(user.events) == 1
            assert user.events[0].type_Action == 'CREATE'
    
    def test_historic_site_tags_relationship(self, app):
        with app.app_context():
            # Crear sitio histórico
            site = HistoricSite(
                name='Test Site',
                brief_description='Test description',
                latitude='-34.6083',
                longitude='-58.3712',
                visible=True
            )
            db.session.add(site)
            db.session.commit()
            
            # Crear tag
            tag = Tag(name='Test Tag', slug='test-tag')
            db.session.add(tag)
            db.session.commit()
            
            # Crear relación
            tag_site = TagHistoricSite(
                Tag_id=tag.id,
                Historic_Site_id=site.id
            )
            db.session.add(tag_site)
            db.session.commit()
            
            # Verificar relación
            assert len(site.tag_historic_sites) == 1
            assert site.tag_historic_sites[0].Tag_id == tag.id

if __name__ == '__main__':
    pytest.main([__file__])
