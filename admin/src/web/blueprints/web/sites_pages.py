from flask import Blueprint, render_template, session, redirect, url_for, request, flash, Response, jsonify
from src.web.auth.decorators import web_permission_required
from src.core.services.state_service import state_service
from src.core.services.category_service import category_service
from src.core.services.historic_site_service import historic_site_service
from src.core.services.site_image_service import site_image_service
from src.core.validators.listing_validator import validate_site_list_params
from src.web import exceptions as exc

sites_web = Blueprint('sites_web', __name__)


def _resolve_site_list_params():
    raw_args = {
        'page': request.args.get('page', 1, type=int),
        'per_page': request.args.get('per_page', 25, type=int),
        'search_text': request.args.get('search'),
        'sort_by': request.args.get('sort_by', 'created_at'),
        'sort_order': request.args.get('sort_order', 'desc'),
        'city_id': request.args.get('city_id', type=int),
        'province_id': request.args.get('province_id', type=int),
        'tag_ids': request.args.get('tag_ids'),
        'state_id': request.args.get('state_id', type=int),
        'date_from': request.args.get('date_from'),
        'date_to': request.args.get('date_to'),
        'visible': request.args.get('visible')
    }
    try:
        return validate_site_list_params(**raw_args)
    except exc.ValidationError as error:
        flash('Parámetros inválidos en el listado: ' + str(error), 'error')
        return validate_site_list_params(
            page=1,
            per_page=25,
            search_text=None,
            sort_by='created_at',
            sort_order='desc',
            city_id=None,
            province_id=None,
            tag_ids=[],
            state_id=None,
            date_from=None,
            date_to=None,
            visible=None,
        )


@sites_web.route("/sitios")
@web_permission_required("get_all_historic_sites")
def lista_sitios():
    """Listado SSR de sitios con filtros, orden y paginación."""
    params = _resolve_site_list_params()

    result = historic_site_service.get_all_historic_sites(
        include_deleted=False,
        page=params['page'],
        per_page=params['per_page'],
        search_text=params['search_text'],
        sort_by=params['sort_by'],
        sort_order=params['sort_order'],
        city_id=params['city_id'],
        province_id=params['province_id'],
        tag_ids=params['tag_ids'],
        state_id=params['state_id'],
        date_from=params['date_from'],
        date_to=params['date_to'],
        visible=params['visible'],
    )

    sites = result.get('sites', [])
    pagination = result.get('pagination', {})
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
@web_permission_required("get_all_historic_sites")
def lista_sitios_fragment():
    """Fragmento HTML para refrescar el listado de sitios (paginación/orden)."""
    params = _resolve_site_list_params()

    result = historic_site_service.get_all_historic_sites(
        include_deleted=False,
        page=params['page'],
        per_page=params['per_page'],
        search_text=params['search_text'],
        sort_by=params['sort_by'],
        sort_order=params['sort_order'],
        city_id=params['city_id'],
        province_id=params['province_id'],
        tag_ids=params['tag_ids'],
        state_id=params['state_id'],
        date_from=params['date_from'],
        date_to=params['date_to'],
        visible=params['visible'],
    )

    sites = result.get('sites', [])
    pagination = result.get('pagination', {})
    return render_template("features/sites/_list_fragment.html.jinja", sites=sites, pagination=pagination)


@sites_web.route("/alta-sitios")
@web_permission_required("create_historic_site")
def alta_sitios():
    """Formulario SSR de alta de sitio (carga de opciones desde servicios)."""
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
@web_permission_required("update_historic_site")
def modificar_sitios():
    """Formulario SSR de edición de sitio (incluye opciones y datos del sitio)."""
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
@web_permission_required("get_historic_site")
def site_detail_fragment(site_id: int):
    """Fragmento HTML con detalle de sitio para uso en modales o vistas parciales."""
    site = historic_site_service.get_historic_site(site_id)
    return render_template("features/sites/_detail.html.jinja", site=site)


@sites_web.route("/sitios/<int:site_id>/eliminar", methods=["POST"])
@web_permission_required("delete_historic_site")
def eliminar_sitio(site_id: int):
    """Elimina lógicamente un sitio histórico (solo con permisos)."""
    data_user = session.get('user_id')
    try:
        historic_site_service.soft_delete_historic_site(site_id, data_user)
        flash('Sitio eliminado correctamente', 'success')
    except Exception as e:
        flash('Error al eliminar sitio: ' + str(e), 'error')
    return redirect(url_for('sites_web.lista_sitios'))


