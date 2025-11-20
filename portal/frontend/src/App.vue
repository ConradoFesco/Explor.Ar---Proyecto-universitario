<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import AppHeader from '@/components/layout/AppHeader.vue'
import { useAuth } from '@/composables/useAuth'

const auth = useAuth()
const route = useRoute()

// Computada: ocultar header en la página de mantenimiento
const showHeader = computed(() => route.name !== 'Maintenance')

// Verificar autenticación al cargar la app
onMounted(async () => {
  await auth.checkAuth()
})
</script>

<template>
  <!-- CAMBIO: AppHeader se pone aquí para que sea global a TODAS las vistas, excepto en mantenimiento -->
  <AppHeader v-if="showHeader" />

  <!-- El RouterView renderiza la vista actual (Home, Sitios, Detalle, Mantenimiento) -->
  <!-- Damos un fondo base para toda la app -->
  <main class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <RouterView />
  </main>

  <!-- <AppFooter /> -->
</template>

<style scoped>
/* Estilos globales (si son necesarios) eliminados para un layout limpio */
</style>
