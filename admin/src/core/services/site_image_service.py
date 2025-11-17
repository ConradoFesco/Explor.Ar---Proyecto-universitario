"""
Servicios de dominio para Imágenes de Sitios Históricos: CRUD, subida a MinIO, ordenamiento y portada.
"""
from src.core.models.site_image import SiteImage
from src.core.models.historic_site import HistoricSite
from src.web import exceptions as exc
from src.web.extensions import db
from src.core.services.event_service import event_service
from flask import current_app
from minio.error import S3Error
import uuid
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB en bytes
MAX_IMAGES_PER_SITE = 10


class SiteImageService:
    """Casos de uso para imágenes de sitios históricos."""
    
    def __init__(self):
        self._minio_client = None
    
    @property
    def minio_client(self):
        """Obtiene el cliente de MinIO desde la aplicación Flask."""
        if self._minio_client is None:
            from flask import current_app
            self._minio_client = current_app.storage
        return self._minio_client
    
    def _get_bucket_name(self) -> str:
        """Obtiene el nombre del bucket desde la configuración."""
        from flask import current_app
        return current_app.config.get('MINIO_BUCKET', 'grupo06')
    
    def _ensure_bucket_exists(self):
        """Asegura que el bucket existe en MinIO."""
        bucket_name = self._get_bucket_name()
        try:
            if not self.minio_client.bucket_exists(bucket_name):
                self.minio_client.make_bucket(bucket_name)
        except S3Error as e:
            raise exc.DatabaseError(f"Error al verificar/crear bucket en MinIO: {e}")
    
    def _validate_file(self, file) -> tuple[bool, Optional[str]]:
        """
        Valida el archivo de imagen.
        
        Returns:
            tuple: (es_valido, mensaje_error)
        """
        if not file or not file.filename:
            return False, "No se proporcionó ningún archivo"
        
        # Validar extensión
        filename = file.filename.lower()
        extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
        if extension not in ALLOWED_EXTENSIONS:
            return False, f"Formato no permitido. Formatos permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
        
        # Validar tamaño
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Resetear posición
        
        if file_size > MAX_FILE_SIZE:
            return False, f"El archivo excede el tamaño máximo de {MAX_FILE_SIZE / (1024*1024)} MB"
        
        if file_size == 0:
            return False, "El archivo está vacío"
        
        return True, None
    
    def _generate_unique_filename(self, original_filename: str, site_id: int) -> str:
        """
        Genera un nombre único para el archivo para evitar colisiones.
        
        Args:
            original_filename: Nombre original del archivo
            site_id: ID del sitio histórico
            
        Returns:
            str: Nombre único del archivo
        """
        # Obtener extensión
        extension = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else 'jpg'
        
        # Generar nombre único: sitio_id_timestamp_uuid.ext
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        safe_name = secure_filename(original_filename.rsplit('.', 1)[0])[:20]  # Limitar longitud
        
        return f"site_{site_id}_{timestamp}_{unique_id}_{safe_name}.{extension}"
    
    def upload_image(self, site_id: int, file, titulo_alt: str, descripcion: Optional[str] = None, 
                    user_id: int = None) -> SiteImage:
        """
        Sube una imagen a MinIO y crea el registro en la base de datos.
        
        Args:
            site_id: ID del sitio histórico
            file: Archivo de imagen (Werkzeug FileStorage)
            titulo_alt: Título/alt text (obligatorio)
            descripcion: Descripción opcional
            user_id: ID del usuario que realiza la acción
            
        Returns:
            SiteImage: Imagen creada
            
        Raises:
            NotFoundError: Si el sitio no existe
            ValidationError: Si hay errores de validación
            DatabaseError: Si falla la operación
        """
        # Validar que el sitio existe
        site = HistoricSite.query.get(site_id)
        if not site or site.deleted:
            raise exc.NotFoundError(f"El sitio histórico con id {site_id} no fue encontrado.")
        
        # Validar límite de imágenes
        current_count = SiteImage.query.filter_by(id_site=site_id).count()
        if current_count >= MAX_IMAGES_PER_SITE:
            raise exc.ValidationError(f"Se ha alcanzado el límite máximo de {MAX_IMAGES_PER_SITE} imágenes por sitio.")
        
        # Validar campos obligatorios
        if not titulo_alt or not titulo_alt.strip():
            raise exc.ValidationError("El título/alt es obligatorio")
        
        if len(titulo_alt.strip()) > 255:
            raise exc.ValidationError("El título/alt no debe superar 255 caracteres")
        
        # Validar archivo
        is_valid, error_msg = self._validate_file(file)
        if not is_valid:
            raise exc.ValidationError(error_msg)
        
        try:
            # Asegurar que el bucket existe
            self._ensure_bucket_exists()
            
            # Generar nombre único
            unique_filename = self._generate_unique_filename(file.filename, site_id)
            bucket_name = self._get_bucket_name()
            
            # Subir archivo a MinIO
            # Leer el contenido del archivo en memoria
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # Volver al inicio
            
            file_data = file.read(file_size)
            file.seek(0)  # Resetear para posibles usos futuros
            
            extension = file.filename.rsplit('.', 1)[-1].lower()
            content_type_map = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'webp': 'image/webp'
            }
            content_type = content_type_map.get(extension, 'image/jpeg')
            
            # Crear un objeto BytesIO para MinIO
            from io import BytesIO
            file_stream = BytesIO(file_data)
            
            self.minio_client.put_object(
                bucket_name,
                unique_filename,
                file_stream,
                length=file_size,
                content_type=content_type
            )
            
            # Construir URL pública
            # La URL puede ser directa a MinIO o a través de un proxy/nginx
            # Por defecto, usamos la URL del servidor MinIO directamente
            minio_server = current_app.config.get('MINIO_SERVER', 'http://127.0.0.1:9000')
            # Remover protocolo si está presente para construir correctamente
            if minio_server.startswith('http://') or minio_server.startswith('https://'):
                url_publica = f"{minio_server}/{bucket_name}/{unique_filename}"
            else:
                # Si no tiene protocolo, asumir http
                url_publica = f"http://{minio_server}/{bucket_name}/{unique_filename}"
            
            # Obtener el siguiente orden
            max_orden = db.session.query(db.func.max(SiteImage.orden)).filter_by(id_site=site_id).scalar() or 0
            nuevo_orden = max_orden + 1
            
            # Crear registro en BD
            new_image = SiteImage(
                id_site=site_id,
                url_publica=url_publica,
                titulo_alt=titulo_alt.strip(),
                descripcion=descripcion.strip() if descripcion else None,
                orden=nuevo_orden,
                es_portada=False  # Por defecto no es portada
            )
            
            db.session.add(new_image)
            
            # Crear evento si se proporciona user_id
            if user_id:
                event_data = {
                    'id_site': site_id,
                    'id_user': user_id,
                    'type_Action': 'UPDATE'  # Cambio de imágenes es una actualización
                }
                event_service.create_event(event_data, commit=False)
            
            db.session.commit()
            return new_image
            
        except S3Error as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al subir imagen a MinIO: {e}")
        except Exception as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al crear imagen: {e}")
    
    def get_images_by_site(self, site_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todas las imágenes de un sitio ordenadas por orden.
        Genera URLs firmadas (presigned) para acceso público a las imágenes.
        
        Args:
            site_id: ID del sitio histórico
            
        Returns:
            List[Dict]: Lista de imágenes en formato dict con URLs firmadas
        """
        images = SiteImage.query.filter_by(id_site=site_id).order_by(SiteImage.orden.asc()).all()
        bucket_name = self._get_bucket_name()
        
        result = []
        for img in images:
            img_dict = img.to_dict()
            # Generar URL firmada (presigned) para acceso público
            try:
                # Extraer el nombre del archivo de la URL almacenada
                filename = img.url_publica.split('/')[-1]
                # Generar URL firmada válida por 7 días
                presigned_url = self.minio_client.presigned_get_object(
                    bucket_name,
                    filename,
                    expires=timedelta(days=7)
                )
                img_dict['url_publica'] = presigned_url
            except Exception as e:
                # Si falla la generación de URL firmada, usar la URL original
                current_app.logger.warning(f"Error al generar URL firmada para imagen {img.id}: {e}")
            
            result.append(img_dict)
        
        return result
    
    def get_cover_image(self, site_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene la imagen portada de un sitio con URL firmada.
        
        Args:
            site_id: ID del sitio histórico
            
        Returns:
            Optional[Dict]: Imagen portada con URL firmada o None
        """
        cover = SiteImage.query.filter_by(id_site=site_id, es_portada=True).first()
        if not cover:
            return None
        
        cover_dict = cover.to_dict()
        bucket_name = self._get_bucket_name()
        
        # Generar URL firmada (presigned) para acceso público
        try:
            # Extraer el nombre del archivo de la URL almacenada
            filename = cover.url_publica.split('/')[-1]
            # Generar URL firmada válida por 7 días
            presigned_url = self.minio_client.presigned_get_object(
                bucket_name,
                filename,
                expires=timedelta(days=7)
            )
            cover_dict['url_publica'] = presigned_url
        except Exception as e:
            # Si falla la generación de URL firmada, usar la URL original
            current_app.logger.warning(f"Error al generar URL firmada para imagen portada {cover.id}: {e}")
        
        return cover_dict
    
    def delete_image(self, image_id: int, user_id: int = None) -> bool:
        """
        Elimina una imagen (tanto de MinIO como de la BD).
        
        Args:
            image_id: ID de la imagen
            user_id: ID del usuario que realiza la acción
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            NotFoundError: Si la imagen no existe
            ValidationError: Si se intenta eliminar la portada
            DatabaseError: Si falla la operación
        """
        image = SiteImage.query.get(image_id)
        if not image:
            raise exc.NotFoundError(f"La imagen con id {image_id} no fue encontrada.")
        
        # Validar que no sea la portada
        if image.es_portada:
            raise exc.ValidationError("No se puede eliminar la imagen portada. Primero debe cambiar la portada a otra imagen.")
        
        site_id = image.id_site
        
        try:
            # Eliminar de MinIO
            bucket_name = self._get_bucket_name()
            # Extraer el nombre del archivo de la URL
            filename = image.url_publica.split('/')[-1]
            try:
                self.minio_client.remove_object(bucket_name, filename)
            except S3Error:
                # Si falla la eliminación en MinIO, continuar (puede que ya no exista)
                pass
            
            # Eliminar de BD
            db.session.delete(image)
            
            # Reordenar las imágenes restantes
            remaining_images = SiteImage.query.filter_by(id_site=site_id).order_by(SiteImage.orden.asc()).all()
            for idx, img in enumerate(remaining_images, start=1):
                img.orden = idx
            
            # Crear evento si se proporciona user_id
            if user_id:
                event_data = {
                    'id_site': site_id,
                    'id_user': user_id,
                    'type_Action': 'UPDATE'
                }
                event_service.create_event(event_data, commit=False)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al eliminar imagen: {e}")
    
    def set_cover_image(self, image_id: int, user_id: int = None) -> SiteImage:
        """
        Marca una imagen como portada (solo una por sitio).
        
        Args:
            image_id: ID de la imagen a marcar como portada
            user_id: ID del usuario que realiza la acción
            
        Returns:
            SiteImage: Imagen actualizada
            
        Raises:
            NotFoundError: Si la imagen no existe
            DatabaseError: Si falla la operación
        """
        image = SiteImage.query.get(image_id)
        if not image:
            raise exc.NotFoundError(f"La imagen con id {image_id} no fue encontrada.")
        
        site_id = image.id_site
        
        try:
            # Desmarcar todas las portadas del sitio
            SiteImage.query.filter_by(id_site=site_id, es_portada=True).update({'es_portada': False})
            
            # Marcar la nueva portada
            image.es_portada = True
            image.updated_at = datetime.utcnow()
            
            # Crear evento si se proporciona user_id
            if user_id:
                event_data = {
                    'id_site': site_id,
                    'id_user': user_id,
                    'type_Action': 'UPDATE'
                }
                event_service.create_event(event_data, commit=False)
            
            db.session.commit()
            return image
            
        except Exception as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al establecer imagen portada: {e}")
    
    def reorder_images(self, site_id: int, image_orders: List[Dict[str, int]], user_id: int = None) -> bool:
        """
        Reordena las imágenes de un sitio.
        
        Args:
            site_id: ID del sitio histórico
            image_orders: Lista de dicts con {'id': image_id, 'orden': nuevo_orden}
            user_id: ID del usuario que realiza la acción
            
        Returns:
            bool: True si se reordenó correctamente
            
        Raises:
            NotFoundError: Si el sitio no existe
            ValidationError: Si hay errores de validación
            DatabaseError: Si falla la operación
        """
        site = HistoricSite.query.get(site_id)
        if not site or site.deleted:
            raise exc.NotFoundError(f"El sitio histórico con id {site_id} no fue encontrado.")
        
        try:
            # Actualizar órdenes
            for order_data in image_orders:
                image_id = order_data.get('id')
                nuevo_orden = order_data.get('orden')
                
                if image_id and nuevo_orden is not None:
                    image = SiteImage.query.get(image_id)
                    if image and image.id_site == site_id:
                        image.orden = nuevo_orden
                        image.updated_at = datetime.utcnow()
            
            # Crear evento si se proporciona user_id
            if user_id:
                event_data = {
                    'id_site': site_id,
                    'id_user': user_id,
                    'type_Action': 'UPDATE'
                }
                event_service.create_event(event_data, commit=False)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al reordenar imágenes: {e}")
    
    def update_image_metadata(self, image_id: int, titulo_alt: Optional[str] = None, 
                              descripcion: Optional[str] = None, user_id: int = None) -> SiteImage:
        """
        Actualiza los metadatos de una imagen (título/alt y descripción).
        
        Args:
            image_id: ID de la imagen
            titulo_alt: Nuevo título/alt (opcional)
            descripcion: Nueva descripción (opcional)
            user_id: ID del usuario que realiza la acción
            
        Returns:
            SiteImage: Imagen actualizada
            
        Raises:
            NotFoundError: Si la imagen no existe
            ValidationError: Si hay errores de validación
            DatabaseError: Si falla la operación
        """
        image = SiteImage.query.get(image_id)
        if not image:
            raise exc.NotFoundError(f"La imagen con id {image_id} no fue encontrada.")
        
        try:
            if titulo_alt is not None:
                titulo_alt = titulo_alt.strip()
                if not titulo_alt:
                    raise exc.ValidationError("El título/alt no puede estar vacío")
                if len(titulo_alt) > 255:
                    raise exc.ValidationError("El título/alt no debe superar 255 caracteres")
                image.titulo_alt = titulo_alt
            
            if descripcion is not None:
                image.descripcion = descripcion.strip() if descripcion.strip() else None
            
            image.updated_at = datetime.utcnow()
            
            # Crear evento si se proporciona user_id
            if user_id:
                event_data = {
                    'id_site': image.id_site,
                    'id_user': user_id,
                    'type_Action': 'UPDATE'
                }
                event_service.create_event(event_data, commit=False)
            
            db.session.commit()
            return image
            
        except exc.ValidationError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al actualizar metadatos de imagen: {e}")


# Instancia del servicio
site_image_service = SiteImageService()

