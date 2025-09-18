from flask import Flask
from flask import render_template
from src.web.handlers import error
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate # <-- Importa Migrate
from dotenv import load_dotenv
import os


load_dotenv()


def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)

    @app.route("/")
    def home():
        return render_template('home.html')
    
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.internal_server_error)

    return app

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---

# Formato: 'postgresql://usuario:contraseña@host:puerto/nombre_db'
# Reemplaza los valores con los tuyos.
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') # <-- Usamos la variable de entorno para la conexión a la base de datos en .env

# Esto es para desactivar una función de SQLAlchemy que no usaremos y que consume recursos.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- INICIALIZACIÓN DE EXTENSIONES ---
db = SQLAlchemy(app)
migrate = Migrate(app, db) # <-- Inicializa Flask-Migrate

# --- FIN DE LA CONFIGURACIÓN ---

# Aquí puedes importar tus modelos para que Migrate los reconozca
# from . import models