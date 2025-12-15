from src.web.exceptions import ValidationError
from .listing_validator import (
    _validate_pagination, 
    _validate_sort, 
    _validate_optional_int, 
    _validate_optional_date, 
)
from .api_validator import validate_positive_int
from .utils import clean_optional_string, clean_string
from typing import Optional

def validate_review_list_params(page=None, per_page=None, sort_by=None, sort_order=None,
                                status=None, site_id=None, user=None,
                                rating_from=None, rating_to=None,
                                date_from=None, date_to=None) -> dict:
    """
    Valida y limpia todos los parámetros para el listado de reseñas.
    Centraliza la lógica que antes estaba dispersa en el controlador.
    """
    page_val, per_page_val = _validate_pagination(page, per_page, default_page=1, default_per_page=25, max_per_page=100)

    allowed_sort = ['created_at', 'rating', 'user_mail', 'site_name']
    sort_by_val, sort_order_val = _validate_sort(
        sort_by, sort_order,
        allowed_fields=allowed_sort,
        default_sort_by='created_at',
        default_sort_order='desc'
    )

    filters = {}

    if status and status not in ['', 'null']:
        allowed_statuses = ['pending', 'approved', 'rejected']
        if status not in allowed_statuses:
            raise ValidationError(f'status inválido. Valores permitidos: {", ".join(allowed_statuses)}')
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

    clean_user = clean_optional_string(user)
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
    """
    Valida el payload para crear una reseña.
    Usa _validate_optional_int para validar el rating.
    """
    rating_val = _validate_optional_int(rating, 'rating', must_be_positive=True)
    
    if rating_val is None:
        raise ValidationError('rating es requerido')
    
    if rating_val < 1 or rating_val > 5:
        raise ValidationError('rating debe estar entre 1 y 5')

    content_val = clean_string(content)
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


def validate_review_detail_params(*, site_id, review_id):
    """
    Valida los parámetros requeridos para obtener el detalle de una reseña.
    
    Args:
        site_id: ID del sitio (requerido)
        review_id: ID de la reseña (requerido)
    
    Returns:
        dict: Parámetros validados con 'site_id' y 'review_id' como enteros
    
    Raises:
        ValidationError: Si los parámetros son inválidos o faltantes
    """
    if not site_id:
        raise ValidationError('site_id es requerido')
    
    site_id_val = validate_positive_int(site_id, 'site_id')
    review_id_val = validate_positive_int(review_id, 'review_id')
    
    return {
        'site_id': site_id_val,
        'review_id': review_id_val,
    }


def validate_rejection_reason(reason):
    """
    Valida el motivo de rechazo de una reseña.
    
    Args:
        reason: Motivo de rechazo (requerido)
    
    Returns:
        str: Motivo de rechazo validado y limpiado
    
    Raises:
        ValidationError: Si el motivo es inválido o faltante
    """
    if not reason or not reason.strip():
        raise ValidationError('Motivo de rechazo requerido')
    
    reason_cleaned = reason.strip()
    
    if len(reason_cleaned) > 200:
        raise ValidationError('El motivo de rechazo no puede superar los 200 caracteres')
    
    return reason_cleaned


def validate_review_sort(sort: Optional[str]) -> str:
    """
    Valida el parámetro de ordenamiento para listado de reseñas.
    
    Args:
        sort: Valor del parámetro sort ('asc' o 'desc')
    
    Returns:
        str: Valor validado (default: 'desc')
    
    Raises:
        ValidationError: Si el valor es inválido
    """
    if sort and sort not in ['asc', 'desc']:
        raise ValidationError("sort debe ser 'asc' o 'desc'")
    
    return sort if sort else 'desc'