#!/usr/bin/env python3
"""
Script para cargar datos iniciales necesarios para producción
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from datetime import datetime
import random
import requests
from io import BytesIO
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
from src.core.models.historic_site import HistoricSite
from src.core.models.review import HistoricSiteReview
from src.core.models.city import City
from src.core.models.province import Province
from src.core.models.site_image import SiteImage
from src.core.services.site_image_service import site_image_service

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
    
    print("[USERS] Verificando usuarios dummy...")

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
            print(f"   [SKIP] Usuario {mail} ya existe, saltando...")
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
    print(f"   [OK] Usuarios dummy creados: {len(dummy_users)}")
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
        print("   [OK] Categoria dummy creada")

    state = StateSite.query.filter_by(deleted=False).first()
    if not state:
        state = StateSite(state="Bueno", deleted=False)
        db.session.add(state)
        db.session.commit()
        print("   [OK] Estado dummy creado")

    return category.id, state.id

# URLs de imágenes de placeholder para sitios históricos
PLACEHOLDER_IMAGE_URLS = [
    "https://picsum.photos/800/600?random=1",
    "https://picsum.photos/800/600?random=2",
    "https://picsum.photos/800/600?random=3",
    "https://picsum.photos/800/600?random=4",
    "https://picsum.photos/800/600?random=5",
    "https://picsum.photos/800/600?random=6",
    "https://picsum.photos/800/600?random=7",
    "https://picsum.photos/800/600?random=8",
    "https://picsum.photos/800/600?random=9",
    "https://picsum.photos/800/600?random=10",
    "https://picsum.photos/800/600?random=11",
    "https://picsum.photos/800/600?random=12",
    "https://picsum.photos/800/600?random=13",
    "https://picsum.photos/800/600?random=14",
    "https://picsum.photos/800/600?random=15",
]

# Descripciones genéricas para las imágenes
IMAGE_DESCRIPTIONS = [
    "Vista exterior del sitio histórico",
    "Detalle arquitectónico del edificio",
    "Vista panorámica del lugar",
    "Interior del sitio histórico",
    "Fachada principal del monumento",
    "Vista lateral del edificio",
    "Detalle de la estructura",
    "Vista desde otro ángulo",
    "Elementos decorativos del sitio",
    "Vista general del entorno",
    "Detalle de la ornamentación",
    "Vista nocturna del sitio",
    "Perspectiva aérea del lugar",
    "Detalle de materiales históricos",
    "Vista del entorno circundante"
]


class MockFileStorage:
    """Clase mock que simula FileStorage para uso en scripts."""
    def __init__(self, stream: BytesIO, filename: str, content_type: str = 'image/jpeg'):
        self.stream = stream
        self.filename = filename
        self.content_type = content_type
    
    def read(self, size: int = -1) -> bytes:
        """Lee datos del stream."""
        return self.stream.read(size)
    
    def seek(self, pos: int, whence: int = 0) -> int:
        """Mueve el cursor del stream."""
        return self.stream.seek(pos, whence)
    
    def tell(self) -> int:
        """Retorna la posición actual del cursor."""
        return self.stream.tell()


def download_image(url: str) -> bytes:
    """Descarga una imagen desde una URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"      ⚠️  Error al descargar imagen: {e}")
        return None


def create_file_storage(image_data: bytes, filename: str) -> MockFileStorage:
    """Crea un objeto mock FileStorage desde bytes."""
    file_obj = BytesIO(image_data)
    file_storage = MockFileStorage(
        stream=file_obj,
        filename=filename,
        content_type='image/jpeg'
    )
    return file_storage


