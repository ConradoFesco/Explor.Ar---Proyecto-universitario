"""
Validaciones de entrada para tags.
"""
from slugify import slugify
from src.web.exceptions import ValidationError, NotFoundError
from src.core.models.tag import Tag
from .utils import ensure_max_length, clean_string

MAX_TAG_NAME = 50

def validate_tag_ids_exist(tag_ids_list: list[int]) -> None:
    """
    Valida que todos los tags en la lista existan y no estén eliminados.
    
    Args:
        tag_ids_list: Lista de IDs de tags a validar
    
    Raises:
        ValidationError: Si algún tag no existe o está eliminado
    """
    if not tag_ids_list:
        return
    
    non_existent_tags = []
    for tag_id in tag_ids_list:
        tag = Tag.query.filter_by(id=tag_id, deleted=False).first()
        if not tag:
            non_existent_tags.append(tag_id)
    
    if non_existent_tags:
        raise ValidationError(f"Los siguientes tags no existen: {non_existent_tags}")

def validate_tag(name: str, tag_id: int | None = None) -> dict:
    """
    Valida nombre de tag y unicidad (para create/update).
    Args:
        name: Nombre del tag (input crudo).
        tag_id: ID del tag a excluir en la verificación de unicidad (solo update).
    """
    name = clean_string(name)
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
