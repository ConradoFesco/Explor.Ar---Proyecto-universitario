import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { Review } from '@/lib/api'

export const useReviewsStore = defineStore('reviews', () => {
  const items = ref<Review[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 1. Obtener reseñas
  async function fetchReviews(siteId: number) {
    isLoading.value = true
    error.value = null
    try {
      const response = await fetch(`/api/sites/${siteId}/reviews`)

      if (!response.ok) throw new Error('Error al cargar reseñas')

      const data = await response.json()
      items.value = data
    } catch (e: any) {
      console.error(e)
      error.value = 'No se pudieron cargar las reseñas.'
    } finally {
      isLoading.value = false
    }
  }

  // 2. Crear reseña (usa content)
  async function createReview(reviewData: { site_id: number; rating: number; content: string }) {
    isLoading.value = true
    try {
      const response = await fetch(`/api/sites/${reviewData.site_id}/reviews`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reviewData)
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.error || 'Error al crear reseña')
      }

      await fetchReviews(reviewData.site_id)

    } catch (e: any) {
      throw e
    } finally {
      isLoading.value = false
    }
  }

  // 3. Actualizar reseña (usa content)
  async function updateReview(reviewId: number, reviewData: { rating: number; content: string }) {
    isLoading.value = true
    try {
      const response = await fetch(`/api/reviews/${reviewId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reviewData)
      })

      if (!response.ok) throw new Error('Error al actualizar')

      // Actualiza localmente
      const idx = items.value.findIndex(r => r.id === reviewId)
      if (idx !== -1) {
        const updated = { ...items.value[idx], ...reviewData }
        items.value[idx] = updated as Review
      }

    } catch (e: any) {
      throw e
    } finally {
      isLoading.value = false
    }
  }

  // 4. Eliminar reseña
  async function deleteReview(reviewId: number) {
    isLoading.value = true
    try {
      const response = await fetch(`/api/reviews/${reviewId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
      })

      if (!response.ok) throw new Error('Error al eliminar')

      items.value = items.value.filter(r => r.id !== reviewId)

    } catch (e: any) {
      throw e
    } finally {
      isLoading.value = false
    }
  }

  return {
    items,
    isLoading,
    error,
    fetchReviews,
    createReview,
    updateReview,
    deleteReview
  }
})
