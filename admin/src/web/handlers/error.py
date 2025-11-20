"""
Manejadores de errores HTTP personalizados.
"""
from dataclasses import dataclass
from flask import render_template


@dataclass
class HTTPError:
    """Representa un error HTTP con código, mensaje y descripción"""
    code: int
    message: str
    description: str


def not_found(error):
    """Manejador para errores 404 - Página no encontrada"""
    error = HTTPError(
        code=404, 
        message="Página no encontrada", 
        description="La página que estás buscando no existe."
    )
    return render_template('shared/error.html', error=error), 404


def unauthorized(error):
    """Manejador para errores 401 - No autorizado"""
    error = HTTPError(
        code=401, 
        message="No autorizado", 
        description="No tenés permisos para acceder a este recurso."
    )
    return render_template('shared/error.html', error=error), 401


def internal_server_error(error):
    """Manejador para errores 500 - Error interno del servidor"""
    error = HTTPError(
        code=500, 
        message="Error interno del servidor", 
        description="Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo más tarde."
    )
    return render_template('shared/error.html', error=error), 500


def register_error_handlers(app):
    """
    Registra todos los manejadores de errores HTTP.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    app.register_error_handler(404, not_found)
    app.register_error_handler(401, unauthorized)
    app.register_error_handler(500, internal_server_error)