from ..models import HistoricSite, Tag, TagHistoricSite
from .. import exceptions as exc
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from ..extensions import db
from ..services.event_service import event_service
from ..services.tag_service import tag_service
from ..services.city_service import city_service
from ..services.province_service import province_service

class HistoricSite_Service:
    def create_historic_site(self, data_site, data_user):
        required_fields = ['name', 'brief_description', 'name_city', 'name_province', 'latitude', 'longitude', 'id_category', 'visible']
        if ( not all(field in data_site for field in required_fields)):
            raise exc.ValidationError("Faltan campos obligatorios del sitio histórico: Nombre, descripción, ciudad, latitud, longitud, categoría y visible")
        id_user = data_user
        if not id_user:
            raise exc.ValidationError("Usuario no autenticado. Por favor, inicie sesión.")
        name = data_site.get('name') 
        brief_description = data_site.get('brief_description')
        complete_description = data_site.get('complete_description',None) 
        name_city = data_site.get('name_city')
        name_province = data_site.get('name_province')
        latitude = data_site.get('latitude')
        longitude = data_site.get('longitude')
        id_estado = data_site.get('id_estado',None) 
        year_inauguration = data_site.get('year_inauguration',None) 
        id_category = data_site.get('id_category')
        visible = data_site.get('visible')
        deleted = False
        created_at = datetime.now()
        try:
            # Primero crear/buscar la provincia
            province = province_service.find_or_create(name_province)
            
            # Luego crear/buscar la ciudad usando el objeto provincia
            city = city_service.find_or_create(name_city, province)
            
            # Asegurar que los cambios de provincia y ciudad se guarden
            db.session.flush()
            
            historic_site = HistoricSite(
                name=name, 
                brief_description=brief_description, 
                complete_description=complete_description, 
                id_ciudad=city.id, 
                latitude=latitude, 
                longitude=longitude, 
                id_estado=id_estado, 
                year_inauguration=year_inauguration, 
                id_category=id_category, 
                visible=visible, 
                deleted=deleted, 
                created_at=created_at)
            
            db.session.add(historic_site)
            db.session.flush()
            
            # Si se proporcionaron tags, agregarlos al sitio (sin crear evento adicional)
            tag_ids = data_site.get('tag_ids', [])
            if tag_ids:
                self.add_tags(historic_site.id, tag_ids, id_user, event_action=False)
            
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
        
        # Crear respuesta personalizada que incluya los tags
        site_data = site.to_dict()
        
        # Agregar información de tags
        site_data['tags'] = []
        for tag_relation in site.tag_historic_sites:
            if not tag_relation.tag.deleted:  # Solo incluir tags no eliminados
                site_data['tags'].append({
                    'id': tag_relation.tag.id,
                    'name': tag_relation.tag.name,
                    'slug': tag_relation.tag.slug
                })
        
        # si se encuentra el sitio histórico, devuelve el sitio histórico
        return site_data
    
    def get_all_historic_sites(self, include_deleted=False, page=1, per_page=25): 
        """Obtiene todos los sitios históricos con paginación."""
        from ..models import Tag
        query = HistoricSite.query
        if not include_deleted:
            query = query.filter_by(deleted=False)
        # Aplicar paginación
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        sites = pagination.items
        sites_data = []
        for site in sites:
            # Obtener tags del sitio
            site_tags = []
            for tag_relation in site.tag_historic_sites:
                if not tag_relation.tag.deleted:  # Solo incluir tags no eliminados
                    site_tags.append({
                        'id': tag_relation.tag.id,
                        'name': tag_relation.tag.name,
                        'slug': tag_relation.tag.slug
                    })
            
            sites_data.append({
                'id': site.id, 
                'name': site.name, 
                'brief_description': site.brief_description,
                'tags': site_tags
            })
        
        return {
            'sites': sites_data,
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
        
        id_user = data_user
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
                'id_user': data_user,
                'type_Action': 'DELETE'
            }
            event_service.create_event(event_data,commit=False)
            db.session.commit()
        except (IntegrityError, exc.ValidationError) as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al eliminar el sitio histórico: {e}")
        # 5. Devuelve el objeto modificado (opcional pero útil)
        return site


    def add_tags(self, site_id, tag_ids_list, data_user, event_action=True): #event_action es true si se quiere crear un evento
        # Validar que el sitio histórico existe
        site = HistoricSite.query.get(site_id)
        if not site:
            raise exc.NotFoundError(f"El sitio histórico con id {site_id} no fue encontrado.")
        
        # Validar que tag_ids_list es una lista
        if not isinstance(tag_ids_list, list):
            raise exc.ValidationError("Los tags deben enviarse como una lista.")
        
        if not tag_ids_list:
            raise exc.ValidationError("La lista de tags no puede estar vacía.")
        
        # Validar que todos los tags existen
        non_existent_tags = []
        for tag_id in tag_ids_list:
            try:
                tag_service.get_tag_by_id(tag_id)
            except exc.NotFoundError:
                non_existent_tags.append(tag_id)
        
        if non_existent_tags:
            raise exc.NotFoundError(f"Los siguientes tags no existen: {non_existent_tags}")

        # Obtener relaciones existentes para evitar duplicados
        existing_relations = TagHistoricSite.query.filter_by(
            Historic_Site_id=site_id
        ).filter(TagHistoricSite.Tag_id.in_(tag_ids_list)).all()
        
        existing_tag_ids = [rel.Tag_id for rel in existing_relations]
        new_tag_ids = [tag_id for tag_id in tag_ids_list if tag_id not in existing_tag_ids]
        
        if not new_tag_ids:
            raise exc.ValidationError("El sitio histórico ya posee todos los tags especificados.")

        # Crear las nuevas relaciones solo para los tags que no existen
        relations_to_add = []
        for tag_id in new_tag_ids:
            relation = TagHistoricSite(
                Historic_Site_id=site_id,
                Tag_id=tag_id
            )
            relations_to_add.append(relation)
        
        try:
            # Agregar todas las relaciones nuevas
            for relation in relations_to_add:
                db.session.add(relation)
            
            # Crear evento si es necesario
            if event_action:
                event_data = {
                    'id_site': site.id,
                    'id_user': data_user,
                    'type_Action': 'UPDATE'
                }
                event_service.create_event(event_data, commit=False)
            
            db.session.commit()
            
            # Retornar información útil sobre qué se agregó
            return {
                'site': site,
                'added_tags': new_tag_ids,
                'skipped_tags': existing_tag_ids,
                'message': f'Se agregaron {len(new_tag_ids)} tags nuevos. Se omitieron {len(existing_tag_ids)} tags que ya existían.'
            }
            
        except (IntegrityError, exc.ValidationError) as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al agregar los tags al sitio histórico y su evento: {e}")

    def update_site_tags(self, site_id, new_tag_ids, data_user):
        """Actualiza completamente los tags de un sitio histórico (agrega nuevos y elimina los que no están en la lista)"""
        # Validar que el sitio histórico existe
        site = HistoricSite.query.get(site_id)
        if not site:
            raise exc.NotFoundError(f"El sitio histórico con id {site_id} no fue encontrado.")
        
        # Validar que new_tag_ids es una lista
        if not isinstance(new_tag_ids, list):
            raise exc.ValidationError("Los tags deben enviarse como una lista.")
        
        # Si new_tag_ids está vacío, significa que queremos quitar todos los tags
        if new_tag_ids:
            # Validar que todos los tags existen
            non_existent_tags = []
            for tag_id in new_tag_ids:
                try:
                    tag_service.get_tag_by_id(tag_id)
                except exc.NotFoundError:
                    non_existent_tags.append(tag_id)
            
            if non_existent_tags:
                raise exc.NotFoundError(f"Los siguientes tags no existen: {non_existent_tags}")

        # Obtener relaciones actuales
        current_relations = TagHistoricSite.query.filter_by(Historic_Site_id=site_id).all()
        current_tag_ids = [rel.Tag_id for rel in current_relations]
        
        # Determinar qué tags agregar y cuáles quitar
        tags_to_add = [tag_id for tag_id in new_tag_ids if tag_id not in current_tag_ids]
        tags_to_remove = [tag_id for tag_id in current_tag_ids if tag_id not in new_tag_ids]
        
        try:
            # Eliminar tags que ya no están en la lista
            if tags_to_remove:
                TagHistoricSite.query.filter_by(Historic_Site_id=site_id).filter(
                    TagHistoricSite.Tag_id.in_(tags_to_remove)
                ).delete(synchronize_session=False)
            
            # Agregar nuevos tags
            for tag_id in tags_to_add:
                new_relation = TagHistoricSite(
                    Historic_Site_id=site_id,
                    Tag_id=tag_id
                )
                db.session.add(new_relation)
            
            # Crear evento solo si hubo cambios
            if tags_to_add or tags_to_remove:
                event_data = {
                    'id_site': site.id,
                    'id_user': data_user,
                    'type_Action': 'UPDATE'
                }
                event_service.create_event(event_data, commit=False)
            
            db.session.commit()
            
            # Retornar información sobre los cambios realizados
            return {
                'site': site,
                'added_tags': tags_to_add,
                'removed_tags': tags_to_remove,
                'final_tags': new_tag_ids,
                'message': f'Se agregaron {len(tags_to_add)} tags y se eliminaron {len(tags_to_remove)} tags.'
            }
            
        except (IntegrityError, exc.ValidationError) as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al actualizar los tags del sitio histórico: {e}")

# instancia de la clase HistoricSite_Service
historic_site_service = HistoricSite_Service()