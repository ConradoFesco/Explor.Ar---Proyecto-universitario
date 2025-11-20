<template>
  <div>
    <!-- LOADING STATE -->
    <div v-if="loading" class="flex gap-4 overflow-x-auto pb-4">
      <div
        v-for="n in 4"
        :key="n"
        class="w-64 h-40 bg-gray-200 rounded-xl animate-pulse"
      ></div>
    </div>

    <!-- EMPTY STATE -->
    <p v-else-if="items.length === 0" class="text-gray-600 italic">
      No hay elementos disponibles.
    </p>

    <!-- CAROUSEL -->
    <div v-else class="flex gap-6 overflow-x-auto pb-4">
      <div
        v-for="site in items"
        :key="site.id"
        class="site-card w-64 rounded-xl shadow bg-white cursor-pointer
               hover:-translate-y-1 hover:shadow-xl transition p-3"
      >
        <!-- IMAGE -->
        <div class="h-36 bg-gray-100 rounded-lg overflow-hidden">
          <img
            :src="site.cover_image_url || '/assets/no-image.jpg'"
            class="w-full h-full object-cover"
            alt="Imagen del sitio"
          />
        </div>

        <!-- INFO -->
        <h3 class="mt-3 text-lg font-bold text-gray-800">
          {{ site.name }}
        </h3>
        <p class="text-sm text-gray-600 line-clamp-2">
          {{ site.brief_description || "Sin descripción" }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { HistoricSite } from "@/lib/api";

defineProps<{
  items: HistoricSite[];
  loading: boolean;
}>();
</script>

<style>
.site-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
</style>
