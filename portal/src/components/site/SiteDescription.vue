<script setup lang="ts">
import { ref, computed } from 'vue'
import { Button } from '@/components/ui/button'
import type { HistoricSiteDetail } from '@/lib/api'

const props = defineProps<{
  site: HistoricSiteDetail
}>()

const showFull = ref(false)

const descriptionToShow = computed(() => {
  return showFull.value
    ? (props.site.complete_description || props.site.brief_description || '')
    : (props.site.brief_description || '')
})

const hasMoreDescription = computed(() => {
  return !!(
    props.site.complete_description &&
    props.site.complete_description !== props.site.brief_description
  )
})
</script>

<template>
  <section class="space-y-2">
    <h2 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-gray-100">Descripción</h2>
    <div class="prose prose-sm sm:prose-base max-w-none dark:prose-invert">
      <p class="whitespace-pre-wrap text-sm sm:text-base text-gray-700 dark:text-gray-300">{{ descriptionToShow }}</p>
    </div>
    <Button
      v-if="hasMoreDescription"
      variant="ghost"
      size="sm"
      @click="showFull = !showFull"
      class="mt-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100"
    >
      {{ showFull ? 'Ver menos' : 'Ver más' }}
    </Button>
  </section>
</template>