def load_images_for_site(site: HistoricSite, min_images: int = 3, max_images: int = 7, user_id: int = None):
    """
    Carga imágenes para un sitio histórico.
    
    Args:
        site: Sitio histórico
        min_images: Número mínimo de imágenes a cargar
        max_images: Número máximo de imágenes a cargar
        user_id: ID del usuario (opcional)
    
    Returns:
        int: Número de imágenes cargadas exitosamente
    """
    try:
        # Verificar cuántas imágenes ya tiene
        current_count = SiteImage.query.filter_by(id_site=site.id).count()
        
        if current_count > 0:
            return 0
        
        # Determinar cuántas imágenes cargar (entre min y max)
        num_images = random.randint(min_images, max_images)
        
        # Mezclar las URLs para tener variedad
        shuffled_urls = random.sample(PLACEHOLDER_IMAGE_URLS, min(num_images, len(PLACEHOLDER_IMAGE_URLS)))
        
        files_data = []
        for idx, url in enumerate(shuffled_urls):
            try:
                # Descargar imagen
                image_data = download_image(url)
                if not image_data:
                    continue
                
                # Crear FileStorage
                filename = f"site_{site.id}_image_{idx + 1}.jpg"
                file_storage = create_file_storage(image_data, filename)
                
                # Generar título y descripción
                titulo_alt = f"{site.name} - {IMAGE_DESCRIPTIONS[idx % len(IMAGE_DESCRIPTIONS)]}"
                descripcion = f"Imagen {idx + 1} de {num_images} del sitio histórico {site.name}"
                
                # Marcar la primera como portada
                is_cover = (idx == 0)
                
                files_data.append({
                    'file': file_storage,
                    'titulo_alt': titulo_alt,
                    'descripcion': descripcion,
                    'is_cover': is_cover,
                    'order': idx
                })
            except Exception as e:
                # Continuar con la siguiente imagen si una falla
                continue
        
        if not files_data:
            return 0
        
        # Subir imágenes usando el servicio
        uploaded_images = site_image_service.upload_multiple_images(
            site_id=site.id,
            files_data=files_data,
            user_id=user_id
        )
        
        return len(uploaded_images) if uploaded_images else 0
        
    except Exception as e:
        # Si falla completamente (por ejemplo, MinIO no configurado), retornar 0 sin fallar
        # El error ya se maneja en la función que llama
        raise


def get_or_create_province(name):
    """Obtiene o crea una provincia"""
    province = Province.query.filter_by(name=name, deleted=False).first()
    if not province:
        province = Province(name=name, deleted=False)
        db.session.add(province)
        db.session.flush()
    return province


def get_or_create_city(name, province_id):
    """Obtiene o crea una ciudad"""
    city = City.query.filter_by(name=name, id_province=province_id, deleted=False).first()
    if not city:
        city = City(name=name, id_province=province_id, deleted=False)
        db.session.add(city)
        db.session.flush()
    return city


