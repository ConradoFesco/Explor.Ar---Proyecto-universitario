# services/tag_service.py

from src.web.models.tag import Tag
from ..extensions import db
from slugify import slugify
from sqlalchemy.exc import IntegrityError
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError

class TagService:
    def create_tag(self,data): 
        """Crea un nuevo tag."""
        name = data.get('name')
        if not name:
            raise ValidationError("El nombre del tag es requerido.")
        slug = slugify(name)
        existing_tag = Tag.query.filter_by(slug=slug).first()
        if existing_tag:
            raise ValidationError("El slug ya existe. El nombre del tag podría ser muy similar a uno ya existente.")
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
            # Regenerar el slug si el nombre ha cambiado
            new_slug = slugify(name)
            if Tag.query.filter_by(slug=new_slug).first():
                raise ValidationError("El nuevo nombre del tag genera un slug que ya existe.")
            tag.slug = new_slug
        try:
            db.session.commit()
            return tag.to_dict()
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al actualizar el tag: {str(e)}")

    def delete_tag(self, tag_id): 
        """Elimina lógicamente un tag por su ID."""
        tag = Tag.query.filter_by(id=tag_id, deleted=False).first()
        if not tag:
            raise NotFoundError("Tag no encontrado.")
        
        tag.deleted = True
        try:
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al eliminar el tag: {str(e)}")

tag_service = TagService()