"""
Rutas Web para gestión de usuarios (renderizado HTML/Jinja).
Requieren permisos equivalentes a los endpoints API.
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from src.web.auth.decorators import web_permission_required
from src.core.services.usuario_service import user_service
from src.web.exceptions import ValidationError

users_web = Blueprint('users_web', __name__)


@users_web.route("/users")
@web_permission_required("get_all_users")
def list_users_page():
    """Listado de usuarios con filtros, orden y paginación (SSR)."""

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)

    filters = {
        "email": request.args.get('search'),
        "activo": request.args.get('activo'),
        "blocked": request.args.get('blocked'),
        "rol": request.args.get('rol')
    }
    filters = {k: v for k, v in filters.items() if v}

    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    result = user_service.list_users(
        filters=filters,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    try:
        admin_summary = user_service.get_user(session.get('user_id'))
        current_is_super_admin = bool(admin_summary.get('is_super_admin'))
    except Exception:
        current_is_super_admin = False
    # Opciones de roles dinámicas para el filtro (respeta módulo de roles)
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
        current_is_super_admin=current_is_super_admin,
        role_options=role_options
    )


@users_web.route('/users/fragment')
@web_permission_required("get_all_users")
def list_users_fragment():
    """Fragmento HTML del listado de usuarios para paginar/filtrar vía fetch HTML."""

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)

    filters = {
        "email": request.args.get('search'),
        "activo": request.args.get('activo'),
        "rol": request.args.get('rol')
    }
    filters = {k: v for k, v in filters.items() if v}

    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    result = user_service.list_users(
        filters=filters,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    try:
        admin_summary = user_service.get_user(session.get('user_id'))
        current_is_super_admin = bool(admin_summary.get('is_super_admin'))
    except Exception:
        current_is_super_admin = False
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
        },
        current_is_super_admin=current_is_super_admin
    )


@users_web.route("/users/<int:user_id>/editar")
@web_permission_required("get_user")
def edit_user_page(user_id: int):
    """Página de edición de usuario con SSR de datos y roles disponibles."""

    user = user_service.get_user(user_id)
    try:
        available_roles = user_service.get_available_roles()
    except Exception:
        available_roles = []

    return render_template('users/edit_user.html', user=user, user_id=user_id, available_roles=available_roles)


@users_web.route('/users/nuevo')
@web_permission_required("create_user")
def create_user_form_page():
    """Formulario de creación de usuario (SSR de roles disponibles)."""

    try:
        available_roles = user_service.get_available_roles()
    except Exception:
        available_roles = []

    return render_template('users/create_user.html', available_roles=available_roles)


@users_web.route('/users', methods=['POST'])
@web_permission_required("create_user")
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
@web_permission_required("delete_user")
def delete_user_page(user_id: int):
    """Elimina lógicamente un usuario con motivo (solo con permiso)."""

    admin_id = session.get("user_id")
    reason = request.form.get("reason", "")
    try:
        user_service.delete_user_with_reason(user_id=user_id, reason=reason, admin_user_data=admin_id)
        msg = "Usuario eliminado correctamente"
        if (reason or '').strip():
            msg += f". Motivo: {reason.strip()}"
        flash(msg, "success")
    except ValidationError as ve:
        flash(str(ve), "error")
    except Exception as e:
        flash("Error al eliminar usuario: " + str(e), "error")
    return redirect(url_for('users_web.list_users_page'))


@users_web.post('/users/<int:user_id>/editar')
@web_permission_required("update_user")
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

