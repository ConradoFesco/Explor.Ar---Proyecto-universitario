from flask import Flask, request, session, redirect, url_for
from flask import render_template
from src.web.handlers import error
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from werkzeug.security import check_password_hash
load_dotenv()
from .routes.login_routes import login_bp
from .extensions import db, migrate


def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)

    # --- Configuración ---
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

    # --- Inicialización de extensiones ---
    db.init_app(app)
    migrate.init_app(app, db)

    # --- Importar modelos después de inicializar db ---
    with app.app_context():
        from .models.user import User
        from .models.category_site import CategorySite

    # --- Rutas HTML ---
    @app.route("/")
    def index():
        return render_template("login.html")

    @app.route("/home")
    def home():
        if "user_id" not in session:
            return redirect(url_for("index"))
        user = User.query.get(session["user_id"])
        return render_template("home.html", usuario=user.mail)

    @app.route("/logout")
    def logout():
        session.pop("user_id", None)
        return redirect(url_for("index"))

    @app.route("/sitios")
    def lista_sitios():
        return render_template("lista_sitios.html")

    # --- Blueprints (JSON API) ---
    from .routes.login_routes import login_bp
    app.register_blueprint(login_bp, url_prefix="/api")

    from .routes.tag_routes import tag_api
    app.register_blueprint(tag_api, url_prefix="/api")

    from .routes.HistoricSite_Routes import site_api
    app.register_blueprint(site_api, url_prefix="/api")

    # --- Manejo de errores ---
    from src.web.handlers import error
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.internal_server_error)

    return app
