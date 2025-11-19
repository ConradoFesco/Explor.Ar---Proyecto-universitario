<script setup lang="ts">
// CAMBIO: Importamos 'onMounted' y 'computed'
import { onMounted, computed } from 'vue'
// Importamos los componentes de la página
import HeroSection from '@/components/home/HeroSection.vue'
import ContentSection from '@/components/home/ContentSection.vue'
// import AppHeader from '@/components/AppHeader.vue' // <-- CAMBIO: Eliminado de aquí
// Importamos el tipo (ajusta la ruta si es necesario)
import type { HistoricSite } from '@/lib/api'
// CAMBIO: Importamos el store de Pinia
import { useSitesStore } from '@/stores/sites'

// CAMBIO: Inicializamos el store
const sitesStore = useSitesStore()

// CAMBIO: Eliminamos el array 'featuredSites' hardcodeado

// CAMBIO: Creamos propiedades computadas que leen del store
// Asumimos que 'sitesStore.items' tiene TODOS los sitios
const mejorPuntuados = computed(() => {
  // Lógica de ejemplo: clonar, ordenar y tomar 5
  // Asumo que tu 'HistoricSite' tiene una propiedad 'rating' o similar.
  // Si no la tiene, tendrás que ajustar esta lógica de orden.
  return [...sitesStore.items]
    // @ts-ignore - Si 'rating' no existe en tu tipo, puedes borrar esta línea
    .sort((a, b) => (b.rating || 0) - (a.rating || 0))
    .slice(0, 5);
})

const recientementeAgregados = computed(() => {
  // Lógica de ejemplo: clonar, ordenar por ID (o fecha) y tomar 5
  // Asumo que ID más alto = más nuevo
  return [...sitesStore.items]
    .sort((a, b) => (b.id || 0) - (a.id || 0))
    .slice(0, 5);
})


// CAMBIO: Cuando el componente se monta, llamamos al store
onMounted(() => {
  // Llamamos a la acción del store para que traiga los sitios
  // Asumo que tienes una acción 'fetchItems' o similar
  // ¡Asegúrate de que esta acción exista en tu store!
  if (sitesStore.items.length === 0) {
     // sitesStore.fetchItems(); // O como se llame tu acción
     console.log("Llamando a fetchItems() desde HomeView [DESCOMENTAR]");
  }
})

</script>

<template>
  <!-- <AppHeader /> --> <!-- <-- CAMBIO: Eliminado de aquí, ahora está en App.vue -->

  <!-- CAMBIO: Eliminado el <main> wrapper, ahora está en App.vue -->

  <!-- 1. Sección Hero (Héroe) -->
    <HeroSection />

    <!-- CAMBIO: Loader mientras se cargan los datos -->
    <div v-if="sitesStore.isLoading" class="text-center py-20">
      <p class="text-gray-500 dark:text-gray-400">Cargando sitios destacados...</p>
      <!-- Aquí iría un componente 'Spinner' si tuvieras -->
    </div>

    <!-- 2. Sección de Contenido (Sitios Destacados) -->
    <!-- CAMBIO: Modificamos el template para usar las propiedades computadas -->
    <template v-if="!sitesStore.isLoading">
      <ContentSection
        v-if="mejorPuntuados.length > 0"
        title="Mejor Puntuados"
        description="Los sitios con las valoraciones más altas."
        :sites="mejorPuntuados"
      />

      <ContentSection
        v-if="recientementeAgregados.length > 0"
        title="Recientemente Agregados"
        description="Descubre los últimos sitios incorporados."
        :sites="recientementeAgregados"
      />
    </template>

  <!-- </main> --> <!-- <-- CAMBIO: Esta era la línea que causaba el error -->

  <!-- <AppFooter /> -->
</template>
