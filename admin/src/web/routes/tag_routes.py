from flask import Blueprint, request, jsonify
from src.web.services.tag_service import tag_service
from src.web.auth.decorators import permission_required
from .. import exceptions as exc

tag_api = Blueprint('tag_api', __name__, url_prefix='/api')

@tag_api.route('/tags', methods=['POST'])
@permission_required('create_tag')
def create_new_tag():
    """Endpoint para crear un nuevo tag."""
    data = request.json
    try:
        tag = tag_service.create_tag(data)
    except exc.ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except exc.DatabaseError as e:
        return jsonify({'error': str(e)}), 409
    return jsonify(tag), 201

@tag_api.route('/tags', methods=['GET'])
@permission_required('get_all_tags')
def get_all_tags_route(): 
    """Endpoint para obtener todos los tags con paginación y filtros."""
    try:
        # Parámetros de paginación
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))
        
        # Parámetros de búsqueda y ordenamiento
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        
        # Parámetro para incluir eliminados
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        result = tag_service.get_all_tags_paginated(
            page=page,
            per_page=per_page,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            include_deleted=include_deleted
        )
        return jsonify(result), 200
    except exc.ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except exc.DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@tag_api.route('/tags/<string:tag_id_or_slug>', methods=['GET'])
@permission_required('get_tag')
def get_tag_by_id_or_slug_route(tag_id_or_slug): 
    """Endpoint para obtener un tag por ID o slug."""
    try:
        # Intenta obtener el tag por ID
        try:
            tag_id = int(tag_id_or_slug)
            tag = tag_service.get_tag_by_id(tag_id)
        except ValueError:
            # Si no es un entero, intenta obtenerlo por slug
            tag = tag_service.get_tag_by_slug(tag_id_or_slug)
        return jsonify(tag), 200
    except exc.NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@tag_api.route('/tags/<int:tag_id>', methods=['PUT'])
@permission_required('update_tag')
def update_tag_route(tag_id): 
    """Endpoint para actualizar un tag."""
    data = request.json
    try:
        updated_tag = tag_service.update_tag(tag_id, data)
    except exc.ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except exc.DatabaseError as e:
        return jsonify({'error': str(e)}), 409
    return jsonify(updated_tag), 200

@tag_api.route('/tags/<int:tag_id>', methods=['DELETE'])
@permission_required('delete_tag')
def delete_tag_route(tag_id): 
    """Endpoint para eliminar un tag (solo si no está asociado a sitios)."""
    try:
        success = tag_service.delete_tag(tag_id)
        return jsonify({'message': 'Tag eliminado exitosamente.'}), 200
    except exc.ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except exc.DatabaseError as e:
        return jsonify({'error': str(e)}), 409

@tag_api.route('/tags/<int:site_id>/tags', methods=['GET'])
@permission_required('get_tag')
def get_tags_by_site_id_route(site_id):
    try:
        result = tag_service.get_tags_by_site_id(site_id)
        return jsonify(result), 200
    except exc.NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except exc.DatabaseError as e:
        return jsonify({'error': str(e)}), 409
