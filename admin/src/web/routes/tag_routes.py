# routes/tag_routes.py

from flask import Blueprint, request, jsonify
from src.web.services.tag_service import tag_service
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError

tag_api = Blueprint('tag_api', __name__, url_prefix='/api')

@tag_api.route('/tag_routes', methods=['POST'])
def create_new_tag():
    """Endpoint para crear un nuevo tag."""
    data = request.json
    try:
        tag = tag_service.create_tag(data)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 409
    return jsonify(tag), 201

@tag_api.route('/tag_routes', methods=['GET'])
def get_all_tags_route(): 
    """Endpoint para obtener todos los tags.
    Acepta un parámetro de query para incluir tags eliminados.
    Ej: /api/tags?include_deleted=true"""
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    tags = tag_service.get_all_tags(include_deleted=include_deleted)
    return jsonify(tags), 200

@tag_api.route('/tag_routes/<string:tag_id_or_slug>', methods=['GET'])
def get_tag_by_id_or_slug_route(tag_id_or_slug): 
    """Endpoint para obtener un tag por ID o slug."""
    try:
        # Intenta obtener el tag por ID
        tag_id = int(tag_id_or_slug)
        tag = tag_service.get_tag_by_id(tag_id)
    except ValueError:
        # Si no es un entero, intenta obtenerlo por slug
        tag = tag_service.get_tag_by_slug(tag_id_or_slug)
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    return jsonify(tag), 200

@tag_api.route('/tag_routes/<int:tag_id>', methods=['PUT'])
def update_tag_route(tag_id): 
    """Endpoint para actualizar un tag."""
    data = request.json
    try:
        updated_tag = tag_service.update_tag(tag_id, data)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 409
    return jsonify(updated_tag), 200

@tag_api.route('/tag_routes/<int:tag_id>', methods=['DELETE'])
def delete_tag_route(tag_id): 
    """Endpoint para "eliminar" (soft delete) un tag."""
    try:
        success = tag_service.delete_tag(tag_id)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 409
    return jsonify({'message': 'Tag eliminado exitosamente.'}), 200