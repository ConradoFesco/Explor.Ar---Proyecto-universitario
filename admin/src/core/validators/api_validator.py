"""
Validaciones específicas para endpoints de API pública.
Maneja validación de parámetros y formateo de errores según la especificación.
"""
from typing import Optional
from src.web.exceptions import ValidationError
from .listing_validator import _validate_pagination


def validate_api_pagination_params(page: Optional[object] = None, per_page: Optional[object] = None,
                                   default_page: int = 1, default_per_page: int = 20,
                                   max_per_page: int = 100) -> tuple[int, int]:
    """
    Valida parámetros de paginación para APIs.
    
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
    try:
        page_val, per_page_val = _validate_pagination(
            page, per_page,
            default_page=default_page,
            default_per_page=default_per_page,
            max_per_page=max_per_page
        )
        return page_val, per_page_val
    except ValidationError as e:
        error_msg = str(e).lower()
        if 'per_page' in error_msg or 'entre' in error_msg:
            raise ValidationError(f'per_page debe ser un entero entre 1 y {max_per_page}')
        elif 'página' in error_msg or 'page' in error_msg:
            raise ValidationError('page debe ser un entero >= 1')
        raise


def validate_positive_int(value: Optional[object], field_name: str, allow_none: bool = False) -> int | None:
    """
    Valida que un valor sea un entero positivo.
    Usa _validate_optional_int internamente para evitar duplicación.
    
    Args:
        value: Valor a validar
        field_name: Nombre del campo para mensajes de error
        allow_none: Si True, permite None (útil para parámetros opcionales)
    
    Returns:
        int | None: Valor validado como entero positivo, o None si allow_none=True y value es None
    
    Raises:
        ValidationError: Si el valor no es un entero positivo o es None cuando allow_none=False
    """
    from .listing_validator import _validate_optional_int
    
    if value is None and allow_none:
        return None
    
    if value is None:
        raise ValidationError(f'{field_name} es requerido')
    
    return _validate_optional_int(value, field_name, must_be_positive=True)


def format_validation_error_for_api(error: ValidationError) -> dict:
    """
    Formatea un error de validación al formato esperado por la API.
    
    Args:
        error: Excepción de validación
    
    Returns:
        dict: Detalles del error formateados por campo
    """
    error_msg = str(error).lower()
    details = {}
    
    if 'per_page' in error_msg:
        if 'entre' in error_msg or 'between' in error_msg:
            details['per_page'] = ['Must be between 1 and 100']
        else:
            details['per_page'] = [str(error)]
    
    if 'page' in error_msg:
        if 'debe ser' in error_msg or 'must be' in error_msg:
            details['page'] = ['Must be a positive integer']
        else:
            details['page'] = [str(error)]
    
    if 'lat' in error_msg or 'latitude' in error_msg:
        if 'debe ser numérico' in error_msg or 'must be' in error_msg:
            details['lat'] = ['Must be a valid latitude']
        elif 'deben enviarse juntos' in error_msg:
            details['lat'] = ['Must be provided together with long']
            details['long'] = ['Must be provided together with lat']
    
    if 'long' in error_msg or 'longitude' in error_msg:
        if 'debe ser numérico' in error_msg or 'must be' in error_msg:
            details['long'] = ['Must be a valid longitude']
    
    if 'radius' in error_msg:
        if 'debe ser mayor a 0' in error_msg or 'must be greater' in error_msg:
            details['radius'] = ['Must be greater than 0']
        elif 'requiere lat y long' in error_msg or 'requires lat and long' in error_msg:
            details['radius'] = ['Requires lat and long parameters']
    
    if 'order_by' in error_msg:
        if 'inválido' in error_msg or 'invalid' in error_msg:
            details['order_by'] = ['Invalid value. Choices: rating-5-1, rating-1-5, latest, oldest']
        else:
            details['order_by'] = [str(error)]
    
    if 'rating' in error_msg:
        if 'entre 1 y 5' in error_msg or 'between 1 and 5' in error_msg:
            details['rating'] = ['Must be between 1 and 5']
        else:
            details['rating'] = [str(error)]
    
    if 'review_id' in error_msg:
        if 'debe ser' in error_msg or 'must be' in error_msg:
            details['review_id'] = ['Must be a positive integer']
        else:
            details['review_id'] = [str(error)]
    
    if 'site_id' in error_msg:
        details['site_id'] = [str(error)]
    
    if 'sort' in error_msg:
        if 'asc' in error_msg or 'desc' in error_msg:
            details['sort'] = ["Must be 'asc' or 'desc'"]
        else:
            details['sort'] = [str(error)]
    
    if not details:
        details['_global'] = [str(error)]
    
    return details

