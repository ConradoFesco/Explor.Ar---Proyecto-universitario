"""
Servicio para ciudades: búsqueda o creación asociada a una provincia.
"""
from src.core.models.city import City
from src.web.extensions import db
from src.web import exceptions as exc
from src.core.validators.location_validator import validate_city_name

class CityService:
    """Encapsula lógica para encontrar/crear ciudades vinculadas a provincias."""
    def find_or_create(self, name, province_obj):
        """
        Busca ciudad por nombre y provincia; si no existe, la crea sin commit.

        Args:
            name (str): Nombre de la ciudad.
            province_obj (Province): Provincia existente.

        Returns:
            City: Instancia existente o nueva (no commit).
        """
        validated_name = validate_city_name(name, province_obj)
            
        city = City.query.filter_by(name=validated_name, id_province=province_obj.id).first()
        
        if not city:
            city = City(name=validated_name, id_province=province_obj.id)
            db.session.add(city)
            
        return city

city_service = CityService()