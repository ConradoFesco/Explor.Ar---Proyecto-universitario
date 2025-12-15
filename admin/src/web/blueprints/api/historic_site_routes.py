from flask import Blueprint, request, jsonify, Response, current_app
from src.core.services.historic_site_service import historic_site_service
from src.core.services.favorite_service import favorite_service
from src.web import exceptions as exc
from src.web.auth.decorators import permission_required, token_or_session_required, get_current_user_id
from src.core.validators.listing_validator import validate_public_site_search_params
from src.core.validators.api_validator import (
    validate_api_pagination_params,
    format_validation_error_for_api
)

site_api = Blueprint('site_api', __name__)


def _json_response(payload, status_code=200):
    response = jsonify(payload)
    response.status_code = status_code
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response


@site_api.route('/sites', methods=['GET'])
def list_public_historic_sites():
    """
    Endpoint público para listar sitios históricos.
    
    Información adicional no especificada en la API:
    - rating: Calificación promedio del sitio (number, opcional)
    - cover_image_url: URL de la imagen de portada (string, opcional)
    - is_favorite: Indica si el sitio es favorito del usuario autenticado (boolean, opcional, solo si hay usuario autenticado)
    - distance_km: Distancia en kilómetros desde el punto de búsqueda geoespacial (number, opcional, solo si se proporcionan lat, long y radius)
    """
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
        'page': request.args.get('page'),
        'per_page': request.args.get('per_page'),
        'favorites_only': request.args.get('fav') == '1'
    }

    try:
        params = validate_public_site_search_params(**raw_params)
    except exc.ValidationError as error:
        error_details = format_validation_error_for_api(error)
        return _json_response(
            {
                "error": {
                    "code": "invalid_query",
                    "message": "Parameter validation failed",
                    "details": error_details,
                }
            },
            400,
        )

    user_id = get_current_user_id()
    params['user_id'] = user_id

    try:
        result = historic_site_service.search_public_sites(**params)
        return _json_response(result, 200)
    except exc.DatabaseError as error:
        current_app.logger.exception("Database error al listar sitios públicos", exc_info=error)
        return _json_response(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            },
            500,
        )
    except Exception as error:
        current_app.logger.exception("Error al listar sitios públicos", exc_info=error)
        return _json_response(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            },
            500,
        )


@site_api.route('/sites/filter-options', methods=['GET'])
def get_public_filter_options():
    """Endpoint público para obtener opciones de filtros (ciudades, provincias, tags)."""
    try:
        result = historic_site_service.get_filter_options()
        return _json_response(result, 200)
    except exc.DatabaseError as error:
        current_app.logger.exception("Database error al obtener opciones de filtro", exc_info=error)
        return _json_response(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            },
            500,
        )
    except Exception as error:
        current_app.logger.exception("Error al obtener opciones de filtro", exc_info=error)
        return _json_response(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            },
            500,
        )


@site_api.route('/sites/<int:site_id>', methods=['GET'])
def get_public_historic_site(site_id):
    """
    Obtiene detalles de un sitio histórico específico por su ID.
    
    Información adicional no especificada en la API:
    - is_favorite: Indica si el sitio es favorito del usuario autenticado (boolean, opcional, solo si hay usuario autenticado)
    """
    try:
        user_id = get_current_user_id()
        site_data = historic_site_service.get_historic_site(site_id, user_id=user_id)
        # TO-DO: no convertir latitude y longitude a float
        try:
            lat_val = float(site_data.get('latitude')) if site_data.get('latitude') is not None else None
            long_val = float(site_data.get('longitude')) if site_data.get('longitude') is not None else None
        except (TypeError, ValueError):
            lat_val = None
            long_val = None

        inserted_at = site_data.get('created_at')
        updated_at = site_data.get('updated_at') or inserted_at
        
        api_payload = {
            'id': site_data.get('id'),
            'name': site_data.get('name'),
            'short_description': site_data.get('brief_description'),
            'description': site_data.get('complete_description'),
            'city': site_data.get('city_name') or site_data.get('city'),
            'province': site_data.get('province_name') or site_data.get('province'),
            'country': 'AR',
            'lat': lat_val,
            'long': long_val,
            'tags': site_data.get('tags', []),
            'state_of_conservation': site_data.get('state_name'),
            'inserted_at': inserted_at,
            'updated_at': updated_at,
        }
        
        if site_data.get('is_favorite') is not None:
            api_payload['is_favorite'] = site_data.get('is_favorite')
        return _json_response(api_payload, 200)
    except exc.NotFoundError as e:
        return _json_response(
            {
                "error": {
                    "code": "not_found",
                    "message": "Site not found",
                }
            },
            404,
        )
    except Exception as error:
        current_app.logger.exception("Error al obtener sitio histórico", exc_info=error)
        return _json_response(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            },
            500,
        )


