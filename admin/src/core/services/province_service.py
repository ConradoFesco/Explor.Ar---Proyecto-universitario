"""
Servicio para provincias: búsqueda o creación por nombre.
"""
from src.core.models.province import Province
from src.web.extensions import db
from src.web import exceptions as exc
from src.core.validators.location_validator import validate_province_name

class ProvinceService:
    """Encapsula lógica para encontrar/crear provincias."""
    def find_or_create(self, name):
        """
        Busca provincia por nombre; si no existe, la crea sin commit.

        Args:
            name (str): Nombre de provincia.

        Returns:
            Province: Instancia existente o nueva (no commit).
        """
        validated_name = validate_province_name(name)
            
        province = Province.query.filter_by(name=validated_name).first()
        
        if not province:
            province = Province(name=validated_name)
            db.session.add(province)
            
        return province

province_service = ProvinceService()