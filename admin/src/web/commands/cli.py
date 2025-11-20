"""
Comandos CLI personalizados para la aplicación Flask.
"""
import click
from flask.cli import with_appcontext
from src.web.extensions import db
def register_commands(app):
    """
    Registra todos los comandos CLI personalizados.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    
    @app.cli.command("init-db")
    @with_appcontext
    def init_db_command():
        """
        Inicializa la base de datos (crea todas las tablas).
        """
        db.create_all()
        click.echo("Base de datos inicializada.")
    
    @app.cli.command("seed-db")
    @with_appcontext
    def seed_db_command():
        """
        Ejecuta los seeds para poblar la base de datos con datos iniciales.
        """
        from src.web.commands.seeds import main as seed_db
        seed_db()
        click.echo("Seeds ejecutados correctamente.")
    
    @app.cli.command("reset-db")
    @with_appcontext
    @click.confirmation_option(prompt="¿Está seguro de que desea eliminar todos los datos?")
    def reset_db_command():
        """
        Elimina y recrea todas las tablas, luego ejecuta los seeds.
        ⚠️ PRECAUCIÓN: Esto eliminará TODOS los datos existentes.
        """
        db.drop_all()
        click.echo("Tablas eliminadas.")
        db.create_all()
        click.echo("Tablas creadas.")
        from src.web.commands.seeds import main as seed_db
        seed_db()
        click.echo("Seeds ejecutados. Base de datos reseteada correctamente.")

