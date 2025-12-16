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
        """
        Lista todas las categorías no eliminadas.
        
        Returns:
            list[dict]: Lista de categorías como diccionarios
            
        Raises:
            NotFoundError: Si no se encuentran categorías
        """
        categories = CategorySite.query.filter_by(deleted=False).all()
        if not categories:
            raise NotFoundError("No se encontraron categorías")
        return [category.to_dict() for category in categories]

    def create_category(self, data_category):
        """
        Crea una nueva categoría de sitio histórico.
        
        Args:
            data_category: Diccionario con los datos de la categoría (debe contener 'name')
            
        Returns:
            CategorySite: Categoría creada (implícito, se persiste en la base de datos)
            
        Raises:
            ValidationError: Si faltan campos obligatorios
            DatabaseError: Si hay un error al persistir en la base de datos
        """
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

    def category_exists(self, category_id: int) -> bool:
        """
        Verifica si existe una categoría con el ID dado (no eliminada).
        
        Args:
            category_id: ID de la categoría a verificar
            
        Returns:
            bool: True si existe, False en caso contrario
        """
        category = CategorySite.query.filter_by(id=category_id, deleted=False).first()
        return category is not None


category_service = CategoryService()