def create_historic_sites_with_images():
    """
    Crea sitios históricos reales con datos completos e imágenes.
    Devuelve la lista de sitios creados.
    """
    print("[SITES] Creando sitios historicos con imagenes...")
    
    # Asegurar que las categorías y estados existan (deben haberse creado en pasos anteriores)
    arquitectura = CategorySite.query.filter_by(name="Arquitectura", deleted=False).first()
    infraestructura = CategorySite.query.filter_by(name="Infraestructura", deleted=False).first()
    arqueologico = CategorySite.query.filter_by(name="Sitio arqueologico", deleted=False).first()
    
    estado_bueno = StateSite.query.filter_by(state="Bueno", deleted=False).first()
    estado_regular = StateSite.query.filter_by(state="Regular", deleted=False).first()
    estado_malo = StateSite.query.filter_by(state="Malo", deleted=False).first()
    
    # Si no existen, crear categorías y estados básicos
    if not arquitectura:
        arquitectura = CategorySite(name="Arquitectura", deleted=False)
        db.session.add(arquitectura)
        db.session.flush()
        print("   [INFO] Categoria 'Arquitectura' creada")
    
    if not infraestructura:
        infraestructura = CategorySite(name="Infraestructura", deleted=False)
        db.session.add(infraestructura)
        db.session.flush()
        print("   [INFO] Categoria 'Infraestructura' creada")
    
    if not arqueologico:
        arqueologico = CategorySite(name="Sitio arqueologico", deleted=False)
        db.session.add(arqueologico)
        db.session.flush()
        print("   [INFO] Categoria 'Sitio arqueologico' creada")
    
    if not estado_bueno:
        estado_bueno = StateSite(state="Bueno", deleted=False)
        db.session.add(estado_bueno)
        db.session.flush()
        print("   [INFO] Estado 'Bueno' creado")
    
    if not estado_regular:
        estado_regular = StateSite(state="Regular", deleted=False)
        db.session.add(estado_regular)
        db.session.flush()
        print("   [INFO] Estado 'Regular' creado")
    
    if not estado_malo:
        estado_malo = StateSite(state="Malo", deleted=False)
        db.session.add(estado_malo)
        db.session.flush()
        print("   [INFO] Estado 'Malo' creado")
    
    # Hacer commit de categorías y estados antes de continuar
    db.session.commit()
    
    # Obtener o crear provincias
    provincia_ba = get_or_create_province("Buenos Aires")
    db.session.commit()
    
    # Obtener o crear ciudades
    la_plata = get_or_create_city("La Plata", provincia_ba.id)
    buenos_aires = get_or_create_city("Ciudad Autónoma de Buenos Aires", provincia_ba.id)
    tigre = get_or_create_city("Tigre", provincia_ba.id)
    san_isidro = get_or_create_city("San Isidro", provincia_ba.id)
    db.session.commit()
    
    # Definir los sitios históricos
    sites_data = [
        {
            "name": "Catedral de La Plata",
            "brief_description": "Majestuosa catedral neogótica, una de las más grandes de América.",
            "complete_description": "La Catedral de La Plata es un templo de estilo neogótico ubicado en el centro de la ciudad. Su construcción comenzó en 1884 y es considerada una de las catedrales más grandes de América Latina. Cuenta con dos torres que alcanzan los 112 metros de altura.",
            "id_ciudad": la_plata.id,
            "latitude": "-34.9214",
            "longitude": "-57.9544",
            "id_estado": estado_bueno.id,
            "year_inauguration": 1932,
            "id_category": arquitectura.id,
            "visible": True
        },
        {
            "name": "Teatro Argentino de La Plata",
            "brief_description": "Principal teatro lírico de la provincia de Buenos Aires.",
            "complete_description": "El Teatro Argentino es el segundo teatro lírico más importante de Argentina. El edificio actual fue inaugurado en 1999 tras el incendio que destruyó el antiguo teatro en 1977. Cuenta con tecnología de última generación y una excelente acústica.",
            "id_ciudad": la_plata.id,
            "latitude": "-34.9205",
            "longitude": "-57.9547",
            "id_estado": estado_bueno.id,
            "year_inauguration": 1999,
            "id_category": arquitectura.id,
            "visible": True
        },
        {
            "name": "Museo de Ciencias Naturales de La Plata",
            "brief_description": "Uno de los museos de ciencias naturales más importantes de América.",
            "complete_description": "El Museo de La Plata fue fundado en 1884 y alberga una de las colecciones más importantes de fósiles, minerales y piezas arqueológicas de Sudamérica. Su arquitectura es de estilo neoclásico griego y cuenta con más de 3 millones de objetos en su colección.",
            "id_ciudad": la_plata.id,
            "latitude": "-34.9068",
            "longitude": "-57.9322",
            "id_estado": estado_bueno.id,
            "year_inauguration": 1888,
            "id_category": arquitectura.id,
            "visible": True
        },
        {
            "name": "Casa Curutchet",
            "brief_description": "Única obra de Le Corbusier en América Latina.",
            "complete_description": "La Casa Curutchet es una vivienda unifamiliar diseñada por Le Corbusier en 1949. Es la única construcción del arquitecto suizo en América Latina y fue declarada Patrimonio Mundial de la UNESCO en 2016. Representa los cinco puntos de la arquitectura moderna.",
            "id_ciudad": la_plata.id,
            "latitude": "-34.9219",
            "longitude": "-57.9462",
            "id_estado": estado_bueno.id,
            "year_inauguration": 1955,
            "id_category": arquitectura.id,
            "visible": True
        },
        {
            "name": "República de los Niños",
            "brief_description": "Primer parque temático educativo de América Latina.",
            "complete_description": "La República de los Niños es un complejo recreativo inaugurado en 1951 durante el gobierno de Juan Domingo Perón. Fue el primer parque temático educativo de América y se dice que inspiró a Walt Disney para crear Disneyland. Cuenta con réplicas de edificios gubernamentales a escala infantil.",
            "id_ciudad": la_plata.id,
            "latitude": "-34.8828",
            "longitude": "-58.0044",
            "id_estado": estado_regular.id,
            "year_inauguration": 1951,
            "id_category": arquitectura.id,
            "visible": True
        },
        {
            "name": "Teatro Colón",
            "brief_description": "Uno de los teatros de ópera más importantes del mundo.",
            "complete_description": "El Teatro Colón es considerado uno de los cinco teatros de ópera más importantes del mundo por su tamaño, acústica y trayectoria. Inaugurado en 1908, presenta arquitectura ecléctica con elementos italianos y franceses. Ha sido escenario de las más importantes figuras de la música y la danza mundial.",
            "id_ciudad": buenos_aires.id,
            "latitude": "-34.6010",
            "longitude": "-58.3832",
            "id_estado": estado_bueno.id,
            "year_inauguration": 1908,
            "id_category": arquitectura.id,
            "visible": True
        },
        {
            "name": "Obelisco de Buenos Aires",
            "brief_description": "Monumento histórico e ícono de la ciudad de Buenos Aires.",
            "complete_description": "El Obelisco fue construido en 1936 para conmemorar el cuarto centenario de la primera fundación de Buenos Aires. Con 67.5 metros de altura, se encuentra en la Plaza de la República, en la intersección de las avenidas Corrientes y 9 de Julio. Es el monumento más emblemático de la ciudad.",
            "id_ciudad": buenos_aires.id,
            "latitude": "-34.6037",
            "longitude": "-58.3816",
            "id_estado": estado_bueno.id,
            "year_inauguration": 1936,
            "id_category": arquitectura.id,
            "visible": True
        },
        {
            "name": "Casa Rosada",
            "brief_description": "Sede del Poder Ejecutivo de Argentina.",
            "complete_description": "La Casa Rosada es la sede del Poder Ejecutivo de la República Argentina. Su característico color rosa se debe a la mezcla de pintura blanca con sangre de vaca, según cuenta la tradición. El edificio actual fue inaugurado en 1898 y alberga el despacho presidencial y el Museo de la Casa Rosada.",
            "id_ciudad": buenos_aires.id,
            "latitude": "-34.6083",
            "longitude": "-58.3712",
            "id_estado": estado_bueno.id,
            "year_inauguration": 1898,
            "id_category": arquitectura.id,
            "visible": True
        },
        {
            "name": "Caminito",
            "brief_description": "Museo a cielo abierto y tradicional pasaje del barrio de La Boca.",
            "complete_description": "Caminito es una calle museo y un pasaje tradicional del barrio de La Boca. Sus coloridas casas de chapa pintadas, sus artistas callejeros y bailarines de tango lo convierten en uno de los lugares más visitados de Buenos Aires. Fue inaugurado como paseo turístico en 1959.",
            "id_ciudad": buenos_aires.id,
            "latitude": "-34.6380",
            "longitude": "-58.3629",
            "id_estado": estado_regular.id,
            "year_inauguration": 1959,
            "id_category": arquitectura.id,
            "visible": True
        },
        {
            "name": "Puerto Madero",
            "brief_description": "Antiguo puerto reconvertido en moderno barrio comercial y residencial.",
            "complete_description": "Puerto Madero fue el puerto de Buenos Aires entre 1887 y 1925. En la década de 1990 fue objeto de una importante renovación urbanística que lo convirtió en un exclusivo barrio de oficinas, viviendas y restaurantes. Conserva los antiguos depósitos de ladrillo rojo reconvertidos.",
            "id_ciudad": buenos_aires.id,
            "latitude": "-34.6118",
            "longitude": "-58.3636",
            "id_estado": estado_bueno.id,
            "year_inauguration": 1897,
            "id_category": infraestructura.id,
            "visible": True
        },
        {
            "name": "Museo Histórico Nacional del Cabildo",
            "brief_description": "Edificio colonial que fue sede del gobierno durante la época virreinal.",
            "complete_description": "El Cabildo de Buenos Aires fue construido en 1725 y funcionó como sede del ayuntamiento durante la época colonial. Fue escenario de la Revolución de Mayo de 1810. Hoy alberga el Museo Histórico Nacional del Cabildo y de la Revolución de Mayo.",
            "id_ciudad": buenos_aires.id,
            "latitude": "-34.6083",
            "longitude": "-58.3731",
            "id_estado": estado_bueno.id,
            "year_inauguration": 1751,
            "id_category": arquitectura.id,
            "visible": True
        },
        {
            "name": "Museo Naval de Tigre",
            "brief_description": "Museo dedicado a la historia naval argentina.",
            "complete_description": "El Museo Naval de la Nación está ubicado en un edificio victoriano de 1880 en Tigre. Exhibe la historia de la Armada Argentina desde sus orígenes hasta nuestros días, con maquetas de embarcaciones, uniformes históricos y objetos navales.",
            "id_ciudad": tigre.id,
            "latitude": "-34.4257",
            "longitude": "-58.5767",
            "id_estado": estado_bueno.id,
            "year_inauguration": 1892,
            "id_category": arquitectura.id,
            "visible": True
        },
        {
            "name": "Catedral de San Isidro",
            "brief_description": "Importante templo neogótico del siglo XIX.",
            "complete_description": "La Catedral de San Isidro fue construida entre 1895 y 1898 en estilo neogótico. Su torre de 68 metros de altura es visible desde varios puntos de la zona norte. El templo resguarda importantes obras de arte religioso y es sede de la Diócesis de San Isidro.",
            "id_ciudad": san_isidro.id,
            "latitude": "-34.4707",
            "longitude": "-58.5122",
            "id_estado": estado_bueno.id,
            "year_inauguration": 1898,
            "id_category": arquitectura.id,
            "visible": True
        },
        {
            "name": "Observatorio Astronómico de La Plata",
            "brief_description": "Histórico observatorio astronómico fundado en 1883.",
            "complete_description": "El Observatorio Astronómico de La Plata fue creado en 1883 por Francisco P. Moreno. Cuenta con telescopios históricos y modernos, y ha realizado importantes contribuciones a la astronomía argentina. Es sede de la Facultad de Ciencias Astronómicas y Geofísicas de la UNLP.",
            "id_ciudad": la_plata.id,
            "latitude": "-34.9059",
            "longitude": "-57.9323",
            "id_estado": estado_bueno.id,
            "year_inauguration": 1883,
            "id_category": arquitectura.id,
            "visible": True
        },
        {
            "name": "Puente Pueyrredón",
            "brief_description": "Histórico puente que conecta Buenos Aires con Avellaneda.",
            "complete_description": "El Puente Pueyrredón es un puente levadizo inaugurado en 1940 que cruza el Riachuelo. Conecta la Ciudad de Buenos Aires con el partido de Avellaneda. Es una importante vía de comunicación y su mecanismo de apertura para el paso de embarcaciones todavía se utiliza ocasionalmente.",
            "id_ciudad": buenos_aires.id,
            "latitude": "-34.6431",
            "longitude": "-58.3531",
            "id_estado": estado_regular.id,
            "year_inauguration": 1940,
            "id_category": infraestructura.id,
            "visible": True
        }
    ]
    
    created_sites = []
    created_count = 0
    skipped_count = 0
    images_total = 0
    
    # Obtener usuario admin para las imágenes (debe existir por el paso anterior)
    admin_user = User.query.filter_by(mail="grupo06@gmail.com").first()
    user_id = admin_user.id if admin_user else None
    
    if not user_id:
        print("   [WARNING] Usuario admin no encontrado. Las imagenes se cargaran sin user_id")
    
    for site_data in sites_data:
        try:
            # Verificar si ya existe
            existing = HistoricSite.query.filter_by(name=site_data["name"]).first()
            if existing:
                skipped_count += 1
                continue
            
            # Crear el sitio
            site = HistoricSite(**site_data, deleted=False, created_at=datetime.utcnow())
            db.session.add(site)
            db.session.flush()  # Para obtener el ID
            
            # Intentar cargar imágenes para el sitio (no fallar si falla)
            images_loaded = 0
            try:
                images_loaded = load_images_for_site(site, min_images=3, max_images=7, user_id=user_id)
                images_total += images_loaded
            except Exception as img_error:
                # No fallar todo el proceso si falla la carga de imágenes
                print(f"      [WARNING] No se pudieron cargar imagenes para '{site_data['name']}': {img_error}")
                images_loaded = 0
            
            created_sites.append(site)
            created_count += 1
            if images_loaded > 0:
                print(f"   [OK] Creado: {site_data['name']} ({images_loaded} imagenes)")
            else:
                print(f"   [OK] Creado: {site_data['name']} (sin imagenes)")
        
        except Exception as e:
            print(f"   [ERROR] Error al crear sitio '{site_data.get('name', 'desconocido')}': {e}")
            db.session.rollback()
            continue
    
    # Hacer commit de todos los sitios creados
    try:
        db.session.commit()
    except Exception as e:
        print(f"   [ERROR] Error al hacer commit de sitios: {e}")
        db.session.rollback()
        return created_sites
    
    if created_count == 0 and skipped_count > 0:
        print(f"   [SKIP] Todos los sitios ya existen ({skipped_count} sitios)")
    elif created_count > 0:
        print(f"   [OK] Sitios creados: {created_count}, omitidos: {skipped_count}, imagenes totales: {images_total}")
    
    return created_sites


