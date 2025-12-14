"""
Rutas Web para gestión de usuarios (renderizado HTML/Jinja).
Requieren permisos equivalentes a los endpoints API.
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from src.web.auth.decorators import web_permission_required
from src.core.services.usuario_service import user_service
from src.web.exceptions import ValidationError, NotFoundError

users_web = Blueprint('users_web', __name__)


@users_web.route("/users")
@web_permission_required("user_index")
def list_users_page():
    """Listado de usuarios con filtros, orden y paginación (SSR)."""
    page = request.args.get('page')
    per_page = request.args.get('per_page')

    filters = {
        "email": request.args.get('search'),
        "activo": request.args.get('activo'),
        "blocked": request.args.get('blocked'),
        "rol": request.args.get('rol')
    }
    filters = {k: v for k, v in filters.items() if v}

    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')

    try:
        result = user_service.list_users(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except ValidationError as e:
        flash(f'Parámetros inválidos en el listado de usuarios: {str(e)}', 'error')
        result = user_service.list_users(
            filters={},
            page=None,
            per_page=None,
            sort_by=None,
            sort_order=None,
        )
    try:
        roles_all = user_service.get_available_roles()
        role_options = [{'value': r.get('name'), 'label': r.get('name').capitalize()} for r in roles_all]
    except Exception:
        role_options = []
    return render_template(
        'users/list_users.html',
        users=result.get('users', []),
        pagination={
            'page': result.get('page', page),
            'per_page': result.get('per_page', per_page),
            'total': result.get('total', 0),
            'pages': result.get('pages', 1),
            'has_prev': result.get('has_prev', False),
            'has_next': result.get('has_next', False),
            'prev_num': result.get('prev_num'),
            'next_num': result.get('next_num'),
        },
        role_options=role_options
    )


@users_web.route('/users/fragment')
@web_permission_required("user_index")
def list_users_fragment():
    """
    Endpoint exclusivo para peticiones asíncronas (AJAX/Fetch).
    
    RAZÓN DE IMPLEMENTACIÓN:
    Permite actualizar la tabla de usuarios (filtrado, ordenamiento y paginación)
    sin necesidad de recargar la página completa (layout, menús, scripts).
    Retorna solo el HTML parcial (_list_fragment) para ser inyectado en el DOM.
    """
    page = request.args.get('page')
    per_page = request.args.get('per_page')

    filters = {
        "email": request.args.get('search'),
        "activo": request.args.get('activo'),
        "rol": request.args.get('rol')
    }
    filters = {k: v for k, v in filters.items() if v}

    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')

    try:
        result = user_service.list_users(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except ValidationError as e:
        flash(f'Parámetros inválidos en el listado de usuarios: {str(e)}', 'error')
        result = user_service.list_users(
            filters={},
            page=1,
            per_page=25,
            sort_by='created_at',
            sort_order='desc',
        )
    return render_template(
        'features/users/_list_fragment.html.jinja',
        users=result.get('users', []),
        pagination={
            'page': result.get('page', page),
            'per_page': result.get('per_page', per_page),
            'total': result.get('total', 0),
            'pages': result.get('pages', 1),
            'has_prev': result.get('has_prev', False),
            'has_next': result.get('has_next', False),
            'prev_num': result.get('prev_num'),
            'next_num': result.get('next_num'),
        }
    )


@users_web.route("/users/<int:user_id>/editar")
@web_permission_required("user_update")
def edit_user_page(user_id: int):
    """Página de edición de usuario con SSR de datos y roles disponibles."""
    try:
        user = user_service.get_user(user_id)
    except NotFoundError:
        flash("Usuario no encontrado", "error")
        return redirect(url_for('users_web.list_users_page'))

    try:
        available_roles = user_service.get_available_roles()
    except Exception:
        available_roles = []
    return render_template('users/edit_user.html', user=user, user_id=user_id, available_roles=available_roles)


@users_web.route('/users/nuevo')
@web_permission_required("user_new")
def create_user_form_page():
    """Formulario de creación de usuario (SSR de roles disponibles)."""
    try:
        available_roles = user_service.get_available_roles()
    except Exception:
        available_roles = []

    return render_template('users/create_user.html', available_roles=available_roles)


@users_web.route('/users', methods=['POST'])
@web_permission_required("user_new")
def create_user_web():
    """Procesa el alta de usuario y redirige con mensajes flash."""
    admin_id = session.get('user_id')
    form = request.form
    name = (form.get('name') or '').strip()
    last_name = (form.get('last_name') or '').strip()
    mail = (form.get('mail') or '').strip()
    password = form.get('password') or ''
    roles_raw = form.getlist('roles')
    try:
        role_ids = [int(r) for r in roles_raw if r.strip()]
    except Exception:
        role_ids = []
    active = bool(form.get('active'))
    blocked = bool(form.get('blocked'))
    data_new_user = { 'name': name, 'last_name': last_name, 'mail': mail, 'password': password, 'roles': role_ids, 'active': active, 'blocked': blocked }
    try:
        user_service.create_user(data_user=admin_id, data_new_user=data_new_user)
        flash('Usuario creado correctamente', 'success')
        return redirect(url_for('users_web.list_users_page'))
    except ValidationError as ve:
        flash(str(ve), 'error')
    except Exception as e:
        flash('Error al crear el usuario: ' + str(e), 'error')
    return redirect(url_for('users_web.create_user_form_page'))


@users_web.post('/users/<int:user_id>/eliminar')
@web_permission_required("user_destroy")
def delete_user_page(user_id: int):
    """Elimina lógicamente un usuario (solo con permiso)."""
    admin_id = session.get("user_id")
    try:
        user_service.delete_user(user_id=user_id, admin_user_id=admin_id)
        flash("Usuario eliminado correctamente", "success")
    except ValidationError as ve:
        flash(str(ve), "error")
    except Exception as e:
        flash("Error al eliminar usuario: " + str(e), "error")
    return redirect(url_for('users_web.list_users_page'))


@users_web.post('/users/<int:user_id>/editar')
@web_permission_required("user_update")
def update_user_page(user_id: int):
    """Actualiza datos y roles de un usuario y redirige con flash."""
    admin_id = session.get('user_id')
    form = request.form
    name = (form.get('name') or '').strip()
    last_name = (form.get('last_name') or '').strip()
    mail = (form.get('mail') or '').strip()
    active = bool(form.get('active'))
    blocked = bool(form.get('blocked'))
    roles_raw = form.getlist('roles')
    try:
        role_ids = [int(r) for r in roles_raw if r.strip()]
    except Exception:
        role_ids = []
    changed_fields = { 'name': name, 'last_name': last_name, 'mail': mail, 'active': active, 'blocked': blocked }
    try:
        user_service.update_user(user_id, changed_fields, admin_user_id=admin_id)
        user_service.update_user_roles(user_id, role_ids, admin_user_id=admin_id)
        flash('Usuario actualizado correctamente', 'success')
    except ValidationError as ve:
        flash(str(ve), 'error')
    except Exception as e:
        flash('Error al actualizar usuario: ' + str(e), 'error')
    return redirect(url_for('users_web.list_users_page'))

