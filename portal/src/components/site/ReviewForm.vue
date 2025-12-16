<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAlert } from '@/composables/useAlert'
import { Button } from '@/components/ui/button'
import { Star, X } from 'lucide-vue-next'
import type { Review } from '@/lib/api'

const props = defineProps<{
  siteId?: number
  siteName: string
  review?: Review | null
  isSubmitting?: boolean
}>()

const emit = defineEmits<{
  submit: [rating: number, content: string]
  close: []
}>()

const rating = ref(0)
const hoveredRating = ref(0)
const content = ref('')
const { showWarning } = useAlert()

const isSubmitting = computed(() => props.isSubmitting || false)

const isEditing = computed(() => !!props.review)

watch(() => props.review, (newReview) => {
  if (newReview) {
    rating.value = newReview.rating
    hoveredRating.value = 0
    content.value = newReview.content
  } else {
    rating.value = 0
    hoveredRating.value = 0
    content.value = ''
  }
}, { immediate: true })

const isValid = computed(() => {
  return rating.value > 0 && content.value.trim().length >= 20 && content.value.trim().length <= 1000
})

const characterCount = computed(() => content.value.length)
const minChars = 20
const maxChars = 1000

function setRating(value: number) {
  rating.value = value
}

async function handleSubmit() {
  if (!isValid.value || isSubmitting.value) return
  
  if (rating.value === 0) {
    await showWarning('Calificación requerida', 'Por favor, seleccione una calificación')
    return
  }
  
  const trimmedContent = content.value.trim()
  if (trimmedContent.length < minChars) {
    await showWarning('Comentario muy corto', `El comentario debe tener al menos ${minChars} caracteres`)
    return
  }
  
  if (trimmedContent.length > maxChars) {
    await showWarning('Comentario muy largo', `El comentario no puede exceder ${maxChars} caracteres`)
    return
  }
  
  emit('submit', rating.value, trimmedContent)
}

function handleClose() {
  if (isSubmitting.value) return
  
  if (!props.review) {
    rating.value = 0
    hoveredRating.value = 0
    content.value = ''
  }
  emit('close')
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    handleClose()
  }
}
</script>

<template>
  <Teleport to="body">
    <div 
      class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 p-4" 
      @click.self="handleClose"
      @keydown="handleKeydown"
    >
      <div 
        class="bg-white dark:bg-gray-800 rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto z-[10000]"
        role="dialog"
        aria-modal="true"
        aria-labelledby="review-form-title"
      >
        <div class="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-3 sm:p-4 flex items-center justify-between z-10">
          <h3 id="review-form-title" class="text-base sm:text-lg font-semibold text-gray-900 dark:text-gray-100">
            {{ isEditing ? 'Modificar Reseña' : 'Escribir Reseña' }}
          </h3>
          <Button 
            variant="ghost" 
            size="icon" 
            @click="handleClose"
            :disabled="isSubmitting"
            aria-label="Cerrar formulario"
          >
            <X class="h-4 w-4" />
          </Button>
        </div>
        
        <form @submit.prevent="handleSubmit" class="p-4 sm:p-6 space-y-4 sm:space-y-6">
          <div>
            <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2 break-words">Sitio: {{ siteName }}</p>
          </div>
          
          <!-- Calificación -->
          <div class="space-y-2">
            <label for="rating" class="text-sm font-medium text-gray-900 dark:text-gray-100">Calificación *</label>
            <div class="flex items-center gap-1" role="radiogroup" aria-label="Calificación">
              <button
                v-for="i in 5"
                :key="i"
                type="button"
                :aria-label="`Calificar con ${i} ${i === 1 ? 'estrella' : 'estrellas'}`"
                :aria-pressed="rating === i"
                @click="setRating(i)"
                @mouseenter="hoveredRating = i"
                @mouseleave="hoveredRating = 0"
                class="focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
              >
                <Star
                  :class="[
                    'h-8 w-8 transition-colors',
                    (hoveredRating >= i || rating >= i)
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-gray-300'
                  ]"
                />
              </button>
              <span v-if="rating > 0" class="ml-2 text-sm text-gray-600 dark:text-gray-400">
                {{ rating }} de 5 estrellas
              </span>
            </div>
          </div>
          
          <!-- Comentario -->
          <div class="space-y-2">
            <label for="review-content" class="text-sm font-medium text-gray-900 dark:text-gray-100">
              Comentario * (mínimo {{ minChars }}, máximo {{ maxChars }} caracteres)
            </label>
            <textarea
              id="review-content"
              v-model="content"
              rows="6"
              required
              :minlength="minChars"
              :maxlength="maxChars"
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border-gray-300 dark:border-gray-600"
              :class="{
                'border-red-500 dark:border-red-500': content.length > 0 && (content.length < minChars || content.length > maxChars),
                'border-green-500 dark:border-green-500': content.length >= minChars && content.length <= maxChars
              }"
              placeholder="Escriba su reseña aquí (mínimo 20 caracteres)..."
              :disabled="isSubmitting"
            ></textarea>
            <div class="flex justify-between text-xs" :class="{
              'text-red-500 dark:text-red-400': content.length < minChars || content.length > maxChars,
              'text-gray-500 dark:text-gray-400': content.length >= minChars && content.length <= maxChars
            }">
              <span>{{ characterCount }} / {{ maxChars }} caracteres</span>
              <span v-if="content.length < minChars">
                Faltan {{ minChars - content.length }} caracteres
              </span>
            </div>
          </div>
          
          <!-- Botones -->
          <div class="flex flex-col sm:flex-row justify-end gap-2">
            <Button 
              type="button"
              variant="outline" 
              @click="handleClose" 
              :disabled="isSubmitting"
              class="w-full sm:w-auto text-xs sm:text-sm"
            >
              Cancelar
            </Button>
            <Button 
              type="submit"
              :disabled="!isValid || isSubmitting"
              class="w-full sm:w-auto text-xs sm:text-sm"
            >
              {{ isSubmitting ? (isEditing ? 'Guardando...' : 'Enviando...') : (isEditing ? 'Modificar Reseña' : 'Enviar Reseña') }}
            </Button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>
