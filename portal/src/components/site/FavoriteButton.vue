<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Heart } from 'lucide-vue-next'
import { useFavorite } from '@/composables/useFavorite'

const props = defineProps<{
  siteId: number
  isFavorite: boolean
  size?: 'sm' | 'lg'
  variant?: 'outline' | 'default' | 'ghost'
}>()

const emit = defineEmits<{
  (e: 'update', newState: boolean): void
}>()

const { toggleSiteFavorite } = useFavorite()

async function handleToggle(e: Event) {
  e.stopPropagation()
  e.preventDefault()

  try {
    await toggleSiteFavorite(
      props.siteId,
      props.isFavorite,
      (confirmedState) => {
        emit('update', confirmedState)
      }
    )
  } catch {
    // El error ya fue manejado en useFavorite
  }
}

const iconSize = props.size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'
</script>

<template>
  <Button
    :variant="variant || 'outline'"
    :size="size || 'sm'"
    @click="handleToggle"
    :title="isFavorite ? 'Quitar de favoritos' : 'Agregar a favoritos'"
    :aria-label="isFavorite ? 'Quitar de favoritos' : 'Agregar a favoritos'"
    class="dark:bg-gray-700"
  >
    <Heart
      :class="[
        iconSize,
        'transition-colors',
        isFavorite ? 'fill-red-500 text-red-500' : 'text-gray-500'
      ]"
    />
  </Button>
</template>

