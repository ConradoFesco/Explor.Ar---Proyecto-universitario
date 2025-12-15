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
        """Lista todos los estados de conservación (o levanta NotFound)."""
        states = StateSite.query.all()
        if not states:
            raise NotFoundError("No se encontraron estados")
        return [state.to_dict() for state in states]

    def create_state(self, data_state):
        """Crea un nuevo estado de conservación."""
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


state_service = StateService()