"""
Validaciones de entrada para acciones de perfil (contraseña).
"""
from src.web.exceptions import ValidationError
from .utils import is_strong_password, clean_string


def validate_new_password(new_password: str) -> str:
    """
    Valida que una nueva contraseña cumpla con los requisitos de seguridad.
    
    Args:
        new_password: Contraseña a validar
        
    Returns:
        str: Contraseña validada y limpiada
        
    Raises:
        ValidationError: Si la contraseña no cumple con los requisitos
    """
    new_password = clean_string(new_password)
    if not is_strong_password(new_password):
        raise ValidationError('La contraseña debe tener al menos 6 caracteres y combinar letras y números')
    return new_password
