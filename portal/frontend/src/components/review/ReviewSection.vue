<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useReviewsStore } from '@/stores/reviews'
import ReviewForm from '@/components/review/ReviewForm.vue'
import ReviewItem from '@/components/review/ReviewItem.vue'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { MessageSquarePlus } from 'lucide-vue-next'
import type { Review } from '@/lib/api'

const props = defineProps<{
  siteId: number
}>()

const reviewsStore = useReviewsStore()

// Estado local para manejar la visibilidad del formulario
const showForm = ref(false)
const editingReview = ref<Review | null>(null)

// Cargar reseñas al montar
onMounted(async () => {
  await reviewsStore.fetchReviews(props.siteId)
})

// Abrir formulario para CREAR
function handleCreateClick() {
  editingReview.value = null
  showForm.value = true
}

// Abrir formulario para EDITAR
function handleEditClick(review: Review) {
  editingReview.value = review
  showForm.value = true
}

// Cancelar acción
function handleCancelForm() {
  showForm.value = false
  editingReview.value = null
}

// Éxito al guardar (crear o editar)
async function handleFormSuccess() {
  showForm.value = false
  editingReview.value = null
  // Recargamos la lista para ver los cambios frescos
  await reviewsStore.fetchReviews(props.siteId)
}

// Éxito al eliminar
async function handleDeleteSuccess() {
  await reviewsStore.fetchReviews(props.siteId)
}
</script>

<template>
  <section class="py-8 border-t dark:border-gray-700 mt-8">
    <div class="max-w-7xl mx-auto px-0 sm:px-6 lg:px-8">

      <!-- Cabecera de la Sección -->
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Reseñas ({{ reviewsStore.items.length }})
        </h2>

        <!-- Botón para agregar nueva reseña (si no estamos viendo el formulario) -->
        <Button
          v-if="!showForm"
          @click="handleCreateClick"
          size="sm"
          class="bg-blue-600 hover:bg-blue-700 text-white"
        >
          <MessageSquarePlus class="w-4 h-4 mr-2" />
          Escribir opinión
        </Button>
      </div>

      <!-- Estado de Carga -->
      <div v-if="reviewsStore.isLoading && reviewsStore.items.length === 0" class="space-y-4">
        <Skeleton class="h-32 w-full dark:bg-gray-800" />
        <Skeleton class="h-32 w-full dark:bg-gray-800" />
      </div>

      <!-- Estado de Error -->
      <div v-else-if="reviewsStore.error" class="p-4 bg-red-50 text-red-600 rounded-md dark:bg-red-900/20 dark:text-red-400">
        {{ reviewsStore.error }}
      </div>

      <!-- Contenido Principal -->
      <div v-else>

        <!-- 1. Formulario (Crear o Editar) -->
        <!-- Se muestra solo cuando showForm es true -->
        <div v-if="showForm" class="mb-8 animate-in fade-in slide-in-from-top-2 duration-300">
          <ReviewForm
            :site-id="siteId"
            :existing-review="editingReview"
            @success="handleFormSuccess"
            @cancel="handleCancelForm"
          />
        </div>

        <!-- 2. Lista de Reseñas -->

        <!-- Caso A: No hay reseñas y no se está creando una -->
        <div v-if="reviewsStore.items.length === 0 && !showForm" class="text-center text-gray-500 dark:text-gray-400 py-12 border-2 border-dashed rounded-lg dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <p class="text-lg font-medium">No hay reseñas aún.</p>
          <p class="text-sm mt-1">¡Sé el primero en compartir tu experiencia sobre este lugar!</p>
          <Button variant="link" @click="handleCreateClick" class="mt-2 text-blue-600 dark:text-blue-400">
            Escribir reseña ahora
          </Button>
        </div>

        <!-- Caso B: Hay reseñas (Listado) -->
        <div v-else class="space-y-4">
          <ReviewItem
            v-for="review in reviewsStore.items"
            :key="review.id"
            :review="review"
            @edit="handleEditClick(review)"
            @delete-success="handleDeleteSuccess"
          />
        </div>

      </div>
    </div>
  </section>
</template>
