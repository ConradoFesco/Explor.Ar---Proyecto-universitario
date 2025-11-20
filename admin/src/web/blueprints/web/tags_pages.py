"""
Rutas Web para gestión de tags (renderizado HTML/Jinja).
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from src.web.auth.decorators import web_permission_required
from src.core.services.tag_service import tag_service

tags_web = Blueprint('tags_web', __name__)


@tags_web.route("/tags")
@web_permission_required("get_all_tags")
def lista_tags():
    """Listado de tags con filtros, orden y paginación (SSR)."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))

    # Parámetros de filtrado/orden
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')

    # Obtener datos del service
    result = tag_service.get_all_tags_paginated(
        page=page,
        per_page=per_page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        include_deleted=False,
    )

    tags = result.get('tags', [])
    p = result.get('pagination', {})
    pagination = {
        'page': p.get('current_page') or p.get('page') or page,
        'pages': p.get('total_pages') or p.get('pages') or 1,
        'per_page': p.get('per_page', per_page),
        'total': p.get('total', 0),
        'has_prev': p.get('has_prev', p.get('prev_page') is not None),
        'has_next': p.get('has_next', p.get('next_page') is not None),
        'prev_num': p.get('prev_page') or p.get('prev_num'),
        'next_num': p.get('next_page') or p.get('next_num'),
    }

    return render_template("tags/list_tags.html", tags=tags, pagination=pagination)


@tags_web.route('/tags/fragment')
@web_permission_required("get_all_tags")
def lista_tags_fragment():
    """Fragmento HTML del listado de tags para paginación/filtrado dinámico."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')

    result = tag_service.get_all_tags_paginated(
        page=page,
        per_page=per_page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        include_deleted=False,
    )

    tags = result.get('tags', [])
    p = result.get('pagination', {})
    pagination = {
        'page': p.get('current_page') or p.get('page') or page,
        'pages': p.get('total_pages') or p.get('pages') or 1,
        'per_page': p.get('per_page', per_page),
        'total': p.get('total', 0),
        'has_prev': p.get('has_prev', p.get('prev_page') is not None),
        'has_next': p.get('has_next', p.get('next_page') is not None),
        'prev_num': p.get('prev_page') or p.get('prev_num'),
        'next_num': p.get('next_page') or p.get('next_num'),
    }

    return render_template('features/tags/_list_fragment.html.jinja', tags=tags, pagination=pagination)


@tags_web.route('/tags', methods=['POST'])
@web_permission_required("create_tag")
def crear_tag_web():
    """Crea un tag a partir de datos de formulario y redirige con flash."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    payload_json = request.get_json(silent=True) or {}
    name = (request.form.get('name') or request.form.get('tagName') or payload_json.get('name') or '').strip()
    try:
        tag_service.create_tag({ 'name': name })
        flash('Tag creado correctamente', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('tags_web.lista_tags'))


@tags_web.route('/tags/<int:tag_id>/editar', methods=['POST'])
@web_permission_required("update_tag")
def editar_tag_web(tag_id: int):
    """Actualiza un tag existente con datos del formulario."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    payload_json = request.get_json(silent=True) or {}
    name = (request.form.get('name') or request.form.get('tagName') or payload_json.get('name') or '').strip()
    try:
        tag_service.update_tag(tag_id, { 'name': name })
        flash('Tag actualizado', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('tags_web.lista_tags'))


@tags_web.route('/tags/<int:tag_id>/eliminar', methods=['POST'])
@web_permission_required("delete_tag")
def eliminar_tag_web(tag_id: int):
    """Elimina un tag y redirige al listado con mensaje flash."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    try:
        tag_service.delete_tag(tag_id)
        flash('Tag eliminado', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('tags_web.lista_tags'))
