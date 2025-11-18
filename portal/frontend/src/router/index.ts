import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
// Se usan los alias '@' que apuntan a 'src/'
import HomeView from '@/views/home/HomeView.vue'
import SitesListView from '@/views/SitesListView.vue'
// Asumiré que el router debe tener un 'name' para los RouterLinks
// (como usamos en AppHeader.vue)

// CAMBIO: Se descomentó y se definió la lista de rutas
const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'HomeView', // Este 'name' lo usa el RouterLink de 'Inicio'
    component: HomeView
  },
  {
    path: '/sitios',
    name: 'SitesList', // Este 'name' lo usa el RouterLink de 'Sitios'
    component: SitesListView
  }
  // Si tienes más vistas (como el detalle de un sitio), irían aquí
  // {
  //   path: '/sitio/:id',
  //   name: 'site-detail',
  //   component: () => import('@/views/SiteDetailView.vue')
  // }
]

// CAMBIO: Se descomentó la creación del router
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // Es buena práctica usar BASE_URL
  routes
})

// CAMBIO: Se exporta el router para que main.ts lo use
export default router
