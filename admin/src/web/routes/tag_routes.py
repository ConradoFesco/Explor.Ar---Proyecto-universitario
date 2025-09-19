# routes/tag_routes.py

from flask import Blueprint, request, jsonify
from app.services import tag_service

tag_bp = Blueprint('tag_bp', __name__, url_prefix='/api/tags')

@tag_bp.route('/', methods=['POST'])
def create_new_tag(): //crear nuevo tag
    """Endpoint para crear un nuevo tag."""
    data = request.json
    tag, error = tag_service.create_tag(data)
    if error:
        return jsonify({'error': error}), 400
    return jsonify(tag), 201

@tag_bp.route('/', methods=['GET'])
def get_all_tags_route(): //obtener todos los tags
    """Endpoint para obtener todos los tags.
    Acepta un parámetro de query para incluir tags eliminados.
    Ej: /api/tags?include_deleted=true"""
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    tags = tag_service.get_all_tags(include_deleted)
    return jsonify(tags), 200

@tag_bp.route('/<string:tag_id_or_slug>', methods=['GET'])
def get_tag_by_id_or_slug_route(tag_id_or_slug): //obtener un tag por ID o slug
    """Endpoint para obtener un tag por ID o slug."""
    try:
        # Intenta obtener el tag por ID
        tag_id = int(tag_id_or_slug)
        tag = tag_service.get_tag_by_id(tag_id)
    except ValueError:
        # Si no es un entero, intenta obtenerlo por slug
        tag = tag_service.get_tag_by_slug(tag_id_or_slug)

    if not tag:
        return jsonify({'error': 'Tag no encontrado.'}), 404
    return jsonify(tag), 200

@tag_bp.route('/<int:tag_id>', methods=['PUT'])
def update_tag_route(tag_id): //actualizar un tag
    """Endpoint para actualizar un tag."""
    data = request.json
    updated_tag, error = tag_service.update_tag(tag_id, data)
    if error:
        return jsonify({'error': error}), 400
    return jsonify(updated_tag), 200

@tag_bp.route('/<int:tag_id>', methods=['DELETE'])
def delete_tag_route(tag_id): //eliminar un tag
    """Endpoint para "eliminar" (soft delete) un tag."""
    success, error = tag_service.delete_tag(tag_id)
    if error:
        return jsonify({'error': error}), 404
    return jsonify({'message': 'Tag eliminado exitosamente.'}), 200