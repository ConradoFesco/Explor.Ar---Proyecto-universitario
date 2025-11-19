<script setup lang="ts">
import type { HistoricSite } from '@/lib/api'
import { useSitesStore } from '@/stores/sites'
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useFavorite } from '@/composables/useFavorite'
import { Card, CardHeader, CardContent, CardFooter, CardTitle, CardDescription } from '@/components/ui/card'
import { AspectRatio } from '@/components/ui/aspect-ratio'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
// Importamos los iconos que faltaban
import { Star } from 'lucide-vue-next'

const props = defineProps<{
  site: HistoricSite
}>()

const store = useSitesStore()
const router = useRouter()
const { toggleSiteFavorite } = useFavorite()
const tagsToShow = computed(() => (props.site.tags || []).slice(0, 5))
const hasImage = computed(() => !!props.site.cover_image_url)
const aspectRatio = computed(() => (hasImage.value ? 16 / 9 : 4 / 3))

async function onToggleFavorite(e: Event) {
  e.stopPropagation()
  e.preventDefault()

  const previousState = props.site.is_favorite ?? false

  try {
    await toggleSiteFavorite(
      props.site.id,
      previousState,
      (newState) => {
        // Actualizar en el store
        const idx = store.items.findIndex(s => s.id === props.site.id)
        if (idx >= 0) {
          store.items[idx] = { ...store.items[idx], is_favorite: newState } as HistoricSite
        }
      }
    )
  } catch {
    // El error ya fue manejado en useFavorite
    console.error('Error toggling favorite')
  }
}

function handleView() {
  router.push({ name: 'site-detail', params: { id: props.site.id } })
}
</script>

<template>
  <!--
    CAMBIO: Añadidas clases de fondo para modo claro/oscuro
    y el click llama a handleView.
  -->
  <Card
    @click="handleView"
    class="overflow-hidden h-full flex flex-col hover:shadow-xl transition-shadow cursor-pointer bg-white dark:bg-gray-800"
  >
    <AspectRatio :ratio="aspectRatio" class="bg-gray-100 dark:bg-gray-700 overflow-hidden">
      <img v-if="site.cover_image_url" :src="site.cover_image_url" :alt="site.name" class="w-full h-full object-cover" />
      <div v-else class="w-full h-full flex items-center justify-center text-gray-400 text-xs">Sin imagen</div>
    </AspectRatio>

    <CardHeader>
      <CardTitle class="text-base text-gray-900 dark:text-gray-100">{{ site.name }}</CardTitle>
      <CardDescription class="text-xs text-gray-500 dark:text-gray-400">
        {{ site.city }} <span v-if="site.city && site.province">·</span> {{ site.province }}
      </CardDescription>
    </CardHeader>

    <CardContent class="flex-1">
      <p v-if="site.brief_description" class="text-sm text-gray-700 dark:text-gray-300 line-clamp-3">{{ site.brief_description }}</p>
      <div class="mt-2 flex flex-wrap gap-1">
        <Badge v-for="t in tagsToShow" :key="t" variant="secondary" class="text-[11px]">{{ t }}</Badge>
        <span v-if="(site.tags?.length || 0) > 5" class="text-xs text-gray-500 dark:text-gray-400">
          +{{ (site.tags?.length || 0) - 5 }}
        </span>
      </div>
      <div v-if="site.state" class="mt-2 text-xs text-gray-600 dark:text-gray-400">
        Estado: {{ site.state }}
      </div>
    </CardContent>

    <CardFooter class="flex justify-between items-center gap-2">
      <span class="text-xs text-gray-500 dark:text-gray-400">#{{ site.id }}</span>
      <div class="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          @click="onToggleFavorite"
          :title="site.is_favorite ? 'Quitar de favoritos' : 'Agregar a favoritos'"
          class="dark:bg-gray-700"
        >
          <!-- Usamos el icono de Estrella -->
          <Star
            class="w-4 h-4 transition-colors"
            :class="site.is_favorite ? 'text-yellow-400 fill-yellow-400' : 'text-gray-500'"
          />
        </Button>
        <Button
          variant="default"
          size="sm"
          @click="handleView"
        >
          Ver
        </Button>
      </div>
    </CardFooter>
  </Card>
</template>
