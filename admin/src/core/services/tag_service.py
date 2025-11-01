"""
Servicios de dominio para Tags: CRUD, listados y utilidades.
"""

from src.core.models.tag import Tag
from src.core.models.tag_historic_site import TagHistoricSite
from src.web.extensions import db
from sqlalchemy.exc import IntegrityError
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError
from src.core.models.historic_site import HistoricSite
from src.core.validators.tag_validator import validate_create_tag, validate_update_tag

class TagService:
    """Operaciones sobre tags, con validaciones de unicidad y relaciones."""
    def create_tag(self, data): 
        """Crea un tag nuevo o recupera uno eliminado (reactiva) si coincide el nombre."""
        name = data.get('name')
        validated = validate_create_tag(name)
        name = validated['name']
        slug = validated['slug']

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
            new_tag = Tag(name=name, slug=slug)
            try:
                db.session.add(new_tag)
                db.session.commit()
                return new_tag.to_dict()
            except IntegrityError as e:
                db.session.rollback()
                raise DatabaseError(f"Error al crear el tag: {str(e)}")

    def get_all_tags(self, include_deleted=False): 
        """
        Lista todos los tags (opcionalmente incluye eliminados).
        """
        query = Tag.query
        if not include_deleted:
            query = query.filter_by(deleted=False)
        tags = query.all()
        return [tag.to_dict() for tag in tags]

    def get_tag_by_id(self, tag_id): 
        """
        Obtiene un tag por ID (no eliminado).
        """
        tag = Tag.query.filter_by(id=tag_id, deleted=False).first()
        if not tag:
            raise NotFoundError("Tag no encontrado.")
        return tag.to_dict()

    def get_tag_by_slug(self, tag_slug):
        """Obtiene un tag por slug (no eliminado)."""
        tag = Tag.query.filter_by(slug=tag_slug, deleted=False).first()
        if not tag:
            raise NotFoundError("Tag no encontrado.")
        return tag.to_dict()

    def update_tag(self, tag_id, data): 
        """
        Actualiza nombre/slug de un tag, validando unicidad.
        """
        tag = Tag.query.filter_by(id=tag_id, deleted=False).first()
        if not tag:
            raise NotFoundError("Tag no encontrado.")
        
        name = data.get('name')
        
        if name and name != tag.name:
            validated = validate_update_tag(tag_id, name)
            tag.name = validated['name']
            tag.slug = validated['slug']
        
        try:
            db.session.commit()
            return tag.to_dict()
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al actualizar el tag: {str(e)}")

    def delete_tag(self, tag_id): 
        """
        Elimina lógicamente un tag si no está asociado a sitios.
        """
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
        """Obtiene tags asociados a un sitio histórico por su ID."""
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
        """
        Lista tags con paginación, búsqueda por prefijo y ordenamiento.

        Returns:
            dict: {'tags': [...], 'pagination': {...}}
        """
        try:
            # Validaciones de entrada
            from src.core.validators.listing_validator import validate_tag_list_params
            v = validate_tag_list_params(page=int(page), per_page=int(per_page), search=search, sort_by=sort_by, sort_order=sort_order)
            page = v['page']; per_page = v['per_page']; search = v['search']; sort_by = v['sort_by']; sort_order = v['sort_order']

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