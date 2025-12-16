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
        """
        Crea un tag nuevo o recupera uno eliminado (reactiva) si coincide el nombre.
        
        Args:
            data: Diccionario con los datos del tag (debe contener 'name')
            
        Returns:
            dict: Tag creado o reactivado como diccionario
            
        Raises:
            ValidationError: Si el nombre es inválido o ya existe
            DatabaseError: Si hay un error al persistir en la base de datos
        """
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
        """
        Lista todos los tags (opcionalmente incluye eliminados).
        
        Args:
            include_deleted: Si True, incluye tags eliminados lógicamente
            
        Returns:
            list[dict]: Lista de tags como diccionarios
        """
        query = Tag.query
        if not include_deleted:
            query = query.filter_by(deleted=False)
        tags = query.all()
        return [tag.to_dict() for tag in tags]

    def get_tag_by_id(self, tag_id):
        """
        Obtiene un tag por ID (no eliminado).
        
        Args:
            tag_id: ID del tag a obtener
            
        Returns:
            dict: Tag como diccionario
            
        Raises:
            NotFoundError: Si el tag no existe o está eliminado
        """
        tag = Tag.query.filter_by(id=tag_id, deleted=False).first()
        if not tag:
            raise NotFoundError("Tag no encontrado.")
        return tag.to_dict()

    def get_tag_by_slug(self, tag_slug):
        """
        Obtiene un tag por slug (no eliminado).
        
        Args:
            tag_slug: Slug del tag a obtener
            
        Returns:
            dict: Tag como diccionario
            
        Raises:
            NotFoundError: Si el tag no existe o está eliminado
        """
        tag = Tag.query.filter_by(slug=tag_slug, deleted=False).first()
        if not tag:
            raise NotFoundError("Tag no encontrado.")
        return tag.to_dict()

    def update_tag(self, tag_id, data):
        """
        Actualiza nombre/slug de un tag, validando unicidad.
        
        Args:
            tag_id: ID del tag a actualizar
            data: Diccionario con los datos a actualizar (puede contener 'name')
            
        Returns:
            dict: Tag actualizado como diccionario
            
        Raises:
            NotFoundError: Si el tag no existe o está eliminado
            ValidationError: Si el nuevo nombre es inválido o ya existe
            DatabaseError: Si hay un error al persistir en la base de datos
        """
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
        """
        Elimina lógicamente un tag si no está asociado a sitios.
        
        Args:
            tag_id: ID del tag a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            NotFoundError: Si el tag no existe o está eliminado
            ValidationError: Si el tag está asociado a sitios históricos
            DatabaseError: Si hay un error al persistir en la base de datos
        """
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
        """
        Obtiene tags asociados a un sitio histórico por su ID.
        
        Args:
            site_id: ID del sitio histórico
            
        Returns:
            list[dict]: Lista de tags asociados al sitio como diccionarios
            
        Raises:
            NotFoundError: Si el sitio histórico no existe
        """
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
        
        Args:
            page: Número de página (por defecto 1)
            per_page: Elementos por página (por defecto 25)
            search: Texto de búsqueda por prefijo del nombre (opcional)
            sort_by: Campo por el cual ordenar ('name' o 'created_at', por defecto 'name')
            sort_order: Dirección del orden ('asc' o 'desc', por defecto 'asc')
            include_deleted: Si True, incluye tags eliminados lógicamente
            
        Returns:
            dict: Diccionario con 'tags' (lista de tags) y 'pagination' (info de paginación)
            
        Raises:
            DatabaseError: Si hay un error al consultar la base de datos
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

    def tag_exists(self, tag_id: int) -> bool:
        """
        Verifica si existe un tag con el ID dado (no eliminado).
        
        Args:
            tag_id: ID del tag a verificar
            
        Returns:
            bool: True si existe, False en caso contrario
        """
        tag = Tag.query.filter_by(id=tag_id, deleted=False).first()
        return tag is not None

    def tag_name_exists(self, name: str, exclude_tag_id: int | None = None) -> bool:
        """
        Verifica si existe un tag con el nombre dado (no eliminado).
        
        Args:
            name: Nombre del tag a verificar
            exclude_tag_id: ID del tag a excluir de la búsqueda (útil para updates)
            
        Returns:
            bool: True si existe, False en caso contrario
        """
        query = Tag.query.filter_by(deleted=False, name=name)
        if exclude_tag_id is not None:
            query = query.filter(Tag.id != exclude_tag_id)
        tag = query.first()
        return tag is not None

    def tag_slug_exists(self, slug: str, exclude_tag_id: int | None = None) -> bool:
        """
        Verifica si existe un tag con el slug dado (no eliminado).
        
        Args:
            slug: Slug del tag a verificar
            exclude_tag_id: ID del tag a excluir de la búsqueda (útil para updates)
            
        Returns:
            bool: True si existe, False en caso contrario
        """
        query = Tag.query.filter_by(deleted=False, slug=slug)
        if exclude_tag_id is not None:
            query = query.filter(Tag.id != exclude_tag_id)
        tag = query.first()
        return tag is not None


tag_service = TagService()