@sites_web.route("/sitios/<int:site_id>/tags", methods=["POST"])
@web_permission_required("update_tags")
def actualizar_tags_sitio(site_id: int):
    """Actualiza las etiquetas asociadas a un sitio histórico."""
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
@web_permission_required("update_tags")
def editar_tags_fragment(site_id: int):
    """Fragmento HTML para selección/edición de tags de un sitio."""
    site = historic_site_service.get_historic_site(site_id)
    options = historic_site_service.get_filter_options()
    tags = options.get('tags', [])
    selected_ids = [t['id'] for t in (site.get('tags') or [])]
    return render_template("features/sites/_edit_tags.html.jinja", site=site, tags=tags, selected_ids=selected_ids)


@sites_web.route('/sitios', methods=['POST'])
@web_permission_required("create_historic_site")
def crear_sitio_web():
    """Procesa la creación de un sitio a partir de datos de formulario."""
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
        tag_ids = []
        try:
            tag_ids = [int(t) for t in form.getlist('tag_ids') if t.strip()]
        except Exception:
            tag_ids = []
        data_site['tag_ids'] = tag_ids
        
        created_site = historic_site_service.create_historic_site(data_site, data_user)
        
        flash('Sitio histórico creado correctamente. Ahora puede agregar imágenes.', 'success')
        return redirect(url_for('sites_web.modificar_sitios', edit=created_site.id))
    except exc.ValidationError as e:
        flash('Error al crear sitio: ' + str(e), 'error')
        return redirect(url_for('sites_web.alta_sitios'))
    except Exception as e:
        flash('Error al crear sitio: ' + str(e), 'error')
        return redirect(url_for('sites_web.alta_sitios'))


@sites_web.route('/sitios/<int:site_id>/editar', methods=['POST'])
@web_permission_required("update_historic_site")
def editar_sitio_web(site_id: int):
    """Procesa la actualización de un sitio histórico y redirige al listado."""
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
@web_permission_required("export_historic_sites")
def export_sites_csv_web():
    """Genera un CSV con sitios históricos respetando filtros actuales."""
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


