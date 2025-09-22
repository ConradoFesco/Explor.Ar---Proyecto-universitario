from ..models import HistoricSite
from .. import exceptions as exc
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from .. import db
from ..services.event_service import event_service

class HistoricSite_Service:
    def create_historic_site(self, data_site, data_user):
        required_fields = ['name', 'brief_description', 'id_ciudad', 'latitude', 'longitude', 'id_category', 'visible']
        if ( not all(field in data_site for field in required_fields)):
            raise exc.ValidationError("Faltan campos obligatorios del sitio histórico: Nombre, descripción, ciudad, latitud, longitud, categoría y visible")
        id_user = data_user.get('id_user')
        if not id_user:
            raise exc.ValidationError("Faltan campos obligatorios del usuario: id_user")
        name = data_site.get('name') 
        brief_description = data_site.get('brief_description')
        complete_description = data_site.get('complete_description',None) 
        id_ciudad = data_site.get('id_ciudad')
        latitude = data_site.get('latitude')
        longitude = data_site.get('longitude')
        id_estado = data_site.get('id_estado',None) 
        year_inauguration = data_site.get('year_inauguration',None) 
        id_category = data_site.get('id_category')
        visible = data_site.get('visible')
        deleted = False
        created_at = datetime.now()
        historic_site = HistoricSite(
            name=name, 
            brief_description=brief_description, 
            complete_description=complete_description, 
            id_ciudad=id_ciudad, 
            latitude=latitude, 
            longitude=longitude, 
            id_estado=id_estado, 
            year_inauguration=year_inauguration, 
            id_category=id_category, 
            visible=visible, 
            deleted=deleted, 
            created_at=created_at)
        try:
            db.session.add(historic_site)
            db.session.flush()
            event_data = {
                'id_site': historic_site.id,
                'id_user': id_user,
                'type_Action': 'CREATE'
            }
            event_service.create_event(event_data,commit=False)
            db.session.commit()
        except (IntegrityError, exc.ValidationError) as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al crear el sitio histórico y su evento: {e}")

        return historic_site

    def get_historic_site(self, id):
        site = HistoricSite.query.get(id)
        # si no se encuentra el sitio histórico, devuelve un error 404
        if site is None or site.deleted:
            raise exc.NotFoundError("Sitio histórico no encontrado")
        # si se encuentra el sitio histórico, devuelve el sitio histórico
        return site
    
    def get_all_historic_sites(self, include_deleted=False, page=1, per_page=25): 
        """Obtiene todos los sitios históricos con paginación."""
        query = HistoricSite.query.with_entities(HistoricSite.id, HistoricSite.name, HistoricSite.brief_description)
        if not include_deleted:
            query = query.filter_by(deleted=False)
        # Aplicar paginación
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        sites = pagination.items
        return {
            'sites': [{'id': site.id, 'name': site.name, 'brief_description': site.brief_description} for site in sites],
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

    def update_historic_site(self, id, data_site, data_user):
        historic_site = HistoricSite.query.get(id)
        # si no se encuentra el sitio histórico, devuelve un error 404
        if historic_site is None:
            raise exc.NotFoundError("Sitio histórico no encontrado")
        # si se encuentra el sitio histórico, actualiza el sitio histórico
        historic_site.name = data_site.get('name',historic_site.name)
        historic_site.brief_description = data_site.get('brief_description',historic_site.brief_description)
        historic_site.complete_description = data_site.get('complete_description',historic_site.complete_description)
        historic_site.id_ciudad = data_site.get('id_ciudad',historic_site.id_ciudad)
        historic_site.latitude = data_site.get('latitude',historic_site.latitude)
        historic_site.longitude = data_site.get('longitude',historic_site.longitude)
        historic_site.id_estado = data_site.get('id_estado',historic_site.id_estado)
        historic_site.year_inauguration = data_site.get('year_inauguration',historic_site.year_inauguration)
        historic_site.id_category = data_site.get('id_category',historic_site.id_category)
        historic_site.deleted = data_site.get('deleted',historic_site.deleted)
        historic_site.visible = data_site.get('visible',historic_site.visible)
        id_user = data_user.get('id_user')
        try:
            event_data = {
                'id_site': historic_site.id,
                'id_user': id_user,
                'type_Action': 'UPDATE'
            }
            event_service.create_event(event_data,commit=False)
            db.session.commit()
        except (IntegrityError, exc.ValidationError) as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al actualizar el sitio histórico y su evento: {e}")
        return historic_site

    def soft_delete_historic_site(self, id, data_user):
        # 1. Busca el sitio histórico por su ID
        site = HistoricSite.query.get(id)
        # 2. Si no lo encuentra, lanza un error claro
        if not site:
            raise exc.NotFoundError(f"El sitio histórico con id {id} no fue encontrado.") 
        # 3. Realiza la "baja lógica" cambiando el estado
        site.deleted = True
        # 4. Guarda los cambios en la base de datos
        try:
            event_data = {
                'id_site': site.id,
                'id_user': data_user.get('id_user'),
                'type_Action': 'DELETE'
            }
            event_service.create_event(event_data,commit=False)
            db.session.commit()
        except (IntegrityError, exc.ValidationError) as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al eliminar el sitio histórico y su evento: {e}")
        # 5. Devuelve el objeto modificado (opcional pero útil)
        return site

# instancia de la clase HistoricSite_Service
historic_site_service = HistoricSite_Service()