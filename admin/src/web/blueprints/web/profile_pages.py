from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from src.web.auth.decorators import web_permission_required
from src.core.services.usuario_service import user_service


profile_web = Blueprint("profile_web", __name__)


@profile_web.route("/profile", methods=["GET"])
@web_permission_required("profile_show")
def view_profile():
    try:
        user = user_service.get_user(session["user_id"])
    except Exception:
        return redirect(url_for("main.index"))
    return render_template("users/profile.html", user=user)


@profile_web.route("/profile/update_password", methods=["POST"])
@web_permission_required("profile_update_password")
def update_password():
    new_password = (request.form.get('new_password') or '').strip()
    if not new_password or len(new_password) < 6:
        flash('La contraseña debe tener al menos 6 caracteres', 'error')
        return redirect(url_for('profile_web.view_profile'))
    try:
        user_service.update_password(session['user_id'], new_password)
        flash('Contraseña actualizada correctamente', 'success')
    except Exception as e:
        flash('Error al actualizar contraseña: ' + str(e), 'error')
    return redirect(url_for('profile_web.view_profile'))

