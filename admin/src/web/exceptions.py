class ValidationError(Exception):
    """Error para validaciones de datos de entrada."""
    pass

class NotFoundError(Exception):
    """Error para cuando un recurso no se encuentra."""
    pass

class DatabaseError(Exception):
    """Error para problemas inesperados con la base de datos."""
    pass