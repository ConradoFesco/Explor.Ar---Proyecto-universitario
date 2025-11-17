/**
 * Formatea una fecha a formato legible en español
 */
export function formatDate(dateString: string | null): string {
  if (!dateString) return ''
  try {
    return new Date(dateString).toLocaleDateString('es-AR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch {
    return dateString
  }
}