def create_dummy_sites_if_needed(id_category, id_estado):
    """
    Crea algunos HistoricSite si no existe ninguno; devuelve la lista de sitios.
    Usa los campos del modelo: id_category, id_estado, brief_description, complete_description, visible.
    """
    sites = HistoricSite.query.filter_by(deleted=False).all()
    if sites:
        print(f"   [OK] Sitios existentes: {len(sites)}")
        return sites

    print("   [WARNING] No hay sitios historicos. Creando sitios dummy...")
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
        db.session.flush()
        
        # Intentar cargar imágenes para sitios dummy también (no fallar si falla)
        try:
            admin_user = User.query.filter_by(mail="grupo06@gmail.com").first()
            user_id = admin_user.id if admin_user else None
            load_images_for_site(s, min_images=2, max_images=5, user_id=user_id)
        except Exception as img_error:
            # No fallar si las imágenes no se pueden cargar
            print(f"      [WARNING] No se pudieron cargar imagenes para sitio dummy: {img_error}")
        
        dummy_sites.append(s)

    db.session.commit()
    print(f"   [OK] Sitios dummy creados: {len(dummy_sites)}")
    return dummy_sites

def create_test_reviews(users):
    """
    Crea reseñas de prueba. Asegura usuarios y sitios (crea dummy si hace falta).
    Usa strings para status ('pending','approved','rejected','deleted').
    """
  
    print("[REVIEWS] Creando resenas de prueba...")

   
    if not users:
        print("   [ERROR] No hay usuarios y no se pudieron crear.")
        return 0

    # 2) Asegurar category/state y sitios
    category_id, state_id = ensure_category_and_state()
    sites = create_dummy_sites_if_needed(category_id, state_id)
    if not sites:
        print("   [ERROR] No se pudieron crear sitios.")
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
    print(f"   [OK] Resenas creadas: {created}")
    return created

