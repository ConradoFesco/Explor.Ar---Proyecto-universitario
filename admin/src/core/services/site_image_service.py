from src.core.models.site_image import SiteImage
from src.core.models.historic_site import HistoricSite
from src.web import exceptions as exc
from src.web.extensions import db
from src.core.services.event_service import event_service
from flask import current_app
from minio.error import S3Error
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from io import BytesIO

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_IMAGES_PER_SITE = 10


class SiteImageService:
    def __init__(self):
        self._minio_client = None
    
    def _extract_object_path_from_url(self, url_publica: str, bucket_name: str) -> str:
        if not url_publica:
            raise ValueError("URL pública no puede estar vacía")
        
        url_str = url_publica.split('?')[0]
        bucket_pattern = f'/{bucket_name}/'
        
        if bucket_pattern in url_str:
            return url_str.split(bucket_pattern, 1)[1]
        
        url_parts = url_str.split('/')
        bucket_index = -1
        
        for i, part in enumerate(url_parts):
            if part == bucket_name:
                bucket_index = i
                break
        
        if bucket_index >= 0 and bucket_index < len(url_parts) - 1:
            return '/'.join(url_parts[bucket_index + 1:])
        elif bucket_index >= 0:
            return ''
        else:
            return url_parts[-1] if url_parts else ''
    
    @property
    def minio_client(self):
        if self._minio_client is None:
            if not hasattr(current_app, 'storage') or current_app.storage is None:
                raise exc.DatabaseError("MinIO no está configurado. Verifique las variables de entorno MINIO_SERVER, MINIO_ACCESS_KEY y MINIO_SECRET_KEY.")
            self._minio_client = current_app.storage
        return self._minio_client
    
    def _get_bucket_name(self) -> str:
        return current_app.config.get('MINIO_BUCKET', 'grupo06')
    
    def _ensure_bucket_exists(self):
        bucket_name = self._get_bucket_name()
        try:
            minio = self.minio_client
            if minio is None:
                raise exc.DatabaseError("MinIO client no está disponible")
            
            if not minio.bucket_exists(bucket_name):
                minio.make_bucket(bucket_name)
            
            try:
                import json
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                        }
                    ]
                }
                minio.set_bucket_policy(bucket_name, json.dumps(policy))
                current_app.logger.info(f"Bucket '{bucket_name}' configurado como público")
            except Exception as policy_error:
                current_app.logger.warning(f"No se pudo configurar el bucket como público: {policy_error}")
                
        except S3Error as e:
            raise exc.DatabaseError(f"Error al verificar/crear bucket '{bucket_name}' en MinIO: {e}")
        except Exception as e:
            raise exc.DatabaseError(f"Error inesperado al verificar bucket en MinIO: {e}")
    
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
        unique_number = int(datetime.now().timestamp() * 1000000) % 100000000
        filename = f"site_image_{unique_number}.{extension}"
        return filename
    
    def upload_image(self, site_id: int, file, titulo_alt: str, descripcion: Optional[str] = None, 
                    user_id: int = None) -> SiteImage:
        site = HistoricSite.query.get(site_id)
        if not site or site.deleted:
            raise exc.NotFoundError(f"El sitio histórico con id {site_id} no fue encontrado.")
        
        current_count = SiteImage.query.filter_by(id_site=site_id).count()
        if current_count >= MAX_IMAGES_PER_SITE:
            raise exc.ValidationError(f"Se ha alcanzado el límite máximo de {MAX_IMAGES_PER_SITE} imágenes por sitio.")
        
        if not titulo_alt:
            raise exc.ValidationError("El título/alt es obligatorio")
        
        titulo_alt = str(titulo_alt).strip()
        if not titulo_alt:
            raise exc.ValidationError("El título/alt es obligatorio")
        
        if len(titulo_alt) > 255:
            raise exc.ValidationError("El título/alt no debe superar 255 caracteres")
        
        is_valid, error_msg = self._validate_file(file)
        if not is_valid:
            raise exc.ValidationError(error_msg)
        
        try:
            self._ensure_bucket_exists()
            bucket_name = self._get_bucket_name()
            
            url_publica, _ = self._upload_file_to_minio(file, site_id, bucket_name)
            
            max_orden = db.session.query(db.func.max(SiteImage.orden)).filter_by(id_site=site_id).scalar() or 0
            nuevo_orden = max_orden + 1
            
            descripcion_final = None
            if descripcion:
                descripcion_final = str(descripcion).strip() or None
            
            new_image = SiteImage(
                id_site=site_id,
                url_publica=url_publica,
                titulo_alt=titulo_alt,
                descripcion=descripcion_final,
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
        if not url_publica:
            return ""
        
        # En producción, convertir HTTP a HTTPS si está configurado
        use_https = current_app.config.get('MINIO_USE_HTTPS', False)
        if use_https and url_publica.startswith('http://'):
            url_publica = url_publica.replace('http://', 'https://', 1)  # Solo reemplazar el primer http://
        
        # Corregir doble slash si existe (excepto después de http:// o https://)
        # Primero normalizar protocolo
        protocol = ''
        if url_publica.startswith('https://'):
            protocol = 'https://'
            url_publica = url_publica[8:]  # Quitar 'https://'
        elif url_publica.startswith('http://'):
            protocol = 'http://'
            url_publica = url_publica[7:]  # Quitar 'http://'
        
        # Eliminar dobles slashes en el path
        url_publica = url_publica.replace('//', '/')
        
        # Reconstruir la URL
        url_publica = f"{protocol}{url_publica}"
        
        return url_publica
    
    def get_images_by_site(self, site_id: int) -> List[Dict[str, Any]]:
        images = SiteImage.query.filter_by(id_site=site_id).order_by(SiteImage.orden.asc()).all()
        bucket_name = self._get_bucket_name()
        
        result = []
        for img in images:
            if not img.url_publica:
                current_app.logger.warning(f"Imagen {img.id} del sitio {site_id} no tiene URL pública")
                continue
            img_dict = img.to_dict()
            img_dict['url_publica'] = self._get_presigned_url(img.url_publica, bucket_name, img.id)
            result.append(img_dict)
        
        return result
    
    def get_cover_image(self, site_id: int) -> Optional[Dict[str, Any]]:
        cover = SiteImage.query.filter_by(id_site=site_id, es_portada=True).first()
        if not cover or not cover.url_publica:
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
        if not file or not hasattr(file, 'filename') or not file.filename:
            raise exc.ValidationError("El archivo no es válido o no tiene nombre")
        
        unique_filename = self._generate_unique_filename(file.filename, site_id)
        file.seek(0)
        file_data_bytes = file.read()
        
        if not file_data_bytes:
            raise exc.ValidationError("El archivo está vacío o no se pudo leer")
        
        file_size = len(file_data_bytes)
        file.seek(0)
        
        extension = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
        content_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'webp': 'image/webp'
        }
        content_type = content_type_map.get(extension, 'image/jpeg')
        file_stream = BytesIO(file_data_bytes)
        file_stream.seek(0)
        
        minio = self.minio_client
        if minio is None:
            raise exc.DatabaseError("MinIO client no está disponible. Verifique la configuración.")
        
        try:
            minio.put_object(
                bucket_name,
                unique_filename,
                file_stream,
                length=file_size,
                content_type=content_type
            )
        except S3Error as e:
            raise exc.DatabaseError(f"Error al subir archivo a MinIO: {e}")
        except AttributeError as e:
            raise exc.DatabaseError(f"Error de configuración de MinIO: {e}. Verifique que MinIO esté correctamente inicializado.")
        except Exception as e:
            raise exc.DatabaseError(f"Error inesperado al subir archivo: {e}")
        
        minio_server = current_app.config.get('MINIO_SERVER', 'http://127.0.0.1:9000')
        
        # Normalizar la URL del servidor MinIO
        if not minio_server.startswith('http://') and not minio_server.startswith('https://'):
            minio_server = f"http://{minio_server}"
        
        # En producción, forzar HTTPS si la URL es HTTP
        # Esto se puede controlar con una variable de entorno MINIO_USE_HTTPS
        use_https = current_app.config.get('MINIO_USE_HTTPS', False)
        if use_https and minio_server.startswith('http://'):
            minio_server = minio_server.replace('http://', 'https://')
        
        # Construir la URL pública, asegurándose de no tener doble slash
        minio_server = minio_server.rstrip('/')
        bucket_name = bucket_name.strip('/')  # Quitar barras al inicio y final
        unique_filename = unique_filename.lstrip('/')  # Quitar barra al inicio si existe
        url_publica = f"{minio_server}/{bucket_name}/{unique_filename}"
        # Normalizar cualquier doble slash que pueda quedar
        url_publica = url_publica.replace('//', '/').replace('http:/', 'http://').replace('https:/', 'https://')
        
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
                
                titulo_alt_raw = file_data.get('titulo_alt', '')
                titulo_alt = str(titulo_alt_raw).strip() if titulo_alt_raw is not None else ''
                
                descripcion_raw = file_data.get('descripcion', '')
                descripcion = str(descripcion_raw).strip() or None if descripcion_raw is not None else None
                
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
                titulo_alt_str = str(titulo_alt).strip() if titulo_alt else ''
                if not titulo_alt_str:
                    raise exc.ValidationError("El título/alt no puede estar vacío")
                if len(titulo_alt_str) > 255:
                    raise exc.ValidationError("El título/alt no debe superar 255 caracteres")
                image.titulo_alt = titulo_alt_str
            
            if descripcion is not None:
                if descripcion:
                    descripcion_str = str(descripcion).strip() or None
                else:
                    descripcion_str = None
                image.descripcion = descripcion_str
            
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

