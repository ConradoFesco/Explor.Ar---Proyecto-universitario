<script setup lang="ts">
import { RouterView } from 'vue-router'
// CAMBIO: Importamos el header global
import AppHeader from '@/components/layout/AppHeader.vue'
</script>

<template>
  <!-- CAMBIO: AppHeader se pone aquí para que sea global a TODAS las vistas -->
  <AppHeader />

  <!-- El RouterView renderiza la vista actual (Home, Sitios, Detalle) -->
  <!-- Damos un fondo base para toda la app -->
  <main class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <RouterView />
  </main>

  <!-- <AppFooter /> -->
</template>

<style scoped>
/* Estilos globales (si son necesarios) eliminados para un layout limpio */
</style>
