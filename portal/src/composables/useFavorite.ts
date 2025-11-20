import { toggleFavorite, type HistoricSite } from '@/lib/api'
import { useAlert } from './useAlert'
import { useAuth } from './useAuth'
import { useSitesStore } from '@/stores/sites'

export function useFavorite() {
  const { showError, showWarning } = useAlert()
  const { isAuthenticated, checkAuth, loginWithGoogle } = useAuth()
  const sitesStore = useSitesStore()

  async function toggleSiteFavorite(
    siteId: number,
    currentFavoriteState: boolean,
    onSuccess?: (newState: boolean) => void
  ): Promise<boolean> {
    // Verificar autenticación
    if (!isAuthenticated.value) {
      await checkAuth()
      if (!isAuthenticated.value) {
        await showWarning(
          'Inicio de sesión requerido',
          'Debe iniciar sesión para marcar sitios como favoritos'
        )
        await loginWithGoogle()
        return currentFavoriteState
      }
    }

    const newFavoriteState = !currentFavoriteState

    try {
      await toggleFavorite(siteId, newFavoriteState)
      
      // Actualizar en el store si el sitio está en la lista
      const idx = sitesStore.items.findIndex(s => s.id === siteId)
      if (idx >= 0) {
        sitesStore.items[idx] = { ...sitesStore.items[idx], is_favorite: newFavoriteState } as HistoricSite
      }

      // Ejecutar callback de éxito
      if (onSuccess) {
        onSuccess(newFavoriteState)
      }

      return newFavoriteState
    } catch (e: unknown) {
      const error = e instanceof Error ? e : { message: String(e) }
      const errorMsg = error.message || ''

      // Manejar errores de autenticación
      if (errorMsg.includes('AUTH_REQUIRED') || errorMsg.includes('401') || 
          errorMsg.includes('Autenticación') || errorMsg.includes('no autenticado')) {
        await showWarning(
          'Inicio de sesión requerido',
          'Debe iniciar sesión para marcar sitios como favoritos'
        )
        await loginWithGoogle()
      } else if (errorMsg.includes('NETWORK_ERROR')) {
        await showError(
          'Error de conexión',
          'No se pudo conectar con el servidor. Verifica tu conexión a internet.'
        )
      } else {
        await showError(
          'Error',
          `No se pudo ${newFavoriteState ? 'agregar' : 'quitar'} el favorito: ${errorMsg.replace(/^(AUTH_REQUIRED|NETWORK_ERROR):\s*/, '')}`
        )
      }

      throw error
    }
  }

  return {
    toggleSiteFavorite,
  }
}

