"""
Validaciones de entrada para Sitios Históricos.
"""
from src.web.exceptions import ValidationError, NotFoundError
from src.core.models.historic_site import HistoricSite
from src.core.models.state_site import StateSite
from src.core.models.category_site import CategorySite
from .utils import require_fields, is_float_like, ensure_max_length, clean_string
from .listing_validator import _validate_optional_int

MAX_NAME = 255
MAX_BRIEF = 2000


def validate_create_site(data: dict) -> dict:
    required = ['name', 'brief_description', 'name_city', 'name_province', 'latitude', 'longitude', 'id_category', 'visible']
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

    if HistoricSite.query.filter_by(name=name, deleted=False).first():
        raise ValidationError('Ya existe un sitio histórico con este nombre')

    if id_estado is not None:
        id_estado = _validate_optional_int(id_estado, 'id_estado', must_be_positive=True)
        if id_estado is not None and not StateSite.query.get(id_estado):
            raise NotFoundError('Estado de conservación no encontrado')
    
    id_category = _validate_optional_int(id_category, 'id_category', must_be_positive=True)
    if id_category is None:
        raise ValidationError('id_category es requerido')
    if not CategorySite.query.get(id_category):
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
        if not StateSite.query.get(val):
            raise NotFoundError('Estado de conservación no encontrado')
        cleaned['id_estado'] = val
    if 'id_category' in data and data.get('id_category') is not None:
        val = _validate_optional_int(data.get('id_category'), 'id_category', must_be_positive=True)
        if val is None:
            raise ValidationError('id_category debe ser un entero positivo')
        if not CategorySite.query.get(val):
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
    from src.core.validators.api_validator import validate_positive_int
    
    site_id = validate_positive_int(site_id, "site_id")
    query = HistoricSite.query.filter_by(id=site_id, deleted=False)
    if must_be_visible:
        query = query.filter_by(visible=True)
    site = query.first()
    if not site:
        if must_be_visible:
            raise NotFoundError("Sitio histórico no encontrado o no visible")
        raise NotFoundError("Sitio histórico no encontrado")
    return site
