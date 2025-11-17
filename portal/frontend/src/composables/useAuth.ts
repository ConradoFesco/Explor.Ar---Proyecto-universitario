import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getApiBaseUrl } from '@/lib/api'

export function useAuth() {
  const router = useRouter()
  const route = useRoute()
  const isAuthenticated = ref(false)

  async function checkAuth(): Promise<boolean> {
    try {
      const base = getApiBaseUrl()
      const testRes = await fetch(`${base}/me/favorites?page=1&per_page=1`, {
        credentials: 'include',
        headers: { 'Accept': 'application/json' },
      })
      isAuthenticated.value = testRes.ok
      return testRes.ok
    } catch {
      isAuthenticated.value = false
      return false
    }
  }

  function redirectToLogin() {
    const returnTo = route.fullPath
    router.push({ 
      name: 'login', 
      query: { returnTo: returnTo !== '/login' ? returnTo : undefined }
    })
  }

  return {
    isAuthenticated,
    checkAuth,
    redirectToLogin,
  }
}

