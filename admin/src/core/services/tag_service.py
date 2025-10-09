# services/tag_service.py

from src.core.models.tag import Tag
from src.core.models.tag_historic_site import TagHistoricSite
from src.web.extensions import db
from slugify import slugify
from sqlalchemy.exc import IntegrityError
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError
from src.core.models.historic_site import HistoricSite

class TagService:
    def create_tag(self, data): 
        """Crea un nuevo tag o recupera uno eliminado si existe."""
        name = data.get('name')
        if not name:
            raise ValidationError("El nombre del tag es requerido.")
        
        # Siempre generar el slug automáticamente desde el nombre
        slug = slugify(name)
        
        # Primero verificar si existe un tag activo con el mismo nombre o slug
        existing_active_tag = Tag.query.filter(
            ((Tag.name == name) | (Tag.slug == slug)) & (Tag.deleted == False)
        ).first()
        
        if existing_active_tag:
            raise ValidationError("El slug ya existe. El nombre del tag podría ser muy similar a uno ya existente.")
        
        # Buscar si existe un tag eliminado con el mismo nombre
        deleted_tag = Tag.query.filter_by(name=name, deleted=True).first()
        
        if deleted_tag:
            # Recuperar el tag eliminado
            deleted_tag.deleted = False
            deleted_tag.slug = slug  # Actualizar el slug por si cambió
            
            try:
                db.session.commit()
                return deleted_tag.to_dict()
            except IntegrityError as e:
                db.session.rollback()
                raise DatabaseError(f"Error al recuperar el tag: {str(e)}")
        else:
            # Crear un nuevo tag
            new_tag = Tag(
                name=name, 
                slug=slug)
            try:
                db.session.add(new_tag)
                db.session.commit()
                return new_tag.to_dict()
            except IntegrityError as e:
                db.session.rollback()
                raise DatabaseError(f"Error al crear el tag: {str(e)}")

    def get_all_tags(self, include_deleted=False): 
        """Obtiene todos los tags."""
        query = Tag.query
        if not include_deleted:
            query = query.filter_by(deleted=False)
        tags = query.all()
        return [tag.to_dict() for tag in tags]

    def get_tag_by_id(self, tag_id): 
        """Obtiene un tag por su ID."""
        tag = Tag.query.filter_by(id=tag_id, deleted=False).first()
        if not tag:
            raise NotFoundError("Tag no encontrado.")
        return tag.to_dict()

    def get_tag_by_slug(self, tag_slug):
        """Obtiene un tag por su slug."""
        tag = Tag.query.filter_by(slug=tag_slug, deleted=False).first()
        if not tag:
            raise NotFoundError("Tag no encontrado.")
        return tag.to_dict()

    def update_tag(self, tag_id, data): 
        """Actualiza un tag existente."""
        tag = Tag.query.filter_by(id=tag_id, deleted=False).first()
        if not tag:
            raise NotFoundError("Tag no encontrado.")
        
        name = data.get('name')
        
        if name and name != tag.name:
            # Verificar que el nombre no exista en otros tags
            existing_tag = Tag.query.filter(Tag.name == name, Tag.id != tag_id, Tag.deleted == False).first()
            if existing_tag:
                raise ValidationError("El nombre del tag ya existe para otro tag.")
            tag.name = name
            
            # Siempre regenerar el slug automáticamente desde el nombre
            new_slug = slugify(name)
            
            # Verificar que el nuevo slug no exista en otros tags
            existing_slug = Tag.query.filter(Tag.slug == new_slug, Tag.id != tag_id, Tag.deleted == False).first()
            if existing_slug:
                raise ValidationError("El slug generado ya existe para otro tag.")
            tag.slug = new_slug
        
        try:
            db.session.commit()
            return tag.to_dict()
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al actualizar el tag: {str(e)}")

    def delete_tag(self, tag_id): 
        """Elimina un tag por su ID (solo si no está asociado a sitios históricos)."""
        tag = Tag.query.filter_by(id=tag_id, deleted=False).first()
        if not tag:
            raise NotFoundError("Tag no encontrado.")
        
        # Verificar si el tag está asociado a sitios históricos
        sites_count = TagHistoricSite.query.filter_by(Tag_id=tag_id).count()
        if sites_count > 0:
            raise ValidationError(f"No se puede eliminar el tag porque está asociado a {sites_count} sitio(s) histórico(s).")
        
        tag.deleted = True
        try:
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al eliminar el tag: {str(e)}")

    def get_tags_by_site_id(self, site_id):
        """Obtiene los tags de un sitio histórico por su ID."""
        site = HistoricSite.query.get(site_id)
        if not site:
            raise NotFoundError("Sitio histórico no encontrado.")
        
        # Obtener tags a través de la relación many-to-many
        tags = Tag.query.join(TagHistoricSite).filter(
            TagHistoricSite.Historic_Site_id == site_id,
            Tag.deleted == False
        ).all()
        
        return [tag.to_dict() for tag in tags]

    def get_all_tags_paginated(self, page=1, per_page=25, search='', sort_by='name', sort_order='asc', include_deleted=False):
        """Obtiene tags con paginación, búsqueda y ordenamiento."""
        try:
            # Construir query base
            query = Tag.query
            
            if not include_deleted:
                query = query.filter_by(deleted=False)
            
            # Aplicar búsqueda (desde el inicio del nombre)
            if search:
                query = query.filter(Tag.name.ilike(f'{search}%'))
            
            # Aplicar ordenamiento
            if sort_by == 'name':
                order_column = Tag.name.asc() if sort_order == 'asc' else Tag.name.desc()
            elif sort_by == 'created_at':
                order_column = Tag.created_at.asc() if sort_order == 'asc' else Tag.created_at.desc()
            else:
                order_column = Tag.name.asc()
            
            query = query.order_by(order_column)
            
            # Obtener total de registros
            total = query.count()
            
            # Aplicar paginación
            tags = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # Convertir a diccionarios y agregar conteo de sitios
            tags_data = []
            for tag in tags:
                tag_dict = tag.to_dict()
                # Obtener conteo de sitios asociados
                sites_count = TagHistoricSite.query.filter_by(Tag_id=tag.id).count()
                tag_dict['sites_count'] = sites_count
                tags_data.append(tag_dict)
            
            # Calcular información de paginación
            total_pages = (total + per_page - 1) // per_page
            has_prev = page > 1
            has_next = page < total_pages
            start = (page - 1) * per_page + 1 if total > 0 else 0
            end = min(page * per_page, total)
            
            return {
                'tags': tags_data,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total': total,
                    'per_page': per_page,
                    'has_prev': has_prev,
                    'has_next': has_next,
                    'prev_page': page - 1 if has_prev else None,
                    'next_page': page + 1 if has_next else None,
                    'start': start,
                    'end': end
                }
            }
        except Exception as e:
            # Si hay algún error en la consulta, devolver una respuesta vacía
            return {
                'tags': [],
                'pagination': {
                    'current_page': page,
                    'total_pages': 0,
                    'total': 0,
                    'per_page': per_page,
                    'has_prev': False,
                    'has_next': False,
                    'prev_page': None,
                    'next_page': None,
                    'start': 0,
                    'end': 0
                }
            }


tag_service = TagService()