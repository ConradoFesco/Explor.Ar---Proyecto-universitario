from src.core.models.event import Event
from src.web.extensions import db
from src.web import exceptions as exc
from datetime import datetime
from sqlalchemy.exc import IntegrityError

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
    
    def get_all_events(self, id, include_deleted=False, page=1, per_page=25,
                       user_id=None, user_email=None, type_action=None, date_from=None, date_to=None):
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
        
        if date_from is not None and date_from.strip():
            try:
                # Convertir string a datetime
                from datetime import datetime as dt
                date_from_obj = dt.strptime(date_from, '%Y-%m-%d')
                query = query.filter(Event.date_time >= date_from_obj)
            except ValueError:
                pass  # Si el formato es inválido, ignorar el filtro
        
        if date_to is not None and date_to.strip():
            try:
                # Convertir string a datetime (incluir todo el día)
                from datetime import datetime as dt, timedelta
                date_to_obj = dt.strptime(date_to, '%Y-%m-%d')
                # Agregar 1 día menos 1 segundo para incluir todo el día
                date_to_obj = date_to_obj + timedelta(days=1, seconds=-1)
                query = query.filter(Event.date_time <= date_to_obj)
            except ValueError:
                pass  # Si el formato es inválido, ignorar el filtro
        
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