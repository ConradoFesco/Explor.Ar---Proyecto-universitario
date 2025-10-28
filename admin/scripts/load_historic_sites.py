#!/usr/bin/env python3
"""
Script para cargar 15 sitios históricos en la base de datos
Uso: python scripts/load_historic_sites.py
"""

import sys
import os

# Agregar el directorio raíz al path para importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.web import create_app
from src.web.extensions import db
from src.core.models.historic_site import HistoricSite
from src.core.models.city import City
from src.core.models.province import Province
from src.core.models.category_site import CategorySite
from src.core.models.state_site import StateSite


def get_or_create_province(name):
    """Obtiene o crea una provincia"""
    province = Province.query.filter_by(name=name).first()
    if not province:
        province = Province(name=name, deleted=False)
        db.session.add(province)
        db.session.flush()
    return province


def get_or_create_city(name, province_id):
    """Obtiene o crea una ciudad"""
    city = City.query.filter_by(name=name, id_province=province_id).first()
    if not city:
        city = City(name=name, id_province=province_id, deleted=False)
        db.session.add(city)
        db.session.flush()
    return city


def get_or_create_category(name):
    """Obtiene o crea una categoría"""
    category = CategorySite.query.filter_by(name=name).first()
    if not category:
        category = CategorySite(name=name, deleted=False)
        db.session.add(category)
        db.session.flush()
    return category


def get_or_create_state(name):
    """Obtiene o crea un estado"""
    state = StateSite.query.filter_by(state=name).first()
    if not state:
        state = StateSite(state=name, deleted=False)
        db.session.add(state)
        db.session.flush()
    return state


def create_historic_sites():
    """Crear 15 sitios históricos"""
    
    # Crear/obtener provincias
    print("📍 Verificando provincias...")
    provincia_ba = get_or_create_province("Buenos Aires")
    
    # Crear/obtener ciudades
    print("🏙️  Verificando ciudades...")
    la_plata = get_or_create_city("La Plata", provincia_ba.id)
    buenos_aires = get_or_create_city("Ciudad Autónoma de Buenos Aires", provincia_ba.id)
    tigre = get_or_create_city("Tigre", provincia_ba.id)
    san_isidro = get_or_create_city("San Isidro", provincia_ba.id)
    
    # Crear/obtener categorías
    print("🏛️  Verificando categorías...")
    arquitectura = get_or_create_category("Arquitectura")
    infraestructura = get_or_create_category("Infraestructura")
    arqueologico = get_or_create_category("Sitio arqueologico")
    
    # Crear/obtener estados
    print("📊 Verificando estados...")
    estado_bueno = get_or_create_state("Bueno")
    estado_regular = get_or_create_state("Regular")
    estado_malo = get_or_create_state("Malo")
    
    # Definir los 15 sitios históricos
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
        }
    ]
    
    # Crear los sitios históricos
    print(f"\n🏛️  Creando {len(sites_data)} sitios históricos...")
    created_count = 0
    skipped_count = 0
    
    for site_data in sites_data:
        # Verificar si ya existe
        existing = HistoricSite.query.filter_by(name=site_data["name"]).first()
        if existing:
            print(f"   ⚠️  '{site_data['name']}' ya existe, omitiendo...")
            skipped_count += 1
            continue
        
        # Crear el sitio
        site = HistoricSite(**site_data, deleted=False)
        db.session.add(site)
        created_count += 1
        print(f"   ✓ Creado: {site_data['name']}")
    
    return created_count, skipped_count


def main():
    """Función principal"""
    print("=" * 70)
    print("🏛️  CARGA DE SITIOS HISTÓRICOS")
    print("=" * 70)
    
    # Crear la aplicación Flask
    app = create_app()
    
    with app.app_context():
        try:
            # Crear los sitios históricos
            created, skipped = create_historic_sites()
            
            # Confirmar los cambios
            db.session.commit()
            
            # Resumen final
            print("\n" + "=" * 70)
            print("✅ ¡Proceso completado exitosamente!")
            print(f"\n📊 Resumen:")
            print(f"   - Sitios creados: {created}")
            print(f"   - Sitios omitidos (ya existían): {skipped}")
            print(f"   - Total de sitios en la BD: {HistoricSite.query.filter_by(deleted=False).count()}")
            print("=" * 70)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al cargar sitios históricos: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

