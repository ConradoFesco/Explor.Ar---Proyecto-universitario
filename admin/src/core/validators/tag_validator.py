"""
Validaciones de entrada para tags.
"""
from slugify import slugify
from src.web.exceptions import ValidationError, NotFoundError
from src.core.models.tag import Tag
from .utils import ensure_max_length

MAX_TAG_NAME = 50


def validate_create_tag(name: str) -> dict:
    name = (name or '').strip()
    if not name:
        raise ValidationError('El nombre del tag es requerido.')
    if not ensure_max_length(name, MAX_TAG_NAME):
        raise ValidationError(f'El nombre del tag no debe superar {MAX_TAG_NAME} caracteres')
    slug = slugify(name)
    # Unicidad nombre/slug activos
    if Tag.query.filter((Tag.name == name) & (Tag.deleted == False)).first():
        raise ValidationError('El nombre del tag ya existe.')
    if Tag.query.filter((Tag.slug == slug) & (Tag.deleted == False)).first():
        raise ValidationError('El slug ya existe. El nombre podría ser muy similar a otro.')
    return {'name': name, 'slug': slug}


def validate_update_tag(tag_id: int, name: str) -> dict:
    name = (name or '').strip()
    if not name:
        raise ValidationError('El nombre del tag es requerido.')
    if not ensure_max_length(name, MAX_TAG_NAME):
        raise ValidationError(f'El nombre del tag no debe superar {MAX_TAG_NAME} caracteres')
    slug = slugify(name)
    # Unicidad contra otros tags activos
    if Tag.query.filter(Tag.id != tag_id, Tag.deleted == False, Tag.name == name).first():
        raise ValidationError('El nombre del tag ya existe para otro tag.')
    if Tag.query.filter(Tag.id != tag_id, Tag.deleted == False, Tag.slug == slug).first():
        raise ValidationError('El slug generado ya existe para otro tag.')
    return {'name': name, 'slug': slug}


