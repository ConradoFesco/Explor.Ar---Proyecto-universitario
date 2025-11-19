from datetime import datetime
from sqlalchemy import func

from src.core.models.review import HistoricSiteReview
from src.core.models.historic_site import HistoricSite
from src.core.models.user import User
from src.web import exceptions as exc
from src.web.extensions import db
from src.core.validators.reviews_validator import (
    validate_review_list_params,
    validate_review_create_payload,
)
from src.core.validators.listing_validator import _validate_sort


class ReviewService:
    """Servicios para reseñas de sitios históricos."""

    def list_reviews(self, filters=None, page=1, per_page=25, sort_by='created_at', sort_order='desc'):
        """
        Lista reseñas con filtros, orden y paginación.
        Devuelve dict con items y pagination.
        Compatible con PostgreSQL.
        """
        # Validaciones de entrada
        pagination = validate_review_list_params(page=page, per_page=per_page)
        page = pagination['page']
        per_page = pagination['per_page']
        
        # Validar sort_by y sort_order
        allowed_sort_fields = ['created_at', 'rating', 'user_mail', 'site_name']
        sort_by, sort_order = _validate_sort(sort_by, sort_order, allowed_fields=allowed_sort_fields)
        
        # Normalizar filtros
        filters = filters or {}
        
        # Query base
        query = HistoricSiteReview.query.join(User).join(HistoricSite)

        # Aplicar filtros combinables
        if filters:
            if filters.get('status'):
                query = query.filter(HistoricSiteReview.status == filters['status'])
            if filters.get('site_id'):
                try:
                    site_id = int(filters['site_id'])
                    query = query.filter(HistoricSiteReview.site_id == site_id)
                except (ValueError, TypeError):
                    pass  # Ignorar site_id inválido
            if filters.get('rating_from') is not None:
                try:
                    rating_from = int(filters['rating_from'])
                    if 1 <= rating_from <= 5:
                        query = query.filter(HistoricSiteReview.rating >= rating_from)
                except (ValueError, TypeError):
                    pass  # Ignorar rating_from inválido
            if filters.get('rating_to') is not None:
                try:
                    rating_to = int(filters['rating_to'])
                    if 1 <= rating_to <= 5:
                        query = query.filter(HistoricSiteReview.rating <= rating_to)
                except (ValueError, TypeError):
                    pass  # Ignorar rating_to inválido
            if filters.get('date_from'):
                try:
                    date_from = datetime.fromisoformat(filters['date_from'].replace('Z', '+00:00'))
                    query = query.filter(HistoricSiteReview.created_at >= date_from)
                except (ValueError, AttributeError):
                    pass  # Ignorar date_from inválido
            if filters.get('date_to'):
                try:
                    date_to = datetime.fromisoformat(filters['date_to'].replace('Z', '+00:00'))
                    query = query.filter(HistoricSiteReview.created_at <= date_to)
                except (ValueError, AttributeError):
                    pass  # Ignorar date_to inválido
            if filters.get('user'):
                user_filter = str(filters['user']).strip()
                if user_filter:
                    query = query.filter(User.mail.ilike(f"%{user_filter}%"))

        # Contar total sin order_by (para evitar el error de PostgreSQL)
        total = query.with_entities(func.count(HistoricSiteReview.id)).scalar()

        # Aplicar orden dinámico solo para obtener los items
        if sort_by == 'created_at':
            query = query.order_by(HistoricSiteReview.created_at.desc() if sort_order == 'desc' else HistoricSiteReview.created_at.asc())
        elif sort_by == 'rating':
            query = query.order_by(HistoricSiteReview.rating.desc() if sort_order == 'desc' else HistoricSiteReview.rating.asc())
        elif sort_by == 'user_mail':
            query = query.order_by(User.mail.desc() if sort_order == 'desc' else User.mail.asc())
        elif sort_by == 'site_name':
            query = query.order_by(HistoricSite.name.desc() if sort_order == 'desc' else HistoricSite.name.asc())

        # Offset y limit manual para paginación
        items_query = query.offset((page - 1) * per_page).limit(per_page).all()

        # Construir lista de items
        items = []
        for review in items_query:
            items.append({
                'id': review.id,
                'site_id': review.site_id,
                'site_name': review.site.name,
                'user_id': review.user_id,
                'user_mail': review.user.mail,
                'rating': review.rating,
                'content': review.content,
                'status': review.status,
                'rejection_reason': review.rejection_reason,
                'created_at': review.created_at.isoformat() if review.created_at else None
            })

        # Construir objeto de paginación
        pages = (total + per_page - 1) // per_page  # ceil
        pagination = {
            'page': page,
            'pages': pages,
            'per_page': per_page,
            'total': total,
            'has_next': page < pages,
            'has_prev': page > 1,
            'next_num': page + 1 if page < pages else None,
            'prev_num': page - 1 if page > 1 else None
        }

        return {
            'items': items,
            'pagination': pagination
        }

    def create_review(self, *, site_id: int, user_id: int, rating, content):
        # Validar IDs
        try:
            site_id = int(site_id)
            if site_id <= 0:
                raise exc.ValidationError("site_id debe ser un entero positivo")
        except (ValueError, TypeError):
            raise exc.ValidationError("site_id debe ser un entero válido")
        
        try:
            user_id = int(user_id)
            if user_id <= 0:
                raise exc.ValidationError("user_id debe ser un entero positivo")
        except (ValueError, TypeError):
            raise exc.ValidationError("user_id debe ser un entero válido")

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
        # Validar IDs
        try:
            site_id = int(site_id)
            if site_id <= 0:
                raise exc.ValidationError("site_id debe ser un entero positivo")
        except (ValueError, TypeError):
            raise exc.ValidationError("site_id debe ser un entero válido")
        
        try:
            review_id = int(review_id)
            if review_id <= 0:
                raise exc.ValidationError("review_id debe ser un entero positivo")
        except (ValueError, TypeError):
            raise exc.ValidationError("review_id debe ser un entero válido")
        
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
        # Agregar site_name para el template
        data['site_name'] = review.site.name if review.site else None
        return data

    def approve_review(self, *, review_id: int) -> None:
        """Marca una reseña como aprobada.

        Lanza NotFoundError si no existe, ValidationError si ya está aprobada,
        y DatabaseError si falla el commit.
        """
        # Validar review_id
        try:
            review_id = int(review_id)
            if review_id <= 0:
                raise exc.ValidationError("review_id debe ser un entero positivo")
        except (ValueError, TypeError):
            raise exc.ValidationError("review_id debe ser un entero válido")
        
        review = HistoricSiteReview.query.get(review_id)
        if not review:
            raise exc.NotFoundError('Reseña no encontrada')
        if review.status == 'approved':
            raise exc.ValidationError('La reseña ya está aprobada')

        review.status = 'approved'
        try:
            db.session.add(review)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise exc.DatabaseError(f'Error al aprobar la reseña: {e}')

    def reject_review(self, *, review_id: int, reason: str) -> None:
        """Marca una reseña como rechazada y guarda el motivo.

        Valida longitud del motivo (<=200). Lanza errores claros en caso de
        entrada inválida, recurso no encontrado o fallo en BD.
        """
        # Validar review_id
        try:
            review_id = int(review_id)
            if review_id <= 0:
                raise exc.ValidationError("review_id debe ser un entero positivo")
        except (ValueError, TypeError):
            raise exc.ValidationError("review_id debe ser un entero válido")
        
        # Validar reason
        if not reason or not reason.strip():
            raise exc.ValidationError('Motivo de rechazo requerido')
        reason = reason.strip()
        if len(reason) > 200:
            raise exc.ValidationError('Motivo de rechazo demasiado largo (max 200)')

        review = HistoricSiteReview.query.get(review_id)
        if not review:
            raise exc.NotFoundError('Reseña no encontrada')
        if review.status == 'rejected':
            raise exc.ValidationError('La reseña ya está rechazada')

        review.status = 'rejected'
        # Guardar motivo si la columna existe
        if hasattr(review, 'rejection_reason'):
            review.rejection_reason = reason

        try:
            db.session.add(review)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise exc.DatabaseError(f'Error al rechazar la reseña: {e}')

    def delete_review_admin(self, *, review_id: int) -> None:
        """Elimina lógicamente una reseña (acción administrativa): status -> 'deleted'.

        Lanza NotFoundError si no existe y DatabaseError si falla el commit.
        """
        # Validar review_id
        try:
            review_id = int(review_id)
            if review_id <= 0:
                raise exc.ValidationError("review_id debe ser un entero positivo")
        except (ValueError, TypeError):
            raise exc.ValidationError("review_id debe ser un entero válido")
        
        review = HistoricSiteReview.query.get(review_id)
        if not review:
            raise exc.NotFoundError('Reseña no encontrada')
        if review.status == 'deleted':
            raise exc.ValidationError('La reseña ya está eliminada')
        review.status = 'deleted'
        try:
            db.session.add(review)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise exc.DatabaseError(f'Error al eliminar la reseña: {e}')

review_service = ReviewService()