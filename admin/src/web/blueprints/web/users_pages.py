from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from src.core.services.usuario_service import user_service
from src.web.exceptions import ValidationError

users_web = Blueprint('users_web', __name__)


@users_web.route("/users")
def list_users_page():
    if "user_id" not in session:
        return redirect(url_for("main.index"))

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
        }
    )


@users_web.route('/users/fragment')
def list_users_fragment():
    if "user_id" not in session:
        return redirect(url_for("main.index"))

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
def edit_user_page(user_id: int):
    if "user_id" not in session:
        return redirect(url_for("main.index"))

    user = user_service.get_user(user_id)
    try:
        available_roles = user_service.get_available_roles()
    except Exception:
        available_roles = []

    return render_template('users/edit_user.html', user=user, user_id=user_id, available_roles=available_roles)


@users_web.route('/users/nuevo')
def create_user_form_page():
    if "user_id" not in session:
        return redirect(url_for("main.index"))

    try:
        available_roles = user_service.get_available_roles()
    except Exception:
        available_roles = []

    return render_template('users/create_user.html', available_roles=available_roles)


@users_web.post('/users/<int:user_id>/eliminar')
def delete_user_page(user_id: int):
    if "user_id" not in session:
        return redirect(url_for("main.index"))

    admin_id = session.get("user_id")
    reason = request.form.get("reason", "")
    try:
        user_service.delete_user_with_reason(user_id=user_id, reason=reason, admin_user_data=admin_id)
        flash("Usuario eliminado correctamente", "success")
    except ValidationError as ve:
        flash(str(ve), "error")
    except Exception as e:
        flash("Error al eliminar usuario: " + str(e), "error")
    return redirect(url_for('users_web.list_users_page'))

