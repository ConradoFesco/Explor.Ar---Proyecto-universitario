#!/usr/bin/env python3
"""
Script provisorio para cargar masivamente imágenes a sitios históricos.
Carga al menos 3-5 imágenes (preferiblemente más) para cada sitio que no tenga imágenes.

Uso: python scripts/bulk_load_images.py [--min-images MIN] [--max-images MAX]
"""

import sys
import os
import random
import requests
from io import BytesIO

# Agregar el directorio raíz al path para importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.web import create_app
from src.web.extensions import db
from src.core.models.historic_site import HistoricSite
from src.core.models.site_image import SiteImage
from src.core.services.site_image_service import site_image_service

# URLs de imágenes de placeholder (puedes cambiarlas por otras fuentes)
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
    "Vista general del entorno"
]


def download_image(url: str) -> bytes:
    """Descarga una imagen desde una URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"   ⚠️  Error al descargar imagen desde {url}: {e}")
        return None


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
    """
    # Verificar cuántas imágenes ya tiene
    current_count = SiteImage.query.filter_by(id_site=site.id).count()
    
    if current_count > 0:
        print(f"   [SKIP] '{site.name}' ya tiene {current_count} imagen(es), omitiendo...")
        return 0
    
    # Determinar cuántas imágenes cargar (entre min y max)
    num_images = random.randint(min_images, max_images)
    
    # Mezclar las URLs para tener variedad
    shuffled_urls = random.sample(PLACEHOLDER_IMAGE_URLS, min(num_images, len(PLACEHOLDER_IMAGE_URLS)))
    
    files_data = []
    for idx, url in enumerate(shuffled_urls):
        # Descargar imagen
        print(f"      Descargando imagen {idx + 1}/{num_images}...", end='\r')
        image_data = download_image(url)
        if not image_data:
            continue
        
        # Crear FileStorage
        filename = f"site_{site.id}_image_{idx + 1}.jpg"
        file_storage = create_file_storage(image_data, filename)
        
        # Generar título y descripción
        titulo_alt = f"{site.name} - {IMAGE_DESCRIPTIONS[idx % len(IMAGE_DESCRIPTIONS)]}"
        descripcion = f"Imagen {idx + 1} de {num_images} del sitio histórico {site.name}"
        
        # Marcar la primera como portada si no hay imágenes
        is_cover = (idx == 0)
        
        files_data.append({
            'file': file_storage,
            'titulo_alt': titulo_alt,
            'descripcion': descripcion,
            'is_cover': is_cover,
            'order': idx
        })
    
    if not files_data:
        print(f"   [ERROR] No se pudieron descargar imagenes para '{site.name}'")
        return 0
    
    try:
        # Subir imágenes usando el servicio
        uploaded_images = site_image_service.upload_multiple_images(
            site_id=site.id,
            files_data=files_data,
            user_id=user_id
        )
        
        print(f"   [OK] Cargadas {len(uploaded_images)} imagen(es) para '{site.name}'")
        return len(uploaded_images)
        
    except Exception as e:
        print(f"   [ERROR] Error al cargar imagenes para '{site.name}': {e}")
        return 0


def bulk_load_images(min_images: int = 3, max_images: int = 7, user_id: int = None):
    """
    Carga imágenes masivamente para todos los sitios históricos.
    
    Args:
        min_images: Número mínimo de imágenes por sitio
        max_images: Número máximo de imágenes por sitio
        user_id: ID del usuario (opcional)
    """
    # Obtener todos los sitios históricos no eliminados
    sites = HistoricSite.query.filter_by(deleted=False).all()
    
    if not sites:
        print("[WARNING] No se encontraron sitios historicos en la base de datos.")
        return 0, 0
    
    print(f"\nCargando imagenes para {len(sites)} sitio(s) historico(s)...")
    print(f"   Rango de imagenes por sitio: {min_images}-{max_images}\n")
    
    total_uploaded = 0
    sites_processed = 0
    
    for site in sites:
        uploaded = load_images_for_site(site, min_images, max_images, user_id)
        if uploaded > 0:
            total_uploaded += uploaded
            sites_processed += 1
    
    return total_uploaded, sites_processed


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Carga masiva de imágenes para sitios históricos')
    parser.add_argument('--min-images', type=int, default=3, 
                       help='Número mínimo de imágenes por sitio (default: 3)')
    parser.add_argument('--max-images', type=int, default=7,
                       help='Número máximo de imágenes por sitio (default: 7)')
    parser.add_argument('--user-id', type=int, default=None,
                       help='ID del usuario que realiza la carga (opcional)')
    
    args = parser.parse_args()
    
    # Validar argumentos
    if args.min_images < 1:
        print("[ERROR] El numero minimo de imagenes debe ser al menos 1")
        return False
    
    if args.max_images < args.min_images:
        print("[ERROR] El numero maximo de imagenes debe ser mayor o igual al minimo")
        return False
    
    print("=" * 70)
    print("CARGA MASIVA DE IMAGENES PARA SITIOS HISTORICOS")
    print("=" * 70)
    print(f"NOTA: Este es un script provisorio que usa imagenes de placeholder")
    print(f"   (Picsum Photos). Para produccion, reemplaza las URLs por imagenes reales.")
    print("=" * 70)
    
    # Crear la aplicación Flask
    app = create_app()
    
    with app.app_context():
        try:
            # Cargar imágenes
            total_uploaded, sites_processed = bulk_load_images(
                min_images=args.min_images,
                max_images=args.max_images,
                user_id=args.user_id
            )
            
            # Resumen final
            print("\n" + "=" * 70)
            print("[SUCCESS] Proceso completado!")
            print(f"\nResumen:")
            print(f"   - Sitios procesados: {sites_processed}")
            print(f"   - Total de imagenes cargadas: {total_uploaded}")
            print(f"   - Promedio de imagenes por sitio: {total_uploaded / sites_processed if sites_processed > 0 else 0:.1f}")
            print("=" * 70)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] Error al cargar imagenes: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

