<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { SiteImage } from '@/lib/api'
import { type CarouselApi } from '@/components/ui/carousel'
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious
} from '@/components/ui/carousel'
import { AspectRatio } from '@/components/ui/aspect-ratio'

const props = defineProps<{
  images: SiteImage[]
  siteName: string
}>()

const api = ref<CarouselApi>()
const currentIndex = ref(0)

const currentImage = computed(() => props.images[currentIndex.value])
const hasMultipleImages = computed(() => props.images.length > 1)

// Sincronizar el índice actual con el carrusel
function onSelect() {
  if (!api.value) return
  currentIndex.value = api.value.selectedScrollSnap()
}

// Ir a una imagen específica desde las miniaturas
function goToImage(index: number) {
  api.value?.scrollTo(index)
}

// Inicializar el API del carrusel
// CAMBIO CLAVE: Renombramos el argumento a 'val' y verificamos que exista
function onInit(val: CarouselApi) {
  if (!val) return // <-- Esta línea soluciona el error "posiblemente undefined"

  api.value = val
  val.on('select', onSelect)
  onSelect() // Llamar una vez para inicializar el índice
}

// Observar cambios en las imágenes para resetear el carrusel
watch(() => props.images.length, (newLength, oldLength) => {
  if (api.value && newLength !== oldLength && newLength > 0) {
    api.value.reInit()
    // Resetear índice si es necesario
    if (currentIndex.value >= newLength) {
      currentIndex.value = 0
      api.value.scrollTo(0)
    }
  }
})
</script>

<template>
  <section class="space-y-3">
    <h2 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-gray-100">Galería de Imágenes</h2>

    <!-- Carrusel Principal -->
    <div class="relative w-full">
      <Carousel
        class="w-full"
        :opts="{
          align: 'start',
          loop: hasMultipleImages,
          dragFree: false,
          containScroll: 'trimSnaps',
          slidesToScroll: 1,
        }"
        @init-api="onInit"
      >
        <CarouselContent>
          <CarouselItem
            v-for="(image, index) in images"
            :key="image.id"
            class="basis-full md:basis-1/2 lg:basis-1/3"
          >
            <div class="p-1">
              <AspectRatio :ratio="4 / 3" class="bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                <img
                  :src="image.url_publica"
                  :alt="image.titulo_alt || `${siteName} - Imagen ${index + 1}`"
                  class="w-full h-full object-contain"
                />
              </AspectRatio>
            </div>
          </CarouselItem>
        </CarouselContent>

        <!-- Controles de Navegación -->
        <template v-if="hasMultipleImages">
          <CarouselPrevious class="left-3 bg-white/80 hover:bg-white dark:bg-gray-800/80 dark:hover:bg-gray-800 shadow-md backdrop-blur-sm" />
          <CarouselNext class="right-3 bg-white/80 hover:bg-white dark:bg-gray-800/80 dark:hover:bg-gray-800 shadow-md backdrop-blur-sm" />
        </template>
      </Carousel>

      <!-- Indicador de Imagen Actual -->
      <div
        v-if="hasMultipleImages"
        class="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black/60 text-white px-3 py-1 rounded-full text-xs font-medium backdrop-blur-sm z-10"
      >
        {{ currentIndex + 1 }} / {{ images.length }}
      </div>
    </div>

    <!-- Descripción de la Imagen Actual -->
    <p v-if="currentImage?.descripcion" class="text-sm text-gray-600 dark:text-gray-400 italic">
      {{ currentImage.descripcion }}
    </p>
  </section>
</template>
