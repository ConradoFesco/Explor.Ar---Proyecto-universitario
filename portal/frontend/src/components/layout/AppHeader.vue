<script setup lang="ts">
// ... existing code ... -->
import { RouterLink } from 'vue-router'
</script>

<template>
  <!--
    Usamos 'sticky top-0' para que el header quede fijo.
    Los fondos con opacidad y 'backdrop-blur' le dan el efecto profesional.
  -->
  <header class="sticky top-0 z-50 w-full border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">

        <!-- Logo/Título del Sitio -->
        <RouterLink :to="{ name: 'HomeView' }" class="flex-shrink-0 flex items-center cursor-pointer gap-2">
          <!-- Idealmente aquí iría tu logo de 'public/logo.png' -->
           <img class="h-8 w-auto" src="/logo.png" alt="Logo Explor.ar">
          <!-- CAMBIO: de font-bold a font-extrabold -->
          <span class="text-2xl font-extrabold text-gray-900 dark:text-gray-100">Explor.ar</span>
        </RouterLink>

        <!-- CAMBIO: Menú de Navegación (oculto en móvil) -->
        <!-- CAMBIO: Aumentamos la separación de space-x-8 a space-x-10 -->
        <nav class="hidden md:flex items-center space-x-10">
          <RouterLink
            :to="{ name: 'HomeView' }"
            class="font-medium text-gray-700 dark:text-gray-300 hover:text-blue-600"
            active-class="text-blue-600 dark:text-blue-500"
          >
            Inicio
          </RouterLink>
          <RouterLink
            :to="{ name: 'SitesList' }"
            class="font-medium text-gray-700 dark:text-gray-300 hover:text-blue-600"
            active-class="text-blue-600 dark:text-blue-500"
          >
            Sitios
          </RouterLink>
          <!-- Aquí puedes agregar más links -->
        </nav>

        <!-- Acciones (Botón de Tema) -->
        <div class="flex items-center">
          <ThemeToggle />
          <!-- Aquí podrían ir otros botones (ej: Login) -->
        </div>

      </div>
    </div>
  </header>
</template>
