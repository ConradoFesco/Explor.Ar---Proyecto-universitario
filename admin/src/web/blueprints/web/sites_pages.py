from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
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
    return render_template("sites/lista_sitios.html", sites=sites, pagination=pagination)


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
    return render_template("sites/alta_sitios.html")


@sites_web.route("/modificar-sitios")
def modificar_sitios():
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    return render_template("sites/modificar_sitios.html")



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
    historic_site_service.soft_delete_historic_site(site_id, data_user)
    # Responder JSON para que el front refresque el listado
    return jsonify({"status": "ok"})


@sites_web.route("/sitios/<int:site_id>/tags", methods=["POST"])
def actualizar_tags_sitio(site_id: int):
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    data = request.get_json() or {}
    tag_ids = data.get('tag_ids', [])
    data_user = session.get('user_id')
    result = historic_site_service.update_site_tags(site_id, tag_ids, data_user)
    return jsonify({"status": "ok", "final_tags": result.get('final_tags', [])})


@sites_web.route("/sitios/<int:site_id>/tags/fragment")
def editar_tags_fragment(site_id: int):
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    site = historic_site_service.get_historic_site(site_id)
    options = historic_site_service.get_filter_options()
    tags = options.get('tags', [])
    selected_ids = [t['id'] for t in (site.get('tags') or [])]
    return render_template("features/sites/_edit_tags.html.jinja", site=site, tags=tags, selected_ids=selected_ids)



