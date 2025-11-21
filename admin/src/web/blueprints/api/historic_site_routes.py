from flask import Blueprint, request, jsonify, Response, current_app
from src.core.services.historic_site_service import historic_site_service
from src.core.services.favorite_service import favorite_service
from src.web import exceptions as exc
from src.web.auth.decorators import permission_required, token_or_session_required, get_current_user_id
from src.core.validators.listing_validator import validate_public_site_search_params

site_api = Blueprint('site_api', __name__)


def _json_response(payload, status_code=200):
    response = jsonify(payload)
    response.status_code = status_code
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response


@site_api.route('/sites', methods=['GET'])
def list_public_historic_sites():
    """Endpoint público para listar sitios históricos."""
    raw_params = {
        'name': request.args.get('name'),
        'description': request.args.get('description'),
        'city': request.args.get('city'),
        'province': request.args.get('province'),
        'tags': request.args.get('tags'),
        'order_by': request.args.get('order_by'),
        'latitude': request.args.get('lat'),
        'longitude': request.args.get('long'),
        'radius': request.args.get('radius'),
        'page': request.args.get('page', default=1, type=int),
        'per_page': request.args.get('per_page', default=20, type=int),
        'favorites_only': request.args.get('fav') == '1'
    }

    try:
        params = validate_public_site_search_params(**raw_params)
    except exc.ValidationError as error:
        return _json_response({'error': str(error)}, 400)

    # Obtener user_id si está autenticado (opcional, no requiere autenticación)
    user_id = get_current_user_id()
    params['user_id'] = user_id

    try:
        result = historic_site_service.search_public_sites(**params)
        return _json_response(result, 200)
    except exc.DatabaseError as error:
        return _json_response({'error': str(error)}, 500)
    except Exception as error:
        current_app.logger.exception("Error al listar sitios públicos", exc_info=error)
        return _json_response({'error': 'Error interno al listar sitios'}, 500)

@site_api.route('/sites/filter-options', methods=['GET'])
def get_public_filter_options():
    """Endpoint público para obtener opciones de filtros (ciudades, provincias, tags)."""
    try:
        result = historic_site_service.get_filter_options()
        return _json_response(result, 200)
    except exc.DatabaseError as error:
        return _json_response({'error': str(error)}, 500)
    except Exception as error:
        current_app.logger.exception("Error al obtener opciones de filtro", exc_info=error)
        return _json_response({'error': 'Error interno al obtener opciones'}, 500)

@site_api.route('/sites', methods=['POST'])
@token_or_session_required
@permission_required("create_historic_site")
def create_historic_site():
    # 1. El controlador recibe el JSON y lo convierte a diccionario
    # si no se reciben datos, devuelve un error 400
    data_site = request.get_json(silent=True)
    if not data_site:
        return _json_response({'error': 'No se recibieron datos'}, 400)
    data_user = get_current_user_id()
    if not data_user:
        return _json_response({'error': 'Usuario no autenticado'}, 401)
    
    # si se reciben datos, llama al servicio para que haga el trabajo pesado
    try:
        # 2. Llama al servicio para que haga el trabajo pesado
        new_site = historic_site_service.create_historic_site(data_site, data_user)
        # 3. Si todo sale bien, devuelve el nuevo objeto y un código 201 (Created)
        return _json_response(new_site.to_dict(), 201)
    except exc.ValidationError as e:
        # si el servicio lanzó un error de validación, lo captura y lo devuelve
        return _json_response({'error': str(e)}, 400) # 400 = Bad Request
    except exc.DatabaseError as e:
        # si el servicio lanzó un error de base de datos, lo captura y lo devuelve
        return _json_response({'error': str(e)}, 500) # DB errors -> 500 segun estándar
    except Exception as error:
        current_app.logger.exception("Error inesperado al crear sitio histórico", exc_info=error)
        return _json_response({'error': 'Error interno al crear sitio'}, 500)

@site_api.route('/sites/<int:site_id>', methods=['GET'])
def get_public_historic_site(site_id):
    # si se recibe el ID, llama al servicio para que haga el trabajo pesado
    try:
        # Obtener user_id si está autenticado (opcional, no requiere autenticación)
        user_id = get_current_user_id()
        # si todo sale bien, devuelve el objeto y un código 200
        site_data = historic_site_service.get_historic_site(site_id, user_id=user_id)
        return _json_response(site_data, 200)
    except exc.NotFoundError as e:
        # si el servicio lanzó un error de validación, lo captura y lo devuelve
        return _json_response({'error': str(e)}, 404) # 404 = Not Found
    except Exception as error:
        current_app.logger.exception("Error al obtener sitio histórico", exc_info=error)
        return _json_response({'error': 'Error interno al obtener sitio'}, 500)

