<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Button } from '@/components/ui/button'
import { Sun, Moon } from 'lucide-vue-next'

// Estado para rastrear el tema actual
const isDarkMode = ref(false)

/**
 * Aplica el tema (claro u oscuro) al documento
 * @param {string} theme - 'dark' o 'light'
 */
const applyTheme = (theme: 'dark' | 'light') => {
  const root = document.documentElement
  if (theme === 'dark') {
    root.classList.add('dark')
    isDarkMode.value = true
  } else {
    root.classList.remove('dark')
    isDarkMode.value = false
  }
}

/**
 * Cambia el tema actual al opuesto
 */
const toggleTheme = () => {
  const newTheme = isDarkMode.value ? 'light' : 'dark'
  applyTheme(newTheme)
  localStorage.setItem('theme', newTheme)
}

// Al montar el componente, verifica el tema guardado o el preferido por el sistema
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches

  if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
    applyTheme('dark')
  } else {
    applyTheme('light')
  }
})
</script>

<template>
  <Button
    variant="outline"
    size="icon"
    @click="toggleTheme"
    class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm"
    aria-label="Cambiar tema"
  >
    <Sun class="h-5 w-5 transition-all" :class="isDarkMode ? 'rotate-90 scale-0' : 'rotate-0 scale-100'" />
    <Moon class="absolute h-5 w-5 transition-all" :class="isDarkMode ? 'rotate-0 scale-100' : '-rotate-90 scale-0'" />
  </Button>
</template>
