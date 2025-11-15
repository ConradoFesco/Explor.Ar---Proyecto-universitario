from src.core.models.favorite_site import FavoriteSite
from src.core.models.historic_site import HistoricSite
from src.core.models.user import User
from src.web import exceptions as exc
from src.web.extensions import db
from src.core.validators.reviews_validator import validate_review_list_params


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
        if not user_id:
            raise exc.ValidationError("Usuario no autenticado")

        user = User.query.filter_by(id=user_id, deleted=False).first()
        if not user:
            raise exc.ValidationError("Usuario inválido")

        params = validate_review_list_params(page=page, per_page=per_page)
        page = params['page']
        per_page = params['per_page']

        query = FavoriteSite.query.filter_by(user_id=user_id).join(HistoricSite).filter(
            HistoricSite.deleted == False,
            HistoricSite.visible == True
        ).order_by(FavoriteSite.created_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        favorites = []
        for favorite in pagination.items:
            site = favorite.site
            favorites.append({
                'site_id': favorite.site_id,
                'marked_at': favorite.created_at.isoformat() if favorite.created_at else None,
                'site': {
                    'id': site.id,
                    'name': site.name,
                    'brief_description': site.brief_description,
                    'city_name': site.city.name if site.city else None,
                    'province_name': site.city.province.name if site.city and site.city.province else None,
                }
            })

        return {
            'favorites': favorites,
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


favorite_service = FavoriteService()