@site_api.route('/HistoricSite_Routes/map', methods=['GET'])
@token_or_session_required
@permission_required("get_all_sites_for_map")
def get_all_sites_for_map():
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    # Validar parámetros
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 25:  # Límite máximo de 25 por página
        per_page = 25
    try:
        result = historic_site_service.get_all_sites_for_map(
            include_deleted=include_deleted, 
            page=page, 
            per_page=per_page
        )
        # si todo sale bien, devuelve el objeto y un código 200
        return jsonify(result), 200
    except exc.NotFoundError as e:
        # si el servicio lanzó un error de validación, lo captura y lo devuelve
        return jsonify({'error': str(e)}), 404 # 404 = Not Found

    
@site_api.route('/HistoricSite_Routes/<int:id>', methods=['PUT'])
@token_or_session_required
@permission_required("update_historic_site")
def update_historic_site(id):
    data_site = request.get_json()
    if not data_site:
        return jsonify({'error': 'No se recibieron datos'}), 400
    
    data_user = get_current_user_id()
    if not data_site or not data_user:
        return jsonify({'error': 'Faltan datos de sitio histórico o usuario'}), 400
    
    try:
        # si todo sale bien, actualiza el sitio histórico
        site = historic_site_service.update_historic_site(id, data_site, data_user)
        return jsonify(site.to_dict()), 200
    except exc.NotFoundError as e:
        # si el servicio lanzó un error de validación, lo captura y lo devuelve
        return jsonify({'error': str(e)}), 404 # 404 = Not Found
    except exc.DatabaseError as e:
        # si el servicio lanzó un error de base de datos, lo captura y lo devuelve
        return jsonify({'error': str(e)}), 409 # 409 = Conflict en la data base


@site_api.route('/HistoricSite_Routes/<int:id>', methods=['DELETE'])
@token_or_session_required
@permission_required("delete_historic_site")
def delete_historic_site(id):
    data_user = get_current_user_id()
    
    try:
        # 1. Llama al servicio para que haga el trabajo
        historic_site_service.soft_delete_historic_site(id, data_user)
        # 2. Si todo sale bien, devuelve un mensaje de éxito y un código 200 (OK)
        return jsonify({'message': f'El sitio histórico con id {id} ha sido eliminado.'}), 200
    except exc.NotFoundError as e:
        # 3. Si el servicio no encontró el sitio, devuelve el error 404
        return jsonify({'error': str(e)}), 404
    except exc.DatabaseError as e:
        # 4. Si el servicio lanzó un error de base de datos, lo captura y lo devuelve
        return jsonify({'error': str(e)}), 409 # 409 = Conflict en la data base


@site_api.route('/HistoricSite_Routes/<int:site_id>/tags', methods=['POST'])
@token_or_session_required
@permission_required("add_tags")
def add_tags(site_id):
    data = request.get_json()
    data_user = get_current_user_id()
    
    if not data or not data_user:
        return jsonify({'error': 'Faltan datos de tags o usuario'}), 400
    
    # Extraer la lista de tag IDs del JSON
    tag_ids = data.get('tag_ids', [])
    
    if not tag_ids:
        return jsonify({'error': 'No se proporcionaron IDs de tags'}), 400
    
    try:
        result = historic_site_service.add_tags(site_id, tag_ids, data_user)
        return jsonify({
            'site': result['site'].to_dict(),
            'added_tags': result['added_tags'],
            'skipped_tags': result['skipped_tags'],
            'message': result['message']
        }), 200
    except exc.NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except exc.ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except exc.DatabaseError as e:
        return jsonify({'error': str(e)}), 409

@site_api.route('/HistoricSite_Routes/<int:site_id>/tags', methods=['PUT'])
@token_or_session_required
@permission_required("update_tags")
def update_site_tags(site_id):
    """Endpoint para actualizar completamente los tags de un sitio (agregar y quitar)"""
    data = request.get_json()
    data_user = get_current_user_id()
    if not data_user:
        return jsonify({'error': 'Usuario no autenticado'}), 400
    
    # Extraer la lista de tag IDs del JSON
    tag_ids = data.get('tag_ids', [])
    
    # tag_ids puede estar vacío para quitar todos los tags
    if not isinstance(tag_ids, list):
        return jsonify({'error': 'Los tags deben enviarse como una lista'}), 400
    
    try:
        result = historic_site_service.update_site_tags(site_id, tag_ids, data_user)
        return jsonify({
            'site': result['site'].to_dict(),
            'added_tags': result['added_tags'],
            'removed_tags': result['removed_tags'],
            'final_tags': result['final_tags'],
            'message': result['message']
        }), 200
    except exc.NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except exc.ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except exc.DatabaseError as e:
        return jsonify({'error': str(e)}), 409

