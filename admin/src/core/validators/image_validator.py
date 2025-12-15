"""
Validaciones para imágenes de sitios históricos.
"""
from typing import Optional
from src.web.exceptions import ValidationError
from .utils import clean_string, ensure_max_length

MAX_TITULO_ALT_LENGTH = 255
MAX_IMAGES_PER_SITE = 10


def validate_titulo_alt(titulo_alt: Optional[str], field_name: str = "título/alt") -> str:
    """
    Valida el título/alt de una imagen.
    
    Args:
        titulo_alt: Título/alt a validar
        field_name: Nombre del campo para mensajes de error
    
    Returns:
        str: Título/alt validado y limpiado
    
    Raises:
        ValidationError: Si el título es inválido
    """
    if not titulo_alt:
        raise ValidationError(f"El {field_name} es obligatorio")
    
    titulo_alt_cleaned = clean_string(titulo_alt)
    if not titulo_alt_cleaned:
        raise ValidationError(f"El {field_name} es obligatorio")
    
    if not ensure_max_length(titulo_alt_cleaned, MAX_TITULO_ALT_LENGTH):
        raise ValidationError(f"El {field_name} no debe superar {MAX_TITULO_ALT_LENGTH} caracteres")
    
    return titulo_alt_cleaned


def validate_image_orders(image_orders: Optional[list]) -> list:
    """
    Valida la lista de órdenes de imágenes.
    
    Args:
        image_orders: Lista de diccionarios con 'id' y 'orden'
    
    Returns:
        list: Lista validada
    
    Raises:
        ValidationError: Si la lista está vacía o es inválida
    """
    if not image_orders:
        raise ValidationError("No se proporcionaron órdenes")
    
    if not isinstance(image_orders, list):
        raise ValidationError("Los órdenes deben enviarse como una lista")
    
    return image_orders

