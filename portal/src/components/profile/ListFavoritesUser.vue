<script setup lang="ts">
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import FavoriteButton from '@/components/site/FavoriteButton.vue'

interface Favorite {
  id: number
  site_name: string
  image_url?: string
  location: string
  added_at: string
}

interface Props {
  favorites: Favorite[]
  loading: boolean
}

const emit = defineEmits<{
  'favorite-removed': []
}>()

const props = defineProps<Props>()

const handleFavoriteUpdate = (newState: boolean) => {
  if (!newState) {
    // Si se eliminó el favorito, emitir evento para refrescar la lista
    emit('favorite-removed')
  }
}
</script>

<template>
  <div class="w-full">

    <!-- Loading state -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <Skeleton v-for="i in 4" :key="i" class="h-[240px] rounded-xl dark:bg-gray-800" />
    </div>

    <!-- Favorites grid -->
    <div v-else-if="favorites.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 max-w-full">
      <Card v-for="fav in favorites" :key="fav.id" class="group overflow-hidden border-0 shadow-md hover:shadow-2xl transition-all duration-500 dark:bg-gray-900">
        <div class="aspect-video w-full bg-gray-100 dark:bg-gray-800 relative overflow-hidden">
          <img
            :src="fav.image_url || 'https://via.placeholder.com/600x400/1e293b/94a3b8?text=Explor.ar'"
            class="object-cover w-full h-full group-hover:scale-110 transition-transform duration-700"
            alt="Sitio"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent"></div>

          <div class="absolute top-3 right-3 z-20">
            <FavoriteButton
              :site-id="fav.id"
              :is-favorite="true"
              size="sm"
              variant="ghost"
              @update="handleFavoriteUpdate"
              class="h-9 w-9 rounded-full bg-white/95 hover:bg-red-50 text-red-500 shadow-lg border-0 transition-all hover:scale-110 [&_svg]:fill-red-500 [&_svg]:text-red-500"
            />
          </div>

          <div class="absolute bottom-0 left-0 right-0 p-3 sm:p-4 text-white z-10">
            <p class="font-bold text-base sm:text-lg leading-tight mb-1 sm:mb-2 drop-shadow-lg line-clamp-2">{{ fav.site_name }}</p>
            <div class="flex items-center justify-between">
              <p class="text-xs text-gray-200 flex items-center backdrop-blur-sm bg-black/40 px-2.5 py-1 rounded-full">
                <i class="fas fa-map-marker-alt mr-1.5 text-red-400"></i> {{ fav.location }}
              </p>
              <span class="text-[10px] text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-sm bg-black/40 px-2 py-0.5 rounded-full">
                {{ fav.added_at }}
              </span>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center py-16 text-center bg-white dark:bg-gray-900/50 rounded-2xl border-2 border-dashed border-gray-300 dark:border-gray-700 w-full max-w-md mx-auto">
      <div class="bg-gradient-to-br from-red-50 to-pink-100 dark:from-red-900/20 dark:to-pink-800/20 p-5 rounded-full mb-5">
        <i class="fas fa-heart text-red-500 dark:text-red-400 text-3xl"></i>
      </div>
      <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">No tienes favoritos</h3>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-6 max-w-[280px]">
        ¡Explora el mapa y guarda lo que te guste!
      </p>
      <Button class="bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 text-white shadow-md hover:shadow-lg transition-all">
        <i class="fas fa-map mr-2"></i>
        Explorar Mapa
      </Button>
    </div>
  </div>
</template>
