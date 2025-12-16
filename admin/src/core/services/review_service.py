from datetime import datetime
from sqlalchemy import func, or_
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
from src.core.validators.api_validator import validate_positive_int
from src.core.validators.user_validator import validate_user_exists
from src.core.services.flag_service import flag_service


class ReviewService:
    def _has_existing_review(self, site_id: int, user_id: int) -> bool:
        """
        Verifica si el usuario ya tiene una reseña pendiente o aprobada para el sitio.
        
        Args:
            site_id: ID del sitio histórico
            user_id: ID del usuario
            
        Returns:
            bool: True si existe una reseña pendiente o aprobada, False en caso contrario
        """
        from sqlalchemy import and_
        existing_review = HistoricSiteReview.query.filter(
            and_(
                HistoricSiteReview.site_id == site_id,
                HistoricSiteReview.user_id == user_id,
                HistoricSiteReview.status.in_(['pending', 'approved']),
            )
        ).first()
        return existing_review is not None

    def list_reviews(self, *, page=None, per_page=None, sort_by=None, sort_order=None,
                     status=None, site_id=None,
                     user=None, rating_from=None, rating_to=None,
                     date_from=None, date_to=None,
                     user_id: int | None = None,
                     only_approved: bool = False,
                     include_user_pending: int | None = None) -> dict:
        """
        Lista reseñas con filtros, orden y paginación.
        Valida todos los parámetros mediante `validate_review_list_params` y
        devuelve un diccionario con `items` y `pagination`.
        
        Args:
            page: Número de página (opcional)
            per_page: Elementos por página (opcional)
            sort_by: Campo por el cual ordenar (opcional)
            sort_order: Dirección del orden (opcional)
            status: Estado de la reseña (opcional: 'pending', 'approved', 'rejected')
            site_id: ID del sitio (opcional)
            user: Email del usuario (opcional)
            rating_from: Calificación mínima (opcional)
            rating_to: Calificación máxima (opcional)
            date_from: Fecha desde (opcional)
            date_to: Fecha hasta (opcional)
            user_id: ID del usuario para filtrar (opcional)
            only_approved: Si True, solo muestra reseñas aprobadas
            include_user_pending: Si se proporciona un user_id, incluye la reseña pendiente
                de ese usuario incluso cuando only_approved=True
                
        Returns:
            dict: Diccionario con 'items' (lista de reseñas) y 'pagination' (info de paginación)
            
        Raises:
            ValidationError: Si los parámetros son inválidos
        """
        params = validate_review_list_params(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            status=status,
            site_id=site_id,
            user=user,
            rating_from=rating_from,
            rating_to=rating_to,
            date_from=date_from,
            date_to=date_to,
        )

        page = params['page']
        per_page = params['per_page']
        sort_by = params['sort_by']
        sort_order = params['sort_order']
        filters = params['filters'] or {}

        query = HistoricSiteReview.query.join(User).join(HistoricSite)

        if only_approved:
            if include_user_pending is not None:
                query = query.filter(
                    or_(
                        HistoricSiteReview.status == 'approved',
                        (HistoricSiteReview.status == 'pending') &
                        (HistoricSiteReview.user_id == include_user_pending)
                    )
                )
            else:
                query = query.filter(HistoricSiteReview.status == 'approved')

        if user_id is not None:
            user_id_int = validate_positive_int(user_id, "user_id")
            query = query.filter(HistoricSiteReview.user_id == user_id_int)

        if 'status' in filters:
            query = query.filter(HistoricSiteReview.status == filters['status'])

        if 'site_id' in filters and filters['site_id'] is not None:
            query = query.filter(HistoricSiteReview.site_id == filters['site_id'])

        if 'rating_from' in filters and filters['rating_from'] is not None:
            query = query.filter(HistoricSiteReview.rating >= filters['rating_from'])

        if 'rating_to' in filters and filters['rating_to'] is not None:
            query = query.filter(HistoricSiteReview.rating <= filters['rating_to'])

        if 'date_from' in filters and filters['date_from'] is not None:
            query = query.filter(HistoricSiteReview.created_at >= filters['date_from'])

        if 'date_to' in filters and filters['date_to'] is not None:
            query = query.filter(HistoricSiteReview.created_at <= filters['date_to'])

        if 'user' in filters and filters['user']:
            user_filter = filters['user']
            query = query.filter(User.mail.ilike(f"{user_filter}%"))

        total = query.with_entities(func.count(HistoricSiteReview.id)).scalar()

        if sort_by == 'created_at':
            query = query.order_by(
                HistoricSiteReview.created_at.desc()
                if sort_order == 'desc'
                else HistoricSiteReview.created_at.asc()
            )
        elif sort_by == 'rating':
            query = query.order_by(
                HistoricSiteReview.rating.desc()
                if sort_order == 'desc'
                else HistoricSiteReview.rating.asc()
            )
        elif sort_by == 'user_mail':
            query = query.order_by(
                User.mail.desc() if sort_order == 'desc' else User.mail.asc()
            )
        elif sort_by == 'site_name':
            query = query.order_by(
                HistoricSite.name.desc() if sort_order == 'desc' else HistoricSite.name.asc()
            )

        items_query = query.offset((page - 1) * per_page).limit(per_page).all()

        items: list[dict] = []
        for review in items_query:
            user_obj = review.user
            items.append(
                {
                    'id': review.id,
                    'site_id': review.site_id,
                    'site_name': review.site.name,
                    'user': {
                        'id': user_obj.id if user_obj else None,
                        'name': user_obj.name if user_obj else None,
                    },
                    'user_mail': user_obj.mail if user_obj else None,
                    'rating': review.rating,
                    'content': review.content,
                    'status': review.status,
                    'rejection_reason': review.rejection_reason,
                    'created_at': review.created_at.isoformat()
                    if review.created_at
                    else None,
                    'updated_at': review.updated_at.isoformat()
                    if review.updated_at
                    else None,
                }
            )

        pages = (total + per_page - 1) // per_page
        pagination = {
            'page': page,
            'pages': pages,
            'per_page': per_page,
            'total': total,
            'has_next': page < pages,
            'has_prev': page > 1,
            'next_num': page + 1 if page < pages else None,
            'prev_num': page - 1 if page > 1 else None,
        }

        return {
            'items': items,
            'pagination': pagination,
        }

    def create_review(self, *, site_id: int, user_id: int, rating, content):
        """
        Crea una nueva reseña para un sitio histórico.
        
        Args:
            site_id: ID del sitio histórico
            user_id: ID del usuario que crea la reseña
            rating: Calificación (1-5)
            content: Contenido de la reseña
            
        Returns:
            HistoricSiteReview: Reseña creada
            
        Raises:
            ValidationError: Si las reseñas están deshabilitadas, ya existe una reseña,
                o los datos son inválidos
            NotFoundError: Si el sitio histórico o usuario no existen
            DatabaseError: Si hay un error al persistir en la base de datos
        """
        if not flag_service.is_reviews_enabled():
            raise exc.ValidationError("Las reseñas están temporalmente deshabilitadas")
        
        site_id = validate_positive_int(site_id, "site_id")
        user_id = validate_positive_int(user_id, "user_id")

        site = HistoricSite.query.filter_by(id=site_id, deleted=False).first()
        if not site:
            raise exc.NotFoundError("Sitio histórico no encontrado")

        validate_user_exists(user_id)

        if self._has_existing_review(site_id, user_id):
            raise exc.ValidationError("Ya existe una reseña para este sitio. Use la opción de editar.")

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
        except Exception as e:
            db.session.rollback()
            error_str = str(e).lower()
            if 'unique' in error_str or 'duplicate' in error_str or 'constraint' in error_str:
                if self._has_existing_review(site_id, user_id):
                    raise exc.ValidationError("Ya existe una reseña para este sitio. Use la opción de editar.")
            raise exc.DatabaseError(f"Error al crear la reseña: {e}")

        return review

    def get_review(self, *, site_id: int, review_id: int, current_user_id: int | None = None, skip_ownership_validation: bool = False):
        """
        Obtiene una reseña específica por su ID y sitio.
        
        Args:
            site_id: ID del sitio histórico
            review_id: ID de la reseña
            current_user_id: ID del usuario actual (opcional, para validar propiedad)
            skip_ownership_validation: Si True, omite la validación de propiedad
            
        Returns:
            dict: Diccionario con los datos de la reseña y relaciones
            
        Raises:
            NotFoundError: Si el sitio o la reseña no existen
            ForbiddenError: Si el usuario no tiene acceso a la reseña
        """
        site_id = validate_positive_int(site_id, "site_id")
        review_id = validate_positive_int(review_id, "review_id")
        
        site = HistoricSite.query.filter_by(id=site_id, deleted=False).first()
        if not site:
            raise exc.NotFoundError("Sitio histórico no encontrado")

        review = HistoricSiteReview.query.filter_by(id=review_id, site_id=site_id).first()
        if not review:
            raise exc.NotFoundError("Reseña no encontrada")

        if not skip_ownership_validation and current_user_id is not None and review.user_id != current_user_id:
            raise exc.ForbiddenError("No tiene acceso a esta reseña")

        return self._build_review_dict(review)
    
    def _build_review_dict(self, review):
        """
        Construye un diccionario con los datos de una reseña y sus relaciones.
        
        Args:
            review: Objeto HistoricSiteReview
            
        Returns:
            dict: Diccionario con los datos de la reseña, usuario y sitio
        """
        user = review.user
        data = review.to_dict()
        if 'rejection_reason' not in data:
            data['rejection_reason'] = review.rejection_reason
        data['user'] = {
            'id': user.id if user else None,
            'mail': user.mail if user else None,
            'name': user.name if user else None
        }
        data['site_name'] = review.site.name if review.site else None
        return data

    def approve_review(self, *, review_id: int) -> None:
        """
        Marca una reseña como aprobada.
        
        Args:
            review_id: ID de la reseña a aprobar
            
        Raises:
            NotFoundError: Si la reseña no existe
            ValidationError: Si la reseña ya está aprobada
            DatabaseError: Si hay un error al persistir en la base de datos
        """
        review_id = validate_positive_int(review_id, "review_id")
        
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
        """
        Marca una reseña como rechazada y guarda el motivo.
        
        Args:
            review_id: ID de la reseña a rechazar
            reason: Motivo del rechazo
            
        Raises:
            NotFoundError: Si la reseña no existe
            ValidationError: Si la reseña ya está rechazada
            DatabaseError: Si hay un error al persistir en la base de datos
        """
        review_id = validate_positive_int(review_id, "review_id")

        review = HistoricSiteReview.query.get(review_id)
        if not review:
            raise exc.NotFoundError('Reseña no encontrada')
        if review.status == 'rejected':
            raise exc.ValidationError('La reseña ya está rechazada')

        review.status = 'rejected'
        if hasattr(review, 'rejection_reason'):
            review.rejection_reason = reason

        try:
            db.session.add(review)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise exc.DatabaseError(f'Error al rechazar la reseña: {e}')

    def get_user_review(self, *, site_id: int, user_id: int):
        """
        Obtiene la reseña del usuario para un sitio específico (pendiente o aprobada).
        
        Args:
            site_id: ID del sitio histórico
            user_id: ID del usuario
            
        Returns:
            dict | None: Diccionario con los datos de la reseña o None si no existe
        """
        site_id = validate_positive_int(site_id, "site_id")
        user_id = validate_positive_int(user_id, "user_id")
        
        from sqlalchemy import and_
        review = HistoricSiteReview.query.filter(
            and_(
                HistoricSiteReview.site_id == site_id,
                HistoricSiteReview.user_id == user_id,
                HistoricSiteReview.status.in_(['pending', 'approved'])
            )
        ).first()
        
        if not review:
            return None
        
        return self._build_review_dict(review)

    def update_review(self, *, site_id: int, review_id: int, user_id: int, rating, content):
        """
        Actualiza una reseña existente. Solo el autor puede actualizarla.
        Si la reseña estaba aprobada, vuelve a estado pendiente.
        
        Args:
            site_id: ID del sitio histórico
            review_id: ID de la reseña a actualizar
            user_id: ID del usuario autor de la reseña
            rating: Nueva calificación (1-5)
            content: Nuevo contenido de la reseña
            
        Returns:
            HistoricSiteReview: Reseña actualizada
            
        Raises:
            ValidationError: Si las reseñas están deshabilitadas o los datos son inválidos
            NotFoundError: Si el sitio o la reseña no existen
            ForbiddenError: Si el usuario no es el autor de la reseña
            DatabaseError: Si hay un error al persistir en la base de datos
        """
        if not flag_service.is_reviews_enabled():
            raise exc.ValidationError("Las reseñas están temporalmente deshabilitadas")
        
        site_id = validate_positive_int(site_id, "site_id")
        review_id = validate_positive_int(review_id, "review_id")
        user_id = validate_positive_int(user_id, "user_id")

        site = HistoricSite.query.filter_by(id=site_id, deleted=False).first()
        if not site:
            raise exc.NotFoundError("Sitio histórico no encontrado")

        review = HistoricSiteReview.query.filter_by(id=review_id, site_id=site_id).first()
        if not review:
            raise exc.NotFoundError("Reseña no encontrada")
        
        if review.user_id != user_id:
            raise exc.ForbiddenError("Solo el autor puede editar esta reseña")

        payload = validate_review_create_payload(rating=rating, content=content)

        review.rating = payload['rating']
        review.content = payload['content']
        if review.status == 'approved':
            review.status = 'pending'

        try:
            db.session.add(review)
            db.session.commit()
            db.session.refresh(review)
        except Exception as e:
            db.session.rollback()
            raise exc.DatabaseError(f"Error al actualizar la reseña: {e}")

        return review

    def delete_review(self, *, site_id: int, review_id: int, current_user_id: int):
        """
        Elimina una reseña. Solo el autor puede eliminarla.
        
        Args:
            site_id: ID del sitio histórico
            review_id: ID de la reseña a eliminar
            current_user_id: ID del usuario que intenta eliminar la reseña
            
        Returns:
            dict: Mensaje de éxito
            
        Raises:
            ValidationError: Si las reseñas están deshabilitadas
            NotFoundError: Si el sitio o la reseña no existen
            ForbiddenError: Si el usuario no es el autor de la reseña
            DatabaseError: Si hay un error al persistir en la base de datos
        """
        if not flag_service.is_reviews_enabled():
            raise exc.ValidationError("Las reseñas están temporalmente deshabilitadas")
        
        site_id = validate_positive_int(site_id, "site_id")
        review_id = validate_positive_int(review_id, "review_id")
        current_user_id = validate_positive_int(current_user_id, "user_id")

        site = HistoricSite.query.filter_by(id=site_id, deleted=False).first()
        if not site:
            raise exc.NotFoundError("Sitio histórico no encontrado")

        review = HistoricSiteReview.query.filter_by(id=review_id, site_id=site_id).first()
        if not review:
            raise exc.NotFoundError("Reseña no encontrada")
        
        if review.user_id != current_user_id:
            raise exc.ForbiddenError("Solo el autor puede eliminar esta reseña")

        try:
            db.session.delete(review)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise exc.DatabaseError(f'Error al eliminar la reseña: {e}')

    def delete_review_admin(self, *, review_id: int) -> None:
        review_id = validate_positive_int(review_id, "review_id")
        
        review = HistoricSiteReview.query.get(review_id)
        if not review:
            raise exc.NotFoundError('Reseña no encontrada')
        
        try:
            db.session.delete(review)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise exc.DatabaseError(f'Error al eliminar la reseña: {e}')


review_service = ReviewService()