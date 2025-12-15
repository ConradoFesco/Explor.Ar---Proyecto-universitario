"""
Validaciones para provincias y ciudades.
"""
from typing import Optional
from src.web.exceptions import ValidationError
from .utils import clean_string


def validate_province_name(name: Optional[str]) -> str:
    """
    Valida el nombre de una provincia.
    
    Args:
        name: Nombre de la provincia
    
    Returns:
        str: Nombre validado y limpiado
    
    Raises:
        ValidationError: Si el nombre es inválido
    """
    if not name or not clean_string(name):
        raise ValidationError("El nombre de la provincia no puede estar vacío")
    return clean_string(name)


def validate_city_name(name: Optional[str], province_obj=None) -> str:
    """
    Valida el nombre de una ciudad y que tenga provincia asociada.
    
    Args:
        name: Nombre de la ciudad
        province_obj: Objeto provincia (opcional, para validar existencia)
    
    Returns:
        str: Nombre validado y limpiado
    
    Raises:
        ValidationError: Si el nombre es inválido o falta provincia
    """
    if not name or not clean_string(name):
        raise ValidationError("El nombre de la ciudad no puede estar vacío")
    
    if province_obj is not None and not province_obj:
        raise ValidationError("La provincia es requerida para crear la ciudad")
    
    return clean_string(name)

