<script setup lang="ts">
import { ref } from 'vue'
// Importamos los componentes de shadcn/vue que usaremos
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
// Importamos un ícono para el botón de búsqueda
import { Search } from 'lucide-vue-next'
// import { useRouter } from 'vue-router' // Descomentar al implementar navegación

// --- CAMBIO CLAVE: Importamos la imagen desde 'src/assets/' ---
// Usamos el alias '@' que apunta a 'src/'
import heroImageUrl from '@/assets/images/ImageHero.jpg'


// const router = useRouter() // Descomentar al implementar navegación
const searchTerm = ref('')

/**
 * Maneja el envío del formulario de búsqueda.
 * Redirige al listado de sitios aplicando el término de búsqueda como filtro.
 */
const handleSearch = () => {
  if (searchTerm.value.trim()) {
    // Lógica de redirección con Vue Router
    // router.push({ path: '/listado', query: { q: searchTerm.value } })

    // Placeholder temporal hasta que se configure Vue Router
    console.log(`Redirigiendo a /listado?q=${searchTerm.value}`)
    // Se ha eliminado el alert()
  }
}
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

      <!-- Buscador Rápido -->
      <!-- CAMBIO: Aumentamos el margen superior de mt-8 a mt-10 para separarlo del subtítulo -->
      <form @submit.prevent="handleSearch" class="mt-10 w-full max-w-lg">
        <div class="flex w-full items-center space-x-2 rounded-lg bg-white/90 p-2 shadow-lg backdrop-blur-sm">

          <!-- Input de shadcn/vue -->
          <Input
            v-model="searchTerm"
            type="text"
            placeholder="Buscar un sitio, ciudad o provincia..."
            class="flex-1 text-gray-900 border-none focus:ring-0 focus:outline-none bg-transparent placeholder:text-gray-600"
          />

          <!-- Button de shadcn/vue -->
          <Button
            type="submit"
            class="bg-blue-600 hover:bg-blue-700 text-white rounded-md"
            aria-label="Buscar"
          >
            <Search class="h-5 w-5" />
            <!-- Texto del botón opcional en pantallas pequeñas -->
            <span class="ml-2 hidden sm:inline"></span>
          </Button>

        </div>
      </form>
    </div>
  </section>
</template>

<style scoped>
/* Estilos específicos para este componente si fueran necesarios */
/* Tailwind se encarga de la mayoría del diseño mobile-first */
</style>
