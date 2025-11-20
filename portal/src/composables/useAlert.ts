import Swal from 'sweetalert2'

export function useAlert() {
  const showError = (title: string, text?: string) => {
    return Swal.fire({
      icon: 'error',
      title,
      text: text || '',
      confirmButtonColor: '#dc2626',
    })
  }

  const showSuccess = (title: string, text?: string) => {
    return Swal.fire({
      icon: 'success',
      title,
      text: text || '',
      confirmButtonColor: '#3B82F6',
    })
  }

  const showWarning = (title: string, text?: string) => {
    return Swal.fire({
      icon: 'warning',
      title,
      text: text || '',
      confirmButtonColor: '#3B82F6',
    })
  }

  const showInfo = (title: string, text?: string) => {
    return Swal.fire({
      icon: 'info',
      title,
      text: text || '',
      confirmButtonColor: '#3B82F6',
    })
  }

  const showConfirm = (title: string, text?: string) => {
    return Swal.fire({
      title,
      text: text || '',
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#dc2626',
      cancelButtonColor: '#6b7280',
      confirmButtonText: 'Sí',
      cancelButtonText: 'Cancelar',
    })
  }

  return {
    showError,
    showSuccess,
    showWarning,
    showInfo,
    showConfirm,
  }
}

