<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { SiteImage } from '@/lib/api'
import type { CarouselApi } from '@/components/ui/carousel'
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
function onInit(carouselApi: CarouselApi) {
  api.value = carouselApi
  api.value.on('select', onSelect)
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
    <h2 class="text-xl font-semibold">Galería de Imágenes</h2>

    <!-- Carrusel Principal -->
    <div class="relative">
      <Carousel
        class="w-full"
        :opts="{
          align: 'start',
          loop: hasMultipleImages,
          dragFree: false,
          containScroll: 'trimSnaps',
        }"
        @init-api="onInit"
      >
        <CarouselContent>
          <CarouselItem
            v-for="(image, index) in images"
            :key="image.id"
          >
            <AspectRatio :ratio="16 / 9" class="bg-gray-100 rounded overflow-hidden">
              <img
                :src="image.url_publica"
                :alt="image.titulo_alt || `${siteName} - Imagen ${index + 1}`"
                class="w-full h-full object-cover"
              />
            </AspectRatio>
          </CarouselItem>
        </CarouselContent>

        <!-- Controles de Navegación -->
        <template v-if="hasMultipleImages">
          <CarouselPrevious
            class="left-2 bg-white/90 hover:bg-white shadow-md"
          />
          <CarouselNext
            class="right-2 bg-white/90 hover:bg-white shadow-md"
          />
        </template>
      </Carousel>

      <!-- Indicador de Imagen Actual -->
      <div
        v-if="hasMultipleImages"
        class="absolute bottom-2 left-1/2 transform -translate-x-1/2 bg-black/50 text-white px-2 py-1 rounded text-xs z-10"
      >
        {{ currentIndex + 1 }} / {{ images.length }}
      </div>
    </div>

    <!-- Miniaturas -->
    <div v-if="hasMultipleImages" class="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-2">
      <button
        v-for="(image, index) in images"
        :key="image.id"
        @click="goToImage(index)"
        :class="[
          'relative aspect-square rounded overflow-hidden border-2 transition-all cursor-pointer',
          currentIndex === index
            ? 'border-blue-500 ring-2 ring-blue-200'
            : 'border-transparent hover:border-gray-300'
        ]"
        :aria-label="`Ver imagen ${index + 1}: ${image.titulo_alt || siteName}`"
      >
        <img
          :src="image.url_publica"
          :alt="image.titulo_alt || `${siteName} - Imagen ${index + 1}`"
          class="w-full h-full object-cover"
        />
      </button>
    </div>

    <!-- Descripción de la Imagen Actual -->
    <p v-if="currentImage?.descripcion" class="text-sm text-gray-600">
      {{ currentImage.descripcion }}
    </p>
  </section>
</template>

