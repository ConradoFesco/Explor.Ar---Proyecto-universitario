import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
// Se usan los alias '@' que apuntan a 'src/'
import HomeView from '@/views/home/HomeView.vue'
import SitesListView from '@/views/SitesListView.vue'
import AuthCallback from '@/views/AuthCallback.vue'
import MaintenanceView from '@/views/MaintenanceView.vue'
import { getApiBaseUrl } from '@/lib/api'
// Asumiré que el router debe tener un 'name' para los RouterLinks
// (como usamos en AppHeader.vue)

// CAMBIO: Se descomentó y se definió la lista de rutas
const routes: Array<RouteRecordRaw> = [
  {
    path: '/mantenimiento',
    name: 'Maintenance',
    component: MaintenanceView,
    meta: { maintenance: true }
  },
  {
    path: '/',
    name: 'HomeView', // Este 'name' lo usa el RouterLink de 'Inicio'
    component: HomeView
  },
  {
    path: '/sitios',
    name: 'SitesList', // Este 'name' lo usa el RouterLink de 'Sitios'
    component: SitesListView
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: AuthCallback
  },
  {
    path: '/sitio/:id',
    name: 'site-detail',
    component: () => import('@/views/SiteDetailView.vue')
  }
]

// CAMBIO: Se descomentó la creación del router
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // Es buena práctica usar BASE_URL
  routes
})

// Helper para crear un AbortSignal con timeout (compatible con navegadores más antiguos)
function createTimeoutSignal(timeoutMs: number): AbortSignal {
  // Si el navegador soporta AbortSignal.timeout, usarlo
  if (typeof AbortSignal.timeout === 'function') {
    return AbortSignal.timeout(timeoutMs)
  }
  
  // Fallback para navegadores más antiguos
  const controller = new AbortController()
  setTimeout(() => controller.abort(), timeoutMs)
  return controller.signal
}

// ===== SISTEMA DE CACHE PARA ESTADO DE MANTENIMIENTO =====
interface MaintenanceStatus {
  maintenance_mode: boolean
  message: string | null
  lastUpdate: number
}

// Cache del estado de mantenimiento
let maintenanceCache: MaintenanceStatus = {
  maintenance_mode: false,
  message: null,
  lastUpdate: 0
}

// Intervalo de actualización: 10 segundos
const CACHE_UPDATE_INTERVAL = 10000 // 10 segundos

// Función para actualizar el cache desde el backend
async function updateMaintenanceCache(): Promise<void> {
  try {
    const base = getApiBaseUrl()
    const response = await fetch(`${base}/config/status`, {
      headers: { 'Accept': 'application/json' },
      credentials: 'omit',
      signal: createTimeoutSignal(3000) // 3 segundos máximo
    })
    
    if (response.ok) {
      const data = await response.json()
      maintenanceCache = {
        maintenance_mode: data.maintenance_mode === true,
        message: data.message || null,
        lastUpdate: Date.now()
      }
    }
  } catch (error) {
    // En caso de error, mantener el cache anterior
    // No actualizar para evitar bloquear el acceso si el backend está caído
    console.error('Error actualizando cache de mantenimiento:', error)
  }
}

// Inicializar el cache al cargar el router
updateMaintenanceCache()

// Configurar intervalo para actualizar el cache cada 10 segundos
let maintenanceInterval: number | null = null

// Función para iniciar el intervalo de actualización
function startMaintenancePolling(): void {
  if (maintenanceInterval !== null) {
    return // Ya está iniciado
  }
  
  maintenanceInterval = window.setInterval(() => {
    updateMaintenanceCache()
  }, CACHE_UPDATE_INTERVAL)
}

// Función para detener el intervalo (útil si se necesita limpiar)
function stopMaintenancePolling(): void {
  if (maintenanceInterval !== null) {
    clearInterval(maintenanceInterval)
    maintenanceInterval = null
  }
}

// Iniciar el polling automáticamente
startMaintenancePolling()

// ===== GUARDIA GLOBAL: Verificar modo mantenimiento antes de cada navegación =====
router.beforeEach(async (to, from, next) => {
  // 1. Evitar bucle infinito: si ya vamos a mantenimiento, dejar pasar
  if (to.name === 'Maintenance') {
    return next()
  }

  // 2. Usar el cache en lugar de hacer fetch cada vez
  // Si el cache está muy desactualizado (más de 15 segundos), hacer una actualización inmediata
  const cacheAge = Date.now() - maintenanceCache.lastUpdate
  if (cacheAge > 15000) {
    // Cache muy viejo, actualizar de inmediato (pero no bloquear la navegación)
    updateMaintenanceCache().catch(err => {
      console.error('Error en actualización inmediata de cache:', err)
    })
  }

  // 3. Usar el valor del cache para decidir
  if (maintenanceCache.maintenance_mode === true) {
    return next({ name: 'Maintenance' })
  }

  // 4. Si no hay mantenimiento, continuar navegación normal
  next()
})

// CAMBIO: Se exporta el router para que main.ts lo use
export default router
