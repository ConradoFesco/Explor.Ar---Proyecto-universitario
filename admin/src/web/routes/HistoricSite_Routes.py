from flask import Blueprint, request, jsonify
from src.web.services.HistoricSite_Service import historic_site_service
from .. import exceptions as exc
from flask import session

site_api = Blueprint('site_api', __name__)

@site_api.route('/HistoricSite_Routes', methods=['POST'])
def create_historic_site():
    # 1. El controlador recibe el JSON y lo convierte a diccionario
    json_content = request.get_json()
    # si no se reciben datos, devuelve un error 400
    if not json_content:
        return jsonify({'error': 'No se recibieron datos'}), 400
    data_site = json_content.get('data_site')
    data_user = session.get('user_id')

    if not data_site or not data_user:
        return jsonify({'error': 'Faltan datos de sitio histórico o usuario'}), 400
    
    # si se reciben datos, llama al servicio para que haga el trabajo pesado
    try:
        # 2. Llama al servicio para que haga el trabajo pesado
        new_site = historic_site_service.create_historic_site(data_site, data_user)
        # 3. Si todo sale bien, devuelve el nuevo objeto y un código 201 (Created)
        return jsonify(new_site.to_dict()), 201
    except exc.ValidationError as e:
        # si el servicio lanzó un error de validación, lo captura y lo devuelve
        return jsonify({'error': str(e)}), 400 # 400 = Bad Request
    except exc.DatabaseError as e:
        # si el servicio lanzó un error de base de datos, lo captura y lo devuelve
        return jsonify({'error': str(e)}), 409 # 409 = Conflict en la data base

@site_api.route('/HistoricSite_Routes/<int:id>', methods=['GET'])
def get_historic_site(id):
    # si se recibe el ID, llama al servicio para que haga el trabajo pesado
    try:
        # si todo sale bien, devuelve el objeto y un código 200
        site = historic_site_service.get_historic_site(id)
        return jsonify(site.to_dict()), 200
    except exc.NotFoundError as e:
        # si el servicio lanzó un error de validación, lo captura y lo devuelve
        return jsonify({'error': str(e)}), 404 # 404 = Not Found

@site_api.route('/HistoricSite_Routes', methods=['GET'])
def get_all_historic_sites():
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    # Validar parámetros
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 25:  # Límite máximo de 25 por página
        per_page = 25
    try:
        result = historic_site_service.get_all_historic_sites(
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
def update_historic_site(id):
    json_content = request.get_json()
    if not json_content:
        return jsonify({'error': 'No se recibieron datos'}), 400
    
    data_site = json_content.get('data_site')
    data_user = session.get('user_id')

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
def delete_historic_site(id):
    data_user = session.get('user_id')
    
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