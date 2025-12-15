from typing import Optional
from src.core.models.favorite_site import FavoriteSite
from src.core.models.historic_site import HistoricSite
from src.core.models.tag import Tag
from src.core.models.tag_historic_site import TagHistoricSite
from src.web import exceptions as exc
from src.web.extensions import db
from src.core.validators.listing_validator import _validate_pagination
from src.core.validators.user_validator import validate_user_exists
from src.core.validators.site_validator import validate_site_exists
from src.core.services.site_image_service import site_image_service


class FavoriteService:
    """Servicios para favoritos de sitios históricos."""

    def mark_favorite(self, *, site_id: int, user_id: int):
        validate_user_exists(user_id)
        validate_site_exists(site_id, must_be_visible=True)

        existing = FavoriteSite.query.filter_by(site_id=site_id, user_id=user_id).first()
        if existing:
            return existing

        favorite = FavoriteSite(site_id=site_id, user_id=user_id)
        try:
            db.session.add(favorite)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al marcar favorito: {e}")

        return favorite

    def unmark_favorite(self, *, site_id: int, user_id: int):
        validate_user_exists(user_id)
        validate_site_exists(site_id, must_be_visible=True)

        favorite = FavoriteSite.query.filter_by(site_id=site_id, user_id=user_id).first()
        if not favorite:
            return False

        try:
            db.session.delete(favorite)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al eliminar favorito: {e}")

        return True

    def list_favorites(self, *, user_id: int, page: Optional[int] = None, per_page: Optional[int] = None):
        """
        Lista los sitios favoritos del usuario autenticado.

        Retorna en el formato de la API pública:
        {
            "data": [...],
            "meta": {
                "page": int,
                "per_page": int,
                "total": int
            }
        }
        Información adicional no especificada en la API:
        - rating: Calificación promedio del sitio (number, opcional)
        - cover_image_url: URL de la imagen de portada (string, opcional)
        - is_favorite: Siempre true para este endpoint (boolean)
        """
        validate_user_exists(user_id)

        page, per_page = _validate_pagination(
            page, per_page, default_page=1, default_per_page=20, max_per_page=100
        )

        query = FavoriteSite.query.filter_by(user_id=user_id).join(HistoricSite).filter(
            HistoricSite.deleted == False,
            HistoricSite.visible == True
        ).order_by(FavoriteSite.created_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        data = []
        for favorite in pagination.items:
            site = favorite.site
            site_id = site.id

            site_tags = (
                Tag.query.join(TagHistoricSite)
                .filter(
                    TagHistoricSite.Historic_Site_id == site_id,
                    Tag.deleted == False,
                )
                .all()
            )
            tags = [t.slug for t in site_tags]

            cover_image = site_image_service.get_cover_image(site_id)

            site_lat = float(site.latitude) if site.latitude is not None else None
            site_lon = float(site.longitude) if site.longitude is not None else None

            inserted_at = (
                favorite.created_at.isoformat() if favorite.created_at else None
            )
            updated_at = (
                site.updated_at.isoformat() if hasattr(site, 'updated_at') and site.updated_at else 
                (site.created_at.isoformat() if site.created_at else inserted_at)
            )

            data.append(
                {
                    "id": site_id,
                    "name": site.name,
                    "short_description": site.brief_description,
                    "description": site.complete_description,
                    "city": site.city.name if site.city else None,
                    "province": site.city.province.name
                    if site.city and site.city.province
                    else None,
                    "country": "AR",
                    "lat": site_lat,
                    "long": site_lon,
                    "tags": tags,
                    "state_of_conservation": site.state_site.state
                    if getattr(site, "state_site", None)
                    else None,
                    "inserted_at": inserted_at,
                    "updated_at": updated_at,
                    "cover_image_url": cover_image["url_publica"]
                    if cover_image
                    else None,
                    "is_favorite": True,
                }
            )

        return {
            "data": data,
            "meta": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
            },
        }


favorite_service = FavoriteService()