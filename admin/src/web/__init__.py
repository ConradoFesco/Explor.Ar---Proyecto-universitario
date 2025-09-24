from flask import Flask
from flask import render_template
from src.web.handlers import error
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
import os

load_dotenv()

# Inicializar extensiones fuera de la función para que estén disponibles globalmente
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)
    
    # --- CONFIGURACIÓN DE LA BASE DE DATOS ---
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')

    # --- CONFIGURACIÓN DE JWT ---
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')  # mejor tomarlo de .env
    jwt.init_app(app)
    
    # --- INICIALIZACIÓN DE EXTENSIONES ---
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # --- URL PRINCIPAL ---
    @app.route("/")
    def home():
        return render_template('home.html')
    
    # --- RUTA PARA LISTA DE SITIOS ---
    @app.route("/sitios")
    def lista_sitios():
        return render_template('lista_sitios.html')
    
    # --- RUTA PARA USUARIOS ---
    @app.route("/users")
    def list_users():
        from .models.user import User
        users = User.query.all()
        return render_template('list_users.html', users=users)

    # --- REGISTRO DE MANEJADORES DE ERRORES ---
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.internal_server_error)

    # Importar modelos para que estén disponibles para Flask-Migrate
    from . import models

    # Importar rutas para que estén disponibles para Flask
    from .routes.tag_routes import tag_api
    app.register_blueprint(tag_api,url_prefix='/api')

    from .routes.HistoricSite_Routes import site_api
    app.register_blueprint(site_api, url_prefix='/api')
    
    from .routes.usuario_routes import user_api
    app.register_blueprint(user_api, url_prefix='/api/users')

    # --- FIN DE LA CONFIGURACIÓN ---
    return app