def main(app=None):
    """
    Función principal para cargar todos los seeds.
    
    Args:
        app: Instancia de Flask (opcional). Si no se proporciona, se crea una nueva.
    """
    print("[SEEDS] Iniciando carga de datos iniciales (seeds)...")
    print("=" * 60)
    
    # Si no se proporciona una app, crear una nueva
    if app is None:
        app = create_app()
        use_context = True
    else:
        # Si ya tenemos una app, asumimos que ya estamos en un contexto
        use_context = False
    
    def _execute_seeds():
        try:
            # 1. Crear permisos
            print("\n[1/9] Creando permisos...")
            permisos_creados = create_permissions()
            print(f"   [OK] Permisos procesados: {permisos_creados} nuevos")
            
            # 2. Crear roles
            print("\n[2/9] Creando roles...")
            roles, roles_creados = create_roles()
            db.session.commit() 
            print(f"   [OK] Roles procesados: {roles_creados} nuevos")
            
            # 3. Asignar permisos a roles
            print("\n[3/9] Asignando permisos a roles...")
            asignaciones = assign_permissions_to_roles(roles)
            db.session.commit()
            print(f"   [OK] Relaciones permiso-rol creadas: {asignaciones}")
            
            # 4. Crear categorías
            print("\n[4/9] Creando categorias...")
            categorias = create_categories()
            db.session.commit()
            print(f"   [OK] Categorias creadas: {categorias}")
            
            # 5. Crear estados
            print("\n[5/9] Creando estados de conservacion...")
            estados = create_states()
            db.session.commit()
            print(f"   [OK] Estados creados: {estados}")
            
            # 6. Crear flags
            print("\n[6/9] Creando flags del sistema...")
            flags = create_flags()
            db.session.commit()
            print(f"   [OK] Flags creados: {flags}")
            
            # 7. Crear super administrador
            print("\n[7/9] Creando usuario super administrador...")
            super_admin_created = create_super_admin()
            if super_admin_created:
                print(f"   [OK] Super Admin creado: grupo06@gmail.com")
            else:
                print(f"   [SKIP] Super Admin ya existe")
            db.session.commit()
            
            # 8. Crear sitios históricos con imágenes
            print("\n[8/9] Creando sitios historicos con imagenes...")
            sites = create_historic_sites_with_images()
            print(f"   [OK] Proceso de sitios completado")
            
            # 9. Crear usuarios dummy y reseñas
            print("\n[9/9] Creando usuarios dummy y reseñas de prueba...")
            users = create_dummy_users(roles)
            reviews = create_test_reviews(users)
            
            # Resumen final
            print("\n" + "=" * 60)
            print("[SUCCESS] Seeds cargados exitosamente!")
            print("\nResumen del sistema:")
            print(f"   - Permisos totales: {Permission.query.count()}")
            print(f"   - Roles totales: {RolUser.query.count()}")
            print(f"   - Relaciones permiso-rol: {PermissionRolUser.query.count()}")
            print(f"   - Categorias: {CategorySite.query.filter_by(deleted=False).count()}")
            print(f"   - Estados: {StateSite.query.filter_by(deleted=False).count()}")
            print(f"   - Flags: {Flag.query.count()}")
            print(f"   - Usuarios: {User.query.filter_by(deleted=False).count()}")
            print(f"   - Relaciones usuario-rol: {RolUserUser.query.count()}")
            print(f"   - Sitios historicos: {HistoricSite.query.filter_by(deleted=False).count()}")
            print(f"   - Imagenes de sitios: {SiteImage.query.count()}")
            print(f"   - Resenas: {HistoricSiteReview.query.count()}")
            
            print("\nCredenciales de acceso:")
            print(f"   Email: grupo06@gmail.com")
            print(f"   Contrasena: grupo06")
            print(f"   Super admin: Si")
            print("\n[WARNING] IMPORTANTE: Cambiar estas credenciales en produccion")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] Error al cargar seeds: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
    
    # Ejecutar dentro o fuera del contexto según corresponda
    if use_context:
        with app.app_context():
            return _execute_seeds()
    else:
        return _execute_seeds()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

