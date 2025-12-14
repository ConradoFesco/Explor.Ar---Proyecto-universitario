"""
Validaciones de entrada para listados (paginación, filtros y ordenamiento).
"""
from datetime import datetime
from typing import Optional
from src.web.exceptions import ValidationError
from .utils import clean_optional_string
from .tag_validator import validate_tag_ids_exist


def _validate_pagination(page: Optional[object], per_page: Optional[object], *, 
                        default_page: int = 1, default_per_page: int = 20, max_per_page: int = 25) -> tuple[int, int]:
    """
    Valida parámetros de paginación.
    Aplica valores por defecto solo si el parámetro viene vacío/None/solo espacios.
    Si viene con valor pero es inválido, lanza excepción.
    
    Args:
        page: Número de página (opcional)
        per_page: Elementos por página (opcional)
        default_page: Valor por defecto para page (solo si viene vacío/None)
        default_per_page: Valor por defecto para per_page (solo si viene vacío/None)
        max_per_page: Máximo de elementos por página
    
    Returns:
        tuple: (page, per_page) validados
    
    Raises:
        ValidationError: Si los parámetros son inválidos
    """
    if page is None or (isinstance(page, str) and page.strip() == ''):
        page = default_page
    if per_page is None or (isinstance(per_page, str) and per_page.strip() == ''):
        per_page = default_per_page
    
    if page is None:
        page = default_page
    if per_page is None:
        per_page = default_per_page
    
    try:
        page = int(page)
    except (TypeError, ValueError):
        raise ValidationError('El número de página debe ser un entero >= 1')
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        raise ValidationError(f'per_page debe ser un entero entre 1 y {max_per_page}')
    
    if page < 1:
        raise ValidationError('El número de página debe ser un entero >= 1')
    if per_page < 1 or per_page > max_per_page:
        raise ValidationError(f'per_page debe ser un entero entre 1 y {max_per_page}')
    
    return page, per_page


def _validate_sort(sort_by: Optional[str], sort_order: Optional[str], *, 
                  allowed_fields: list[str], default_sort_by: Optional[str] = None,
                  default_sort_order: str = 'desc') -> tuple[str, str]:
    """
    Valida parámetros de ordenamiento.
    Aplica valores por defecto solo si el parámetro viene vacío/None.
    Si viene con valor pero es inválido, lanza excepción.
    
    Args:
        sort_by: Campo por el cual ordenar (opcional)
        sort_order: Dirección del orden (opcional)
        allowed_fields: Lista de campos permitidos
        default_sort_by: Valor por defecto para sort_by (solo si viene vacío/None)
        default_sort_order: Valor por defecto para sort_order (solo si viene vacío/None)
    
    Returns:
        tuple: (sort_by, sort_order) validados
    
    Raises:
        ValidationError: Si los valores son inválidos
    """
    cleaned_sort_by = clean_optional_string(sort_by)
    if not cleaned_sort_by:
        if default_sort_by and default_sort_by in allowed_fields:
            sort_by = default_sort_by
        elif allowed_fields:
            sort_by = allowed_fields[0] 
        else:
            raise ValidationError("No hay campos de orden permitidos")
    else:
        sort_by = cleaned_sort_by
        if sort_by not in allowed_fields:
            raise ValidationError(f"Campo de orden inválido: {sort_by}. Opciones válidas: {allowed_fields}")
    
    cleaned_sort_order = clean_optional_string(sort_order)
    if not cleaned_sort_order:
        sort_order = default_sort_order
    else:
        sort_order = cleaned_sort_order.lower()
        if sort_order not in ['asc', 'desc']:
            raise ValidationError(f"Sentido de orden inválido: {sort_order}. Debe ser 'asc' o 'desc'.")
    
    return sort_by, sort_order


def _validate_optional_int(value: Optional[int | str | object], field_name: str, 
                          must_be_positive: bool = False) -> Optional[int]:
    """
    Valida un entero opcional.
    
    Args:
        value: Valor a validar (puede ser int, str o None)
        field_name: Nombre del campo para mensajes de error
        must_be_positive: Si True, valida que el entero sea positivo
    
    Returns:
        Optional[int]: Entero validado o None
    """
    if value is None or value == '':
        return None
    
    try:
        int_val = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} debe ser entero")
    
    if must_be_positive and int_val <= 0:
        raise ValidationError(f"{field_name} debe ser un entero positivo")
    
    return int_val


