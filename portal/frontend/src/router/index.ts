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

// GUARDIA GLOBAL: Verificar modo mantenimiento antes de cada navegación
router.beforeEach(async (to, from, next) => {
  // 1. Evitar bucle infinito: si ya vamos a mantenimiento, dejar pasar
  if (to.name === 'Maintenance') {
    return next()
  }

  try {
    // 2. Consultar al backend el estado del flag
    const base = getApiBaseUrl()
    const response = await fetch(`${base}/config/status`, {
      headers: { 'Accept': 'application/json' },
      credentials: 'omit',
      // Timeout corto para no bloquear la navegación si el backend no responde
      signal: createTimeoutSignal(3000) // 3 segundos máximo
    })
    
    if (response.ok) {
      const data = await response.json()
      
      // 3. Si el flag está activo, redirigir a Mantenimiento
      if (data.maintenance_mode === true) {
        return next({ name: 'Maintenance' })
      }
    }
  } catch (error) {
    // En caso de error (red, timeout, etc.), continuar navegación normal
    // para no bloquear el acceso si el backend está caído
    console.error('Error verificando estado de mantenimiento:', error)
  }

  // 4. Si no hay mantenimiento, continuar navegación normal
  next()
})

// CAMBIO: Se exporta el router para que main.ts lo use
export default router
