import { ref, computed } from 'vue'
import { fetchSiteReviews, createReview, updateReview, deleteReview, getMyReview, type Review } from '@/lib/api'
import { useAlert } from './useAlert'
import { useAuth } from './useAuth'
import { useFlags } from './useFlags'

const REVIEWS_PER_PAGE = 25

export function useReviews(siteId: number | (() => number)) {
  const reviews = ref<Review[]>([])
  const reviewsPage = ref(1)
  const reviewsTotal = ref(0)
  const reviewsTotalPages = ref(0)
  const isLoadingReviews = ref(false)
  const myReview = ref<Review | null>(null)
  const isLoadingMyReview = ref(false)
  const { showError, showWarning, showSuccess, showConfirm, showInfo } = useAlert()
  const { loginWithGoogle, user } = useAuth()
  
  const currentSiteId = computed(() => typeof siteId === 'function' ? siteId() : siteId)

  async function loadReviews(page: number) {
    if (isLoadingReviews.value) return

    isLoadingReviews.value = true

    try {
      const response = await fetchSiteReviews(currentSiteId.value, page, REVIEWS_PER_PAGE)
      reviews.value = response.reviews
      reviewsPage.value = response.pagination.page
      reviewsTotal.value = response.pagination.total
      reviewsTotalPages.value = response.pagination.pages
    } catch (e: unknown) {
      const error = e instanceof Error ? e : { message: String(e) }
      if (error.message?.includes('401') || error.message?.includes('Autenticación')) {
        reviews.value = []
        reviewsTotal.value = 0
      } else {
        console.error('Error loading reviews:', e)
      }
    } finally {
      isLoadingReviews.value = false
    }
  }

  async function loadMyReview() {
    if (!user.value || isLoadingMyReview.value) return

    isLoadingMyReview.value = true
    try {
      myReview.value = await getMyReview(currentSiteId.value)
    } catch (e: unknown) {
      console.error('Error loading my review:', e)
      myReview.value = null
    } finally {
      isLoadingMyReview.value = false
    }
  }

  async function submitReview(rating: number, content: string, reviewId?: number): Promise<void> {
    // Verificar si las reseñas están habilitadas antes de enviar (consulta directa sin caché)
    const { checkReviewsEnabledDirectly } = useFlags()
    const reviewsEnabled = await checkReviewsEnabledDirectly()
    if (!reviewsEnabled) {
      await showWarning(
        'Reseñas deshabilitadas',
        'Las reseñas están temporalmente deshabilitadas. Por favor, intente más tarde.'
      )
      throw new Error('REVIEWS_DISABLED')
    }
    
    try {
      if (reviewId) {
        // Editar reseña existente
        await updateReview(currentSiteId.value, reviewId, rating, content)
      } else {
        // Crear nueva reseña
        await createReview(currentSiteId.value, rating, content)
      }
      
      // Recargar mi reseña primero (con await) para que se actualice el estado inmediatamente
      await loadMyReview()
      
      // Recargar lista de reseñas en segundo plano (sin await para no bloquear)
      loadReviews(1).catch(err => console.error('Error al recargar reseñas:', err))
      
      // Mostrar mensaje de éxito (sin await para no bloquear el cierre del formulario)
      if (reviewId) {
        showSuccess(
          'Reseña actualizada',
          'Su reseña ha sido actualizada. Si estaba aprobada, volverá a estado pendiente para moderación.'
        )
      } else {
        showSuccess(
          'Reseña creada',
          'Su reseña ha sido creada y está pendiente de moderación.'
        )
      }
    } catch (e: unknown) {
      const error = e instanceof Error ? e : new Error(String(e))
      const errorMsg = error.message || ''
      
      // Log del error para debugging
      console.error('Error al enviar reseña:', errorMsg)

      if (errorMsg.includes('401') || errorMsg.includes('Autenticación') || errorMsg.includes('no autenticado')) {
        await showWarning(
          'Inicio de sesión requerido',
          'Debe iniciar sesión para escribir una reseña'
        )
        await loginWithGoogle()
        throw error
      } else if (errorMsg.includes('Ya existe una reseña') || errorMsg.includes('Use la opción de editar')) {
        // Este error se manejará en el componente padre para mostrar confirmación
        throw new Error('REVIEW_EXISTS')
      } else {
        // Extraer el mensaje de error más específico
        let displayMsg = errorMsg
        if (errorMsg.includes('400:')) {
          // El mensaje viene como "Error al crear reseña (400): {mensaje}"
          const parts = errorMsg.split('400:')
          if (parts.length > 1 && parts[1]) {
            displayMsg = parts[1].trim()
          }
        }
        
        await showError(
          'Error al crear reseña',
          displayMsg || 'No se pudo crear la reseña. Verifique que la calificación sea entre 1 y 5, y que el comentario tenga entre 20 y 1000 caracteres.'
        )
        throw error
      }
    }
  }

  async function removeReview(reviewId: number): Promise<void> {
    // Verificar si las reseñas están habilitadas antes de eliminar (consulta directa sin caché)
    const { checkReviewsEnabledDirectly } = useFlags()
    const reviewsEnabled = await checkReviewsEnabledDirectly()
    if (!reviewsEnabled) {
      await showWarning(
        'Reseñas deshabilitadas',
        'Las reseñas están temporalmente deshabilitadas. Por favor, intente más tarde.'
      )
      return
    }
    
    const result = await showConfirm(
      'Eliminar reseña',
      '¿Está seguro de que desea eliminar su reseña? Esta acción no se puede deshacer.'
    )

    if (!result.isConfirmed) {
      return
    }

    try {
      await deleteReview(currentSiteId.value, reviewId)
      await showSuccess(
        'Reseña eliminada',
        'Su reseña ha sido eliminada correctamente.'
      )
      await loadReviews(1) // Recargar primera página
      await loadMyReview() // Recargar mi reseña
    } catch (e: unknown) {
      const error = e instanceof Error ? e : { message: String(e) }
      const errorMsg = error.message || ''

      if (errorMsg.includes('403') || errorMsg.includes('Forbidden')) {
        await showError(
          'Acceso denegado',
          'No tiene permiso para eliminar esta reseña.'
        )
      } else {
        await showError(
          'Error',
          `No se pudo eliminar la reseña: ${errorMsg}`
        )
      }
      throw error
    }
  }

  const isMyReview = (review: Review) => {
    return user.value && review.user?.id === user.value.id
  }

  return {
    reviews,
    reviewsPage,
    reviewsTotal,
    reviewsTotalPages,
    isLoadingReviews,
    myReview,
    isLoadingMyReview,
    loadReviews,
    loadMyReview,
    submitReview,
    removeReview,
    isMyReview,
  }
}

