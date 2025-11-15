from src.core.models.review import HistoricSiteReview
from src.core.models.historic_site import HistoricSite
from src.core.models.user import User
from src.web import exceptions as exc
from src.web.extensions import db
from src.core.validators.reviews_validator import (
    validate_review_list_params,
    validate_review_create_payload,
)


class ReviewService:
    """Servicios para reseñas de sitios históricos."""

    def list_reviews(self, *, site_id: int, page: int = 1, per_page: int = 25):
        params = validate_review_list_params(page=page, per_page=per_page)
        page = params['page']
        per_page = params['per_page']

        site = HistoricSite.query.filter_by(id=site_id, deleted=False).first()
        if not site:
            raise exc.NotFoundError("Sitio histórico no encontrado")

        query = HistoricSiteReview.query.filter_by(site_id=site_id).order_by(HistoricSiteReview.created_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        review_items = []
        for review in pagination.items:
            user = User.query.get(review.user_id)
            review_items.append({
                'id': review.id,
                'site_id': review.site_id,
                'user': {
                    'id': user.id if user else None,
                    'mail': user.mail if user else None,
                    'name': user.name if user else None
                },
                'rating': review.rating,
                'content': review.content,
                'status': review.status,
                'created_at': review.created_at.isoformat() if review.created_at else None
            })

        return {
            'reviews': review_items,
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

    def create_review(self, *, site_id: int, user_id: int, rating, content):
        if not user_id:
            raise exc.ValidationError("Usuario no autenticado")

        site = HistoricSite.query.filter_by(id=site_id, deleted=False).first()
        if not site:
            raise exc.NotFoundError("Sitio histórico no encontrado")

        user = User.query.filter_by(id=user_id, deleted=False).first()
        if not user:
            raise exc.ValidationError("Usuario no válido")

        payload = validate_review_create_payload(rating=rating, content=content)

        review = HistoricSiteReview(
            site_id=site_id,
            user_id=user_id,
            rating=payload['rating'],
            content=payload['content'],
            status='pending',
        )

        try:
            db.session.add(review)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al crear la reseña: {error}")

        return review

    def get_review(self, *, site_id: int, review_id: int, current_user_id: int | None = None):
        site = HistoricSite.query.filter_by(id=site_id, deleted=False).first()
        if not site:
            raise exc.NotFoundError("Sitio histórico no encontrado")

        review = HistoricSiteReview.query.filter_by(id=review_id, site_id=site_id).first()
        if not review:
            raise exc.NotFoundError("Reseña no encontrada")

        if current_user_id and review.user_id != current_user_id:
            raise exc.ForbiddenError("No tiene acceso a esta reseña")

        user = User.query.get(review.user_id)
        data = review.to_dict()
        data['user'] = {
            'id': user.id if user else None,
            'mail': user.mail if user else None,
            'name': user.name if user else None
        }
        return data

    def delete_review(self, *, site_id: int, review_id: int, current_user_id: int | None = None):
        site = HistoricSite.query.filter_by(id=site_id, deleted=False).first()
        if not site:
            raise exc.NotFoundError("Sitio histórico no encontrado")

        review = HistoricSiteReview.query.filter_by(id=review_id, site_id=site_id).first()
        if not review:
            raise exc.NotFoundError("Reseña no encontrada")

        if current_user_id and review.user_id != current_user_id:
            raise exc.ForbiddenError("No tiene permiso para eliminar esta reseña")

        try:
            db.session.delete(review)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al eliminar la reseña: {error}")


review_service = ReviewService()