<script setup lang="ts">
import { Badge } from '@/components/ui/badge'
import type { HistoricSiteDetail } from '@/lib/api'

const props = defineProps<{
  tags: HistoricSiteDetail['tags']
  onTagClick: (tagSlug: string) => void
}>()
</script>

<template>
  <section v-if="tags && tags.length > 0" class="space-y-2">
    <h2 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-gray-100">Tags</h2>
    <div class="flex flex-wrap gap-2">
      <Badge
        v-for="tag in tags"
        :key="tag.id"
        variant="secondary"
        class="cursor-pointer transition-colors"
        @click="onTagClick(tag.slug)"
        :aria-label="`Filtrar por tag: ${tag.name}`"
      >
        {{ tag.name }}
      </Badge>
    </div>
  </section>
</template>

