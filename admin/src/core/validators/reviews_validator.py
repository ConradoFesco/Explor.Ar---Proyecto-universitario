from src.web.exceptions import ValidationError
from .listing_validator import (
    _validate_pagination, 
    _validate_sort, 
    _validate_optional_int, 
    _validate_optional_date, 
    _clean_optional_str
)

def validate_review_list_params(
    page=None, per_page=None,
    sort_by=None, sort_order=None,
    status=None, site_id=None, user=None,
    rating_from=None, rating_to=None,
    date_from=None, date_to=None
) -> dict:
    """
    Valida y limpia todos los parámetros para el listado de reseñas.
    Centraliza la lógica que antes estaba dispersa en el controlador.
    """
    
    page_val, per_page_val = _validate_pagination(page, per_page, max_per_page=50)

    allowed_sort = ['created_at', 'rating', 'user_mail', 'site_name']
    sort_by_val, sort_order_val = _validate_sort(sort_by, sort_order, allowed_fields=allowed_sort)

    filters = {}

    if status and status not in ['', 'null']:
        filters['status'] = status

    if site_id:
        filters['site_id'] = _validate_optional_int(site_id, 'site_id')
    
    if rating_from:
        filters['rating_from'] = _validate_optional_int(rating_from, 'rating_from')
    
    if rating_to:
        filters['rating_to'] = _validate_optional_int(rating_to, 'rating_to')

    if date_from:
        filters['date_from'] = _validate_optional_date(date_from, 'date_from')
    if date_to:
        filters['date_to'] = _validate_optional_date(date_to, 'date_to')

    clean_user = _clean_optional_str(user)
    if clean_user:
        filters['user'] = clean_user

    return {
        'page': page_val,
        'per_page': per_page_val,
        'sort_by': sort_by_val,
        'sort_order': sort_order_val,
        'filters': filters
    }


def validate_review_create_payload(*, rating, content):
    try:
        rating_val = int(rating)
    except (TypeError, ValueError):
        raise ValidationError('rating debe ser un entero entre 1 y 5')

    if rating_val < 1 or rating_val > 5:
        raise ValidationError('rating debe estar entre 1 y 5')

    content_val = (content or '').strip()
    if not content_val:
        raise ValidationError('El contenido de la reseña es obligatorio')
    
    if len(content_val) < 20:
        raise ValidationError('El contenido de la reseña debe tener al menos 20 caracteres')
    
    if len(content_val) > 1000:
        raise ValidationError('El contenido de la reseña no puede exceder 1000 caracteres')

    return {
        'rating': rating_val,
        'content': content_val,
    }