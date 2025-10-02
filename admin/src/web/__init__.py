from flask import Flask, request, session, redirect, url_for
from flask import render_template
from src.web.handlers import error
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from .routes.auth_routes import login_bp
from .extensions import db, migrate, session_ext
from flask_session import Session
from flask_jwt_extended import JWTManager
import os

load_dotenv()


jwt = JWTManager() 
def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')


    app.config['SESSION_TYPE'] = 'filesystem'  # o 'redis' si tenés
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora
    app.config['SESSION_COOKIE_SECURE'] = True  # solo HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


    session_ext.init_app(app)

   
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')  # mejor tomarlo de .env
    jwt.init_app(app)
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    with app.app_context():
        from .models.user import User
        from .models.category_site import CategorySite


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

    from .routes.auth_routes import login_bp
    app.register_blueprint(login_bp, url_prefix="/api")

    from .routes.tag_routes import tag_api
    app.register_blueprint(tag_api, url_prefix="/api")

    from .routes.HistoricSite_Routes import site_api
    app.register_blueprint(site_api, url_prefix="/api")

    from datetime import datetime
    @app.template_filter('format_date')
    def format_date(date_value):
        if not date_value:
            return 'Sin fecha'

        if isinstance(date_value, datetime):
            return date_value.strftime("%d/%m/%Y")

        # Si es un string, intentar convertirlo
        if isinstance(date_value, str):
            try:
                date_obj = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                return date_obj.strftime("%d/%m/%Y")
            except:
                return date_value

        return 'Sin fecha'

    @app.route("/users")
    def list_users():
        from .models.user import User
        users = User.query.all()
        return render_template('list_users.html', users=users)

    @app.route("/users/<int:user_id>/editar")
    def edit_user(user_id):
        user = User.query.get_or_404(user_id)
        return render_template('edit_user.html', user=user)

    from src.web.handlers import error
    
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.internal_server_error)

    from . import models

    
    from .routes.user_routes import user_api
    app.register_blueprint(user_api, url_prefix='/api/users')

    return app
