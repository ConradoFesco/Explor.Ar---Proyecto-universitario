import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getApiBaseUrl } from '@/lib/api'

const user = ref<any>(null)

export function useAuth() {
  const router = useRouter()
  const route = useRoute()

  // Computada: es true si 'user' tiene datos, false si es null
  const isAuthenticated = computed(() => !!user.value)

  // Función para actualizar el usuario (llamada desde checkAuth o login)
  function setUser(userData: any) {
    user.value = userData
  }

  // Función para limpiar (logout)
  function clearUser() {
    user.value = null
  }

  async function checkAuth(): Promise<boolean> {
    try {
      const base = getApiBaseUrl()
      // Usar el endpoint específico /me para verificar autenticación (más eficiente)
      const res = await fetch(`${base}/me`, {
        credentials: 'include',
        headers: { 'Accept': 'application/json' },
      })
      
      if (!res.ok) {
        clearUser()
        return false
      }
      
      const data = await res.json()
      if (data.authenticated === true && data.user) {
        setUser(data.user)
        return true
      } else {
        clearUser()
        return false
      }
    } catch {
      clearUser()
      return false
    }
  }

  async function loginWithGoogle() {
    try {
      const base = getApiBaseUrl()
      // Obtener la URL de autorización de Google desde el backend
      const response = await fetch(`${base}/google/login`, {
        credentials: 'include',
        headers: { 'Accept': 'application/json' },
      })
      
      if (!response.ok) {
        console.error('Error al obtener la URL de autorización')
        return
      }
      
      const data = await response.json()
      
      if (data.status === 'success' && data.auth_url) {
        // Redirigir al usuario a Google OAuth
        window.location.href = data.auth_url
      } else {
        console.error('Error: respuesta inesperada del servidor')
      }
    } catch (error) {
      console.error('Error al iniciar el flujo de autenticación:', error)
    }
  }

  async function logout() {
    try {
      const base = getApiBaseUrl()
      await fetch(`${base}/logout`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Accept': 'application/json' },
      })
    } catch (error) {
      console.error('Error al cerrar sesión:', error)
    } finally {
      clearUser()
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
    user,
    isAuthenticated,
    setUser,
    clearUser,
    checkAuth,
    loginWithGoogle,
    logout,
    redirectToLogin,
  }
}

