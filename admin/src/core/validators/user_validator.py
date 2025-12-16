"""
Validaciones de entrada para usuarios.
"""
from src.core.models.user import User
from src.core.services.usuario_service import user_service
from src.core.validators.api_validator import validate_positive_int
from src.web.exceptions import NotFoundError, ValidationError

from .utils import clean_string, ensure_max_length, is_strong_password, is_valid_email, require_fields


MAX_NAME = 120
MAX_MAIL = 120


def validate_create_user(data: dict) -> dict:
    """
    Valida y limpia los datos para crear un usuario.
    
    Args:
        data: Diccionario con los datos del usuario
        
    Returns:
        dict: Diccionario con los datos validados y limpiados
        
    Raises:
        ValidationError: Si faltan campos obligatorios, el email es inválido,
            la contraseña es débil, los campos exceden la longitud máxima o
            ya existe un usuario con ese email
    """
    missing = require_fields(data, ['mail', 'name', 'last_name', 'password'])
    if missing:
        raise ValidationError(f"Faltan campos obligatorios: {', '.join(missing)}")

    mail = clean_string(data.get('mail'))
    name = clean_string(data.get('name'))
    last_name = clean_string(data.get('last_name'))
    password = data.get('password') or ''

    if not is_valid_email(mail):
        raise ValidationError('Email inválido')
    if not is_strong_password(password):
        raise ValidationError('La contraseña debe tener al menos 6 caracteres y combinar letras y números')
    if not ensure_max_length(name, MAX_NAME) or not ensure_max_length(last_name, MAX_NAME):
        raise ValidationError('El nombre y apellido no deben superar 120 caracteres')
    if not ensure_max_length(mail, MAX_MAIL):
        raise ValidationError('El email no debe superar 120 caracteres')

    if user_service.user_exists_by_email(mail):
        raise ValidationError('Ya existe un usuario con ese mail')

    return {
        'mail': mail,
        'name': name,
        'last_name': last_name,
        'password': password,
    }


def validate_update_user(data: dict) -> dict:
    """
    Valida y limpia los datos para actualizar un usuario.
    
    Args:
        data: Diccionario con los campos a actualizar
        
    Returns:
        dict: Diccionario con los campos validados y limpiados
        
    Raises:
        ValidationError: Si los datos son inválidos (email inválido, contraseña débil,
            campos que exceden la longitud máxima)
    """
    cleaned = {}
    if 'mail' in data:
        mail = clean_string(data.get('mail'))
        if not is_valid_email(mail):
            raise ValidationError('Email inválido')
        if not ensure_max_length(mail, MAX_MAIL):
            raise ValidationError('El email no debe superar 120 caracteres')
        cleaned['mail'] = mail
    if 'name' in data:
        name = clean_string(data.get('name'))
        if not ensure_max_length(name, MAX_NAME):
            raise ValidationError('El nombre no debe superar 120 caracteres')
        cleaned['name'] = name
    if 'last_name' in data:
        last_name = clean_string(data.get('last_name'))
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
    if 'is_super_admin' in data:
        cleaned['is_super_admin'] = bool(data.get('is_super_admin'))
    return cleaned


def validate_role_ids(role_ids: list[int]) -> list[int]:
    """
    Valida que todos los IDs de roles existan y no estén eliminados.
    
    Args:
        role_ids: Lista de IDs de roles a validar
        
    Returns:
        list[int]: Lista de IDs validados
        
    Raises:
        ValidationError: Si los IDs no son válidos
        NotFoundError: Si algún rol no existe
    """
    if role_ids is None:
        return []
    try:
        ids = [int(r) for r in role_ids]
    except Exception:
        raise ValidationError('IDs de roles inválidos')
    missing = []
    for rid in ids:
        if not user_service.role_exists(rid):
            missing.append(rid)
    if missing:
        raise NotFoundError(f"Roles no encontrados: {missing}")
    return ids


def validate_user_exists(user_id: int) -> User:
    """
    Valida que un usuario existe y no está eliminado.
    
    Args:
        user_id: ID del usuario a validar
    
    Returns:
        User: Usuario encontrado
    
    Raises:
        ValidationError: Si el usuario no existe o está eliminado
    """
    user_id = validate_positive_int(user_id, "user_id")
    try:
        user = user_service.get_user_object(user_id)
        return user
    except NotFoundError:
        raise ValidationError("Usuario inválido")
