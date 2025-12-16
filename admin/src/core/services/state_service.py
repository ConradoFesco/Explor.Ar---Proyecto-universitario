"""
Servicio de estados de conservación de sitios.
"""
from src.core.models.state_site import StateSite
from src.web.extensions import db
from sqlalchemy.exc import IntegrityError
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError


class StateService:
    """Operaciones básicas para listar y crear estados de sitio."""
    def get_all_states(self):
        """
        Lista todos los estados de conservación.
        
        Returns:
            list[dict]: Lista de estados de conservación como diccionarios
            
        Raises:
            NotFoundError: Si no se encuentran estados
        """
        states = StateSite.query.all()
        if not states:
            raise NotFoundError("No se encontraron estados")
        return [state.to_dict() for state in states]

    def create_state(self, data_state):
        """
        Crea un nuevo estado de conservación.
        
        Args:
            data_state: Diccionario con los datos del estado (debe contener 'state')
            
        Returns:
            StateSite: Estado creado (implícito, se persiste en la base de datos)
            
        Raises:
            ValidationError: Si faltan campos obligatorios
            DatabaseError: Si hay un error al persistir en la base de datos
        """
        required_fields = ['state']
        if not all(field in data_state for field in required_fields):
            raise ValidationError("Faltan campos obligatorios")
        new_state = StateSite(state=data_state.get('state'))
        try:
            db.session.add(new_state)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al crear el estado: {e}")

    def state_exists(self, state_id: int) -> bool:
        """
        Verifica si existe un estado de conservación con el ID dado.
        
        Args:
            state_id: ID del estado a verificar
            
        Returns:
            bool: True si existe, False en caso contrario
        """
        state = StateSite.query.get(state_id)
        return state is not None


state_service = StateService()