from dataclasses import dataclass
from flask import render_template


@dataclass
class HTTPError:
    code: int
    message: str
    description: str

def not_found(error):
    error = HTTPError(
        code=404, 
        message="Página no encontrada", 
        description="La página que estás buscando no existe."
    )

    return render_template('shared/error.html', error=error), 404

def unauthorized(error):
    error = HTTPError(
        code=401, 
        message="No autorizado", 
        description="No tenés permisos para acceder a este recurso."
    )

    return render_template('shared/error.html', error=error), 401

def internal_server_error(error):
    error = HTTPError(
        code=500, 
        message="Error interno del servidor", 
        description="Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo más tarde."
    )

    return render_template('shared/error.html', error=error), 500