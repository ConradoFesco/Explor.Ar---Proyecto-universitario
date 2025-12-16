"""
Validaciones de entrada para tags.
"""
from slugify import slugify

from src.web.exceptions import ValidationError, NotFoundError

from .utils import clean_string, ensure_max_length

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
    
    # Lazy import para evitar importación circular
    from src.core.services.tag_service import tag_service
    
    non_existent_tags = []
    for tag_id in tag_ids_list:
        if not tag_service.tag_exists(tag_id):
            non_existent_tags.append(tag_id)
    
    if non_existent_tags:
        raise ValidationError(f"Los siguientes tags no existen: {non_existent_tags}")


def validate_tag(name: str, tag_id: int | None = None) -> dict:
    """
    Valida nombre de tag y unicidad (para create/update).
    
    Args:
        name: Nombre del tag (input crudo)
        tag_id: ID del tag a excluir en la verificación de unicidad (solo update)
        
    Returns:
        dict: Diccionario con 'name' y 'slug' validados
        
    Raises:
        ValidationError: Si el nombre es inválido, muy largo o ya existe
    """
    name = clean_string(name)
    if not name:
        raise ValidationError('El nombre del tag es requerido.')
    if not ensure_max_length(name, MAX_TAG_NAME):
        raise ValidationError(f'El nombre del tag no debe superar {MAX_TAG_NAME} caracteres')

    slug = slugify(name)

    # Lazy import para evitar importación circular
    from src.core.services.tag_service import tag_service
    
    if tag_service.tag_name_exists(name, exclude_tag_id=tag_id):
        raise ValidationError('El nombre del tag ya existe.')
    if tag_service.tag_slug_exists(slug, exclude_tag_id=tag_id):
        raise ValidationError('El slug ya existe. El nombre podría ser muy similar a otro.')
    return {'name': name, 'slug': slug}
