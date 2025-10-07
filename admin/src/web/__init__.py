from flask import Flask, request, session, redirect, url_for
from flask import render_template
from src.web.handlers import error
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from .routes.auth_routes import login_bp
from .extensions import db, migrate, session_ext
from flask_session import Session
from flask_jwt_extended import JWTManager
from datetime import timedelta
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
    app.config['SESSION_COOKIE_SECURE'] = False # solo HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)

    session_ext = Session()
    session_ext.init_app(app)

   
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')  # mejor tomarlo de .env
    jwt.init_app(app)
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    with app.app_context():
        from .models.user import User
        from .models.category_site import CategorySite
        from .models.flag import Flag
        from .models.user import User

    @app.before_request
    def check_admin_maintenance():
        # Ignorar rutas públicas (login, static, etc.)
        if request.endpoint in ['login_bp.login', 'index', 'static']:
            return None

        # Consultar el flag
        admin_flag = Flag.query.filter_by(key="admin_maintenance_mode").first()
        if admin_flag and admin_flag.enabled:
            user_id = session.get("user_id")
            if not user_id:
                return None  # no logueado, deja pasar (ver login)

            permisos = user.get_user_roles() 
            if permisos: 
                # Redirige al template de mantenimiento
                return render_template(
                    "maintenance.html",
                    message=admin_flag.message or "El sitio de administración está temporalmente inactivo."
                )
    @app.route("/")
    def index():
        return render_template("login.html")

    @app.route("/home")
    def home():
        if "user_id" not in session:
            return redirect(url_for("index"))
        userd = User.query.get(session["user_id"])
        return render_template("home.html", user=userd)
    @app.route("/logout")
    def logout():
        session.pop("user_id", None)
        return redirect(url_for("index"))

    @app.route("/sitios")
    def lista_sitios():
        if "user_id" not in session:
            return redirect(url_for("index"))
        return render_template("lista_sitios.html")

    @app.route("/alta-sitios")
    def alta_sitios():
        if "user_id" not in session:
            return redirect(url_for("index"))
        return render_template("alta_sitios.html")

    @app.route("/modificar-sitios")
    def modificar_sitios():
        if "user_id" not in session:
            return redirect(url_for("index"))
        return render_template("modificar_sitios.html")

    @app.route("/tags")
    def lista_tags():
        if "user_id" not in session:
            return redirect(url_for("index"))
        return render_template("list_tags.html")

    from .routes.auth_routes import login_bp
    app.register_blueprint(login_bp, url_prefix="/api")

    from .routes.profile_routes import profile_bp
    app.register_blueprint(profile_bp)

    from .routes.tag_routes import tag_api
    app.register_blueprint(tag_api, url_prefix="/api")

    from .routes.HistoricSite_Routes import site_api
    app.register_blueprint(site_api, url_prefix="/api")
    
    from .routes.state_routes import state_api
    app.register_blueprint(state_api, url_prefix="/api")
    
    from .routes.category_routes import category_api
    app.register_blueprint(category_api, url_prefix="/api")

    from .routes.event_routes import event_api
    app.register_blueprint(event_api, url_prefix="/api")

    from src.web.routes.flag_routes import flag_api
    app.register_blueprint(flag_api, url_prefix="/flags")

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
        return render_template('list_users.html')

    @app.route("/users/<int:user_id>/editar")
    def edit_user(user_id):
        return render_template('edit_user.html', user_id=user_id)
    
    @app.route('/users/nuevo')
    def create_user_form():
        return render_template('create_user.html')

    from src.web.handlers import error
    
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.internal_server_error)

    from . import models

    
    from .routes.user_routes import user_api
    app.register_blueprint(user_api, url_prefix='/api/users')

    return app
