"""
Validaciones de entrada para tags.
"""
from slugify import slugify
from src.web.exceptions import ValidationError
from src.core.models.tag import Tag
from .utils import ensure_max_length

MAX_TAG_NAME = 50

def validate_tag(name: str, tag_id: int | None = None) -> dict:
    """
    Valida nombre de tag y unicidad (para create/update).
    Args:
        name: Nombre del tag (input crudo).
        tag_id: ID del tag a excluir en la verificación de unicidad (solo update).
    """
    name = (name or '').strip()
    if not name:
        raise ValidationError('El nombre del tag es requerido.')
    if not ensure_max_length(name, MAX_TAG_NAME):
        raise ValidationError(f'El nombre del tag no debe superar {MAX_TAG_NAME} caracteres')

    slug = slugify(name)

    base_filter = (Tag.deleted == False)
    if tag_id is not None:
        base_filter = base_filter & (Tag.id != tag_id)
    if Tag.query.filter(base_filter & (Tag.name == name)).first():
        raise ValidationError('El nombre del tag ya existe.')
    if Tag.query.filter(base_filter & (Tag.slug == slug)).first():
        raise ValidationError('El slug ya existe. El nombre podría ser muy similar a otro.')
    return {'name': name, 'slug': slug}
