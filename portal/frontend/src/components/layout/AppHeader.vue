<script setup lang="ts">
// Importamos RouterLink para la navegación
import { RouterLink } from 'vue-router'

// IMPORTANTE: Verifica que esta ruta sea correcta.
// Si moviste el archivo a 'components/ui/', usa esta:
import ThemeToggle from '@/components/ui/theme/ThemeToggle.vue'
// Si el archivo sigue suelto en 'components/', usa esta otra (descoméntala si falla la de arriba):
// import ThemeToggle from '@/components/ThemeToggle.vue'
</script>

<template>
  <!-- Header fijo y con efecto blur -->
  <header class="sticky top-0 z-50 w-full border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">

        <!-- 1. Logo/Título (Izquierda) -->
        <RouterLink :to="{ name: 'HomeView' }" class="flex-shrink-0 flex items-center cursor-pointer gap-2">
           <img class="h-8 w-auto" src="/logo.png" alt="Logo Explor.ar">
          <span class="text-2xl font-extrabold text-gray-900 dark:text-gray-100">Explor.ar</span>
        </RouterLink>

        <!-- 2. Menú de Navegación (Centro) -->
        <nav class="hidden md:flex items-center space-x-10">
          <RouterLink
            :to="{ name: 'HomeView' }"
            class="font-medium text-gray-700 dark:text-gray-300 hover:text-blue-600 transition-colors"
            active-class="text-blue-600 dark:text-blue-500"
          >
            Inicio
          </RouterLink>
          <RouterLink
            :to="{ name: 'SitesList' }"
            class="font-medium text-gray-700 dark:text-gray-300 hover:text-blue-600 transition-colors"
            active-class="text-blue-600 dark:text-blue-500"
          >
            Sitios
          </RouterLink>
        </nav>

        <!-- 3. Acciones (Derecha) - ¡AQUÍ DEBE ESTAR EL BOTÓN! -->
        <div class="flex items-center gap-4">
          <!-- Este es el componente del botón de tema -->
          <ThemeToggle />
        </div>

      </div>
    </div>
  </header>
</template>
