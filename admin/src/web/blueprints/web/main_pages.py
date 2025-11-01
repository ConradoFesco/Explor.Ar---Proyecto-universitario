"""
Blueprint Web principal: páginas base (index, home, logout).
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from src.core.models.user import User
from src.core.services.HistoricSite_Service import historic_site_service

main = Blueprint('main', __name__)


@main.route("/")
def index():
    return render_template("auth/login.html")


@main.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    user = User.query.get(session["user_id"])
    # SSR de sitios para mapa (subset razonable)
    try:
        result = historic_site_service.get_all_sites_for_map(include_deleted=False, page=1, per_page=500)
        sites_for_map = result.get('sites', [])
    except Exception:
        sites_for_map = []
    return render_template("shared/home.html", user=user, sites_for_map=sites_for_map)


@main.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("main.index"))


@main.route('/login', methods=['POST'])
def login_post():
    from src.core.services.auth_service import auth_service
    mail = (request.form.get('mail') or '').strip()
    password = request.form.get('password') or ''
    try:
        user = auth_service.login(mail, password)
        session['user_id'] = user.id
        return redirect(url_for('main.home'))
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('main.index'))


