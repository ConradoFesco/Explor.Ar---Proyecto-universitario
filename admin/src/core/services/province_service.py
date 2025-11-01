"""
Servicio para provincias: búsqueda o creación por nombre.
"""
from src.core.models.province import Province
from src.web.extensions import db
from src.web import exceptions as exc

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
        # Validar que el nombre no esté vacío
        if not name or not name.strip():
            raise exc.ValidationError("El nombre de la provincia no puede estar vacío")
            
        # Busca la provincia por nombre
        province = Province.query.filter_by(name=name.strip()).first()
        
        # Si no existe, la crea
        if not province:
            province = Province(name=name.strip())
            db.session.add(province)
            
        return province

province_service = ProvinceService()