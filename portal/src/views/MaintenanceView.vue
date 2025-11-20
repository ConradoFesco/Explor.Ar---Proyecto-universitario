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
      
      if (data.maintenance_mode === false) {
        // Si el mantenimiento se desactivó, redirigir al home
        router.push({ name: 'HomeView' })
        return false
      }
      
      maintenanceMessage.value = data.message || 'El sitio se encuentra en mantenimiento programado.'
      return true
    }
  } catch (error) {
    console.error('Error verificando estado de mantenimiento:', error)
    // En caso de error, asumir que no hay mantenimiento
    router.push({ name: 'HomeView' })
    return false
  }
  
  return true
}

onMounted(async () => {
  await checkMaintenanceStatus()
  isLoading.value = false
  
  // Verificar periódicamente si el mantenimiento se desactivó
  checkInterval = window.setInterval(async () => {
    const stillInMaintenance = await checkMaintenanceStatus()
    if (!stillInMaintenance && checkInterval) {
      clearInterval(checkInterval)
      checkInterval = null
    }
  }, 5000) // Verificar cada 5 segundos
})

onBeforeUnmount(() => {
  if (checkInterval) {
    clearInterval(checkInterval)
    checkInterval = null
  }
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center px-4">
    <div class="max-w-2xl w-full text-center">
      <!-- Loading State -->
      <div v-if="isLoading" class="space-y-6">
        <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
        <p class="text-gray-600 dark:text-gray-400">Verificando estado...</p>
      </div>

      <!-- Maintenance Content -->
      <div v-else class="space-y-8">
        <!-- Icono animado -->
        <div class="maintenance-animation">
          <div class="inline-block p-8 bg-white dark:bg-gray-800 rounded-full shadow-2xl">
            <svg class="w-32 h-32 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
          </div>
        </div>

        <!-- Título y mensaje -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 md:p-12">
          <h1 class="text-4xl md:text-5xl font-bold text-gray-800 dark:text-gray-100 mb-4">
            🛠️ Modo Mantenimiento
          </h1>
          
          <div class="w-24 h-1 bg-gradient-to-r from-blue-500 to-purple-600 mx-auto mb-6 rounded-full"></div>
          
          <p class="text-lg md:text-xl text-gray-600 dark:text-gray-300 leading-relaxed">
            {{ maintenanceMessage || 'El sitio se encuentra temporalmente inactivo por tareas de mantenimiento.' }}
          </p>
        </div>

        <!-- Footer -->
        <div class="mt-8 text-gray-500 dark:text-gray-400 text-sm">
          <p>Estamos trabajando para mejorar tu experiencia. Vuelve pronto.</p>
          <p class="mt-2">Si tienes alguna consulta urgente, contacta al equipo de soporte.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.maintenance-animation {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { 
    transform: translateY(0px); 
  }
  50% { 
    transform: translateY(-15px); 
  }
}
</style>

