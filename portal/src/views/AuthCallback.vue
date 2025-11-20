<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { getApiBaseUrl } from '@/lib/api'

const route = useRoute()
const router = useRouter()
const auth = useAuth()

onMounted(async () => {
  try {
    const code = route.query.code as string
    const state = route.query.state as string | undefined

    if (!code) {
      router.push({ name: 'HomeView' })
      return
    }

    const base = getApiBaseUrl()
    const response = await fetch(`${base}/google/exchange`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ code, state }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData?.error?.message || errorData?.message || 'Error al autenticar'
      alert(errorMessage)
      router.push({ name: 'HomeView' })
      return
    }

    const data = await response.json()
    
    if (data.status === 'success' && data.user) {
      auth.setUser(data.user)
      await new Promise(resolve => setTimeout(resolve, 100))
      await auth.checkAuth()
      router.push({ name: 'HomeView' })
    } else {
      router.push({ name: 'HomeView' })
    }
  } catch (error) {
    router.push({ name: 'HomeView' })
  }
})
</script>

<template>
  <div class="flex items-center justify-center min-h-screen">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p class="text-gray-600 dark:text-gray-400">Completando autenticación...</p>
    </div>
  </div>
</template>

