"""
Servicios de dominio para Sitios Históricos: CRUD, listados, filtros, tags y exportación.
Usado por Web y API; retorna estructuras Python puras (dict/list).
"""
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
from src.core.validators.site_validator import validate_create_site, validate_update_site
import csv
import io
import math


class HistoricSiteService:
    """Casos de uso de sitios históricos (crear, obtener, listar, actualizar, tags, exportar)."""
    def create_historic_site(self, data_site, data_user):
        """
        Crea un sitio histórico y registra evento de creación.

        Args:
            data_site (dict): Campos del sitio (name, brief_description, name_city, name_province,
                latitude, longitude, id_category, visible, id_estado?, year_inauguration?, tag_ids?).
            data_user (int): ID del usuario actor.

        Returns:
            HistoricSite: Objeto sitio creado.

        Raises:
            ValidationError: Si faltan campos o datos inválidos.
            DatabaseError: Si falla la persistencia.
        """
        required_fields = ['name', 'brief_description', 'name_city', 'name_province', 'latitude', 'longitude', 'id_category', 'visible']
        if ( not all(field in data_site for field in required_fields)):
            raise exc.ValidationError("Faltan campos obligatorios del sitio histórico: Nombre, descripción, ciudad, latitud, longitud, categoría y visible")
        id_user = data_user
        if not id_user:
            raise exc.ValidationError("Usuario no autenticado. Por favor, inicie sesión.")
        validated = validate_create_site(data_site)
        name = validated.get('name')
        brief_description = validated.get('brief_description')
        complete_description = validated.get('complete_description')
        name_city = validated.get('name_city')
        name_province = validated.get('name_province')
        latitude = validated.get('latitude')
        longitude = validated.get('longitude')
        id_estado = validated.get('id_estado')
        year_inauguration = validated.get('year_inauguration')
        id_category = validated.get('id_category')
        visible = validated.get('visible')
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
        """
        Obtiene un sitio histórico con datos relacionados y tags.

        Args:
            id (int): ID del sitio.

        Returns:
            dict: Representación del sitio con relaciones y tags.

        Raises:
            NotFoundError: Si no existe.
        """
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
        
        # Agregar información de tags (solo no eliminados) usando consulta
        from src.core.models.tag import Tag
        site_tags = Tag.query.join(TagHistoricSite).\
            filter(TagHistoricSite.Historic_Site_id == site.id, Tag.deleted == False).all()
        site_data['tags'] = [{ 'id': t.id, 'name': t.name, 'slug': t.slug } for t in site_tags]
        
        # Agregar información de relaciones usando los joins
        site_data['city_name'] = site.city.name if hasattr(site, 'city') and site.city else None
        site_data['province_name'] = site.city.province.name if hasattr(site, 'city') and site.city and site.city.province else None
        site_data['state_name'] = site.state_site.state if hasattr(site, 'state_site') and site.state_site else None
        site_data['category_name'] = site.category.name if hasattr(site, 'category') and site.category else None
        
        # Agregar imágenes del sitio
        from src.core.services.site_image_service import site_image_service
        site_data['images'] = site_image_service.get_images_by_site(site.id)
        
        # Agregar imagen portada (si existe) con URL firmada
        site_data['cover_image'] = site_image_service.get_cover_image(site.id)
        
        # si se encuentra el sitio histórico, devuelve el sitio histórico
        return site_data
    
    def get_all_historic_sites(self, include_deleted=False, page=1, per_page=25, 
                              search_text=None, sort_by='created_at', sort_order='desc',
                              city_id=None, province_id=None, tag_ids=None, 
                              state_id=None, date_from=None, date_to=None, 
                              visible=None): 
        """
        Lista sitios con paginación, filtros y orden.

        Args: ver parámetros.

        Returns:
            dict: {'sites': [...], 'pagination': {...}}
        """
        from sqlalchemy import and_, or_, desc, asc, func
        
        # Validaciones de entrada
        from src.core.validators.listing_validator import validate_site_list_params
        params = validate_site_list_params(
            page=page, per_page=per_page, search_text=search_text, sort_by=sort_by, sort_order=sort_order,
            city_id=city_id, province_id=province_id, tag_ids=tag_ids, state_id=state_id,
            date_from=date_from, date_to=date_to, visible=visible,
        )
        page = params['page']; per_page = params['per_page']; search_text = params['search_text']
        sort_by = params['sort_by']; sort_order = params['sort_order']; city_id = params['city_id']
        province_id = params['province_id']; tag_ids = params['tag_ids']; state_id = params['state_id']
        date_from = params['date_from']; date_to = params['date_to']; visible = params['visible']

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
        
        # Filtro por tags (multiselección): deben contener TODOS los seleccionados
        if tag_ids and len(tag_ids) > 0:
            tags_subq = (
                db.session.query(TagHistoricSite.Historic_Site_id)
                .filter(TagHistoricSite.Tag_id.in_(tag_ids))
                .group_by(TagHistoricSite.Historic_Site_id)
                .having(func.count(func.distinct(TagHistoricSite.Tag_id)) == len(tag_ids))
                .subquery()
            )
            query = query.filter(HistoricSite.id.in_(tags_subq))
        
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
            site_tags = self._get_site_tags(site.id)
            # Obtener imagen portada con URL firmada
            from src.core.services.site_image_service import site_image_service
            cover_image = site_image_service.get_cover_image(site.id)
            sites_data.append({
                'id': site.id, 
                'name': site.name, 
                'brief_description': site.brief_description,
                'created_at': site.created_at.isoformat() if site.created_at else None,
                'city_name': site.city.name if site.city else None,
                'province_name': site.city.province.name if site.city and site.city.province else None,
                'state_name': site.state_site.state if site.state_site else None,
                'visible': site.visible,
                'tags': site_tags,
                'cover_image': cover_image
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
        """
        Actualiza campos de un sitio histórico y registra evento UPDATE.

        Args:
            id (int): ID del sitio.
            data_site (dict): Campos a actualizar.
            data_user (int): ID del usuario actor.

        Returns:
            HistoricSite: Objeto actualizado.

        Raises:
            NotFoundError: Si no existe.
            DatabaseError: Si falla la persistencia.
        """
        historic_site = HistoricSite.query.get(id)
        # si no se encuentra el sitio histórico, devuelve un error 404
        if historic_site is None:
            raise exc.NotFoundError("Sitio histórico no encontrado")
        # Validaciones de entrada parcial
        cleaned = validate_update_site(data_site or {})

        # si se encuentra el sitio histórico, actualiza el sitio histórico
        historic_site.name = cleaned.get('name', historic_site.name)
        historic_site.brief_description = cleaned.get('brief_description', historic_site.brief_description)
        historic_site.complete_description = cleaned.get('complete_description', historic_site.complete_description)
        historic_site.id_ciudad = cleaned.get('id_ciudad', historic_site.id_ciudad)
        historic_site.latitude = cleaned.get('latitude', historic_site.latitude)
        historic_site.longitude = cleaned.get('longitude', historic_site.longitude)
        historic_site.id_estado = cleaned.get('id_estado', historic_site.id_estado)
        historic_site.year_inauguration = cleaned.get('year_inauguration', historic_site.year_inauguration)
        historic_site.id_category = cleaned.get('id_category', historic_site.id_category)
        historic_site.deleted = cleaned.get('deleted', historic_site.deleted)
        historic_site.visible = cleaned.get('visible', historic_site.visible)
        
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
        """
        Baja lógica de un sitio y registra evento DELETE.

        Args:
            id (int): ID del sitio.
            data_user (int): ID del usuario actor.

        Returns:
            HistoricSite: Objeto modificado.

        Raises:
            NotFoundError: Si no existe.
            DatabaseError: Si falla la persistencia.
        """
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
        """
        Agrega tags a un sitio evitando duplicados. Opcionalmente registra evento UPDATE.

        Args:
            site_id (int): ID del sitio.
            tag_ids_list (list[int]): IDs de tags a agregar.
            data_user (int): ID del actor.
            event_action (bool): Si True, crea evento.

        Returns:
            dict: {'site': HistoricSite, 'added_tags': [...], 'skipped_tags': [...], 'message': str}

        Raises:
            ValidationError/NotFoundError/DatabaseError según corresponda.
        """
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
        """
        Reemplaza completamente los tags de un sitio histórico.

        Args:
            site_id (int): ID del sitio.
            new_tag_ids (list[int]): Lista final de tags.
            data_user (int): ID del actor.

        Returns:
            dict: Resumen con agregados y removidos.

        Raises:
            ValidationError/NotFoundError/DatabaseError según corresponda.
        """
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
        """
        Devuelve sitios con lat/long para mapa, con paginación.

        Args:
            include_deleted (bool): Incluir eliminados.
            page (int): Página.
            per_page (int): Tamaño de página.

        Returns:
            dict: {'sites': [...], 'pagination': {...}}
        """
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
            site_tags = self._get_site_tags(site.id)
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

    def search_public_sites(self, *, name=None, description=None, city=None, province=None,
                            tags=None, order_by='latest', latitude=None, longitude=None,
                            radius_km=None, page=1, per_page=25):
        """
        Devuelve sitios visibles para el portal público respetando filtros estandarizados.
        """
        from sqlalchemy import asc, desc, func, literal, or_, cast, Float

        tags = tags or []
        query = HistoricSite.query.join(City).join(Province)
        query = query.filter(HistoricSite.deleted == False, HistoricSite.visible == True)

        # Búsqueda por texto: busca en nombre O descripción (OR, no AND)
        # Si ambos parámetros están presentes, se usa el mismo texto para ambos
        search_text = name or description
        if search_text:
            # Búsqueda "comienza con" (no "contiene")
            like_pattern = f"{search_text}%"
            query = query.filter(or_(
                HistoricSite.name.ilike(like_pattern),
                HistoricSite.brief_description.ilike(like_pattern),
            ))

        if city:
            query = query.filter(func.lower(City.name) == city.lower())

        if province:
            query = query.filter(func.lower(Province.name) == province.lower())

        if tags:
            normalized_tags = [slug.lower() for slug in tags]
            tags_subquery = (
                db.session.query(TagHistoricSite.Historic_Site_id)
                .join(Tag, TagHistoricSite.Tag_id == Tag.id)
                .filter(func.lower(Tag.slug).in_(normalized_tags))
                .group_by(TagHistoricSite.Historic_Site_id)
                .having(func.count(func.distinct(Tag.id)) == len(normalized_tags))
                .subquery()
            )
            query = query.filter(HistoricSite.id.in_(tags_subquery))

        if latitude is not None and longitude is not None and radius_km is not None:
            lat_col = cast(HistoricSite.latitude, Float)
            lon_col = cast(HistoricSite.longitude, Float)
            km_per_lat = 111.32
            km_per_lon = max(abs(111.32 * math.cos(math.radians(latitude))), 1e-6)
            distance_expr = func.sqrt(
                func.pow((lat_col - latitude) * km_per_lat, 2) +
                func.pow((lon_col - longitude) * km_per_lon, 2)
            )
            query = query.filter(distance_expr <= radius_km)

        if order_by == 'latest':
            query = query.order_by(desc(HistoricSite.created_at))
        elif order_by == 'oldest':
            query = query.order_by(asc(HistoricSite.created_at))
        elif order_by == 'rating-5-1':
            rating_expr = literal(0)
            query = query.order_by(desc(rating_expr), desc(HistoricSite.created_at))
        elif order_by == 'rating-1-5':
            rating_expr = literal(0)
            query = query.order_by(asc(rating_expr), desc(HistoricSite.created_at))
        else:
            query = query.order_by(desc(HistoricSite.created_at))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        sites_payload = []
        # Importar el servicio de imágenes una sola vez
        from src.core.services.site_image_service import site_image_service
        
        for site in pagination.items:
            site_lat = self._safe_float(site.latitude)
            site_lon = self._safe_float(site.longitude)
            distance_value = None
            if latitude is not None and longitude is not None and site_lat is not None and site_lon is not None:
                distance_value = self._distance_between(latitude, longitude, site_lat, site_lon)

            # Obtener imagen portada con URL firmada
            cover_image = site_image_service.get_cover_image(site.id)
            
            site_data = {
                'id': site.id,
                'name': site.name,
                'brief_description': site.brief_description,
                'complete_description': site.complete_description,
                'city': site.city.name if site.city else None,
                'province': site.city.province.name if site.city and site.city.province else None,
                'latitude': site_lat,
                'longitude': site_lon,
                'created_at': site.created_at.isoformat() if site.created_at else None,
                'tags': self._get_site_tags(site.id),
                'rating': None,
                'cover_image': cover_image,
                'cover_image_url': cover_image['url_publica'] if cover_image else None
            }
            if distance_value is not None:
                site_data['distance_km'] = round(distance_value, 3)

            sites_payload.append(site_data)

        return {
            'sites': sites_payload,
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

    def _get_site_tags(self, site_id: int) -> list[dict]:
        """Obtiene los tags activos asociados a un sitio histórico."""
        tags_q = Tag.query.join(TagHistoricSite).\
            filter(
                TagHistoricSite.Historic_Site_id == site_id,
                Tag.deleted == False
            ).all()
        return [{'id': t.id, 'name': t.name, 'slug': t.slug} for t in tags_q]

    @staticmethod
    def _safe_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _distance_between(lat1, lon1, lat2, lon2):
        """Calcula distancia Haversine aproximada en KM."""
        from math import radians, sin, cos, sqrt, atan2

        if lat2 is None or lon2 is None:
            return None

        r = 6371.0
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return r * c

    def get_filter_options(self):
        """
        Obtiene opciones de filtros (ciudades, provincias, tags, estados).

        Returns:
            dict: {'cities': [...], 'provinces': [...], 'tags': [...], 'states': [...]}
        """
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
        Exporta sitios históricos a CSV respetando filtros.

        Returns:
            tuple[str, str]: (contenido_csv, nombre_archivo)
        """
        from sqlalchemy import and_, or_, desc, asc, func
        # Validaciones de entrada (mismos parámetros que el listado)
        from src.core.validators.listing_validator import validate_site_list_params
        params = validate_site_list_params(
            page=1, per_page=25, search_text=search_text, sort_by=sort_by, sort_order=sort_order,
            city_id=city_id, province_id=province_id, tag_ids=tag_ids, state_id=state_id,
            date_from=date_from, date_to=date_to, visible=visible,
        )
        search_text = params['search_text']; sort_by = params['sort_by']; sort_order = params['sort_order']
        city_id = params['city_id']; province_id = params['province_id']; tag_ids = params['tag_ids']
        state_id = params['state_id']; date_from = params['date_from']; date_to = params['date_to']
        visible = params['visible']
        
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
        
        # Filtro por tags (multiselección): deben contener TODOS los seleccionados
        if tag_ids and len(tag_ids) > 0:
            tags_subq = (
                db.session.query(TagHistoricSite.Historic_Site_id)
                .filter(TagHistoricSite.Tag_id.in_(tag_ids))
                .group_by(TagHistoricSite.Historic_Site_id)
                .having(func.count(func.distinct(TagHistoricSite.Tag_id)) == len(tag_ids))
                .subquery()
            )
            query = query.filter(HistoricSite.id.in_(tags_subq))
        
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
            site_tags = [tag['name'] for tag in self._get_site_tags(site.id)]
            
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


# instancia de la clase HistoricSiteService
historic_site_service = HistoricSiteService()


