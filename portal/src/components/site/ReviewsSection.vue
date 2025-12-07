<script setup lang="ts">
import { computed } from 'vue'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import ReviewItem from './ReviewItem.vue'
import type { Review } from '@/lib/api'

const props = defineProps<{
  reviews: Review[]
  isLoading: boolean
  currentPage: number
  totalPages: number
  isAuthenticated: boolean
  onWriteReview: () => void
  onPageChange: (page: number) => void
  onEditReview?: (review: Review) => void
  onDeleteReview?: (reviewId: number) => void
  isMyReview?: (review: Review) => boolean
  hasMyReview?: boolean
}>()

const hasReviews = computed(() => props.reviews.length > 0)
const showPagination = computed(() => props.totalPages > 1)
const buttonText = computed(() => {
  if (props.hasMyReview) {
    return 'Modificar reseña'
  }
  return 'Escribir reseña'
})

function handleWriteReview() {
  if (props.onWriteReview) {
    props.onWriteReview()
  }
}
</script>

<template>
  <section class="space-y-4">
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4">
      <h2 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-gray-100">Reseñas</h2>
      <Button
        :variant="isAuthenticated ? 'default' : 'outline'"
        size="sm"
        @click="handleWriteReview"
        class="w-full sm:w-auto text-xs sm:text-sm"
      >
        {{ buttonText }}
      </Button>
    </div>

    
    <div v-if="isLoading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="border border-gray-200 dark:border-gray-700 rounded-lg p-3 space-y-2 bg-white dark:bg-gray-800">
        <Skeleton class="h-4 w-1/4" />
        <Skeleton class="h-4 w-full" />
        <Skeleton class="h-4 w-3/4" />
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!hasReviews" class="text-center py-8 text-gray-500 dark:text-gray-400 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800">
      <p>No hay reseñas aún.</p>
      <p class="text-sm mt-1">Sé el primero en escribir una reseña.</p>
    </div>

    <!-- Reviews List -->
    <div v-else class="space-y-4">
      <ReviewItem
        v-for="review in reviews"
        :key="review.id"
        :review="review"
        :is-mine="isMyReview ? isMyReview(review) : false"
        :on-edit="onEditReview"
        :on-delete="onDeleteReview"
      />

      <!-- Pagination -->
      <nav v-if="showPagination" class="flex items-center justify-center gap-2">
        <Button
          variant="outline"
          size="sm"
          :disabled="currentPage <= 1"
          @click="onPageChange(currentPage - 1)"
          aria-label="Página anterior"
        >
          Anterior
        </Button>
        <span class="text-sm text-gray-600 dark:text-gray-400">
          Página {{ currentPage }} de {{ totalPages }}
        </span>
        <Button
          variant="outline"
          size="sm"
          :disabled="currentPage >= totalPages"
          @click="onPageChange(currentPage + 1)"
          aria-label="Página siguiente"
        >
          Siguiente
        </Button>
      </nav>
    </div>
  </section>
</template>

