"""
Rutas Web para administración de Feature Flags.
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from src.web.auth.decorators import web_permission_required, web_system_admin_required
from src.core.services.flag_service import flag_service

flags_web = Blueprint('flags_web', __name__)


@flags_web.route("/flags", methods=["GET"])
@web_permission_required("flag_admin")
def list_flags_page():
    """Listado de flags del sistema para administradores."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    flags = flag_service.get_all_flags()
    return render_template("flags/list_flags.html", flags=flags)


@flags_web.route("/flags/<int:flag_id>/set", methods=["POST"])
@web_permission_required("flag_admin")
def set_flag(flag_id: int):
    """Establece explícitamente el estado del flag (on/off)."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    user_id = session.get('user_id')
    raw = (request.form.get('enabled') or '').strip().lower()
    enabled = True if raw in ('1','true','on','yes') else False
    message = (request.form.get('message') or '').strip() or None
    try:
        flag = flag_service.set_flag_state(flag_id, enabled, user_id, message=message)
        # Feedback al usuario (SweetAlert via flash)
        if enabled:
            flash('Modo activado correctamente', 'success')
        else:
            flash('Modo desactivado correctamente', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('flags_web.list_flags_page'))


@flags_web.route("/flags/<int:flag_id>/message", methods=["POST"])
@web_permission_required("flag_admin")
def set_flag_message(flag_id: int):
    """Actualiza solo el mensaje del flag (vía Web)."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    user_id = session.get('user_id')
    message = (request.form.get('message') or '').strip()
    try:
        flag_service.update_flag_message(flag_id, message, data_user=user_id)
        flash('Mensaje actualizado correctamente', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('flags_web.list_flags_page'))


@flags_web.route("/flags/public-maintenance", methods=["POST"])
@web_system_admin_required
def toggle_public_maintenance():
    """Establece el estado del modo mantenimiento del portal público (vía Web)."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    user_id = session.get('user_id')
    raw = (request.form.get('enabled') or '').strip().lower()
    enabled = True if raw in ('1', 'true', 'on', 'yes') else False
    message = (request.form.get('message') or '').strip() or None
    try:
        flag_service.set_flag_state_by_key(
            key="portal_maintenance_mode",
            enabled=enabled,
            data_user=user_id,
            message=message
        )
        # Feedback al usuario (SweetAlert via flash)
        if enabled:
            flash('Mantenimiento público activado correctamente', 'success')
        else:
            flash('Mantenimiento público desactivado correctamente', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('flags_web.list_flags_page'))

