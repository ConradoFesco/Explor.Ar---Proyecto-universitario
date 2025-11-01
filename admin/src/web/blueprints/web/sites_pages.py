from flask import Blueprint, render_template, session, redirect, url_for, request, flash, Response
from src.core.services.state_service import state_service
from src.core.services.category_service import category_service
from src.core.services.HistoricSite_Service import historic_site_service

sites_web = Blueprint('sites_web', __name__)


@sites_web.route("/sitios")
def lista_sitios():
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    # Parámetros de filtrado
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    search_text = request.args.get('search')
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    city_id = request.args.get('city_id', type=int)
    province_id = request.args.get('province_id', type=int)
    state_id = request.args.get('state_id', type=int)
    visible_param = request.args.get('visible')
    visible = None
    if visible_param is not None and visible_param != '':
        visible = True if visible_param.lower() == 'true' else False

    result = historic_site_service.get_all_historic_sites(
        include_deleted=False,
        page=page,
        per_page=per_page,
        search_text=search_text,
        sort_by=sort_by,
        sort_order=sort_order,
        city_id=city_id,
        province_id=province_id,
        state_id=state_id,
        visible=visible,
    )

    sites = result.get('sites', [])
    pagination = result.get('pagination', {})
    # Cargar opciones de filtros (SSR)
    filters = historic_site_service.get_filter_options()
    def map_opts(items):
        return [{ 'value': str(it.get('id')), 'label': it.get('name') } for it in (items or [])]
    filters_options = {
        'cities': map_opts(filters.get('cities')),
        'provinces': map_opts(filters.get('provinces')),
        'states': map_opts(filters.get('states')),
        'tags': map_opts(filters.get('tags')),
    }
    return render_template("sites/lista_sitios.html", sites=sites, pagination=pagination, filters_options=filters_options)


@sites_web.route("/sitios/fragment")
def lista_sitios_fragment():
    if "user_id" not in session:
        return redirect(url_for("main.index"))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    search_text = request.args.get('search')
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    city_id = request.args.get('city_id', type=int)
    province_id = request.args.get('province_id', type=int)
    state_id = request.args.get('state_id', type=int)
    visible_param = request.args.get('visible')
    visible = None
    if visible_param is not None and visible_param != '':
        visible = True if visible_param.lower() == 'true' else False

    result = historic_site_service.get_all_historic_sites(
        include_deleted=False,
        page=page,
        per_page=per_page,
        search_text=search_text,
        sort_by=sort_by,
        sort_order=sort_order,
        city_id=city_id,
        province_id=province_id,
        state_id=state_id,
        visible=visible,
    )

    sites = result.get('sites', [])
    pagination = result.get('pagination', {})
    return render_template("features/sites/_list_fragment.html.jinja", sites=sites, pagination=pagination)


@sites_web.route("/alta-sitios")
def alta_sitios():
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    # Pasar opciones de tags para SSR en selector
    try:
        options = historic_site_service.get_filter_options()
        tags = options.get('tags', [])
    except Exception:
        tags = []
    try:
        states = state_service.get_all_states()
    except Exception:
        states = []
    try:
        categories = category_service.get_all_categories()
    except Exception:
        categories = []
    return render_template("sites/alta_sitios.html", tags_options=tags, states_options=states, categories_options=categories)


@sites_web.route("/modificar-sitios")
def modificar_sitios():
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    edit_id = request.args.get('edit', type=int)
    site = None
    if edit_id:
        try:
            site = historic_site_service.get_historic_site(edit_id)
        except Exception:
            site = None
    try:
        states = state_service.get_all_states()
    except Exception:
        states = []
    try:
        categories = category_service.get_all_categories()
    except Exception:
        categories = []
    return render_template("sites/modificar_sitios.html", site_edit=site, states_options=states, categories_options=categories)



@sites_web.route("/sitios/<int:site_id>/fragment")
def site_detail_fragment(site_id: int):
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    site = historic_site_service.get_historic_site(site_id)
    return render_template("features/sites/_detail.html.jinja", site=site)


@sites_web.route("/sitios/<int:site_id>/eliminar", methods=["POST"])
def eliminar_sitio(site_id: int):
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    data_user = session.get('user_id')
    try:
        historic_site_service.soft_delete_historic_site(site_id, data_user)
        flash('Sitio eliminado correctamente', 'success')
    except Exception as e:
        flash('Error al eliminar sitio: ' + str(e), 'error')
    return redirect(url_for('sites_web.lista_sitios'))


