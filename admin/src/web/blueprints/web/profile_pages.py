from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from src.core.services.usuario_service import user_service

profile_web = Blueprint("profile_web", __name__)


@profile_web.route("/profile", methods=["GET"])
def view_profile():
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    try:
        user = user_service.get_user(session["user_id"])  # dict
    except Exception:
        return redirect(url_for("main.index"))
    return render_template("users/profile.html", user=user)


@profile_web.route("/profile/update_password", methods=["POST"])
def update_password():
    if "user_id" not in session:
        return redirect(url_for("main.index"))
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

