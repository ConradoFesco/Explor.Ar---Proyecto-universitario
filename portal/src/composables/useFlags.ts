import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { getApiBaseUrl } from '@/lib/api'

interface SystemStatus {
  maintenance_mode: boolean
  message: string | null
  reviews_enabled: boolean
  lastUpdate: number
}

// Estado global del sistema (compartido entre componentes)
const systemStatus = ref<SystemStatus>({
  maintenance_mode: false,
  message: null,
  reviews_enabled: true,
  lastUpdate: 0
})

// Intervalo de actualización: 10 segundos
const CACHE_UPDATE_INTERVAL = 10000

// Helper para crear un AbortSignal con timeout
function createTimeoutSignal(timeoutMs: number): AbortSignal {
  if (typeof AbortSignal.timeout === 'function') {
    return AbortSignal.timeout(timeoutMs)
  }
  
  const controller = new AbortController()
  setTimeout(() => controller.abort(), timeoutMs)
  return controller.signal
}

// Función para actualizar el estado desde el backend
async function updateSystemStatus(): Promise<void> {
  try {
    const base = getApiBaseUrl()
    const response = await fetch(`${base}/config/status`, {
      headers: { 'Accept': 'application/json' },
      credentials: 'omit',
      signal: createTimeoutSignal(3000)
    })
    
    if (response.ok) {
      const data = await response.json()
      systemStatus.value = {
        maintenance_mode: data.maintenance_mode === true,
        message: data.message || null,
        reviews_enabled: data.reviews_enabled !== false, // Por defecto true si no viene
        lastUpdate: Date.now()
      }
    }
  } catch (error) {
    // En caso de error, mantener el estado anterior
    console.error('Error actualizando estado del sistema:', error)
  }
}

// Intervalo global
let statusInterval: number | null = null

// Función para iniciar el polling
function startPolling(): void {
  if (statusInterval !== null) {
    return // Ya está iniciado
  }
  
  // Actualizar inmediatamente
  updateSystemStatus()
  
  // Configurar intervalo
  statusInterval = window.setInterval(() => {
    updateSystemStatus()
  }, CACHE_UPDATE_INTERVAL)
}

// Función para detener el polling
function stopPolling(): void {
  if (statusInterval !== null) {
    clearInterval(statusInterval)
    statusInterval = null
  }
}

// Iniciar polling automáticamente al cargar el módulo
// Nota: El router también hace polling, pero este composable permite acceso reactivo desde componentes
startPolling()

// Función para consultar directamente el estado de reviews sin usar caché
async function checkReviewsEnabledDirectly(): Promise<boolean> {
  try {
    const base = getApiBaseUrl()
    const response = await fetch(`${base}/config/status`, {
      headers: { 'Accept': 'application/json' },
      credentials: 'omit',
      signal: createTimeoutSignal(3000),
      cache: 'no-cache' // Forzar consulta directa sin caché
    })
    
    if (response.ok) {
      const data = await response.json()
      return data.reviews_enabled !== false // Por defecto true si no viene
    }
  } catch (error) {
    console.error('Error consultando estado de reseñas:', error)
    // En caso de error, asumir que están habilitadas para no bloquear
    return true
  }
  
  // Por defecto, asumir que están habilitadas
  return true
}

export function useFlags() {
  // Computadas reactivas (usan el caché)
  const isMaintenanceMode = computed(() => systemStatus.value.maintenance_mode)
  const maintenanceMessage = computed(() => systemStatus.value.message)
  const areReviewsEnabled = computed(() => systemStatus.value.reviews_enabled)

  // Función para forzar actualización manual
  const refreshStatus = async () => {
    await updateSystemStatus()
  }

  return {
    isMaintenanceMode,
    maintenanceMessage,
    areReviewsEnabled, // Valor del caché (para UI reactiva)
    checkReviewsEnabledDirectly, // Consulta directa sin caché (para validaciones críticas)
    refreshStatus
  }
}

