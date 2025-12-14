"""
Validaciones de entrada para acciones de perfil (contraseña).
"""
from src.web.exceptions import ValidationError
from .utils import is_strong_password


def validate_new_password(new_password: str) -> str:
    from .utils import clean_string
    new_password = clean_string(new_password)
    if not is_strong_password(new_password):
        raise ValidationError('La contraseña debe tener al menos 6 caracteres y combinar letras y números')
    return new_password
