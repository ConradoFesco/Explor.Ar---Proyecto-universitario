"""
Validaciones de entrada para usuarios.
"""
from src.web.exceptions import ValidationError, NotFoundError
from src.core.models.user import User
from src.core.models.rol_user import RolUser
from .utils import require_fields, is_valid_email, ensure_max_length, is_strong_password


MAX_NAME = 120
MAX_MAIL = 120


def validate_create_user(data: dict) -> dict:
    missing = require_fields(data, ['mail', 'name', 'last_name', 'password'])
    if missing:
        raise ValidationError(f"Faltan campos obligatorios: {', '.join(missing)}")

    mail = (data.get('mail') or '').strip()
    name = (data.get('name') or '').strip()
    last_name = (data.get('last_name') or '').strip()
    password = data.get('password') or ''

    if not is_valid_email(mail):
        raise ValidationError('Email inválido')
    if not is_strong_password(password):
        raise ValidationError('La contraseña debe tener al menos 6 caracteres y combinar letras y números')
    if not ensure_max_length(name, MAX_NAME) or not ensure_max_length(last_name, MAX_NAME):
        raise ValidationError('El nombre y apellido no deben superar 120 caracteres')
    if not ensure_max_length(mail, MAX_MAIL):
        raise ValidationError('El email no debe superar 120 caracteres')

    # Unicidad de mail
    existing = User.query.filter_by(mail=mail, deleted=False).first()
    if existing:
        raise ValidationError('Ya existe un usuario con ese mail')

    return {
        'mail': mail,
        'name': name,
        'last_name': last_name,
        'password': password,
    }


def validate_update_user(data: dict) -> dict:
    cleaned = {}
    if 'mail' in data:
        mail = (data.get('mail') or '').strip()
        if not is_valid_email(mail):
            raise ValidationError('Email inválido')
        if not ensure_max_length(mail, MAX_MAIL):
            raise ValidationError('El email no debe superar 120 caracteres')
        cleaned['mail'] = mail
    if 'name' in data:
        name = (data.get('name') or '').strip()
        if not ensure_max_length(name, MAX_NAME):
            raise ValidationError('El nombre no debe superar 120 caracteres')
        cleaned['name'] = name
    if 'last_name' in data:
        last_name = (data.get('last_name') or '').strip()
        if not ensure_max_length(last_name, MAX_NAME):
            raise ValidationError('El apellido no debe superar 120 caracteres')
        cleaned['last_name'] = last_name
    if 'password' in data:
        password = data.get('password') or ''
        if not is_strong_password(password):
            raise ValidationError('La contraseña debe tener al menos 6 caracteres y combinar letras y números')
        cleaned['password'] = password
    if 'active' in data:
        cleaned['active'] = bool(data.get('active'))
    if 'blocked' in data:
        cleaned['blocked'] = bool(data.get('blocked'))
    return cleaned


def validate_role_ids(role_ids: list[int]) -> list[int]:
    if role_ids is None:
        return []
    try:
        ids = [int(r) for r in role_ids]
    except Exception:
        raise ValidationError('IDs de roles inválidos')
    # Integridad referencial
    missing = []
    for rid in ids:
        if not RolUser.query.get(rid):
            missing.append(rid)
    if missing:
        raise NotFoundError(f"Roles no encontrados: {missing}")
    return ids


