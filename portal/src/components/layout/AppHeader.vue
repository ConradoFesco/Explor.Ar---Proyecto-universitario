<script setup lang="ts">
// Importamos RouterLink para la navegación
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/composables/useAuth'
import { onClickOutside } from '@vueuse/core'

// Obtenemos las variables reactivas
const { isAuthenticated, user, logout, loginWithGoogle } = useAuth()

// Estado para controlar el menú desplegable
const dropdownOpen = ref(false)
const dropdownRef = ref<HTMLDivElement | null>(null)

// Cerrar el menú cuando se hace click fuera
onClickOutside(dropdownRef, () => {
  dropdownOpen.value = false
})

// Función para toggle del menú
const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value
}

// Cerrar el menú cuando se navega
const closeDropdown = () => {
  dropdownOpen.value = false
}

// Función para manejar el cierre de sesión
const handleLogout = async () => {
  await logout()
  closeDropdown()
  // Redirigir al home si es necesario
}

// Avatar por defecto por si el usuario no tiene foto o falla la carga
const defaultAvatar = "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
</script>

<template>
  <!-- Header fijo y con efecto blur -->
  <header class="sticky top-0 z-50 w-full border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
    <div class="w-full px-4 sm:px-6 lg:px-8 xl:px-12">
      <div class="flex justify-between items-center h-16 gap-2 sm:gap-4">

        <!-- 1. Logo/Título (Izquierda) -->
        <RouterLink :to="{ name: 'HomeView' }" class="flex-shrink-0 flex items-center cursor-pointer gap-1 sm:gap-2">
           <img class="h-6 sm:h-8 w-auto" src="/logo.png" alt="Logo Explor.ar">
          <span class="text-lg sm:text-2xl font-extrabold text-gray-900 dark:text-gray-100">Explor.ar</span>
        </RouterLink>

        <!-- 2. Menú de Navegación (Centro) -->
        <nav class="flex items-center space-x-2 sm:space-x-4 md:space-x-8 flex-1 justify-center">
          <RouterLink
            :to="{ name: 'HomeView' }"
            class="relative px-3 sm:px-6 md:px-8 py-2 sm:py-3 rounded-lg text-sm sm:text-base md:text-lg font-semibold text-gray-700 dark:text-gray-300 
                   hover:bg-gray-100 dark:hover:bg-gray-800 
                   transition-all duration-200 ease-in-out
                   hover:text-blue-600 dark:hover:text-blue-400 whitespace-nowrap"
            active-class="text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30"
          >
            Inicio
          </RouterLink>
          <RouterLink
            :to="{ name: 'SitesList' }"
            class="relative px-3 sm:px-6 md:px-8 py-2 sm:py-3 rounded-lg text-sm sm:text-base md:text-lg font-semibold text-gray-700 dark:text-gray-300 
                   hover:bg-gray-100 dark:hover:bg-gray-800 
                   transition-all duration-200 ease-in-out
                   hover:text-blue-600 dark:hover:text-blue-400 whitespace-nowrap"
            active-class="text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30"
          >
            Sitios
          </RouterLink>
        </nav>

        <!-- 3. Acciones (Derecha) -->
        <div class="flex items-center gap-2 sm:gap-4 flex-shrink-0">
          <!-- Botón de Login (solo si NO está autenticado) -->
          <Button 
            v-if="!isAuthenticated" 
            @click="loginWithGoogle"
            class="text-xs sm:text-sm px-2 sm:px-4"
          >
            <span class="hidden sm:inline">Iniciar Sesión con Google</span>
            <span class="sm:hidden">Iniciar Sesión</span>
          </Button>

          <!-- Perfil del usuario (solo si está autenticado) -->
          <div v-else class="flex items-center gap-2 sm:gap-3">
            <span class="hidden sm:inline text-gray-700 dark:text-gray-300 font-medium text-sm">
              {{ user?.name }}
            </span>

            <div ref="dropdownRef" class="relative">
              <button
                @click="toggleDropdown"
                class="focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-full"
                aria-label="Menú de usuario"
                :aria-expanded="dropdownOpen"
              >
                <img 
                  :src="user?.avatar_url || defaultAvatar" 
                  alt="Perfil" 
                  class="w-10 h-10 rounded-full border border-gray-200 dark:border-gray-700 cursor-pointer object-cover hover:ring-2 hover:ring-blue-500 transition-all"
                />
              </button>
              
              <!-- Menú desplegable -->
              <div 
                v-show="dropdownOpen"
                class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 z-50 border border-gray-200 dark:border-gray-700"
              >
                <RouterLink 
                  :to="{ name: 'UserProfile' }"
                  @click="closeDropdown"
                  class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  Mi Perfil
                </RouterLink>
                <button 
                  @click="handleLogout" 
                  class="block w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  Cerrar Sesión
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </header>
</template>
