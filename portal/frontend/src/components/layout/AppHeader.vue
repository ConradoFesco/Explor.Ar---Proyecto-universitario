<script setup lang="ts">
// Importamos RouterLink para la navegación
import { RouterLink } from 'vue-router'
import ThemeToggle from '@/components/ui/theme/ThemeToggle.vue'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/composables/useAuth'

// Obtenemos las variables reactivas
const { isAuthenticated, user, logout, loginWithGoogle } = useAuth()

// Función para manejar el cierre de sesión
const handleLogout = async () => {
  await logout()
  // Redirigir al home si es necesario
}

// Avatar por defecto por si el usuario no tiene foto o falla la carga
const defaultAvatar = "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
</script>

<template>
  <!-- Header fijo y con efecto blur -->
  <header class="sticky top-0 z-50 w-full border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
    <div class="w-full px-4 sm:px-6 lg:px-8 xl:px-12">
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

        <!-- 3. Acciones (Derecha) -->
        <div class="flex items-center gap-4">
          <!-- Botón de Login (solo si NO está autenticado) -->
          <Button 
            v-if="!isAuthenticated" 
            @click="loginWithGoogle"
          >
            Iniciar Sesión con Google
          </Button>

          <!-- Perfil del usuario (solo si está autenticado) -->
          <div v-else class="flex items-center gap-3">
            <span class="text-gray-700 dark:text-gray-300 font-medium">
              {{ user?.name }}
            </span>

            <div class="relative group">
              <img 
                :src="user?.avatar_url || defaultAvatar" 
                alt="Perfil" 
                class="w-10 h-10 rounded-full border border-gray-200 dark:border-gray-700 cursor-pointer object-cover"
              />
              
              <div class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 hidden group-hover:block z-50 border border-gray-200 dark:border-gray-700">
                <a href="#" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">Mi Perfil</a>
                <button 
                  @click="handleLogout" 
                  class="block w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  Cerrar Sesión
                </button>
              </div>
            </div>
          </div>
          
          <ThemeToggle />
        </div>

      </div>
    </div>
  </header>
</template>