@sites_web.route("/sitios/<int:site_id>/imagenes", methods=["GET"])
@web_permission_required("get_historic_site")
def obtener_imagenes_sitio(site_id: int):
    """Devuelve las imágenes de un sitio en formato JSON para el gestor de imágenes del panel."""
    try:
        images = site_image_service.get_images_by_site(site_id)
        return jsonify({'success': True, 'images': images}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error al cargar imágenes: {str(e)}'}), 500


@sites_web.route("/sitios/<int:site_id>/imagenes", methods=["POST"])
@web_permission_required("update_historic_site")
def subir_imagen_sitio(site_id: int):
    """Sube una o varias imágenes para un sitio histórico."""
    data_user = session.get('user_id')
    
    if 'imagenes' in request.files:
        files = request.files.getlist('imagenes')
        if not files or not any(f.filename for f in files):
            return jsonify({'success': False, 'error': 'No se proporcionaron archivos'}), 400
        
        titulos = request.form.getlist('titulo_alt[]')
        descripciones = request.form.getlist('descripcion[]')
        cover_index = request.form.get('cover_index', type=int)
        
        files_data = []
        for idx, file in enumerate(files):
            if file and file.filename:
                if idx < len(titulos) and titulos[idx]:
                    titulo_alt = str(titulos[idx]).strip() if titulos[idx] else file.filename
                else:
                    titulo_alt = file.filename
                
                if idx < len(descripciones) and descripciones[idx]:
                    descripcion = str(descripciones[idx]).strip() or None
                else:
                    descripcion = None
                
                if not titulo_alt:
                    return jsonify({'success': False, 'error': f'El título/alt es obligatorio para la imagen {idx + 1}'}), 400
                
                is_cover = (cover_index is not None and idx == cover_index)
                
                files_data.append({
                    'file': file,
                    'titulo_alt': titulo_alt,
                    'descripcion': descripcion,
                    'is_cover': is_cover
                })
        
        if not files_data:
            return jsonify({'success': False, 'error': 'No se proporcionaron archivos válidos'}), 400
        
        try:
            images = site_image_service.upload_multiple_images(site_id, files_data, data_user)
            return jsonify({
                'success': True,
                'images': [img.to_dict() for img in images],
                'message': f'Se subieron {len(images)} imagen(es) correctamente'
            }), 200
        except exc.ValidationError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except exc.NotFoundError as e:
            return jsonify({'success': False, 'error': str(e)}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': f'Error al subir imágenes: {str(e)}'}), 500
    
    if 'imagen' not in request.files:
        return jsonify({'success': False, 'error': 'No se proporcionó ningún archivo'}), 400
    
    file = request.files['imagen']
    titulo_alt = request.form.get('titulo_alt', '').strip()
    descripcion = request.form.get('descripcion', '').strip() or None
    
    if not titulo_alt:
        return jsonify({'success': False, 'error': 'El título/alt es obligatorio'}), 400
    
    try:
        image = site_image_service.upload_image(
            site_id=site_id,
            file=file,
            titulo_alt=titulo_alt,
            descripcion=descripcion,
            user_id=data_user
        )
        return jsonify({'success': True, 'image': image.to_dict(), 'message': 'Imagen subida correctamente'}), 200
    except exc.ValidationError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except exc.NotFoundError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error al subir imagen: {str(e)}'}), 500


@sites_web.route("/sitios/<int:site_id>/imagenes/<int:image_id>", methods=["DELETE"])
@web_permission_required("update_historic_site")
def eliminar_imagen_sitio(site_id: int, image_id: int):
    """Elimina una imagen de un sitio. Responde JSON para el gestor de imágenes."""
    data_user = session.get('user_id')
    
    try:
        site_image_service.delete_image(image_id, user_id=data_user)
        return jsonify({'success': True}), 200
    except exc.ValidationError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except exc.NotFoundError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error al eliminar imagen: {str(e)}'}), 500


@sites_web.route("/sitios/<int:site_id>/imagenes/<int:image_id>/portada", methods=["POST"])
@web_permission_required("update_historic_site")
def marcar_portada_imagen(site_id: int, image_id: int):
    """Marca una imagen como portada. Responde JSON para el gestor de imágenes."""
    data_user = session.get('user_id')
    
    try:
        image = site_image_service.set_cover_image(image_id, user_id=data_user)
        return jsonify({'success': True, 'image': image.to_dict()}), 200
    except exc.NotFoundError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error al marcar portada: {str(e)}'}), 500


@sites_web.route("/sitios/<int:site_id>/imagenes/reordenar", methods=["POST"])
@web_permission_required("update_historic_site")
def reordenar_imagenes_sitio(site_id: int):
    """Reordena imágenes de un sitio."""
    data_user = session.get('user_id')
    
    try:
        image_orders = []
        
        if request.is_json:
            data = request.get_json()
            image_orders = data.get('orders', [])
        else:
            for key in request.form.keys():
                if key.startswith('orden_'):
                    image_id = int(key.replace('orden_', ''))
                    nuevo_orden = int(request.form.get(key))
                    image_orders.append({'id': image_id, 'orden': nuevo_orden})
        
        if not image_orders:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'No se proporcionaron órdenes'}), 400
            flash('No se proporcionaron órdenes', 'error')
            return redirect(url_for('sites_web.modificar_sitios', edit=site_id))
        
        site_image_service.reorder_images(site_id, image_orders, user_id=data_user)

        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Imágenes reordenadas correctamente'}), 200
        flash('Imágenes reordenadas correctamente', 'success')
    except exc.NotFoundError as e:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 404
        flash('Error: ' + str(e), 'error')
    except Exception as e:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': f'Error al reordenar imágenes: {str(e)}'}), 500
        flash('Error al reordenar imágenes: ' + str(e), 'error')
    return redirect(url_for('sites_web.modificar_sitios', edit=site_id))


@sites_web.route("/sitios/<int:site_id>/imagenes/<int:image_id>/actualizar", methods=["POST"])
@web_permission_required("update_historic_site")
def actualizar_metadatos_imagen(site_id: int, image_id: int):
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    
    data_user = session.get('user_id')
    
    try:
        titulo_alt = request.form.get('titulo_alt', '').strip() or None
        descripcion = request.form.get('descripcion', '').strip() or None
        
        image = site_image_service.update_image_metadata(
            image_id,
            titulo_alt=titulo_alt,
            descripcion=descripcion,
            user_id=data_user
        )
        flash('Metadatos actualizados correctamente', 'success')
    except exc.ValidationError as e:
        flash('Error: ' + str(e), 'error')
    except exc.NotFoundError as e:
        flash('Error: ' + str(e), 'error')
    except Exception as e:
        flash('Error al actualizar metadatos: ' + str(e), 'error')
    
    return redirect(url_for('sites_web.modificar_sitios', edit=site_id))
