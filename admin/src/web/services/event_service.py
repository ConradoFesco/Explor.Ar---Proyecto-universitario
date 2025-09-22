from src.web.models.event import Event
from .. import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from src.web.exceptions import ValidationError, DatabaseError, NotFoundError

class EventService:
    def create_event(self, data, commit=True):
        required_fields = ['id_site', 'id_user', 'type_Action']
        if ( not all(field in data for field in required_fields)):
            raise ValidationError("Faltan campos obligatorios: id_site, id_user y type_Action")
        id_site = data.get('id_site')
        id_user = data.get('id_user')
        date_time = data.get('date_time', datetime.now())
        type_Action = data.get('type_Action')
        deleted = False
        event = Event(
            id_site=id_site,
            id_user=id_user,
            date_time=date_time,
            type_Action=type_Action,
            deleted=deleted,
        )
        try:
            db.session.add(event)
            if commit:
                db.session.commit()
            return event.to_dict()
        except IntegrityError as e:
            db.session.rollback()
            raise DatabaseError(f"Error al crear el evento: {e}")

event_service = EventService()