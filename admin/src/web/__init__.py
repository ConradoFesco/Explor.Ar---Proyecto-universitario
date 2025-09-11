from flask import Flask

# Crea una instancia de la aplicación Flask
def create_app(env="development", static_folder=""):
    app = Flask(__name__, static_folder=static_folder)

# Define la ruta (URL) y la función que se ejecutará
    @app.route("/")
    def home():
        return "¡Hola mundo!"
    return app