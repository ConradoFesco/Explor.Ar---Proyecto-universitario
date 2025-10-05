from ..models import Province
from ..extensions import db
from .. import exceptions as exc

class ProvinceService:
    def find_or_create(self, name):
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