from src.core.models.favorite_site import FavoriteSite
from src.core.models.historic_site import HistoricSite
from src.core.models.user import User
from src.web import exceptions as exc
from src.web.extensions import db
from src.core.validators.listing_validator import _validate_pagination


class FavoriteService:
    """Servicios para favoritos de sitios históricos."""

    def mark_favorite(self, *, site_id: int, user_id: int):
        if not user_id:
            raise exc.ValidationError("Usuario no autenticado")

        site = HistoricSite.query.filter_by(id=site_id, deleted=False, visible=True).first()
        if not site:
            raise exc.NotFoundError("Sitio histórico no encontrado")

        user = User.query.filter_by(id=user_id, deleted=False).first()
        if not user:
            raise exc.ValidationError("Usuario inválido")

        existing = FavoriteSite.query.filter_by(site_id=site_id, user_id=user_id).first()
        if existing:
            return existing

        favorite = FavoriteSite(site_id=site_id, user_id=user_id)
        try:
            db.session.add(favorite)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al marcar favorito: {error}")

        return favorite

    def unmark_favorite(self, *, site_id: int, user_id: int):
        if not user_id:
            raise exc.ValidationError("Usuario no autenticado")

        site = HistoricSite.query.filter_by(id=site_id, deleted=False, visible=True).first()
        if not site:
            raise exc.NotFoundError("Sitio histórico no encontrado")

        favorite = FavoriteSite.query.filter_by(site_id=site_id, user_id=user_id).first()
        if not favorite:
            return False

        try:
            db.session.delete(favorite)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al eliminar favorito: {error}")

        return True

    def list_favorites(self, *, user_id: int, page: int = 1, per_page: int = 20):
        """
        Lista los sitios favoritos del usuario en formato compatible con el frontend.
        
        Returns:
            dict: {
                'items': [sitios en formato HistoricSite],
                'total': int,
                'total_pages': int,
                'page': int,
                'per_page': int
            }
        """
        if not user_id:
            raise exc.ValidationError("Usuario no autenticado")

        user = User.query.filter_by(id=user_id, deleted=False).first()
        if not user:
            raise exc.ValidationError("Usuario inválido")

        # Validar paginación; ante valores inválidos se lanza ValidationError (no se toman defaults).
        page, per_page = _validate_pagination(page, per_page, max_per_page=50)

        query = FavoriteSite.query.filter_by(user_id=user_id).join(HistoricSite).filter(
            HistoricSite.deleted == False,
            HistoricSite.visible == True
        ).order_by(FavoriteSite.created_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        from src.core.services.site_image_service import site_image_service
        from src.core.models.tag import Tag
        from src.core.models.tag_historic_site import TagHistoricSite

        items = []
        for favorite in pagination.items:
            site = favorite.site
            site_id = site.id
            
            site_tags = Tag.query.join(TagHistoricSite).\
                filter(TagHistoricSite.Historic_Site_id == site_id, Tag.deleted == False).all()
            tags = [t.slug for t in site_tags]
            
            cover_image = site_image_service.get_cover_image(site_id)
            
            site_lat = float(site.latitude) if site.latitude is not None else None
            site_lon = float(site.longitude) if site.longitude is not None else None
            
            items.append({
                'id': site_id,
                'name': site.name,
                'brief_description': site.brief_description,
                'complete_description': site.complete_description,
                'city': site.city.name if site.city else None,
                'province': site.city.province.name if site.city and site.city.province else None,
                'latitude': site_lat,
                'longitude': site_lon,
                'created_at': site.created_at.isoformat() if site.created_at else None,
                'tags': tags,
                'rating': None,
                'cover_image': cover_image,
                'cover_image_url': cover_image['url_publica'] if cover_image else None,
                'is_favorite': True
            })

        return {
            'items': items,
            'total': pagination.total,
            'total_pages': pagination.pages,
            'page': pagination.page,
            'per_page': pagination.per_page
        }


favorite_service = FavoriteService()