def _validate_optional_bool_str(value: Optional[str]) -> Optional[bool]:
    """Valida un string opcional como booleano."""
    if value is None:
        return None
    cleaned = clean_optional_string(value)
    if not cleaned:
        return None
    s = cleaned.lower()
    if s in ['true', '1', 'si', 'sí', 'yes', 'y']:
        return True
    if s in ['false', '0', 'no', 'n']:
        return False
    raise ValidationError('Parámetro booleano inválido')



def _validate_optional_float(value: Optional[object], field_name: str) -> Optional[float]:
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} debe ser numérico")


def _split_csv_values(raw_values: Optional[object]) -> list[str]:
    """Divide valores separados por comas y los normaliza."""
    if not raw_values:
        return []
    cleaned = clean_string(raw_values)
    if not cleaned:
        return []
    return [
        clean_string(item).lower()
        for item in cleaned.split(',')
        if clean_string(item)
    ]


def _validate_tag_ids(tag_ids: Optional[object]) -> list[int]:
    """
    Valida y normaliza una lista de IDs de tags.
    - Si no se envía ningún valor (None / '' / []), retorna lista vacía.
    - Si se envía algo y no puede convertirse completamente a enteros válidos,
      lanza ValidationError en lugar de ignorar silenciosamente.
    """
    if tag_ids is None or tag_ids == '' or tag_ids == []:
        return []

    ints: list[int] = []

    if isinstance(tag_ids, str):
        parts = [p.strip() for p in tag_ids.split(',') if p.strip()]
        if not parts:
            return []
        try:
            ints = [int(p) for p in parts]
        except Exception:
            raise ValidationError("tag_ids debe ser una lista de IDs numéricos separados por comas")
        return ints

    if isinstance(tag_ids, list):
        if not tag_ids:
            return []
        try:
            ints = [int(t) for t in tag_ids]
        except Exception:
            raise ValidationError("tag_ids debe ser una lista de IDs numéricos")
        return ints

    raise ValidationError("tag_ids tiene un formato inválido")


def _validate_optional_date(date_str: Optional[str], field: str) -> Optional[str]:
    if not date_str:
        return None
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        raise ValidationError(f"{field} debe tener formato YYYY-MM-DD")


