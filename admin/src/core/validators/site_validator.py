"""
Validaciones de entrada para Sitios Históricos.
"""
from src.core.models.historic_site import HistoricSite
from src.core.services.category_service import category_service
from src.core.services.historic_site_service import historic_site_service
from src.core.services.state_service import state_service
from src.core.validators.api_validator import validate_positive_int
from src.web.exceptions import ValidationError, NotFoundError

from .listing_validator import _validate_optional_int
from .utils import clean_string, ensure_max_length, is_float_like, require_fields

MAX_NAME = 255
MAX_BRIEF = 2000


def validate_create_site(data: dict) -> dict:
    """
    Valida y limpia los datos para crear un sitio histórico.
    
    Args:
        data: Diccionario con los datos del sitio histórico
        
    Returns:
        dict: Diccionario con los datos validados y limpiados
        
    Raises:
        ValidationError: Si faltan campos obligatorios o los datos son inválidos
        NotFoundError: Si el estado de conservación o categoría no existen
    """
    required = [
        'name', 'brief_description', 'name_city', 'name_province',
        'latitude', 'longitude', 'id_category', 'visible'
    ]
    missing = require_fields(data, required)
    if missing:
        raise ValidationError(f"Faltan campos obligatorios del sitio histórico: {', '.join(missing)}")

    name = clean_string(data.get('name'))
    brief = clean_string(data.get('brief_description'))
    complete = data.get('complete_description') or None
    name_city = clean_string(data.get('name_city'))
    name_province = clean_string(data.get('name_province'))
    lat = data.get('latitude')
    lng = data.get('longitude')
    id_estado = data.get('id_estado')
    year_inauguration = data.get('year_inauguration')
    id_category = data.get('id_category')
    visible = bool(data.get('visible'))

    if not ensure_max_length(name, MAX_NAME):
        raise ValidationError('El nombre no debe superar 255 caracteres')
    if not ensure_max_length(brief, MAX_BRIEF):
        raise ValidationError('La descripción breve es demasiado larga')
    if not is_float_like(lat) or not is_float_like(lng):
        raise ValidationError('Latitud/Longitud inválidas')

    if historic_site_service.site_name_exists(name):
        raise ValidationError('Ya existe un sitio histórico con este nombre')

    if id_estado is not None:
        id_estado = _validate_optional_int(id_estado, 'id_estado', must_be_positive=True)
        if id_estado is not None and not state_service.state_exists(id_estado):
            raise NotFoundError('Estado de conservación no encontrado')

    id_category = _validate_optional_int(id_category, 'id_category', must_be_positive=True)
    if id_category is None:
        raise ValidationError('id_category es requerido')
    if not category_service.category_exists(id_category):
        raise NotFoundError('Categoría no encontrada')

    if year_inauguration not in (None, ''):
        year_val = _validate_optional_int(year_inauguration, 'year_inauguration')
        if year_val is not None and year_val <= 0:
            raise ValidationError('Año de inauguración inválido')

    return {
        'name': name,
        'brief_description': brief,
        'complete_description': complete,
        'name_city': name_city,
        'name_province': name_province,
        'latitude': str(lat),
        'longitude': str(lng),
        'id_estado': id_estado,
        'year_inauguration': year_inauguration,
        'id_category': id_category,
        'visible': visible,
    }


def validate_update_site(data: dict) -> dict:
    """
    Valida y limpia los datos para actualizar un sitio histórico.
    
    Args:
        data: Diccionario con los campos a actualizar
        
    Returns:
        dict: Diccionario con los campos validados y limpiados
        
    Raises:
        ValidationError: Si los datos son inválidos
        NotFoundError: Si el estado de conservación o categoría no existen
    """
    cleaned = {}
    if 'name' in data:
        name = clean_string(data.get('name'))
        if not name:
            raise ValidationError('El nombre es requerido')
        if not ensure_max_length(name, MAX_NAME):
            raise ValidationError('El nombre no debe superar 255 caracteres')
        cleaned['name'] = name
    if 'brief_description' in data:
        brief = clean_string(data.get('brief_description'))
        if not brief:
            raise ValidationError('La descripción breve es requerida')
        if not ensure_max_length(brief, MAX_BRIEF):
            raise ValidationError('La descripción breve es demasiado larga')
        cleaned['brief_description'] = brief
    if 'complete_description' in data:
        cleaned['complete_description'] = data.get('complete_description') or None
    if 'latitude' in data:
        if not is_float_like(data.get('latitude')):
            raise ValidationError('Latitud inválida')
        cleaned['latitude'] = str(data.get('latitude'))
    if 'longitude' in data:
        if not is_float_like(data.get('longitude')):
            raise ValidationError('Longitud inválida')
        cleaned['longitude'] = str(data.get('longitude'))

    if 'id_estado' in data and data.get('id_estado') is not None:
        val = _validate_optional_int(data.get('id_estado'), 'id_estado', must_be_positive=True)
        if val is None:
            raise ValidationError('id_estado debe ser un entero positivo')
        if not state_service.state_exists(val):
            raise NotFoundError('Estado de conservación no encontrado')
        cleaned['id_estado'] = val
    if 'id_category' in data and data.get('id_category') is not None:
        val = _validate_optional_int(data.get('id_category'), 'id_category', must_be_positive=True)
        if val is None:
            raise ValidationError('id_category debe ser un entero positivo')
        if not category_service.category_exists(val):
            raise NotFoundError('Categoría no encontrada')
        cleaned['id_category'] = val
    if 'year_inauguration' in data and data.get('year_inauguration') not in (None, ''):
        year_val = _validate_optional_int(data.get('year_inauguration'), 'year_inauguration')
        if year_val is None:
            raise ValidationError('Año de inauguración inválido')
        if year_val <= 0:
            raise ValidationError('Año de inauguración debe ser positivo')
        cleaned['year_inauguration'] = year_val
    if 'visible' in data:
        cleaned['visible'] = bool(data.get('visible'))
    return cleaned


def validate_site_exists(site_id: int, must_be_visible: bool = False) -> HistoricSite:
    """
    Valida que un sitio histórico existe, no está eliminado y opcionalmente es visible.
    
    Args:
        site_id: ID del sitio a validar
        must_be_visible: Si True, también valida que el sitio sea visible
    
    Returns:
        HistoricSite: Sitio encontrado
    
    Raises:
        NotFoundError: Si el sitio no existe, está eliminado o no es visible (si se requiere)
    """
    site_id = validate_positive_int(site_id, "site_id")
    return historic_site_service.get_site_object(site_id, must_be_visible=must_be_visible)
