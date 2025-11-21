<script setup lang="ts">
import { computed } from 'vue'
import { Button } from '@/components/ui/button'

interface Props {
  // Para uso simple (un solo campo): modelValue es la dirección
  modelValue?: 'asc' | 'desc'
  // Para uso con múltiples campos: currentField y currentDir
  currentField?: string
  currentDir?: 'asc' | 'desc'
  // Campo de este botón
  field?: string
  // Etiqueta del botón
  label?: string
  // Si es true, muestra el contenedor con "Ordenar:"
  showContainer?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  label: 'Fecha',
  showContainer: false
})

const emit = defineEmits<{
  'update:modelValue': [value: 'asc' | 'desc']
  'sort-change': [field: string, dir: 'asc' | 'desc']
}>()

// Determinar si este botón está activo
const isActive = computed(() => {
  if (props.field && props.currentField) {
    return props.field === props.currentField
  }
  return true // Si no hay field, siempre está activo (modo simple)
})

// Determinar la dirección actual
const currentDirection = computed(() => {
  if (props.field && props.currentField && props.currentDir) {
    return isActive.value ? props.currentDir : 'asc'
  }
  return props.modelValue || 'desc'
})

// Determinar el ícono a mostrar
const sortIcon = computed(() => {
  if (props.field && !isActive.value) {
    return '' // No mostrar flecha si no está activo
  }
  return currentDirection.value === 'asc' ? '↑' : '↓'
})

const handleClick = () => {
  if (props.field) {
    // Modo múltiples campos
    const newDir = isActive.value && props.currentDir === 'asc' ? 'desc' : 'asc'
    emit('sort-change', props.field, newDir)
  } else {
    // Modo simple (un solo campo)
    const newValue = currentDirection.value === 'asc' ? 'desc' : 'asc'
    emit('update:modelValue', newValue)
  }
}
</script>

<template>
  <div v-if="showContainer" class="flex items-center gap-2 bg-white dark:bg-gray-800 px-4 py-2 rounded-full shadow-lg border border-gray-200 dark:border-gray-700">
    <span class="text-xs font-medium text-gray-500 dark:text-gray-400 whitespace-nowrap">Ordenar:</span>
    <Button 
      variant="outline" 
      size="sm" 
      @click="handleClick"
      class="bg-transparent border-0 focus:ring-0 text-sm font-semibold text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
    >
      {{ label }} {{ sortIcon }}
    </Button>
  </div>
  <Button 
    v-else
    variant="outline" 
    size="sm" 
    @click="handleClick"
    class="bg-transparent border-0 focus:ring-0 text-xs sm:text-sm font-semibold text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 px-2 sm:px-3"
  >
    {{ label }} {{ sortIcon }}
  </Button>
</template>

