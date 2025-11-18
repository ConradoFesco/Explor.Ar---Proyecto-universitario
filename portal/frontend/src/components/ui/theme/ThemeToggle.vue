<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Button } from '@/components/ui/button'
import { Sun, Moon } from 'lucide-vue-next'

const isDarkMode = ref(false)

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

const toggleTheme = () => {
  const newTheme = isDarkMode.value ? 'light' : 'dark'
  applyTheme(newTheme)
  localStorage.setItem('theme', newTheme)
}

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
    class="
      relative
      transition-all duration-300
      border-2
      bg-white text-black border-gray-200 hover:bg-gray-100
      dark:bg-slate-950 dark:text-white dark:border-slate-700 dark:hover:bg-slate-900
    "
    aria-label="Cambiar tema"
  >
    <Sun
      class="h-5 w-5 transition-all duration-500 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
      :class="isDarkMode ? 'rotate-90 scale-0 opacity-0' : 'rotate-0 scale-100 opacity-100'"
    />
    <Moon
      class="h-5 w-5 transition-all duration-500 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
      :class="isDarkMode ? 'rotate-0 scale-100 opacity-100' : '-rotate-90 scale-0 opacity-0'"
    />
  </Button>
</template>
