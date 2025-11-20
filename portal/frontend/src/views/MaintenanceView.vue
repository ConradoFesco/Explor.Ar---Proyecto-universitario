<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { getApiBaseUrl } from '@/lib/api'

const router = useRouter()
const maintenanceMessage = ref<string | null>(null)
const isLoading = ref(true)
let checkInterval: number | null = null

async function checkMaintenanceStatus(): Promise<boolean> {
  try {
    const base = getApiBaseUrl()
    const response = await fetch(`${base}/config/status`, {
      headers: { 'Accept': 'application/json' },
      credentials: 'omit'
    })
    
    if (response.ok) {
      const data = await response.json()
      
      // Si el mantenimiento se desactivó, redirigir a la home
      if (data.maintenance_mode === false) {
        return false // Mantenimiento desactivado
      }
      
      // Actualizar mensaje si cambió
      maintenanceMessage.value = data.message || 'El sitio se encuentra en mantenimiento programado.'
      return true // Mantenimiento activo
    }
    
    return true // En caso de error, asumir que sigue en mantenimiento
  } catch (error) {
    console.error('Error al verificar estado de mantenimiento:', error)
    return true // En caso de error, asumir que sigue en mantenimiento
  }
}

onMounted(async () => {
  // Cargar mensaje inicial
  await checkMaintenanceStatus()
  isLoading.value = false
  
  // Verificar periódicamente si el mantenimiento se desactivó (cada 5 segundos)
  checkInterval = window.setInterval(async () => {
    const isMaintenanceActive = await checkMaintenanceStatus()
    
    if (!isMaintenanceActive) {
      // Limpiar intervalo antes de redirigir
      if (checkInterval !== null) {
        clearInterval(checkInterval)
        checkInterval = null
      }
      
      // Redirigir a la home cuando el mantenimiento se desactiva
      router.push({ name: 'HomeView' })
    }
  }, 5000) // Verificar cada 5 segundos
})

onBeforeUnmount(() => {
  // Limpiar intervalo cuando el componente se desmonte
  if (checkInterval !== null) {
    clearInterval(checkInterval)
    checkInterval = null
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
    <div class="max-w-md w-full text-center space-y-6">
      <!-- Icono o ilustración -->
      <div class="flex justify-center">
        <div class="w-24 h-24 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
          <svg
            class="w-12 h-12 text-blue-600 dark:text-blue-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
      </div>

      <!-- Título -->
      <div class="space-y-2">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          Sitio en Mantenimiento
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          Estamos realizando mejoras para brindarte una mejor experiencia
        </p>
      </div>

      <!-- Mensaje de mantenimiento -->
      <div v-if="!isLoading" class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-gray-700 dark:text-gray-300 whitespace-pre-line">
          {{ maintenanceMessage }}
        </p>
      </div>

      <!-- Loading state -->
      <div v-if="isLoading" class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
        <div class="animate-pulse space-y-2">
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mx-auto"></div>
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mx-auto"></div>
        </div>
      </div>

      <!-- Información adicional -->
      <div class="text-sm text-gray-500 dark:text-gray-400">
        <p>Vuelve pronto. ¡Estamos trabajando para ti!</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Estilos adicionales si son necesarios */
</style>

