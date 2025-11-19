import { ref, computed } from 'vue'
import { fetchSiteReviews, createReview, type Review } from '@/lib/api'
import { useAlert } from './useAlert'
import { useAuth } from './useAuth'

const REVIEWS_PER_PAGE = 25

export function useReviews(siteId: number | (() => number)) {
  const reviews = ref<Review[]>([])
  const reviewsPage = ref(1)
  const reviewsTotal = ref(0)
  const reviewsTotalPages = ref(0)
  const isLoadingReviews = ref(false)
  const { showError, showWarning } = useAlert()
  const { redirectToLogin } = useAuth()
  
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

  async function submitReview(rating: number, content: string): Promise<void> {
    try {
      await createReview(currentSiteId.value, rating, content)
      await loadReviews(1) // Recargar primera página
    } catch (e: unknown) {
      const error = e instanceof Error ? e : { message: String(e) }
      const errorMsg = error.message || ''

      if (errorMsg.includes('401') || errorMsg.includes('Autenticación') || errorMsg.includes('no autenticado')) {
        await showWarning(
          'Inicio de sesión requerido',
          'Debe iniciar sesión para escribir una reseña'
        )
        redirectToLogin()
        throw error
      } else {
        await showError(
          'Error',
          `No se pudo crear la reseña: ${errorMsg}`
        )
        throw error
      }
    }
  }

  return {
    reviews,
    reviewsPage,
    reviewsTotal,
    reviewsTotalPages,
    isLoadingReviews,
    loadReviews,
    submitReview,
  }
}

