<script setup lang="ts">
// Importamos 'onMounted' y 'computed'
import { onMounted, computed } from 'vue'
// Importamos los componentes de la página
import HeroSection from '@/components/home/HeroSection.vue'
import ContentSection from '@/components/home/ContentSection.vue'
// Importamos el tipo (ajusta la ruta si es necesario)
import type { HistoricSite } from '@/lib/api'
// Importamos el store de Pinia
import { useSitesStore } from '@/stores/sites'

// Inicializamos el store
const sitesStore = useSitesStore()

// Creamos propiedades computadas que leen del store
// Asumimos que 'sitesStore.items' tiene TODOS los sitios
const mejorPuntuados = computed(() => {
  // Lógica de ejemplo: clonar, ordenar y tomar 5
  return [...sitesStore.items]
    // @ts-ignore - La propiedad 'rating' viene del mock/API
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


// Cuando el componente se monta, llamamos al store
onMounted(() => {
  // Disparamos la carga de los sitios si aún no se ha hecho.
  // Esto asegura que al entrar a la Home, siempre se intente cargar el contenido.
  if (sitesStore.items.length === 0) {
     // sitesStore.loadFirstPage(); // <-- DESCOMENTA ESTA LÍNEA CUANDO USES LA ACCIÓN REAL
     console.log("Llamando a loadFirstPage() desde HomeView [RECUERDA DESCOMENTAR]");
     // Como es un mock, llamamos el mock loadFirstPage para que cargue los sitios de prueba.
     sitesStore.loadFirstPage();
  }
})

</script>

<template>
  <!-- 1. Sección Hero (Héroe) -->
    <HeroSection />

    <!-- CAMBIO: Loader visible mientras se cargan los datos -->
    <!-- Esto soluciona que la página se vea vacía al inicio -->
    <div v-if="sitesStore.isLoading" class="text-center py-20">
      <p class="text-gray-500 dark:text-gray-400">Cargando sitios destacados...</p>
      <!-- Aquí iría un componente 'Spinner' si tuvieras -->
    </div>

    <!-- 2. Sección de Contenido (Sitios Destacados) -->
    <!-- Solo se renderizan los carruseles si NO estamos cargando -->
    <template v-else-if="!sitesStore.isLoading">
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

      <!-- Mensaje si no hay ningún sitio en el store -->
      <div v-if="mejorPuntuados.length === 0 && recientementeAgregados.length === 0" class="text-center py-20">
        <p class="text-lg text-gray-600 dark:text-gray-400">
          Aún no hay sitios históricos cargados en el sistema.
        </p>
      </div>
    </template>

</template>
