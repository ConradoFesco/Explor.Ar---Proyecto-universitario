<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { fetchPublicSites } from "@/lib/api";

// Shadcn components
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";

import Logo from "@/assets/logo.png";

// Estado
const loading = ref(true);
const query = ref("");

const bestRated = ref<any[]>([]);
const mostVisited = ref<any[]>([]);
const recent = ref<any[]>([]);

// ⭐ Simulación de criterios (por falta de endpoints dedicados)
const loadData = async () => {
  loading.value = true;
  const res = await fetchPublicSites({ perPage: 30 });

  const items = res.items ?? [];

  bestRated.value = [...items].sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0)).slice(0, 10);
  mostVisited.value = [...items].sort(() => Math.random() - 0.5).slice(0, 10); // placeholder
  recent.value = [...items].sort((a, b) => b.id - a.id).slice(0, 10);

  loading.value = false;
};

onMounted(loadData);

function openDetails(id: number) {
  alert("Detalle todavía no implementado, ID: " + id);
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- HEADER -->
    <header class="bg-white border-b shadow-sm sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-6 py-4 flex flex-col items-center gap-3">

        <h1
          class="text-4xl font-extrabold bg-gradient-to-r from-blue-600 to-purple-600 text-transparent bg-clip-text"
        >
          ExplorAR
        </h1>

        <!-- SEARCH -->
        <div class="w-full max-w-xl">
          <Input
            v-model="query"
            placeholder="Buscar sitios históricos..."
            class="text-lg h-12 px-4"
            @keyup.enter="loadData"
          />
        </div>
      </div>
    </header>

    <!-- BODY -->
    <main class="max-w-7xl mx-auto px-6 mt-10 space-y-16">
      <!-- COMPONENTE SECCIÓN -->
      <SectionCarousel
        title="⭐ Mejores Puntuados"
        :sites="bestRated"
        :loading="loading"
        @open-details="openDetails"
      />

      <SectionCarousel
        title="🔥 Más Buscados"
        :sites="mostVisited"
        :loading="loading"
        @open-details="openDetails"
      />

      <SectionCarousel
        title="🆕 Recientes"
        :sites="recent"
        :loading="loading"
        @open-details="openDetails"
      />
    </main>
  </div>
</template>

<style scoped>
</style>
