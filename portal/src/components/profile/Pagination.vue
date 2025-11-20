<script setup lang="ts">
import { Button } from '@/components/ui/button'

interface Props {
  currentPage: number
  totalPages: number
  disabled?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'change-page': [delta: number]
}>()

const handlePageChange = (delta: number) => {
  emit('change-page', delta)
}
</script>

<template>
  <div v-if="!disabled && totalPages > 0" class="flex items-center justify-center gap-3 mt-16 mb-8 pt-8 border-t border-gray-200 dark:border-gray-700">
    <Button
      variant="outline"
      size="sm"
      @click="handlePageChange(-1)"
      :disabled="currentPage === 1"
      class="rounded-full px-5 shadow-sm hover:shadow-md transition-all disabled:opacity-50"
    >
      <i class="fas fa-chevron-left mr-2 text-xs"></i>
      Anterior
    </Button>
    <span class="text-sm font-medium text-gray-700 dark:text-gray-300 px-4 py-1.5 bg-white dark:bg-gray-800 rounded-full shadow-sm border border-gray-200 dark:border-gray-700">
      {{ currentPage }} / {{ totalPages }}
    </span>
    <Button
      variant="outline"
      size="sm"
      @click="handlePageChange(1)"
      :disabled="currentPage === totalPages"
      class="rounded-full px-5 shadow-sm hover:shadow-md transition-all disabled:opacity-50"
    >
      Siguiente
      <i class="fas fa-chevron-right ml-2 text-xs"></i>
    </Button>
  </div>
</template>

