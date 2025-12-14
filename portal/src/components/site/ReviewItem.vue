<script setup lang="ts">
import { Star, Edit, Trash2 } from 'lucide-vue-next'
import type { Review } from '@/lib/api'
import { formatDate } from '@/utils/date'
import { Button } from '@/components/ui/button'
import { useFlags } from '@/composables/useFlags'

const props = defineProps<{
  review: Review
  isMine?: boolean
  onEdit?: (review: Review) => void
  onDelete?: (reviewId: number) => void
}>()

const { areReviewsEnabled } = useFlags()

function handleEdit() {
  if (props.onEdit && areReviewsEnabled.value) {
    props.onEdit(props.review)
  }
}

function handleDelete() {
  if (props.onDelete && areReviewsEnabled.value) {
    props.onDelete(props.review.id)
  }
}
</script>

<template>
  <article class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-2 bg-white dark:bg-gray-800">
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <div class="flex items-center gap-2 mb-1">
          <span class="font-semibold text-sm text-gray-900 dark:text-gray-100">
            {{ review.author_name || review.user?.name || 'Usuario anónimo' }}
          </span>
          <div class="flex items-center gap-1" :aria-label="`Calificación: ${review.rating} de 5 estrellas`">
            <Star
              v-for="i in 5"
              :key="i"
              :class="['h-4 w-4', i <= review.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300 dark:text-gray-600']"
            />
          </div>
        </div>
        <time class="text-xs text-gray-500 dark:text-gray-400" :datetime="review.created_at || undefined">
          {{ formatDate(review.created_at) }}
        </time>
      </div>
      <div v-if="isMine && (onEdit || onDelete)" class="flex items-center gap-2">
        <Button
          v-if="onEdit"
          variant="ghost"
          size="sm"
          :disabled="!areReviewsEnabled"
          @click="handleEdit"
          class="h-8 w-8 p-0 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20"
          aria-label="Editar reseña"
        >
          <Edit class="h-4 w-4" />
        </Button>
        <Button
          v-if="onDelete"
          variant="ghost"
          size="sm"
          :disabled="!areReviewsEnabled"
          @click="handleDelete"
          class="h-8 w-8 p-0 text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20"
          aria-label="Eliminar reseña"
        >
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>
    </div>
    <p class="text-sm whitespace-pre-wrap text-gray-700 dark:text-gray-300">{{ review.content }}</p>
  </article>
</template>