@sites_web.route("/sitios/<int:site_id>/tags", methods=["POST"])
def actualizar_tags_sitio(site_id: int):
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    tag_ids = []
    try:
        tag_ids = [int(t) for t in request.form.getlist('tag_ids') if t.strip()]
    except Exception:
        tag_ids = []
    data_user = session.get('user_id')
    try:
        historic_site_service.update_site_tags(site_id, tag_ids, data_user)
        flash('Tags actualizados', 'success')
    except Exception as e:
        flash('Error al actualizar tags: ' + str(e), 'error')
    return redirect(url_for('sites_web.lista_sitios'))


@sites_web.route("/sitios/<int:site_id>/tags/fragment")
def editar_tags_fragment(site_id: int):
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    site = historic_site_service.get_historic_site(site_id)
    options = historic_site_service.get_filter_options()
    tags = options.get('tags', [])
    selected_ids = [t['id'] for t in (site.get('tags') or [])]
    return render_template("features/sites/_edit_tags.html.jinja", site=site, tags=tags, selected_ids=selected_ids)


@sites_web.route('/sitios', methods=['POST'])
def crear_sitio_web():
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    data_user = session.get('user_id')
    form = request.form
    data_site = {
        'name': form.get('nombre'),
        'brief_description': form.get('descripcion_breve'),
        'complete_description': form.get('descripcion_completa') or None,
        'latitude': float(form.get('latitud')) if form.get('latitud') else None,
        'longitude': float(form.get('longitud')) if form.get('longitud') else None,
        'year_inauguration': form.get('año_inauguración') or None,
        'id_estado': int(form.get('estado')) if form.get('estado') else None,
        'id_category': int(form.get('categoria')) if form.get('categoria') else None,
        'visible': True,
        'name_city': form.get('ciudad'),
        'name_province': form.get('provincia')
    }
    try:
        historic_site_service.create_historic_site(data_site, data_user)
        flash('Sitio histórico creado', 'success')
    except Exception as e:
        flash('Error al crear sitio: ' + str(e), 'error')
    return redirect(url_for('sites_web.lista_sitios'))


@sites_web.route('/sitios/<int:site_id>/editar', methods=['POST'])
def editar_sitio_web(site_id: int):
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    data_user = session.get('user_id')
    form = request.form
    data_site = {
        'name': form.get('nombre'),
        'brief_description': form.get('descripcion_breve'),
        'complete_description': form.get('descripcion_completa') or None,
        'latitude': float(form.get('latitud')) if form.get('latitud') else None,
        'longitude': float(form.get('longitud')) if form.get('longitud') else None,
        'year_inauguration': form.get('año_inauguración') or None,
        'id_estado': int(form.get('estado')) if form.get('estado') else None,
        'id_category': int(form.get('categoria')) if form.get('categoria') else None,
        'visible': True
    }
    try:
        historic_site_service.update_historic_site(site_id, data_site, data_user)
        flash('Sitio histórico actualizado', 'success')
    except Exception as e:
        flash('Error al actualizar sitio: ' + str(e), 'error')
    return redirect(url_for('sites_web.lista_sitios'))



@sites_web.route("/sitios/export-csv", methods=["GET"])
def export_sites_csv_web():
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    try:
        search_text = request.args.get('search', None)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        city_id = request.args.get('city_id', type=int)
        province_id = request.args.get('province_id', type=int)
        state_id = request.args.get('state_id', type=int)
        visible_param = request.args.get('visible')
        visible = None
        if visible_param is not None:
            visible = visible_param.lower() == 'true'
        tag_ids = request.args.get('tag_ids', '')
        if tag_ids:
            try:
                tag_ids = [int(tid.strip()) for tid in tag_ids.split(',') if tid.strip()]
            except ValueError:
                tag_ids = []
        else:
            tag_ids = []
        date_from = request.args.get('date_from', None)
        date_to = request.args.get('date_to', None)
        if sort_by not in ['name', 'city', 'created_at']:
            sort_by = 'created_at'
        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'
        csv_content, filename = historic_site_service.export_sites_to_csv(
            search_text=search_text,
            sort_by=sort_by,
            sort_order=sort_order,
            city_id=city_id,
            province_id=province_id,
            tag_ids=tag_ids,
            state_id=state_id,
            date_from=date_from,
            date_to=date_to,
            visible=visible
        )
        response = Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
        return response
    except Exception as e:
        flash('Error al exportar CSV: ' + str(e), 'error')
        return redirect(url_for('sites_web.lista_sitios'))

