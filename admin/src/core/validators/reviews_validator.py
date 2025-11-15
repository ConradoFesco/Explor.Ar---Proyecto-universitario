from src.web.exceptions import ValidationError
from .listing_validator import _validate_pagination


def validate_review_list_params(*, page: int | str | None, per_page: int | str | None) -> dict:
    try:
        page_val = int(page) if page is not None else 1
    except (TypeError, ValueError):
        raise ValidationError('El número de página debe ser un entero >= 1')

    try:
        per_page_val = int(per_page) if per_page is not None else 10
    except (TypeError, ValueError):
        raise ValidationError('per_page debe ser un entero entre 1 y 100')

    page_val, per_page_val = _validate_pagination(page_val, per_page_val, max_per_page=100)
    return {
        'page': page_val,
        'per_page': per_page_val
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

    return {
        'rating': rating_val,
        'content': content_val,
    }

