"""
Filtros personalizados para templates Jinja2.
"""
from datetime import datetime


def register_filters(app):
    """
    Registra todos los filtros de template personalizados.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    
    @app.template_filter('format_date')
    def format_date(date_value):
        """
        Formatea una fecha al formato DD/MM/YYYY.
        
        Args:
            date_value: Valor de fecha (datetime, string o None)
            
        Returns:
            str: Fecha formateada o 'Sin fecha'
        """
        if not date_value:
            return 'Sin fecha'

        if isinstance(date_value, datetime):
            return date_value.strftime("%d/%m/%Y")

        if isinstance(date_value, str):
            try:
                date_obj = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                return date_obj.strftime("%d/%m/%Y")
            except:
                return date_value

        return 'Sin fecha'

