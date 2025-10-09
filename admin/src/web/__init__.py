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
from config import get_current_config
from src.web.models import User, Flag
import os

load_dotenv()

jwt = JWTManager() 
def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)

    current_config = get_current_config(env)
    app.config.from_object(current_config)

    #app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
   # app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')


    #app.config['SESSION_TYPE'] = 'filesystem'  # o 'redis' si tenés
    ##app.config['SESSION_PERMANENT'] = True
    ##app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora
    #app.config['SESSION_COOKIE_SECURE'] = False # solo HTTPS
    #app.config['SESSION_COOKIE_HTTPONLY'] = True
    #app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    #app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)

    session_ext = Session()
    session_ext.init_app(app)

   
    #app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')  # mejor tomarlo de .env
    jwt.init_app(app)
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    with app.app_context():
        if env == "production":
            from src.web.commands.seeds import seed_data as seed_db
            # Borra y crea la base de datos
            db.drop_all()
            db.create_all()
            # Corre los seeds
            seed_db()
        

    @app.before_request
    def check_admin_maintenance():
        """
        Verifica antes de cada petición si el modo mantenimiento está activo.
        Solo los superAdmin pueden acceder cuando está activo.
        """
        # Ignorar rutas públicas (login, static, logout, archivos estáticos)
        public_endpoints = [
            'login_bp.login',      # POST /api/login
            'login_bp.logout',     # GET/POST /api/logout
            'index',               # GET /
            'static',              # Archivos estáticos
            None                   # Peticiones sin endpoint definido
        ]
        
        if request.endpoint in public_endpoints:
            return None
        
        # Ignorar todas las peticiones a /static/
        if request.path and request.path.startswith('/static/'):
            return None
        
        # Consultar el flag de mantenimiento
        try:
            admin_flag = Flag.query.filter_by(name="admin_maintenance_mode").first()
        except Exception as e:
            # Si hay error al consultar la BD, permitir acceso
            return None
        
        # Si el flag NO existe o está desactivado, continuar normalmente
        if not admin_flag or not admin_flag.enabled:
            return None
        
        # Flag activo: verificar si el usuario es superAdmin
        user_id = session.get("user_id")
        
        # Si no está logueado, permitir acceso (otras rutas lo redirigen)
        if not user_id:
            return None
        
        # Obtener el usuario completo
        try:
            user = User.query.get(user_id)
        except Exception as e:
            # Error en BD, limpiar sesión
            session.clear()
            return redirect(url_for('index'))
        
        # Si no se encuentra el usuario, cerrar sesión y redirigir
        if not user:
            session.clear()
            return redirect(url_for('index'))
        
        # Verificar si es superAdmin
        try:
            user_roles = user.get_user_roles()
            
            if 'superAdmin' in user_roles:
                # SuperAdmin puede acceder siempre
                return None
        except Exception as e:
            # Error al obtener roles, asumir no es superAdmin
            pass
        
        # Usuario normal: mostrar página de mantenimiento
        return render_template(
            "mantenimiento.html",
            message=admin_flag.message or "El sitio de administración está temporalmente inactivo."
        )
    @app.route("/")
    def index():
        return render_template("login.html")

    @app.context_processor
    def inject_user():
        """Inyecta el usuario actual en todos los templates"""
        user_id = session.get("user_id")
        if user_id:
            try:
                user = User.query.get(user_id)
                if user:
                    user_roles = user.get_user_roles()
                    user_initials = f"{user.name[0]}{user.last_name[0]}".upper() if user.name and user.last_name else "U"
                    return {
                        'current_user': user,
                        'user_roles': user_roles,
                        'user_initials': user_initials,
                        'is_admin': 'admin' in user_roles or 'superAdmin' in user_roles
                    }
            except Exception as e:
                pass
        return {'current_user': None, 'user_roles': [], 'user_initials': '', 'is_admin': False}

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
