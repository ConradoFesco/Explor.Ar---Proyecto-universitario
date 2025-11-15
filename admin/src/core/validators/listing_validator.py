"""
Validaciones de entrada para listados (paginación, filtros y ordenamiento).
"""
from datetime import datetime
from typing import Optional
from src.web.exceptions import ValidationError


def _validate_pagination(page: int | str | None, per_page: int | str | None, *, max_per_page: int = 25) -> tuple[int, int]:
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


def _validate_sort(sort_by: str, sort_order: str, *, allowed_fields: list[str]) -> tuple[str, str]:
    # Fallback a valores por defecto si no son válidos
    if sort_by not in allowed_fields:
        sort_by = allowed_fields[0] if allowed_fields else 'created_at'
    if sort_order not in ['asc', 'desc']:
        sort_order = 'desc'
    return sort_by, sort_order


def _validate_optional_int(value: Optional[int], field_name: str) -> Optional[int]:
    if value is None:
        return None
    if not isinstance(value, int):
        raise ValidationError(f"{field_name} debe ser entero")
    return value


def _validate_optional_bool_str(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    s = str(value).strip().lower()
    if s in ['true', '1', 'si', 'sí', 'yes', 'y']:
        return True
    if s in ['false', '0', 'no', 'n']:
        return False
    raise ValidationError('Parámetro booleano inválido')


def _clean_optional_str(value: Optional[object]) -> Optional[str]:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _validate_optional_float(value: Optional[object], field_name: str) -> Optional[float]:
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} debe ser numérico")


def _split_csv_values(raw_values: Optional[object]) -> list[str]:
    if not raw_values:
        return []
    return [
        item.strip().lower()
        for item in str(raw_values).split(',')
        if item.strip()
    ]


def _validate_tag_ids(tag_ids: Optional[object]) -> list[int]:
    """
    Devuelve una lista de ints válida. Si el formato es inválido, retorna lista vacía
    (comportamiento tolerante pedido en las correcciones).
    """
    if not tag_ids:
        return []
    if isinstance(tag_ids, str):
        # aceptar formato '1,2,3'
        parts = [p.strip() for p in tag_ids.split(',') if p.strip()]
        ints = []
        for p in parts:
            try:
                ints.append(int(p))
            except Exception:
                # ignorar entradas inválidas
                pass
        return ints
    if isinstance(tag_ids, list):
        ints = []
        for t in tag_ids:
            try:
                ints.append(int(t))
            except Exception:
                # ignorar entradas inválidas
                pass
        return ints
    # formato no esperado: ignorar filtro
    return []


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


def validate_site_list_params(*, page: int, per_page: int, search_text: Optional[str], sort_by: str, sort_order: str,
                              city_id: Optional[int], province_id: Optional[int], tag_ids: Optional[list[int]],
                              state_id: Optional[int], date_from: Optional[str], date_to: Optional[str],
                              visible: Optional[bool | str]) -> dict:
    page, per_page = _validate_pagination(page, per_page, max_per_page=25)
    sort_by, sort_order = _validate_sort(sort_by, sort_order, allowed_fields=['name', 'city', 'created_at'])
    city_id = _validate_optional_int(city_id, 'city_id')
    province_id = _validate_optional_int(province_id, 'province_id')
    state_id = _validate_optional_int(state_id, 'state_id')
    tag_ids = _validate_tag_ids(tag_ids)
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
                                      per_page: Optional[int]) -> dict:
    normalized_page = page if page is not None else 1
    normalized_per_page = per_page if per_page is not None else 20
    page, per_page = _validate_pagination(normalized_page, normalized_per_page, max_per_page=100)

    allowed_order = ['latest', 'oldest', 'rating-5-1', 'rating-1-5']
    normalized_order = (order_by or 'latest').strip().lower()
    if normalized_order not in allowed_order:
        raise ValidationError(f"order_by inválido. Valores permitidos: {', '.join(allowed_order)}")

    normalized_name = _clean_optional_str(name)
    normalized_description = _clean_optional_str(description)
    normalized_city = _clean_optional_str(city)
    normalized_province = _clean_optional_str(province)
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

    return {
        'name': normalized_name,
        'description': normalized_description,
        'city': normalized_city,
        'province': normalized_province,
        'tags': normalized_tags,
        'order_by': normalized_order,
        'latitude': lat,
        'longitude': lon,
        'radius_km': radius_value,
        'page': page,
        'per_page': per_page,
    }


def validate_tag_list_params(*, page: int, per_page: int, search: Optional[str], sort_by: str, sort_order: str) -> dict:
    page, per_page = _validate_pagination(page, per_page, max_per_page=50)
    sort_by, sort_order = _validate_sort(sort_by, sort_order, allowed_fields=['name', 'created_at'])
    return {
        'page': page,
        'per_page': per_page,
        'search': (search or '').strip(),
        'sort_by': sort_by,
        'sort_order': sort_order,
    }


def validate_user_list_params(*, page: int, per_page: int, filters: dict, sort_by: str, sort_order: str) -> dict:
    page, per_page = _validate_pagination(page, per_page, max_per_page=25)
    sort_by, sort_order = _validate_sort(sort_by, sort_order, allowed_fields=['created_at', 'name'])
    email = (filters.get('email') or '').strip() if filters else ''
    raw_activo = filters.get('activo') if filters else None
    raw_blocked = filters.get('blocked') if filters else None
    rol = (filters.get('rol') or '').strip() if filters else ''
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


def validate_event_list_params(*, page: int, per_page: int, user_id: Optional[int], user_email: Optional[str],
                               type_action: Optional[str], date_from: Optional[str], date_to: Optional[str]) -> dict:
    """Valida filtros de eventos y devuelve tipos correctos para el servicio (datetime)."""
    page, per_page = _validate_pagination(page, per_page, max_per_page=50)
    user_id = _validate_optional_int(user_id, 'user_id')
    # Validar formato de fechas y convertir a datetime
    date_from_str = _validate_optional_date(date_from, 'date_from')
    date_to_str = _validate_optional_date(date_to, 'date_to')
    date_from_dt = _parse_date_yyyy_mm_dd(date_from_str) if date_from_str else None
    date_to_dt = _end_of_day(_parse_date_yyyy_mm_dd(date_to_str)) if date_to_str else None
    return {
        'page': page,
        'per_page': per_page,
        'user_id': user_id,
        'user_email': (user_email or '').strip() or None,
        'type_action': (type_action or '').strip() or None,
        'date_from': date_from_dt,
        'date_to': date_to_dt,
    }