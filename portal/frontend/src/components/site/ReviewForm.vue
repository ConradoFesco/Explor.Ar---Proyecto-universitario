<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAlert } from '@/composables/useAlert'
import { Button } from '@/components/ui/button'
import { Star, X } from 'lucide-vue-next'

const props = defineProps<{
  siteId?: number
  siteName: string
}>()

const emit = defineEmits<{
  submit: [rating: number, content: string]
  close: []
}>()

const rating = ref(0)
const hoveredRating = ref(0)
const content = ref('')
const isSubmitting = ref(false)
const { showWarning } = useAlert()

const isValid = computed(() => {
  return rating.value > 0 && content.value.trim().length > 0
})

function setRating(value: number) {
  rating.value = value
}

async function handleSubmit() {
  if (!isValid.value || isSubmitting.value) return
  
  if (rating.value === 0) {
    await showWarning('Calificación requerida', 'Por favor, seleccione una calificación')
    return
  }
  if (!content.value.trim()) {
    await showWarning('Comentario requerido', 'Por favor, escriba un comentario')
    return
  }
  
  emit('submit', rating.value, content.value.trim())
}

function handleClose() {
  if (isSubmitting.value) return
  
  // Resetear formulario al cerrar
  rating.value = 0
  hoveredRating.value = 0
  content.value = ''
  isSubmitting.value = false
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
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" 
      @click.self="handleClose"
      @keydown="handleKeydown"
    >
      <div 
        class="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        role="dialog"
        aria-modal="true"
        aria-labelledby="review-form-title"
      >
        <div class="sticky top-0 bg-white border-b p-4 flex items-center justify-between z-10">
          <h3 id="review-form-title" class="text-lg font-semibold">Escribir Reseña</h3>
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
        
        <form @submit.prevent="handleSubmit" class="p-6 space-y-6">
          <div>
            <p class="text-sm text-gray-600 mb-2">Sitio: {{ siteName }}</p>
          </div>
          
          <!-- Calificación -->
          <div class="space-y-2">
            <label for="rating" class="text-sm font-medium">Calificación *</label>
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
              <span v-if="rating > 0" class="ml-2 text-sm text-gray-600">
                {{ rating }} de 5 estrellas
              </span>
            </div>
          </div>
          
          <!-- Comentario -->
          <div class="space-y-2">
            <label for="review-content" class="text-sm font-medium">Comentario *</label>
            <textarea
              id="review-content"
              v-model="content"
              rows="6"
              required
              minlength="1"
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Escriba su reseña aquí..."
              :disabled="isSubmitting"
            ></textarea>
          </div>
          
          <!-- Botones -->
          <div class="flex justify-end gap-2">
            <Button 
              type="button"
              variant="outline" 
              @click="handleClose" 
              :disabled="isSubmitting"
            >
              Cancelar
            </Button>
            <Button 
              type="submit"
              :disabled="!isValid || isSubmitting"
            >
              {{ isSubmitting ? 'Enviando...' : 'Enviar Reseña' }}
            </Button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>
