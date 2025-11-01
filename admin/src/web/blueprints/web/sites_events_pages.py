"""
Rutas Web para historial de eventos de sitios (fragmentos SSR).
"""
from flask import Blueprint, render_template, session, redirect, url_for, request
from src.web.auth.decorators import web_permission_required
from src.core.services.event_service import event_service

sites_events_web = Blueprint('sites_events_web', __name__)


@sites_events_web.route("/sitios/<int:site_id>/eventos/fragment")
@web_permission_required("get_all_events")
def historial_eventos_fragment(site_id: int):
    """Fragmento HTML del historial de eventos de un sitio histórico."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    user_email = request.args.get('user_email')
    type_action = request.args.get('type_action')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    result = event_service.get_all_events(
        site_id,
        page=page,
        per_page=per_page,
        user_email=user_email,
        type_action=type_action,
        date_from=date_from,
        date_to=date_to
    )
    return render_template(
        "features/sites/events/_events.html.jinja",
        events=result.get('events', []),
        pagination=result.get('pagination', {}),
        site_id=site_id
    )


