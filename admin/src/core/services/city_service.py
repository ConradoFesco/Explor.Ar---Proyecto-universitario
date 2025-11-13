"""
Servicio para ciudades: búsqueda o creación asociada a una provincia.
"""
from src.core.models.city import City
from src.web.extensions import db
from src.web import exceptions as exc

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
        # Validar que el nombre no esté vacío
        if not name or not name.strip():
            raise exc.ValidationError("El nombre de la ciudad no puede estar vacío")
            
        # Validar que la provincia existe
        if not province_obj:
            raise exc.ValidationError("La provincia es requerida para crear la ciudad")
            
        # Busca la ciudad por nombre Y por el ID de la provincia (corregido: id_province)
        city = City.query.filter_by(name=name.strip(), id_province=province_obj.id).first()
        
        # Si no existe, la crea y la asocia a la provincia
        if not city:
            city = City(name=name.strip(), id_province=province_obj.id)
            db.session.add(city)
            
        return city

city_service = CityService()