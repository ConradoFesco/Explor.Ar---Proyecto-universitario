<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-white text-gray-900">
    <header class="border-b">
      <div class="app-container py-3 flex items-center justify-between">
        <RouterLink to="/" class="flex items-center gap-2">
          <img alt="Logo" class="h-8 w-8" src="@/assets/logo.svg" />
          <span class="font-semibold">Patrimonio</span>
        </RouterLink>
        <nav class="flex items-center gap-4 text-sm">
          <RouterLink to="/" class="nav-link">Inicio</RouterLink>
          <RouterLink to="/sitios" class="nav-link">Sitios</RouterLink>
        </nav>
      </div>
    </header>
    <div class="app-container py-4 md:py-6">
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
.app-container {
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1rem;
  padding-right: 1rem;
}
.nav-link {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
}
.nav-link.router-link-active {
  background-color: #f3f4f6;
}
</style>