def _parse_date_yyyy_mm_dd(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    return datetime.strptime(date_str, '%Y-%m-%d')


def _end_of_day(dt: datetime) -> datetime:
    from datetime import timedelta
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def validate_site_list_params(*, page: Optional[int] = None, per_page: Optional[int] = None, 
                              search_text: Optional[str] = None, sort_by: Optional[str] = None, 
                              sort_order: Optional[str] = None,
                              city_id: Optional[int] = None, province_id: Optional[int] = None, 
                              tag_ids: Optional[list[int]] = None,
                              state_id: Optional[int] = None, date_from: Optional[str] = None, 
                              date_to: Optional[str] = None,
                              visible: Optional[bool | str] = None) -> dict:
    page, per_page = _validate_pagination(page, per_page, default_page=1, default_per_page=25, max_per_page=25)
    sort_by, sort_order = _validate_sort(
        sort_by, sort_order, 
        allowed_fields=['name', 'city', 'created_at'],
        default_sort_by='created_at',
        default_sort_order='desc'
    )
    city_id = _validate_optional_int(city_id, 'city_id')
    province_id = _validate_optional_int(province_id, 'province_id')
    state_id = _validate_optional_int(state_id, 'state_id')
    tag_ids = _validate_tag_ids(tag_ids)
    if tag_ids:
        validate_tag_ids_exist(tag_ids)
    if isinstance(visible, str):
        visible = _validate_optional_bool_str(visible)
    date_from = _validate_optional_date(date_from, 'date_from')
    date_to = _validate_optional_date(date_to, 'date_to')
    return {
        'page': page,
        'per_page': per_page,
        'search_text': (search_text or '').strip() or None,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'city_id': city_id,
        'province_id': province_id,
        'tag_ids': tag_ids,
        'state_id': state_id,
        'date_from': date_from,
        'date_to': date_to,
        'visible': visible,
    }


def validate_public_site_search_params(*, name: Optional[str], description: Optional[str],
                                      city: Optional[str], province: Optional[str],
                                      tags: Optional[str], order_by: Optional[str],
                                      latitude: Optional[object], longitude: Optional[object],
                                      radius: Optional[object], page: Optional[int],
                                      per_page: Optional[int], favorites_only: Optional[bool] = None) -> dict:
    page_val, per_page_val = _validate_pagination(page, per_page, default_page=1, default_per_page=20, max_per_page=100)

    allowed_order = ['latest', 'oldest', 'rating-5-1', 'rating-1-5', 'name-asc', 'name-desc']
    normalized_order: Optional[str] = None
    if order_by is not None and order_by != '':
        normalized_order = clean_optional_string(order_by)
        if normalized_order: 
            normalized_order_lower = normalized_order.lower()
            if normalized_order_lower not in allowed_order:
                raise ValidationError(f"order_by inválido. Valores permitidos: {', '.join(allowed_order)}")
            normalized_order = normalized_order_lower

    normalized_name = clean_optional_string(name)
    normalized_description = clean_optional_string(description)
    normalized_city = clean_optional_string(city)
    normalized_province = clean_optional_string(province)
    normalized_tags = _split_csv_values(tags)

    lat = _validate_optional_float(latitude, 'lat')
    lon = _validate_optional_float(longitude, 'long')
    radius_value = _validate_optional_float(radius, 'radius')

    if (lat is None) ^ (lon is None):
        raise ValidationError('lat y long deben enviarse juntos')
    if radius_value is not None and (lat is None or lon is None):
        raise ValidationError('radius requiere lat y long')
    if radius_value is not None and radius_value <= 0:
        raise ValidationError('radius debe ser mayor a 0')
    
    radius_km = None
    if radius_value is not None:
        radius_km = radius_value / 1000.0

    return {
        'name': normalized_name,
        'description': normalized_description,
        'city': normalized_city,
        'province': normalized_province,
        'tags': normalized_tags,
        'order_by': normalized_order,
        'latitude': lat,
        'longitude': lon,
        'radius_km': radius_km,
        'page': page_val,
        'per_page': per_page_val,
        'favorites_only': favorites_only if favorites_only is not None else False,
    }


def validate_tag_list_params(*, page: Optional[int] = None, per_page: Optional[int] = None, 
                             search: Optional[str] = None, sort_by: Optional[str] = None, 
                             sort_order: Optional[str] = None) -> dict:
    page, per_page = _validate_pagination(page, per_page, default_page=1, default_per_page=25, max_per_page=50)
    sort_by, sort_order = _validate_sort(
        sort_by, sort_order,
        allowed_fields=['name', 'created_at'],
        default_sort_by='name',
        default_sort_order='asc'
    )
    return {
        'page': page,
        'per_page': per_page,
        'search': clean_optional_string(search) or '',
        'sort_by': sort_by,
        'sort_order': sort_order,
    }


def validate_user_list_params(*, page: Optional[int] = None, per_page: Optional[int] = None,
                             filters: Optional[dict] = None, sort_by: Optional[str] = None, 
                             sort_order: Optional[str] = None) -> dict:
    page, per_page = _validate_pagination(page, per_page, default_page=1, default_per_page=25, max_per_page=25)
    sort_by, sort_order = _validate_sort(
        sort_by, sort_order,
        allowed_fields=['created_at', 'name'],
        default_sort_by='created_at',
        default_sort_order='desc'
    )
    email = clean_optional_string(filters.get('email') if filters else None) or '' if filters else ''
    raw_activo = filters.get('activo') if filters else None
    raw_blocked = filters.get('blocked') if filters else None
    rol = clean_optional_string(filters.get('rol') if filters else None) or '' if filters else ''
    activo = None
    if raw_activo is not None:
        activo = _validate_optional_bool_str(raw_activo)
    blocked = None
    if raw_blocked is not None:
        blocked = _validate_optional_bool_str(raw_blocked)
    return {
        'page': page,
        'per_page': per_page,
        'filters': {
            'email': email or None,
            'activo': activo,
            'blocked': blocked,
            'rol': rol or None,
        },
        'sort_by': sort_by,
        'sort_order': sort_order,
    }


def validate_event_list_params(*, page: Optional[object], per_page: Optional[object], user_id: Optional[object], user_email: Optional[str],
                               type_action: Optional[str], date_from: Optional[str], date_to: Optional[str]) -> dict:
    """Valida filtros de eventos y devuelve tipos correctos para el servicio (datetime)."""
    page, per_page = _validate_pagination(page, per_page, default_page=1, default_per_page=10, max_per_page=50)
    user_id = _validate_optional_int(user_id, 'user_id')
    date_from_str = _validate_optional_date(date_from, 'date_from')
    date_to_str = _validate_optional_date(date_to, 'date_to')
    date_from_dt = _parse_date_yyyy_mm_dd(date_from_str) if date_from_str else None
    date_to_dt = _end_of_day(_parse_date_yyyy_mm_dd(date_to_str)) if date_to_str else None
    return {
        'page': page,
        'per_page': per_page,
        'user_id': user_id,
        'user_email': clean_optional_string(user_email),
        'type_action': clean_optional_string(type_action),
        'date_from': date_from_dt,
        'date_to': date_to_dt,
    }