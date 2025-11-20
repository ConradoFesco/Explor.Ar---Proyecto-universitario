import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Detectar y aplicar la preferencia de tema del navegador automáticamente
function applySystemTheme() {
  const root = document.documentElement
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  
  if (systemPrefersDark) {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
  
  // Escuchar cambios en la preferencia del sistema
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (e.matches) {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  })
}

// Aplicar el tema antes de montar la app para evitar flash
applySystemTheme()

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
