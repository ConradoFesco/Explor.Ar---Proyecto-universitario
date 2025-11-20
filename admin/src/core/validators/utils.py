"""
Utilidades de validación comunes (tipos, longitudes, formatos).
"""

import re


def require_fields(data: dict, required: list[str]):
    missing = [f for f in required if (f not in data or data.get(f) in (None, '', []))]
    return missing


def ensure_max_length(value: str | None, max_len: int) -> bool:
    if value is None:
        return True
    return len(str(value)) <= max_len


def is_non_empty_string(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_bool(value) -> bool:
    return isinstance(value, bool)


def is_int(value) -> bool:
    return isinstance(value, int)


def is_float_like(value) -> bool:
    try:
        float(value)
        return True
    except Exception:
        return False


EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def is_valid_email(email: str | None) -> bool:
    if not email or not isinstance(email, str):
        return False
    return EMAIL_REGEX.match(email.strip()) is not None


PASSWORD_REGEX = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{6,}$")


def is_strong_password(password: str | None) -> bool:
    if not password or not isinstance(password, str):
        return False
    return PASSWORD_REGEX.match(password) is not None


