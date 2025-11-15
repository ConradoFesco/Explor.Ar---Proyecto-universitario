from flask import Blueprint, request, jsonify
from src.core.services.state_service import state_service
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError
from src.web.auth.decorators import permission_required, token_or_session_required

state_api = Blueprint('state_api', __name__)

@state_api.route('/state_routes', methods=['GET'])
@token_or_session_required
@permission_required('get_all_states')
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


