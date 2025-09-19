# services/tag_service.py

from app.models.tag import Tag
from app.database import db
from slugify import slugify

def create_tag(data): //crear nuevo tag
    """Crea un nuevo tag."""
    name = data.get('name')
    
    if not name:
        return None, "El nombre del tag es requerido."

    slug = data.get('slug')
    existing_tag = Tag.query.filter_by(slug=slug).first()
    if existing_tag:
        return None, "El slug ya existe. El nombre del tag podría ser muy similar a uno ya existente."

    new_tag = Tag(name=name, slug=slug)
    try:
        db.session.add(new_tag)
        db.session.commit()
        return new_tag.to_dict(), None
    except Exception as e:
        db.session.rollback()
        return None, f"Error al crear el tag: {str(e)}"

def get_all_tags(): //obtener todos los tags
    """Obtiene todos los tags."""
    query = Tag.query
    if not include_deleted:
        query = query.filter_by(deleted=False)
    
    tags = query.all()
    return [tag.to_dict() for tag in tags]

def get_tag_by_id(tag_id): //obtener un tag por ID
    """Obtiene un tag por su ID."""
    tag = Tag.query.filter_by(id=tag_id, deleted=False).first()
    return tag.to_dict() if tag else None

def get_tag_by_slug(tag_slug):
    """Obtiene un tag por su slug."""
    tag = Tag.query.filter_by(slug=tag_slug, deleted=False).first()
    return tag.to_dict() if tag else None

def update_tag(tag_id, data): //actualizar un tag
    """Actualiza un tag existente."""
    tag = Tag.query.filter_by(id=tag_id, deleted=False).first()
    if not tag:
        return None, "Tag no encontrado."

    name = data.get('name')
    if name and name != tag.name:
        tag.name = name
        # Regenerar el slug si el nombre ha cambiado
        new_slug = slugify(name)
        if Tag.query.filter_by(slug=new_slug).first():
            return None, "El nuevo nombre del tag genera un slug que ya existe."
        tag.slug = new_slug
    
    try:
        db.session.commit()
        return tag.to_dict(), None
    except Exception as e:
        db.session.rollback()
        return None, f"Error al actualizar el tag: {str(e)}"

def delete_tag(tag_id): //eliminar un tag
    """Elimina lógicamente un tag por su ID."""
    tag = Tag.query.filter_by(id=tag_id, deleted=False).first()
    if not tag:
        return False, "Tag no encontrado."
    
    tag.deleted = True
    try:
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, f"Error al eliminar el tag: {str(e)}"