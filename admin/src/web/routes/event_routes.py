from flask import Blueprint, request, jsonify
from src.web.services.event_service import event_service
from .. import exceptions as exc

event_api = Blueprint('event_api', __name__)

@event_api.route('/event_routes/<int:id>', methods=['GET'])
def get_all_events(id):
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    # Validar parámetros
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 25:  # Límite máximo de 25 por página
        per_page = 25
    try:
        result = event_service.get_all_events(
            id=id,
            include_deleted=include_deleted, 
            page=page, 
            per_page=per_page
        )
        # si todo sale bien, devuelve el objeto y un código 200
        return jsonify(result), 200
    except exc.NotFoundError as e:
        # si el servicio lanzó un error de validación, lo captura y lo devuelve
        return jsonify({'error': str(e)}), 404 # 404 = Not Found


@event_api.route('/event_routes/<int:id>', methods=['DELETE'])
def delete_event(id):
    json_content = request.get_json()
    if not json_content:
        return jsonify({'error': 'No se recibieron datos'}), 400
    
    data_user = json_content.get('data_user')
    if not data_user:
        return jsonify({'error': 'Faltan datos de usuario'}), 400
    
    try:
        # 1. Llama al servicio para que haga el trabajo
        event_service.soft_delete_event(id, data_user)
        # 2. Si todo sale bien, devuelve un mensaje de éxito y un código 200 (OK)
        return jsonify({'message': f'El evento con id {id} ha sido eliminado.'}), 200
    except exc.NotFoundError as e:
        # 3. Si el servicio no encontró el sitio, devuelve el error 404
        return jsonify({'error': str(e)}), 404
    except exc.DatabaseError as e:
        # 4. Si el servicio lanzó un error de base de datos, lo captura y lo devuelve
        return jsonify({'error': str(e)}), 409 # 409 = Conflict en la data base