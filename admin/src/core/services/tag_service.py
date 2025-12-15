"""
Servicios de dominio para Tags: CRUD, listados y utilidades.
"""

from src.core.models.tag import Tag
from src.core.models.tag_historic_site import TagHistoricSite
from src.web.extensions import db
from sqlalchemy.exc import IntegrityError
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError
from src.core.models.historic_site import HistoricSite
from src.core.validators.tag_validator import validate_tag
from src.core.validators.listing_validator import validate_tag_list_params


class TagService:
    """Operaciones sobre tags, con validaciones de unicidad y relaciones."""
    def create_tag(self, data):
        """Crea un tag nuevo o recupera uno eliminado (reactiva) si coincide el nombre."""
        name = data.get('name')
        validated = validate_tag(name)
        name = validated['name']
        slug = validated['slug']

        deleted_tag = Tag.query.filter_by(name=name, deleted=True).first()
        
        if deleted_tag:
            deleted_tag.deleted = False
            deleted_tag.slug = slug
            
            try:
                db.session.commit()
                return deleted_tag.to_dict()
            except IntegrityError as e:
                db.session.rollback()
                raise DatabaseError(f"Error al recuperar el tag: {str(e)}")
        else:
            new_tag = Tag(name=name, slug=slug)
            try:
                db.session.add(new_tag)
                db.session.commit()
                return new_tag.to_dict()
            except IntegrityError as e:
                db.session.rollback()
                raise DatabaseError(f"Error al crear el tag: {str(e)}")

    def get_all_tags(self, include_deleted=False):
        """Lista todos los tags (opcionalmente incluye eliminados)."""
        query = Tag.query
        if not include_deleted:
            query = query.filter_by(deleted=False)
        tags = query.all()
        return [tag.to_dict() for tag in tags]

    def get_tag_by_id(self, tag_id):
        """Obtiene un tag por ID (no eliminado)."""
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
        """Actualiza nombre/slug de un tag, validando unicidad."""
        tag = Tag.query.filter_by(id=tag_id, deleted=False).first()
        if not tag:
            raise NotFoundError("Tag no encontrado.")
        
        name = data.get('name')
        
        if name and name != tag.name:
            validated = validate_tag(name, tag_id=tag_id)
            tag.name = validated['name']
            tag.slug = validated['slug']
        
        try:
            db.session.commit()
            return tag.to_dict()
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al actualizar el tag: {str(e)}")

    def delete_tag(self, tag_id):
        """Elimina lógicamente un tag si no está asociado a sitios."""
        tag = Tag.query.filter_by(id=tag_id, deleted=False).first()
        if not tag:
            raise NotFoundError("Tag no encontrado.")
        
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
        v = validate_tag_list_params(page=page, per_page=per_page, search=search, sort_by=sort_by, sort_order=sort_order)
        page = v['page']
        per_page = v['per_page']
        search = v['search']
        sort_by = v['sort_by']
        sort_order = v['sort_order']

        query = Tag.query

        if not include_deleted:
            query = query.filter_by(deleted=False)

        if search:
            query = query.filter(Tag.name.ilike(f'{search}%'))

        if sort_by == 'name':
            order_column = Tag.name.asc() if sort_order == 'asc' else Tag.name.desc()
        elif sort_by == 'created_at':
            order_column = Tag.created_at.asc() if sort_order == 'asc' else Tag.created_at.desc()
        else:
            order_column = Tag.name.asc()

        query = query.order_by(order_column)

        try:
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        except Exception as e:
            raise DatabaseError(f"Error al listar tags paginados: {e}")

        items = pagination.items

        tags_data = []
        for tag in items:
            tag_dict = tag.to_dict()
            sites_count = TagHistoricSite.query.filter_by(Tag_id=tag.id).count()
            tag_dict['sites_count'] = sites_count
            tags_data.append(tag_dict)

        return {
            'tags': tags_data,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next,
                'prev_num': pagination.prev_num,
                'next_num': pagination.next_num,
            },
        }


tag_service = TagService()