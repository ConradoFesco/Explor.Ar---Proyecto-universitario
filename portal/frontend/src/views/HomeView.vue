<template>
  <div class="min-h-screen bg-gray-50">

    <!-- ==========================
         HERO / ENCABEZADO
    =========================== -->
    <section class="bg-white shadow-sm border-b py-10">
      <div class="max-w-5xl mx-auto px-6 text-center">

        <!-- LOGO + TÍTULO -->
        <div class="flex flex-col items-center mb-6">
          <h1 class="text-4xl font-extrabold text-gray-800 tracking-tight bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            ExplorAR
          </h1>

          <p class="text-gray-600 text-lg mt-1">
            Descubrí sitios históricos de Argentina
          </p>
        </div>

        <!-- BARRA DE BÚSQUEDA -->
        <div class="flex justify-center mt-6">
          <div class="relative w-full max-w-3xl">

            <input
              v-model="searchText"
              @keyup.enter="buscar"
              type="text"
              placeholder="Buscar sitios históricos..."
              class="w-full py-4 px-6 rounded-full border border-gray-300 shadow-md
                     focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400
                     text-gray-700 text-lg outline-none transition"
            />

            <button
              @click="buscar"
              class="absolute right-2 top-1/2 -translate-y-1/2 bg-indigo-500 hover:bg-indigo-600
                     text-white p-3 rounded-full shadow transition"
            >
              🔍
            </button>

          </div>
        </div>
      </div>
    </section>

    <!-- ==========================
         CONTENIDO PRINCIPAL
    =========================== -->
    <main class="max-w-6xl mx-auto px-6 py-12">

      <!-- === SECCIÓN: Mejores puntuados === -->
      <section class="mb-12">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold text-gray-800">Mejores Puntuados</h2>
          <RouterLink to="/sites" class="text-indigo-600 hover:text-indigo-800 text-sm font-medium">
            Ver todos →
          </RouterLink>
        </div>

        <div class="flex gap-6 overflow-x-auto pb-4 no-scrollbar">
          <SiteCard
            v-for="s in bestRated"
            :key="s.id"
            :site="s"
          />
          <p v-if="bestRated.length === 0" class="text-gray-500 italic">No hay elementos disponibles.</p>
        </div>
      </section>

      <!-- === SECCIÓN: Más Visitados === -->
      <section class="mb-12">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold text-gray-800">Más Visitados</h2>
          <RouterLink to="/sites" class="text-indigo-600 hover:text-indigo-800 text-sm font-medium">
            Ver todos →
          </RouterLink>
        </div>

        <div class="flex gap-6 overflow-x-auto pb-4 no-scrollbar">
          <SiteCard
            v-for="s in mostVisited"
            :key="s.id"
            :site="s"
          />
          <p v-if="mostVisited.length === 0" class="text-gray-500 italic">No hay elementos disponibles.</p>
        </div>
      </section>

      <!-- === SECCIÓN: Recientes === -->
      <section class="mb-12">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold text-gray-800">Recientemente Agregados</h2>
          <RouterLink to="/sites" class="text-indigo-600 hover:text-indigo-800 text-sm font-medium">
            Ver todos →
          </RouterLink>
        </div>

        <div class="flex gap-6 overflow-x-auto pb-4 no-scrollbar">
          <SiteCard
            v-for="s in recent"
            :key="s.id"
            :site="s"
          />
          <p v-if="recent.length === 0" class="text-gray-500 italic">No hay elementos disponibles.</p>
        </div>
      </section>
    </main>

  </div>
</template>



<script setup lang="ts">
import { ref, onMounted } from "vue";
import { fetchPublicSites } from "@/lib/api"; // tu API real
import type { HistoricSite } from "@/lib/api";
import SiteCard from "@/components/site/SiteCard.vue";

const searchText = ref("");

// Datos de cada carrusel
const bestRated = ref<HistoricSite[]>([]);
const mostVisited = ref<HistoricSite[]>([]);
const recent = ref<HistoricSite[]>([]);

async function cargarCarruseles() {
  try {
    // Mejor Puntuados — orden rating
    const ratingRes = await fetchPublicSites({
      orderBy: "rating",
      orderDir: "desc",
      perPage: 10,
    });
    bestRated.value = ratingRes.items;

    // Más Visitados — usamos orden por "visitas" si el backend lo soporta,
    // o usamos "rating" como fallback
    const visitedRes = await fetchPublicSites({
      orderBy: "created_at", // fallback
      orderDir: "desc",
      perPage: 10,
    });
    mostVisited.value = visitedRes.items;

    // Recientes — orden por fecha
    const recentRes = await fetchPublicSites({
      orderBy: "created_at",
      orderDir: "desc",
      perPage: 10,
    });
    recent.value = recentRes.items;

  } catch (err) {
    console.error("Error cargando carruseles:", err);
  }
}

function buscar() {
  console.log("Buscando:", searchText.value);
  // Redirigir al listado general con el texto como query
  window.location.href = `/sites?search=${encodeURIComponent(searchText.value)}`;
}

onMounted(() => {
  cargarCarruseles();
});
</script>



<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
</style>
