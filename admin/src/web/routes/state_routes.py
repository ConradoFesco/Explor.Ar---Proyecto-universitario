from flask import Blueprint, request, jsonify
from src.web.services.state_service import state_service
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError

state_api = Blueprint('state_api', __name__)

@state_api.route('/state_routes', methods=['GET'])
def get_all_states():
    try:
        states = state_service.get_all_states()
        return jsonify(states), 200
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 409
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404