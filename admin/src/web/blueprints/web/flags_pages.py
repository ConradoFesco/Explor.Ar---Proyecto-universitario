from flask import Blueprint, render_template, session, redirect, url_for
from src.core.services.flag_service import flag_service

flags_web = Blueprint('flags_web', __name__)


@flags_web.route("/flags", methods=["GET"])
def list_flags_page():
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    flags = flag_service.get_all_flags()
    return render_template("flags/list_flags.html", flags=flags)


@flags_web.route("/flags/<int:flag_id>/toggle", methods=["POST"])
def toggle_flag(flag_id: int):
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    user_id = session.get('user_id')
    flag_service.toggle_flag(flag_id, user_id)
    return redirect(url_for('flags_web.list_flags_page'))

