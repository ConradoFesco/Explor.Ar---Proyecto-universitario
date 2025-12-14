"""
Validaciones de entrada para Sitios Históricos.
"""
from src.web.exceptions import ValidationError, NotFoundError
from src.core.models.historic_site import HistoricSite
from src.core.models.state_site import StateSite
from src.core.models.category_site import CategorySite
from .utils import require_fields, is_float_like, ensure_max_length
from .listing_validator import _validate_optional_int

MAX_NAME = 255
MAX_BRIEF = 2000


def validate_create_site(data: dict) -> dict:
    required = ['name', 'brief_description', 'name_city', 'name_province', 'latitude', 'longitude', 'id_category', 'visible']
    missing = require_fields(data, required)
    if missing:
        raise ValidationError(f"Faltan campos obligatorios del sitio histórico: {', '.join(missing)}")

    name = (data.get('name') or '').strip()
    brief = (data.get('brief_description') or '').strip()
    complete = (data.get('complete_description') or None)
    name_city = (data.get('name_city') or '').strip()
    name_province = (data.get('name_province') or '').strip()
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
        name = (data.get('name') or '').strip()
        if not name:
            raise ValidationError('El nombre es requerido')
        if not ensure_max_length(name, MAX_NAME):
            raise ValidationError('El nombre no debe superar 255 caracteres')
        cleaned['name'] = name
    if 'brief_description' in data:
        brief = (data.get('brief_description') or '').strip()
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
        try:
            val = int(data.get('id_estado'))
        except Exception:
            raise ValidationError('id_estado debe ser entero')
        if not StateSite.query.get(val):
            raise NotFoundError('Estado de conservación no encontrado')
        cleaned['id_estado'] = val
    if 'id_category' in data and data.get('id_category') is not None:
        try:
            val = int(data.get('id_category'))
        except Exception:
            raise ValidationError('id_category debe ser entero')
        if not CategorySite.query.get(val):
            raise NotFoundError('Categoría no encontrada')
        cleaned['id_category'] = val
    if 'year_inauguration' in data and data.get('year_inauguration') not in (None, ''):
        try:
            cleaned['year_inauguration'] = int(data.get('year_inauguration'))
        except Exception:
            raise ValidationError('Año de inauguración inválido')
    if 'visible' in data:
        cleaned['visible'] = bool(data.get('visible'))
    return cleaned
