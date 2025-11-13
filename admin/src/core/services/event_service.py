"""
Servicio de eventos de auditoría para operaciones sobre sitios.
"""
from src.core.models.event import Event
from src.web.extensions import db
from src.web import exceptions as exc
from datetime import datetime
from sqlalchemy.exc import IntegrityError

class EventService:
    """Crear, listar (con filtros) y eliminar lógicamente eventos."""
    def create_event(self, data, commit=True):
        """
        Crea un evento de auditoría.

        Args:
            data (dict): {'id_site', 'id_user', 'type_Action', 'date_time'(opcional)}
            commit (bool): Si True, confirma la transacción.

        Returns:
            dict: Evento creado en formato dict.

        Raises:
            ValidationError: Si faltan campos requeridos.
            DatabaseError: Si falla la escritura en base.
        """
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
    
    def get_all_events(self, id, include_deleted=False, page=1, per_page=25,
                       user_id=None, user_email=None, type_action=None, date_from: datetime | None = None, date_to: datetime | None = None):
        """
        Lista eventos de un sitio con filtros y paginación.

        Args:
            id (int): ID del sitio.
            include_deleted (bool): Incluir eliminados lógicamente.
            page (int): Página.
            per_page (int): Tamaño de página.
            user_id (int|None): Filtro por usuario.
            user_email (str|None): Prefijo de email.
            type_action (str|None): Tipo de acción.
            date_from (datetime|None): fecha/hora desde (inclusive).
            date_to (datetime|None): fecha/hora hasta (inclusive).

        Returns:
            dict: {'events': [...], 'pagination': {...}}
        """
        from src.core.models.user import User

        query = Event.query.filter_by(id_site=id)
        if not include_deleted:
            query = query.filter_by(deleted=False)
        
        # Join con User para filtros por usuario
        query = query.join(User, Event.id_user == User.id)

        # Aplicar filtros
        if user_id is not None:
            query = query.filter(Event.id_user == user_id)

        if user_email is not None and user_email.strip():
            query = query.filter(User.mail.ilike(f"{user_email.strip()}%"))
        
        if type_action is not None and type_action.strip():
            query = query.filter(Event.type_Action == type_action)
        
        if date_from is not None:
            query = query.filter(Event.date_time >= date_from)
        
        if date_to is not None:
            query = query.filter(Event.date_time <= date_to)
        
        # Ordenar por fecha cronológicamente (más reciente primero)
        query = query.order_by(Event.date_time.desc())
        
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        events = pagination.items
        return {
            'events': [{
                'id': event.id, 
                'id_site': event.id_site, 
                'id_user': event.id_user, 
                'date_time': event.date_time, 
                'type_Action': event.type_Action,
                'user_email': event.user.mail if event.user else ''
            } for event in events],
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'next_num': pagination.next_num,
                'prev_num': pagination.prev_num
            }
        }

    def soft_delete_event(self, id, data_user):
        """
        Realiza baja lógica del evento.

        Args:
            id (int): ID del evento.
            data_user (int): ID del usuario actor.

        Returns:
            Event: Objeto evento modificado.

        Raises:
            NotFoundError: Si no existe.
            DatabaseError: Si falla commit.
        """
        # 1. Busca el evento por su ID
        event = Event.query.get(id)
        # 2. Si no lo encuentra, lanza un error claro
        if not event:
            raise exc.NotFoundError(f"El evento con id {id} no fue encontrado.") 
        # 3. Realiza la "baja lógica" cambiando el estado
        event.deleted = True
        # 4. Guarda los cambios en la base de datos
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al eliminar el evento: {e}")
        return event

# instancia de la clase EventService
event_service = EventService()