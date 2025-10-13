"""
Blueprint para rutas principales de la aplicación.
Incluye páginas de vistas HTML (no API).
"""
from flask import Blueprint, render_template, session, redirect, url_for
from src.core.models.user import User

main = Blueprint('main', __name__)


@main.route("/")
def index():
    """Página de inicio/login"""
    return render_template("auth/login.html")


@main.route("/home")
def home():
    """Página principal después del login"""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    user = User.query.get(session["user_id"])
    return render_template("shared/home.html", user=user)


@main.route("/logout")
def logout():
    """Cierra la sesión del usuario"""
    session.pop("user_id", None)
    return redirect(url_for("main.index"))


@main.route("/sitios")
def lista_sitios():
    """Lista de sitios históricos"""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    return render_template("sites/lista_sitios.html")


@main.route("/alta-sitios")
def alta_sitios():
    """Formulario de alta de sitios"""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    return render_template("sites/alta_sitios.html")


@main.route("/modificar-sitios")
def modificar_sitios():
    """Formulario de modificación de sitios"""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    return render_template("sites/modificar_sitios.html")


@main.route("/tags")
def lista_tags():
    """Lista de tags"""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    return render_template("tags/list_tags.html")


@main.route("/users")
def list_users():
    """Lista de usuarios"""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    return render_template('users/list_users.html')


@main.route("/users/<int:user_id>/editar")
def edit_user(user_id):
    """Formulario de edición de usuario"""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    return render_template('users/edit_user.html', user_id=user_id)


@main.route('/users/nuevo')
def create_user_form():
    """Formulario de creación de usuario"""
    if "user_id" not in session:
        return redirect(url_for("main.index"))
    return render_template('users/create_user.html')

