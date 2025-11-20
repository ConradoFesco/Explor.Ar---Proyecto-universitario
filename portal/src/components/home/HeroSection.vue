<script setup lang="ts">
// --- CAMBIO CLAVE: Importamos la imagen desde 'src/assets/' ---
// Usamos el alias '@' que apunta a 'src/'
import heroImageUrl from '@/assets/images/ImageHero.jpg'
</script>

<template>
  <!--
    Contenido principal de la sección.
    Usamos 'relative' para posicionar el contenido y el overlay.
    AÑADIMOS 'isolate': Esto crea un nuevo contexto de apilamiento.
    Ahora, el 'z-10' de la imagen se quedará "atrás" pero DENTRO de esta sección,
    sin esconderse detrás del fondo general de la página.
  -->
  <section class="relative w-full h-[60vh] md:h-[70vh] text-white isolate">

    <!--
      Imagen de Fondo
      CAMBIO CLAVE: Usamos ':src' (binding) para pasar la variable
      'heroImageUrl' que importamos arriba en el script.
      NO usamos src="assets/..."
    -->
    <img
      :src="heroImageUrl"
      alt="Imagen de fondo de un sitio histórico emblemático"
      class="absolute inset-0 w-full h-full object-cover -z-10"
      onerror="this.src='https://placehold.co/1920x800/57534e/f5f5f4?text=Error+Cargando+Imagen'"
    />

    <!--
      Overlay Oscuro
      CAMBIO: Aumentamos la opacidad de 60% a 75% (bg-black/75)
      para un contraste mucho más fuerte.
    -->
    <div class="absolute inset-0 bg-black/75 z-0"></div>

    <!-- Contenido Centrado -->
    <div class="relative z-10 h-full flex flex-col justify-center items-center text-center p-4">

      <!-- Título del Proyecto -->
      <h1 class="text-5xl sm:text-6xl md:text-7xl font-extrabold text-white drop-shadow-lg">
        Explor.ar
      </h1>

      <!-- Frase Invitacional -->
      <!-- CAMBIO: Se redujo el tamaño de la fuente para mejor jerarquía visual -->
      <p class="mt-4 text-base md:text-xl text-gray-200 drop-shadow-md max-w-2xl">
        Descubre los sitios históricos y el patrimonio cultural de nuestro país.
      </p>
    </div>
  </section>
</template>

<style scoped>
/* Estilos específicos para este componente si fueran necesarios */
/* Tailwind se encarga de la mayoría del diseño mobile-first */
</style>
