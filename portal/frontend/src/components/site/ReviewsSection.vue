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
}>()

const hasReviews = computed(() => props.reviews.length > 0)
const showPagination = computed(() => props.totalPages > 1)
</script>

<template>
  <section class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-semibold">Reseñas</h2>
      <Button
        :variant="isAuthenticated ? 'default' : 'outline'"
        size="sm"
        @click="onWriteReview"
      >
        Escribir reseña
      </Button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="border rounded p-3 space-y-2">
        <Skeleton class="h-4 w-1/4" />
        <Skeleton class="h-4 w-full" />
        <Skeleton class="h-4 w-3/4" />
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!hasReviews" class="text-center py-8 text-gray-500 border rounded">
      <p>No hay reseñas aún.</p>
      <p class="text-sm mt-1">Sé el primero en escribir una reseña.</p>
    </div>

    <!-- Reviews List -->
    <div v-else class="space-y-4">
      <ReviewItem
        v-for="review in reviews"
        :key="review.id"
        :review="review"
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
        <span class="text-sm text-gray-600">
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

