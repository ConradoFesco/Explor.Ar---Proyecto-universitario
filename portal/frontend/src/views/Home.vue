<script setup>
// Importamos el componente HeroSection
import HeroSection from '@/components/HeroSection.vue'

// Aquí importaremos ContentSection cuando esté listo
// import ContentSection from '@/components/ContentSection.vue'
</script>

<template>
  <main class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- 1. Sección Hero (Héroe) -->
    <HeroSection />

    <!-- 2. Sección de Contenido (Espacio reservado) -->
    <div class="py-16 px-4 md:px-8">
      <div class="max-w-7xl mx-auto">
        <h2 class="text-3xl font-bold text-center text-gray-900 dark:text-gray-100 mb-12">
          Explora Nuestras Colecciones
        </h2>

        <!--
          Aquí es donde irá el componente ContentSection
          con los carruseles de sitios.
        -->
        <div class="text-center text-gray-600 dark:text-gray-400 p-8 bg-gray-100 dark:bg-gray-800 rounded-lg">
          <p class="italic">
            (Próximamente: El componente `ContentSection` con los carruseles de "Mejor Puntuados", "Recientemente Agregados", etc.)
          </p>
          <!-- <ContentSection /> -->
        </div>

      </div>
    </div>
  </main>
</template>

<style>
/* Podemos añadir estilos globales para esta vista si es necesario */
</style>
