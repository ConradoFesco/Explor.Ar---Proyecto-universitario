<script setup lang="ts">
import { onMounted, ref } from 'vue'
import HeroSection from '@/components/home/HeroSection.vue'
import ContentSection from '@/components/home/ContentSection.vue'
import type { HistoricSite } from '@/lib/api'
import { fetchPublicSites, fetchMyFavorites } from '@/lib/api'
import { useAuth } from '@/composables/useAuth'

const { isAuthenticated } = useAuth()

// Estados para los sitios del home
const mejorPuntuados = ref<HistoricSite[]>([])
const recientementeAgregados = ref<HistoricSite[]>([])
const favoritos = ref<HistoricSite[]>([])

// Estados de carga independientes para cada sección
const isLoadingMejorPuntuados = ref(true)
const isLoadingRecientementeAgregados = ref(true)
const isLoadingFavoritos = ref(true)

// Función para obtener la fecha de hoy en formato ISO (solo fecha, sin hora)
function getTodayDateString(): string {
  const today = new Date()
  const dateString = today.toISOString().split('T')[0] // Formato: YYYY-MM-DD
  return dateString || today.toISOString().substring(0, 10) // Fallback si split falla
}

// Cargar sitios mejor puntuados (carga independiente)
async function loadMejorPuntuados() {
  isLoadingMejorPuntuados.value = true
  try {
    const response = await fetchPublicSites({
      orderBy: 'rating',
      orderDir: 'desc',
      page: 1,
      perPage: 5,
    })
    mejorPuntuados.value = response.items
  } catch (error) {
    console.error('Error al cargar mejor puntuados:', error)
    mejorPuntuados.value = []
  } finally {
    isLoadingMejorPuntuados.value = false
  }
}

// Cargar sitios recientemente agregados (del día actual) - carga independiente
async function loadRecientementeAgregados() {
  isLoadingRecientementeAgregados.value = true
  try {
    const response = await fetchPublicSites({
      orderBy: 'created_at',
      orderDir: 'desc',
      page: 1,
      perPage: 20, // Obtener más para filtrar por fecha
    })
    
    // Filtrar solo los del día actual
    const today = getTodayDateString()
    const recientes = response.items.filter(site => {
      if (!site.created_at) return false
      const siteDate = site.created_at.split('T')[0] // Obtener solo la fecha
      return siteDate === today
    })
    
    recientementeAgregados.value = recientes.slice(0, 5)
  } catch (error) {
    console.error('Error al cargar recientemente agregados:', error)
    recientementeAgregados.value = []
  } finally {
    isLoadingRecientementeAgregados.value = false
  }
}

// Cargar favoritos del usuario (carga independiente)
async function loadFavoritos() {
  isLoadingFavoritos.value = true
  if (!isAuthenticated.value) {
    favoritos.value = []
    isLoadingFavoritos.value = false
    return
  }
  
  try {
    const response = await fetchMyFavorites(1, 5)
    favoritos.value = response.items
  } catch (error) {
    // Si hay error (ej: no autenticado), simplemente no mostrar favoritos
    console.warn('Error al cargar favoritos:', error)
    favoritos.value = []
  } finally {
    isLoadingFavoritos.value = false
  }
}

// Cargar todos los datos de forma independiente cuando se monta el componente
// Cada sección se carga y muestra tan pronto como sus datos estén listos
onMounted(() => {
  // Cargar cada sección de forma independiente (sin esperar a las demás)
  // Esto mejora la percepción de velocidad porque el usuario ve contenido apareciendo progresivamente
  loadMejorPuntuados()
  loadRecientementeAgregados()
  loadFavoritos()
})

</script>

<template>
  <!-- <AppHeader /> --> <!-- <-- CAMBIO: Eliminado de aquí, ahora está en App.vue -->

  <!-- CAMBIO: Eliminado el <main> wrapper, ahora está en App.vue -->

  <!-- 1. Sección Hero (Héroe) -->
    <HeroSection />

    <!-- Secciones de Contenido (Sitios Destacados) -->
    <!-- Cada sección se muestra tan pronto como sus datos estén listos -->
    
    <!-- Favoritos -->
    <ContentSection
      v-if="!isLoadingFavoritos && favoritos.length > 0"
      title="Mis Favoritos"
      description="Tus sitios favoritos guardados."
      :sites="favoritos"
      category="favorites"
    />
    <div v-else-if="isLoadingFavoritos && isAuthenticated" class="py-12 px-4">
      <div class="text-center text-gray-500 dark:text-gray-400">Cargando favoritos...</div>
    </div>

    <!-- Mejor Puntuados -->
    <ContentSection
      v-if="!isLoadingMejorPuntuados && mejorPuntuados.length > 0"
      title="Mejor Puntuados"
      description="Los sitios con las valoraciones más altas."
      :sites="mejorPuntuados"
      category="best-rated"
    />
    <div v-else-if="isLoadingMejorPuntuados" class="py-12 px-4">
      <div class="text-center text-gray-500 dark:text-gray-400">Cargando mejor puntuados...</div>
    </div>

    <!-- Recientemente Agregados -->
    <ContentSection
      v-if="!isLoadingRecientementeAgregados && recientementeAgregados.length > 0"
      title="Recientemente Agregados"
      description="Descubre los últimos sitios incorporados hoy."
      :sites="recientementeAgregados"
      category="recent"
    />
    <div v-else-if="isLoadingRecientementeAgregados" class="py-12 px-4">
      <div class="text-center text-gray-500 dark:text-gray-400">Cargando recientemente agregados...</div>
    </div>

  <!-- </main> --> <!-- <-- CAMBIO: Esta era la línea que causaba el error -->

  <!-- <AppFooter /> -->
</template>
