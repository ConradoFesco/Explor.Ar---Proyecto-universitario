"""
Aplicación Flask - Admin de Sitios Históricos
Factory para crear y configurar la aplicación Flask.
"""
import os
from flask import Flask
from flask_cors import CORS
from .storage import storage
from dotenv import load_dotenv

from config import get_current_config
from .extensions import db, migrate, session_ext, oauth

load_dotenv()

def create_app(env="development", static_folder="../../static"):
    """
    Factory para crear y configurar la aplicación Flask.
    
    Args:
        env (str): Ambiente de ejecución ('development', 'production', 'testing')
        static_folder (str): Ruta a la carpeta de archivos estáticos
        
    Returns:
        Flask: Aplicación Flask configurada
    """
    app = Flask(__name__, static_folder=static_folder)

    configure_app(app, env)
    
    initialize_extensions(app)

    storage.init_app(app)
    
    cors_origins_env = os.getenv("CORS_ORIGINS", "")
    
    if cors_origins_env:
        cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
        CORS(app, 
             resources={ r"/api/*": {
                 "origins": cors_origins,
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization", "Accept"],
                 "supports_credentials": True
             }},
             supports_credentials=True)
    else:
        dev_origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
        CORS(app, 
             resources={ r"/api/*": {
                 "origins": dev_origins,
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization", "Accept"],
                 "supports_credentials": True
             }},
            supports_credentials=True)
    register_blueprints(app)
    
    register_hooks(app)
    
    register_filters(app)
    
    register_error_handlers(app)
    
    register_commands(app)
    
    with app.app_context():
        from src.core import models
    
    return app


def configure_app(app, env):
    """
    Carga la configuración de la aplicación.
    
    Args:
        app: Instancia de la aplicación Flask
        env (str): Ambiente de ejecución
    """
    current_config = get_current_config(env)
    app.config.from_object(current_config)

    app.config['MINIO_SERVER'] = os.getenv("MINIO_SERVER", "http://127.0.0.1:9000")
    app.config['MINIO_ACCESS_KEY'] = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    app.config['MINIO_SECRET_KEY'] = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    app.config['MINIO_BUCKET'] = os.getenv("MINIO_BUCKET", "grupo06")
    app.config['MINIO_SECURE'] = os.getenv("MINIO_SECURE", "False").lower() == "true"
    app.config['MINIO_USE_HTTPS'] = os.getenv("MINIO_USE_HTTPS", "True").lower() == "true"

   
def initialize_extensions(app):
    """
    Inicializa todas las extensiones de Flask.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    db.init_app(app)
    migrate.init_app(app, db)
    session_ext.init_app(app)
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )


def register_blueprints(app):
    """
    Registra todos los blueprints de la aplicación.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    from .blueprints_registry import register_blueprints as _register_blueprints
    _register_blueprints(app)


def register_hooks(app):
    """
    Registra hooks (before_request, context_processor, etc.).
    
    Args:
        app: Instancia de la aplicación Flask
    """
    from .hooks import register_hooks as _register_hooks
    _register_hooks(app)


def register_filters(app):
    """
    Registra filtros personalizados de templates.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    from .template_filters import register_filters as _register_filters
    _register_filters(app)


def register_error_handlers(app):
    """
    Registra manejadores de errores HTTP.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    from .handlers.error import register_error_handlers as _register_error_handlers
    _register_error_handlers(app)


def register_commands(app):
    """
    Registra comandos CLI personalizados.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    from .commands.cli import register_commands as _register_commands
    _register_commands(app)


def initialize_database_if_needed(app):
    """
    Inicializa la base de datos automáticamente en cada deploy.
    
    Esta función borra la base de datos, la recrea y ejecuta los seeds
    en cada despliegue.
    
    Puede deshabilitarse con variable de entorno AUTO_INIT_DB=false
    
    Args:
        app: Instancia de la aplicación Flask
    """
    auto_init = os.getenv("AUTO_INIT_DB", "true").lower() == "true"
    
    if not auto_init:
        return
    
    with app.app_context():
        try:
            app.logger.info("🔧 Inicializando base de datos en cada deploy...")
            
            from src.core import models
            
            db.drop_all()
            app.logger.info("✅ Tablas eliminadas")
            
            db.create_all()
            app.logger.info("✅ Tablas creadas correctamente")
            
            try:
                from src.web.commands.seeds import main as seed_db
                seed_db(app)
                app.logger.info("✅ Seeds ejecutados correctamente")
            except Exception as e:
                app.logger.error(f"❌ Error al ejecutar seeds: {e}")
                import traceback
                app.logger.error(traceback.format_exc())
                raise
                
        except Exception as e:
            app.logger.error(f"❌ Error al inicializar base de datos: {e}")