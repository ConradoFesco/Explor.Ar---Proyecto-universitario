<script setup lang="ts">
import type { HistoricSiteDetail } from '@/lib/api'
import { computed } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Star, MapPin } from 'lucide-vue-next'
import FavoriteButton from '@/components/site/FavoriteButton.vue'

const props = defineProps<{
  site: HistoricSiteDetail
  reviewsTotal: number
}>()

const emit = defineEmits<{
  (e: 'favoriteUpdate', newState: boolean): void
}>()

const locationText = computed(() => {
  const parts = [
    props.site.city_name || props.site.city,
    props.site.province_name || props.site.province
  ].filter(Boolean)
  return parts.join(', ')
})

const ratingDisplay = computed(() => {
  if (!props.site.rating) return null
  return Number(props.site.rating).toFixed(1)
})
</script>

<template>
  <header class="space-y-3">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div class="flex-1 min-w-0">
        <h1 class="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100 break-words">{{ site.name }}</h1>
        <div v-if="locationText" class="flex flex-wrap items-center gap-2 mt-2 text-xs sm:text-sm text-gray-600 dark:text-gray-400">
          <MapPin class="h-3 w-3 sm:h-4 sm:w-4 shrink-0" />
          <span>{{ locationText }}</span>
        </div>
      </div>
      <FavoriteButton
        :site-id="site.id"
        :is-favorite="site.is_favorite ?? false"
        size="sm"
        class="shrink-0"
        @update="(newState) => emit('favoriteUpdate', newState)"
      />
    </div>
    
    <div class="flex flex-wrap items-center gap-2">
      <Badge v-if="site.state_name" variant="secondary">
        Estado: {{ site.state_name }}
      </Badge>
      <Badge v-if="ratingDisplay" variant="secondary" class="flex items-center gap-1">
        <Star class="h-3 w-3 fill-yellow-400 text-yellow-400" />
        {{ ratingDisplay }}
        <span v-if="reviewsTotal > 0" class="text-xs">
          ({{ reviewsTotal }})
        </span>
      </Badge>
    </div>
  </header>
</template>

