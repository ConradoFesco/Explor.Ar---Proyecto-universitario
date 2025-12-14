"""
Rutas Web para historial de eventos de sitios (fragmentos SSR).
"""
from flask import Blueprint, render_template, session, redirect, url_for, request
from src.web.auth.decorators import web_permission_required
from src.core.services.event_service import event_service
from src.core.validators.listing_validator import validate_event_list_params

sites_events_web = Blueprint('sites_events_web', __name__)


@sites_events_web.route("/sitios/<int:site_id>/eventos/fragment")
@web_permission_required("event_index")
def historial_eventos_fragment(site_id: int):
    """Fragmento HTML del historial de eventos de un sitio histórico."""
    raw = {
        'page': request.args.get('page'),
        'per_page': request.args.get('per_page'),
        'user_id': request.args.get('user_id'),
        'user_email': request.args.get('user_email'),
        'type_action': request.args.get('type_action'),
        'date_from': request.args.get('date_from'),
        'date_to': request.args.get('date_to'),
    }
    params = validate_event_list_params(**raw)
    result = event_service.get_all_events(
        site_id,
        page=params['page'],
        per_page=params['per_page'],
        user_id=params['user_id'],
        user_email=params['user_email'],
        type_action=params['type_action'],
        date_from=params['date_from'],
        date_to=params['date_to']
    )
    return render_template(
        "features/sites/events/_events.html.jinja",
        events=result.get('events', []),
        pagination=result.get('pagination', {}),
        site_id=site_id
    )


