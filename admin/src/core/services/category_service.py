"""
Servicio de categorías de sitios históricos.
"""
from src.core.models.category_site import CategorySite
from src.web.extensions import db
from sqlalchemy.exc import IntegrityError
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError

class CategoryService:
    """Operaciones básicas para listar y crear categorías."""
    def get_all_categories(self):
        """Lista categorías no eliminadas o levanta NotFound si no hay."""
        categories = CategorySite.query.filter_by(deleted=False).all()
        if not categories:
            raise NotFoundError("No se encontraron categorías")
        return [category.to_dict() for category in categories]
    

    def create_category(self, data_category):
        """Crea una nueva categoría de sitio histórico."""
        required_fields = ['name']
        if not all(field in data_category for field in required_fields):
            raise ValidationError("Faltan campos obligatorios")
        new_category = CategorySite(name=data_category.get('name'))
        try:
            db.session.add(new_category)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al crear la categoría: {e}")


category_service = CategoryService()
