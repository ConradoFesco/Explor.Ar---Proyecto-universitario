"""
Blueprint Web principal: páginas base (index, home, logout).
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from src.core.services.historic_site_service import historic_site_service

main = Blueprint('main', __name__)


@main.route("/")
def index():
    """Página de login (renderiza el formulario de acceso)."""
    return render_template("auth/login.html")


@main.route("/home")
def home():
    """Home del panel: renderiza el mapa y contenido inicial (SSR)."""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    # SSR de sitios para mapa (subset razonable)
    try:
        result = historic_site_service.get_all_sites_for_map(include_deleted=False, page=1, per_page=500)
        sites_for_map = result.get('sites', [])
    except Exception:
        sites_for_map = []
    return render_template("shared/home.html", sites_for_map=sites_for_map)


@main.route("/logout")
def logout():
    """Cierra la sesión y redirige a la página de login."""
    session.pop("user_id", None)
    return redirect(url_for("main.index"))


@main.route('/login', methods=['POST'])
def login_post():
    """Procesa el login del formulario Web y redirige con flash en error."""
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


