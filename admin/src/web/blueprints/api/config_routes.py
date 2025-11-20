"""
Rutas API para configuración pública del sistema.
Estos endpoints son públicos (sin autenticación requerida) para que la app pública pueda consultar el estado del sistema.
"""
from flask import Blueprint, jsonify
from src.core.services.flag_service import flag_service

config_api = Blueprint("config_api", __name__)


@config_api.route("/config/status", methods=["GET"])
def get_system_status():
    """
    Endpoint público para que Vue consulte el estado del sistema.
    Especialmente útil para verificar si el portal está en modo mantenimiento.
    """
    try:
        maintenance_mode = flag_service.is_portal_maintenance_mode()
        maintenance_message = flag_service.get_portal_maintenance_message()
        
        return jsonify({
            "maintenance_mode": maintenance_mode,
            "message": maintenance_message or "El sitio se encuentra en mantenimiento programado."
        }), 200
    except Exception as e:
        # En caso de error, asumir que no hay mantenimiento para evitar bloquear el acceso
        return jsonify({
            "maintenance_mode": False,
            "message": None
        }), 200

