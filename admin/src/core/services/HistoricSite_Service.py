from src.core.models.historic_site import HistoricSite
from src.core.models.tag import Tag
from src.core.models.tag_historic_site import TagHistoricSite
from src.core.models.city import City
from src.core.models.province import Province
from src.core.models.state_site import StateSite
from src.web import exceptions as exc
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from src.web.extensions import db
from src.core.services.event_service import event_service
from src.core.services.tag_service import tag_service
from src.core.services.city_service import city_service
from src.core.services.province_service import province_service
import csv
import io

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
        except IntegrityError as e:
            db.session.rollback()
            # Verificar si es un error de violación de unicidad del nombre
            if "Historic_Site_name_key" in str(e):
                raise exc.ValidationError("Ya existe un sitio histórico con este nombre. Por favor, elija otro nombre.")
            else:
                raise exc.DatabaseError(f"Error al crear el sitio histórico: {e}")
        except exc.ValidationError as e:
            db.session.rollback()
            raise e

        return historic_site

    def get_historic_site(self, id):
        from src.core.models.category_site import CategorySite
        
        # Hacer join para obtener datos de relaciones
        site = HistoricSite.query.join(City, HistoricSite.id_ciudad == City.id)\
                                 .join(Province, City.id_province == Province.id)\
                                 .join(StateSite, HistoricSite.id_estado == StateSite.id, isouter=True)\
                                 .join(CategorySite, HistoricSite.id_category == CategorySite.id, isouter=True)\
                                 .filter(HistoricSite.id == id, HistoricSite.deleted == False)\
                                 .first()
        
        if site is None:
            raise exc.NotFoundError("Sitio histórico no encontrado")
        
        # Crear respuesta personalizada que incluya los tags y relaciones
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
        
        # Agregar información de relaciones usando los joins
        site_data['city_name'] = site.city.name if hasattr(site, 'city') and site.city else None
        site_data['province_name'] = site.city.province.name if hasattr(site, 'city') and site.city and site.city.province else None
        site_data['state_name'] = site.state_site.state if hasattr(site, 'state_site') and site.state_site else None
        site_data['category_name'] = site.category.name if hasattr(site, 'category') and site.category else None
        
        # si se encuentra el sitio histórico, devuelve el sitio histórico
        return site_data
    
    def get_all_historic_sites(self, include_deleted=False, page=1, per_page=25, 
                              search_text=None, sort_by='created_at', sort_order='desc',
                              city_id=None, province_id=None, tag_ids=None, 
                              state_id=None, date_from=None, date_to=None, 
                              visible=None): 
        """Obtiene todos los sitios históricos con paginación, filtros y ordenamiento."""
        from sqlalchemy import and_, or_, desc, asc
        
        # Query base
        query = HistoricSite.query
        
        # Variable para controlar si ya se hizo join con City
        city_joined = False
        
        # Filtro de eliminados
        if not include_deleted:
            query = query.filter_by(deleted=False)
        
        # Filtro de búsqueda por texto (prefijo en nombre o descripción breve)
        if search_text:
            prefix = f"{search_text.strip()}%"
            search_filter = or_(
                HistoricSite.name.ilike(prefix),
                HistoricSite.brief_description.ilike(prefix)
            )
            query = query.filter(search_filter)
        
        # Filtro por ciudad
        if city_id:
            query = query.filter(HistoricSite.id_ciudad == city_id)
        
        # Filtro por provincia (a través de la relación con ciudad)
        if province_id:
            query = query.join(City)
            city_joined = True
            query = query.filter(City.id_province == province_id)
        
        # Filtro por tags (multiselección)
        if tag_ids and len(tag_ids) > 0:
            # Filtrar sitios que tengan al menos uno de los tags especificados
            query = query.join(TagHistoricSite).filter(TagHistoricSite.Tag_id.in_(tag_ids))
        
        # Filtro por estado del sitio
        if state_id:
            query = query.filter(HistoricSite.id_estado == state_id)
        
        # Filtro por rango de fechas
        if date_from:
            query = query.filter(HistoricSite.created_at >= date_from)
        if date_to:
            query = query.filter(HistoricSite.created_at <= date_to)
        
        # Filtro por visibilidad
        if visible is not None:
            query = query.filter(HistoricSite.visible == visible)
        
        # Ordenamiento
        if sort_by == 'name':
            if sort_order == 'desc':
                query = query.order_by(desc(HistoricSite.name))
            else:
                query = query.order_by(asc(HistoricSite.name))
        elif sort_by == 'city':
            # Solo hacer join si no se hizo antes
            if not city_joined:
                query = query.join(City)
            if sort_order == 'desc':
                query = query.order_by(desc(City.name))
            else:
                query = query.order_by(asc(City.name))
        elif sort_by == 'created_at':
            if sort_order == 'desc':
                query = query.order_by(desc(HistoricSite.created_at))
            else:
                query = query.order_by(asc(HistoricSite.created_at))
        else:
            # Por defecto, ordenar por fecha de creación descendente
            query = query.order_by(desc(HistoricSite.created_at))
        
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
                'created_at': site.created_at.isoformat() if site.created_at else None,
                'city_name': site.city.name if site.city else None,
                'province_name': site.city.province.name if site.city and site.city.province else None,
                'state_name': site.state_site.state if site.state_site else None,
                'visible': site.visible,
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


    def get_all_sites_for_map(self, include_deleted=False, page=1, per_page=25): 
        """Obtiene todos los sitios históricos con información para el mapa, incluyendo paginación."""
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
                'latitude': site.latitude,
                'longitude': site.longitude,
                'name_city': site.city.name if site.city else None,
                'name_province': site.city.province.name if site.city and site.city.province else None,
                'year_inauguration': site.year_inauguration,
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

    def get_filter_options(self):
        """Obtiene las opciones de filtros disponibles para sitios históricos"""
        try:
            # Obtener ciudades
            cities = City.query.filter_by(deleted=False).all()
            cities_data = [{'id': city.id, 'name': city.name} for city in cities]
            
            # Obtener provincias
            provinces = Province.query.filter_by(deleted=False).all()
            provinces_data = [{'id': province.id, 'name': province.name} for province in provinces]
            
            # Obtener tags
            tags = Tag.query.filter_by(deleted=False).all()
            tags_data = [{'id': tag.id, 'name': tag.name, 'slug': tag.slug} for tag in tags]
            
            # Obtener estados
            states = StateSite.query.filter_by(deleted=False).all()
            states_data = [{'id': state.id, 'name': state.state} for state in states]
            
            return {
                'cities': cities_data,
                'provinces': provinces_data,
                'tags': tags_data,
                'states': states_data
            }
        except Exception as e:
            raise exc.DatabaseError(f"Error al obtener opciones de filtro: {e}")

    def export_sites_to_csv(self, search_text=None, sort_by='created_at', sort_order='desc',
                           city_id=None, province_id=None, tag_ids=None, 
                           state_id=None, date_from=None, date_to=None, 
                           visible=None):
        """
        Exporta sitios históricos a CSV respetando los filtros aplicados.
        
        Retorna una tupla (csv_content, filename) donde csv_content es el contenido del CSV
                   y filename es el nombre del archivo generado
        """
        from sqlalchemy import and_, or_, desc, asc
        
        # Query base - similar al método get_all_historic_sites pero sin paginación
        query = HistoricSite.query.join(City).join(Province).join(StateSite, isouter=True)
        
        # Filtro de eliminados (solo sitios no eliminados)
        query = query.filter_by(deleted=False)
        
        # Filtro de búsqueda por texto (prefijo en nombre o descripción breve)
        if search_text:
            prefix = f"{search_text.strip()}%"
            search_filter = or_(
                HistoricSite.name.ilike(prefix),
                HistoricSite.brief_description.ilike(prefix)
            )
            query = query.filter(search_filter)
        
        # Filtro por ciudad
        if city_id:
            query = query.filter(HistoricSite.id_ciudad == city_id)
        
        # Filtro por provincia
        if province_id:
            query = query.filter(City.id_province == province_id)
        
        # Filtro por tags (multiselección)
        if tag_ids and len(tag_ids) > 0:
            query = query.join(TagHistoricSite).filter(TagHistoricSite.Tag_id.in_(tag_ids))
        
        # Filtro por estado del sitio
        if state_id:
            query = query.filter(HistoricSite.id_estado == state_id)
        
        # Filtro por rango de fechas
        if date_from:
            query = query.filter(HistoricSite.created_at >= date_from)
        if date_to:
            query = query.filter(HistoricSite.created_at <= date_to)
        
        # Filtro por visibilidad
        if visible is not None:
            query = query.filter(HistoricSite.visible == visible)
        
        # Ordenamiento
        if sort_by == 'name':
            if sort_order == 'desc':
                query = query.order_by(desc(HistoricSite.name))
            else:
                query = query.order_by(asc(HistoricSite.name))
        elif sort_by == 'city':
            if sort_order == 'desc':
                query = query.order_by(desc(City.name))
            else:
                query = query.order_by(asc(City.name))
        elif sort_by == 'created_at':
            if sort_order == 'desc':
                query = query.order_by(desc(HistoricSite.created_at))
            else:
                query = query.order_by(asc(HistoricSite.created_at))
        else:
            # Por defecto, ordenar por fecha de creación descendente
            query = query.order_by(desc(HistoricSite.created_at))
        
        # Obtener todos los sitios (sin paginación)
        sites = query.all()
        
        if not sites:
            raise exc.NotFoundError("No hay datos para exportar")
        
        # Crear el contenido CSV
        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        
        # Escribir encabezados
        headers = [
            'ID del sitio',
            'Nombre',
            'Descripción breve',
            'Ciudad',
            'Provincia',
            'Estado de conservación',
            'Fecha de registro',
            'Coordenadas de geolocalización',
            'Tags asociados'
        ]
        writer.writerow(headers)
        
        # Escribir datos
        for site in sites:
            # Obtener tags del sitio
            site_tags = []
            for tag_relation in site.tag_historic_sites:
                if not tag_relation.tag.deleted:
                    site_tags.append(tag_relation.tag.name)
            
            # Formatear coordenadas
            coordinates = f"{site.latitude},{site.longitude}"
            
            # Formatear fecha
            date_str = site.created_at.strftime('%Y-%m-%d %H:%M:%S') if site.created_at else ''
            
            # Escribir fila
            row = [
                site.id,
                site.name,
                site.brief_description,
                site.city.name if site.city else '',
                site.city.province.name if site.city and site.city.province else '',
                site.state_site.state if site.state_site else '',
                date_str,
                coordinates,
                '; '.join(site_tags)  # Separar tags con punto y coma
            ]
            writer.writerow(row)
        
        # Obtener el contenido CSV
        csv_content = output.getvalue()
        output.close()
        
        # Generar nombre del archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f'sitios_{timestamp}.csv'
        
        return csv_content, filename

# instancia de la clase HistoricSite_Service
historic_site_service = HistoricSite_Service()