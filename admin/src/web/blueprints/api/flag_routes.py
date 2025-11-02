from flask import Blueprint, jsonify, request, session
from src.web.auth.decorators import permission_required
from src.core.services.flag_service import flag_service

flag_api = Blueprint("flag_api", __name__)


@flag_api.route("/flags/<int:flag_id>/toggle", methods=["POST"])
@permission_required('flag_admin')
def toggle_flag_route(flag_id: int):
    """API: fija estado explícito (enabled) y opcionalmente mensaje. Devuelve JSON."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Sesión o usuario inválido"}), 401
    data = request.get_json(silent=True) or request.form or {}
    raw_enabled = str(data.get('enabled', '')).strip().lower()
    enabled = True if raw_enabled in ('1','true','on','yes') else False
    message = (data.get('message') or '').strip() or None
    try:
        flag = flag_service.set_flag_state(flag_id, enabled, user_id, message=message)
        return jsonify({
            "success": True,
            "id": flag.id,
            "enabled": bool(flag.enabled),
            "message": flag.message or None,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@flag_api.route("/flags/<int:flag_id>/message", methods=["POST"])
@permission_required('flag_admin')
def update_flag_message_route(flag_id: int):
    """API: Actualiza únicamente el mensaje (con validación)."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Sesión o usuario inválido"}), 401
    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()
    try:
        flag = flag_service.update_flag_message(flag_id, message, data_user=user_id)
        return jsonify({
            "success": True,
            "id": flag.id,
            "message": flag.message or None,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400