@site_api.route('/HistoricSite_Routes/filter-options', methods=['GET'])
@token_or_session_required
@permission_required("get_filter_options")
def get_filter_options():
    """Endpoint para obtener las opciones de filtros disponibles"""
    try:
        result = historic_site_service.get_filter_options()
        return jsonify(result), 200
    except exc.DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@site_api.route('/HistoricSite_Routes/export-csv', methods=['GET'])
@token_or_session_required
@permission_required("export_historic_sites")
def export_sites_csv():
    """Endpoint para exportar sitios históricos a CSV"""
    try:
        # Obtener los mismos parámetros de filtro que usa get_all_historic_sites
        search_text = request.args.get('search', None)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Filtros
        city_id = request.args.get('city_id', type=int)
        province_id = request.args.get('province_id', type=int)
        state_id = request.args.get('state_id', type=int)
        visible_param = request.args.get('visible')
        visible = None
        if visible_param is not None:
            visible = visible_param.lower() == 'true'
        
        # Filtro de tags (puede venir como lista separada por comas)
        tag_ids = request.args.get('tag_ids', '')
        if tag_ids:
            try:
                tag_ids = [int(tid.strip()) for tid in tag_ids.split(',') if tid.strip()]
            except ValueError:
                tag_ids = []
        else:
            tag_ids = []
        
        # Filtro de fechas
        date_from = request.args.get('date_from', None)
        date_to = request.args.get('date_to', None)
        
        # Validar sort_by
        valid_sort_fields = ['name', 'city', 'created_at']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        # Validar sort_order
        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'
        
        # Llamar al servicio para generar el CSV
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
        
        # Crear respuesta con el archivo CSV
        response = Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
        
        return response
        
    except exc.NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except exc.DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Error inesperado al exportar: ' + str(e)}), 500


@site_api.route('/sites/<int:site_id>/favorite', methods=['PUT'])
@token_or_session_required
def mark_favorite(site_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return _json_response({'error': 'Usuario no autenticado'}, 401)
    try:
        favorite_service.mark_favorite(site_id=site_id, user_id=user_id)
        return '', 204
    except exc.NotFoundError as error:
        return _json_response({'error': str(error)}, 404)
    except exc.ValidationError as error:
        return _json_response({'error': str(error)}, 400)
    except exc.DatabaseError as error:
        return _json_response({'error': str(error)}, 500)
    except Exception as error:
        current_app.logger.exception("Error al marcar favorito", exc_info=error)
        return _json_response({'error': 'Error interno al marcar favorito'}, 500)


@site_api.route('/sites/<int:site_id>/favorite', methods=['DELETE'])
@token_or_session_required
def unmark_favorite(site_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return _json_response({'error': 'Usuario no autenticado'}, 401)
    try:
        favorite_service.unmark_favorite(site_id=site_id, user_id=user_id)
        return '', 204
    except exc.NotFoundError as error:
        return _json_response({'error': str(error)}, 404)
    except exc.ValidationError as error:
        return _json_response({'error': str(error)}, 400)
    except exc.DatabaseError as error:
        return _json_response({'error': str(error)}, 500)
    except Exception as error:
        current_app.logger.exception("Error al eliminar favorito", exc_info=error)
        return _json_response({'error': 'Error interno al eliminar favorito'}, 500)


@site_api.route('/me/favorites', methods=['GET'])
@token_or_session_required
def list_my_favorites():
    """Endpoint para listar los sitios favoritos del usuario autenticado."""
    user_id = get_current_user_id()
    if not user_id:
        return _json_response({'error': 'Usuario no autenticado'}, 401)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)

    try:
        result = favorite_service.list_favorites(user_id=user_id, page=page, per_page=per_page)
        return _json_response(result, 200)
    except exc.ValidationError as error:
        return _json_response({'error': str(error)}, 400)
    except exc.DatabaseError as error:
        return _json_response({'error': str(error)}, 500)
    except Exception as error:
        current_app.logger.exception("Error al listar favoritos", exc_info=error)
        return _json_response({'error': 'Error interno al listar favoritos'}, 500)



