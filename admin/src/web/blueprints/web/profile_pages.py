from flask import Blueprint, render_template, session, redirect, url_for
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


