"""
Utilidades de validación comunes (tipos, longitudes, formatos).
"""

import re
from typing import Optional

def require_fields(data: dict, required: list[str]):
    """Verifica que los campos requeridos estén presentes y no vacíos."""
    missing = [f for f in required if (f not in data or data.get(f) in (None, '', []))]
    return missing


def clean_string(value: Optional[str | object], default: str = '') -> str:
    """
    Limpia y normaliza un string.
    
    Args:
        value: Valor a limpiar (puede ser str, None u otro tipo)
        default: Valor por defecto si value es None o vacío
    
    Returns:
        String limpio (sin espacios al inicio/fin) o default si está vacío
    """
    if value is None:
        return default
    cleaned = str(value).strip()
    return cleaned if cleaned else default


def clean_optional_string(value: Optional[str | object]) -> Optional[str]:
    """
    Limpia un string opcional, retornando None si está vacío.
    
    Args:
        value: Valor a limpiar
    
    Returns:
        String limpio o None si está vacío
    """
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned if cleaned else None


def ensure_max_length(value: str | None, max_len: int) -> bool:
    """Verifica que un string no exceda la longitud máxima."""
    if value is None:
        return True
    return len(str(value)) <= max_len


def is_non_empty_string(value) -> bool:
    """Verifica que un valor sea un string no vacío."""
    return isinstance(value, str) and bool(value.strip())


def is_bool(value) -> bool:
    """Verifica que un valor sea booleano."""
    return isinstance(value, bool)


def is_int(value) -> bool:
    """Verifica que un valor sea entero."""
    return isinstance(value, int)


def is_float_like(value) -> bool:
    """Verifica que un valor pueda convertirse a float."""
    try:
        float(value)
        return True
    except Exception:
        return False


EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def is_valid_email(email: str | None) -> bool:
    """Valida formato de email."""
    if not email or not isinstance(email, str):
        return False
    return EMAIL_REGEX.match(email.strip()) is not None


PASSWORD_REGEX = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{6,}$")

def is_strong_password(password: str | None) -> bool:
    """Valida que la contraseña sea fuerte (al menos 6 caracteres, letras y números)."""
    if not password or not isinstance(password, str):
        return False
    return PASSWORD_REGEX.match(password) is not None

