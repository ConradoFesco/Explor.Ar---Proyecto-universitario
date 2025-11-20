<script setup lang="ts">
import { Star } from 'lucide-vue-next'
import type { Review } from '@/lib/api'
import { formatDate } from '@/utils/date'

const props = defineProps<{
  review: Review
}>()
</script>

<template>
  <article class="border rounded p-4 space-y-2">
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <div class="flex items-center gap-2 mb-1">
          <span class="font-semibold text-sm">
            {{ review.user.name || review.user.mail || 'Usuario anónimo' }}
          </span>
          <div class="flex items-center gap-1" :aria-label="`Calificación: ${review.rating} de 5 estrellas`">
            <Star
              v-for="i in 5"
              :key="i"
              :class="['h-4 w-4', i <= review.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300']"
            />
          </div>
        </div>
        <time class="text-xs text-gray-500" :datetime="review.created_at || undefined">
          {{ formatDate(review.created_at) }}
        </time>
      </div>
    </div>
    <p class="text-sm whitespace-pre-wrap">{{ review.content }}</p>
  </article>
</template>