@site_api.route('/sites/<int:site_id>/favorite', methods=['PUT'])
@token_or_session_required
def mark_favorite(site_id: int):
    user_id = get_current_user_id()
    try:
        favorite_service.mark_favorite(site_id=site_id, user_id=user_id)
        return '', 204
    except exc.NotFoundError as error:
        return _json_response(
            {
                "error": {
                    "code": "not_found",
                    "message": "Site not found",
                }
            },
            404,
        )
    except exc.ValidationError as error:
        return _json_response(
            {
                "error": {
                    "code": "invalid_request",
                    "message": str(error),
                }
            },
            400,
        )
    except exc.DatabaseError as error:
        current_app.logger.exception("Database error al marcar favorito", exc_info=error)
        return _json_response(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            },
            500,
        )
    except Exception as error:
        current_app.logger.exception("Error al marcar favorito", exc_info=error)
        return _json_response(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            },
            500,
        )


@site_api.route('/sites/<int:site_id>/favorite', methods=['DELETE'])
@token_or_session_required
def unmark_favorite(site_id: int):
    user_id = get_current_user_id()
    try:
        favorite_service.unmark_favorite(site_id=site_id, user_id=user_id)
        return '', 204
    except exc.NotFoundError as error:
        return _json_response(
            {
                "error": {
                    "code": "not_found",
                    "message": "Site not found",
                }
            },
            404,
        )
    except exc.ValidationError as error:
        return _json_response(
            {
                "error": {
                    "code": "invalid_request",
                    "message": str(error),
                }
            },
            400,
        )
    except exc.DatabaseError as error:
        current_app.logger.exception("Database error al eliminar favorito", exc_info=error)
        return _json_response(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            },
            500,
        )
    except Exception as error:
        current_app.logger.exception("Error al eliminar favorito", exc_info=error)
        return _json_response(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            },
            500,
        )


@site_api.route('/me/favorites', methods=['GET'])
@token_or_session_required
def list_my_favorites():
    """
    Endpoint para listar los sitios favoritos del usuario autenticado.
    
    Información adicional no especificada en la API:
    - rating: Calificación promedio del sitio (number, opcional)
    - cover_image_url: URL de la imagen de portada (string, opcional)
    - is_favorite: Siempre true para este endpoint (boolean)
    """
    user_id = get_current_user_id()
    try:
        page, per_page = validate_api_pagination_params(
            page=request.args.get('page'),
            per_page=request.args.get('per_page'),
            default_page=1,
            default_per_page=20,
            max_per_page=100
        )
    except exc.ValidationError as error:
        error_details = format_validation_error_for_api(error)
        return _json_response(
            {
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": error_details,
                }
            },
            400,
        )

    try:
        result = favorite_service.list_favorites(
            user_id=user_id, page=page, per_page=per_page
        )
        return _json_response(result, 200)
    except exc.ValidationError as error:
        error_details = format_validation_error_for_api(error)
        return _json_response(
            {
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": error_details,
                }
            },
            400,
        )
    except exc.DatabaseError as error:
        current_app.logger.exception("Database error al listar favoritos", exc_info=error)
        return _json_response(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            },
            500,
        )
    except Exception as error:
        current_app.logger.exception("Error al listar favoritos", exc_info=error)
        return _json_response(
            {
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred",
                }
            },
            500,
        )
