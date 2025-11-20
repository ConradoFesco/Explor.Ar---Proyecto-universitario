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
from io import BytesIO

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_IMAGES_PER_SITE = 10


class SiteImageService:
    def __init__(self):
        self._minio_client = None
    
    def _extract_object_path_from_url(self, url_publica: str, bucket_name: str) -> str:
        url_str = url_publica.split('?')[0]
        url_parts = url_str.split('/')
        
        bucket_index = -1
        for i, part in enumerate(url_parts):
            if part == bucket_name:
                bucket_index = i
                break
        
        if bucket_index >= 0 and bucket_index < len(url_parts) - 1:
            return '/'.join(url_parts[bucket_index + 1:])
        elif f'/{bucket_name}/' in url_str:
            return url_str.split(f'/{bucket_name}/', 1)[1]
        else:
            return url_parts[-1]
    
    @property
    def minio_client(self):
        if self._minio_client is None:
            self._minio_client = current_app.storage
        return self._minio_client
    
    def _get_bucket_name(self) -> str:
        return current_app.config.get('MINIO_BUCKET', 'grupo06')
    
    def _ensure_bucket_exists(self):
        bucket_name = self._get_bucket_name()
        try:
            if not self.minio_client.bucket_exists(bucket_name):
                self.minio_client.make_bucket(bucket_name)
        except S3Error as e:
            raise exc.DatabaseError(f"Error al verificar/crear bucket en MinIO: {e}")
    
    def _validate_file(self, file) -> tuple[bool, Optional[str]]:
        if not file or not file.filename:
            return False, "No se proporcionó ningún archivo"
        
        filename = file.filename.lower()
        extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
        if extension not in ALLOWED_EXTENSIONS:
            return False, f"Formato no permitido. Formatos permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
        
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return False, f"El archivo excede el tamaño máximo de {MAX_FILE_SIZE / (1024*1024)} MB"
        
        if file_size == 0:
            return False, "El archivo está vacío"
        
        return True, None
    
    def _generate_unique_filename(self, original_filename: str, site_id: int) -> str:
        extension = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else 'jpg'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        safe_name = secure_filename(original_filename.rsplit('.', 1)[0])[:20]
        filename = f"{timestamp}_{unique_id}_{safe_name}.{extension}"
        return f"Sites/{site_id}/{filename}"
    
    def upload_image(self, site_id: int, file, titulo_alt: str, descripcion: Optional[str] = None, 
                    user_id: int = None) -> SiteImage:
        site = HistoricSite.query.get(site_id)
        if not site or site.deleted:
            raise exc.NotFoundError(f"El sitio histórico con id {site_id} no fue encontrado.")
        
        current_count = SiteImage.query.filter_by(id_site=site_id).count()
        if current_count >= MAX_IMAGES_PER_SITE:
            raise exc.ValidationError(f"Se ha alcanzado el límite máximo de {MAX_IMAGES_PER_SITE} imágenes por sitio.")
        
        if not titulo_alt or not titulo_alt.strip():
            raise exc.ValidationError("El título/alt es obligatorio")
        
        if len(titulo_alt.strip()) > 255:
            raise exc.ValidationError("El título/alt no debe superar 255 caracteres")
        
        is_valid, error_msg = self._validate_file(file)
        if not is_valid:
            raise exc.ValidationError(error_msg)
        
        try:
            self._ensure_bucket_exists()
            
            unique_filename = self._generate_unique_filename(file.filename, site_id)
            bucket_name = self._get_bucket_name()
            
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            file_data = file.read(file_size)
            file.seek(0)
            
            extension = file.filename.rsplit('.', 1)[-1].lower()
            content_type_map = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'webp': 'image/webp'
            }
            content_type = content_type_map.get(extension, 'image/jpeg')
            
            file_stream = BytesIO(file_data)
            
            self.minio_client.put_object(
                bucket_name,
                unique_filename,
                file_stream,
                length=file_size,
                content_type=content_type
            )
            
            minio_server = current_app.config.get('MINIO_SERVER', 'http://127.0.0.1:9000')
            if minio_server.startswith('http://') or minio_server.startswith('https://'):
                url_publica = f"{minio_server}/{bucket_name}/{unique_filename}"
            else:
                url_publica = f"http://{minio_server}/{bucket_name}/{unique_filename}"
            
            max_orden = db.session.query(db.func.max(SiteImage.orden)).filter_by(id_site=site_id).scalar() or 0
            nuevo_orden = max_orden + 1
            
            new_image = SiteImage(
                id_site=site_id,
                url_publica=url_publica,
                titulo_alt=titulo_alt.strip(),
                descripcion=descripcion.strip() if descripcion else None,
                orden=nuevo_orden,
                es_portada=False
            )
            
            db.session.add(new_image)
            
            if user_id:
                event_data = {
                    'id_site': site_id,
                    'id_user': user_id,
                    'type_Action': 'UPDATE'
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
    
    def _get_presigned_url(self, url_publica: str, bucket_name: str, image_id: int) -> str:
        use_presigned = current_app.config.get('MINIO_USE_PRESIGNED_URLS', False)
        
        if not use_presigned:
            return url_publica
        
        try:
            object_path = self._extract_object_path_from_url(url_publica, bucket_name)
            expires_days = current_app.config.get('MINIO_PRESIGNED_EXPIRY_DAYS', 365)
            return self.minio_client.presigned_get_object(
                bucket_name,
                object_path,
                expires=timedelta(days=expires_days)
            )
        except Exception as e:
            error_msg = str(e)
            if '10061' in error_msg or 'Connection refused' in error_msg or 'denegó expresamente' in error_msg:
                current_app.logger.warning(
                    f"MinIO no está disponible. Usando URL original para imagen {image_id}. "
                    f"Para generar URLs presignadas, asegúrate de que MinIO esté corriendo en {current_app.config.get('MINIO_SERVER', '127.0.0.1:9000')}"
                )
            else:
                current_app.logger.warning(f"Error al generar URL firmada para imagen {image_id}: {e}")
            return url_publica
    
    def get_images_by_site(self, site_id: int) -> List[Dict[str, Any]]:
        images = SiteImage.query.filter_by(id_site=site_id).order_by(SiteImage.orden.asc()).all()
        bucket_name = self._get_bucket_name()
        
        result = []
        for img in images:
            img_dict = img.to_dict()
            img_dict['url_publica'] = self._get_presigned_url(img.url_publica, bucket_name, img.id)
            result.append(img_dict)
        
        return result
    
    def get_cover_image(self, site_id: int) -> Optional[Dict[str, Any]]:
        cover = SiteImage.query.filter_by(id_site=site_id, es_portada=True).first()
        if not cover:
            return None
        
        cover_dict = cover.to_dict()
        bucket_name = self._get_bucket_name()
        cover_dict['url_publica'] = self._get_presigned_url(cover.url_publica, bucket_name, cover.id)
        return cover_dict
    
    def delete_image(self, image_id: int, user_id: int = None) -> bool:
        image = SiteImage.query.get(image_id)
        if not image:
            raise exc.NotFoundError(f"La imagen con id {image_id} no fue encontrada.")
        
        if image.es_portada:
            raise exc.ValidationError("No se puede eliminar la imagen portada. Primero debe cambiar la portada a otra imagen.")
        
        site_id = image.id_site
        
        try:
            bucket_name = self._get_bucket_name()
            object_path = self._extract_object_path_from_url(image.url_publica, bucket_name)
            try:
                self.minio_client.remove_object(bucket_name, object_path)
            except S3Error:
                pass
            
            db.session.delete(image)
            
            remaining_images = SiteImage.query.filter_by(id_site=site_id).order_by(SiteImage.orden.asc()).all()
            for idx, img in enumerate(remaining_images, start=1):
                img.orden = idx
            
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
        image = SiteImage.query.get(image_id)
        if not image:
            raise exc.NotFoundError(f"La imagen con id {image_id} no fue encontrada.")
        
        site_id = image.id_site
        
        try:
            SiteImage.query.filter_by(id_site=site_id, es_portada=True).update({'es_portada': False})
            image.es_portada = True
            image.updated_at = datetime.utcnow()
            
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
        site = HistoricSite.query.get(site_id)
        if not site or site.deleted:
            raise exc.NotFoundError(f"El sitio histórico con id {site_id} no fue encontrado.")
        
        try:
            for order_data in image_orders:
                image_id = order_data.get('id')
                nuevo_orden = order_data.get('orden')
                
                if image_id and nuevo_orden is not None:
                    image = SiteImage.query.get(image_id)
                    if image and image.id_site == site_id:
                        image.orden = nuevo_orden
                        image.updated_at = datetime.utcnow()
            
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
    
    def _upload_file_to_minio(self, file, site_id: int, bucket_name: str) -> tuple[str, str]:
        unique_filename = self._generate_unique_filename(file.filename, site_id)
        
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        file_data_bytes = file.read(file_size)
        file.seek(0)
        
        extension = file.filename.rsplit('.', 1)[-1].lower()
        content_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'webp': 'image/webp'
        }
        content_type = content_type_map.get(extension, 'image/jpeg')
        
        file_stream = BytesIO(file_data_bytes)
        
        self.minio_client.put_object(
            bucket_name,
            unique_filename,
            file_stream,
            length=file_size,
            content_type=content_type
        )
        
        minio_server = current_app.config.get('MINIO_SERVER', 'http://127.0.0.1:9000')
        if minio_server.startswith('http://') or minio_server.startswith('https://'):
            url_publica = f"{minio_server}/{bucket_name}/{unique_filename}"
        else:
            url_publica = f"http://{minio_server}/{bucket_name}/{unique_filename}"
        
        return url_publica, unique_filename
    
    def upload_multiple_images(self, site_id: int, files_data: List[Dict[str, Any]], 
                              user_id: int = None) -> List[SiteImage]:
        site = HistoricSite.query.get(site_id)
        if not site or site.deleted:
            raise exc.NotFoundError(f"El sitio histórico con id {site_id} no fue encontrado.")
        
        current_count = SiteImage.query.filter_by(id_site=site_id).count()
        if current_count + len(files_data) > MAX_IMAGES_PER_SITE:
            raise exc.ValidationError(f"Se alcanzaría el límite máximo de {MAX_IMAGES_PER_SITE} imágenes por sitio.")
        
        uploaded_images = []
        
        try:
            self._ensure_bucket_exists()
            bucket_name = self._get_bucket_name()
            max_orden = db.session.query(db.func.max(SiteImage.orden)).filter_by(id_site=site_id).scalar() or 0
            
            for idx, file_data in enumerate(files_data):
                file = file_data.get('file')
                titulo_alt = file_data.get('titulo_alt', '').strip()
                descripcion = file_data.get('descripcion', '').strip() or None
                
                if not titulo_alt:
                    raise exc.ValidationError("El título/alt es obligatorio para todas las imágenes")
                
                if len(titulo_alt) > 255:
                    raise exc.ValidationError(f"El título/alt '{titulo_alt}' excede 255 caracteres")
                
                is_valid, error_msg = self._validate_file(file)
                if not is_valid:
                    raise exc.ValidationError(f"Error en archivo '{file.filename}': {error_msg}")
                
                url_publica, _ = self._upload_file_to_minio(file, site_id, bucket_name)
                
                orden_from_data = file_data.get('order')
                if orden_from_data is not None:
                    nuevo_orden = max_orden + orden_from_data + 1
                else:
                    nuevo_orden = max_orden + idx + 1
                
                is_cover = file_data.get('is_cover', False)
                
                if is_cover and current_count > 0:
                    SiteImage.query.filter_by(id_site=site_id, es_portada=True).update({'es_portada': False})
                
                new_image = SiteImage(
                    id_site=site_id,
                    url_publica=url_publica,
                    titulo_alt=titulo_alt,
                    descripcion=descripcion,
                    orden=nuevo_orden,
                    es_portada=is_cover
                )
                
                db.session.add(new_image)
                uploaded_images.append(new_image)
            
            cover_images = [img for img in uploaded_images if img.es_portada]
            if len(cover_images) > 1:
                for img in cover_images[1:]:
                    img.es_portada = False
            
            if current_count == 0 and len(cover_images) == 0 and uploaded_images:
                uploaded_images[0].es_portada = True
            
            if user_id and uploaded_images:
                event_data = {
                    'id_site': site_id,
                    'id_user': user_id,
                    'type_Action': 'UPDATE'
                }
                event_service.create_event(event_data, commit=False)
            
            db.session.commit()
            return uploaded_images
            
        except S3Error as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al subir imágenes a MinIO: {e}")
        except Exception as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al crear imágenes: {e}")
    
    def update_image_metadata(self, image_id: int, titulo_alt: Optional[str] = None, 
                              descripcion: Optional[str] = None, user_id: int = None) -> SiteImage:
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


site_image_service = SiteImageService()

