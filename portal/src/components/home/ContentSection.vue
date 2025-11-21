<script setup lang="ts">
import { useRouter } from 'vue-router'
import SiteCard from '@/components/site/SiteCard.vue'
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from '@/components/ui/carousel'
import { Button } from '@/components/ui/button'
import { ArrowRight } from 'lucide-vue-next'
import type { HistoricSite } from '@/lib/api'

const props = defineProps<{
  title: string
  description: string
  sites: HistoricSite[]
  category?: 'favorites' | 'best-rated' | 'recent'
}>()

const router = useRouter()

function handleVerTodos() {
  if (!props.category) {
    // Si no hay categoría, ir al listado normal
    router.push({ name: 'SitesList' })
    return
  }

  // Navegar al listado con los filtros correspondientes
  const query: Record<string, string> = {}
  
  if (props.category === 'favorites') {
    query.fav = '1'
  } else if (props.category === 'best-rated') {
    query.sort = 'rating:desc'
  } else if (props.category === 'recent') {
    query.sort = 'created_at:desc'
    // Para recientes, podríamos agregar un filtro de fecha si el backend lo soporta
    // Por ahora, solo ordenamos por fecha descendente
  }
  
  router.push({ 
    name: 'SitesList',
    query 
  })
}
</script>

<template>
  <section class="py-12 md:py-16">
    <div class="w-full px-4 sm:px-6 lg:px-8 xl:px-12">

      <!-- Encabezado de la Sección -->
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6 sm:mb-8">
        <div class="flex-1 min-w-0">
          <h2 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            {{ title }}
          </h2>
          <p class="text-sm sm:text-base text-gray-600 dark:text-gray-400">
            {{ description }}
          </p>
        </div>
        <!-- Botón "Ver todos" que coincide con el diseño -->
        <Button 
          variant="ghost" 
          class="text-blue-600 hover:text-blue-700 font-semibold shrink-0 text-sm sm:text-base"
          @click="handleVerTodos"
        >
          Ver todos
          <ArrowRight class="w-4 h-4 ml-2" />
        </Button>
      </div>

      <!-- Carrusel de Sitios -->
      <Carousel
        :opts="{
          align: 'start',
          loop: false,
        }"
        class="w-full"
      >
        <CarouselContent class="-ml-4">
          <!-- Iteramos sobre la lista de sitios -->
          <CarouselItem
            v-for="site in sites"
            :key="site.id"
            class="pl-4 md:basis-1/2 lg:basis-1/3"
          >
            <div class="p-1 h-full">
              <!-- Usamos el componente SiteCard -->
              <!-- 'site' ahora es un objeto HistoricSite, que es lo que SiteCard espera -->
              <SiteCard :site="site" />
            </div>
          </CarouselItem>
        </CarouselContent>

        <!-- Controles del Carrusel (se ocultan en pantallas muy pequeñas) -->
        <CarouselPrevious class="hidden sm:flex" />
        <CarouselNext class="hidden sm:flex" />
      </Carousel>

      <!-- Mensaje si no hay sitios -->
      <div v-if="!sites || sites.length === 0" class="text-center text-gray-500 py-10">
        <p>No hay sitios disponibles en esta sección por el momento.</p>
      </div>

    </div>
  </section>
</template>
