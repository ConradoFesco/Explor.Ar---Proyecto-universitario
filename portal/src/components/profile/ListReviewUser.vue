<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

interface Review {
  id: number
  site_id: number
  site_name: string
  rating: number
  date: string
  excerpt: string
  status?: string
}

interface Props {
  reviews: Review[]
  loading: boolean
}

defineProps<Props>()

const emit = defineEmits(['edit', 'delete'])

const normalizeStatus = (status: string | undefined): string => {
  if (!status) return 'pending'
  return status.trim().toLowerCase()
}

const getStatusColor = (status: string | undefined) => {
  const s = normalizeStatus(status)
  switch (s) {
    case 'approved':
    case 'aprobada':
      return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/30'
    case 'rejected':
    case 'rechazada':
      return 'bg-rose-100 text-rose-700 dark:bg-rose-500/20 dark:text-rose-400 border border-rose-200 dark:border-rose-500/30'
    case 'pending':
    case 'pendiente':
      return 'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400 border border-amber-200 dark:border-amber-500/30'
    default:
      return 'bg-gray-100 text-gray-700 dark:bg-gray-700/30 dark:text-gray-300 border border-gray-200 dark:border-gray-600/30'
  }
}

const getStatusLabel = (status: string | undefined) => {
  const s = normalizeStatus(status)
  switch (s) {
    case 'approved':
    case 'aprobada':
      return 'Aprobada'
    case 'rejected':
    case 'rechazada':
      return 'Rechazada'
    case 'pending':
    case 'pendiente':
      return 'Pendiente'
    default:
      return 'Desconocido'
  }
}

const getStatusIcon = (status: string | undefined) => {
  const s = normalizeStatus(status)
  switch (s) {
    case 'approved':
    case 'aprobada':
      return 'fa-check-circle'
    case 'rejected':
    case 'rechazada':
      return 'fa-times-circle'
    case 'pending':
    case 'pendiente':
      return 'fa-clock'
    default:
      return 'fa-question-circle'
  }
}
</script>

<template>
  <div class="w-full">
    <div v-if="loading" class="space-y-4">
      <Card v-for="i in 3" :key="i" class="dark:bg-gray-800/50 dark:border-gray-700/50 backdrop-blur">
        <CardHeader>
          <div class="flex gap-4">
            <Skeleton class="h-12 w-12 rounded-full shrink-0 dark:bg-gray-700" />
            <div class="space-y-3 flex-1">
              <Skeleton class="h-5 w-[40%] dark:bg-gray-700" />
              <Skeleton class="h-4 w-full dark:bg-gray-700" />
            </div>
          </div>
        </CardHeader>
      </Card>
    </div>

    <div v-else-if="reviews.length > 0" class="grid gap-4 max-w-full">
      <Card v-for="review in reviews" :key="review.id" class="group hover:shadow-xl transition-all duration-300 dark:bg-gray-800/50 dark:border-gray-700/50 backdrop-blur hover:scale-[1.01] overflow-hidden">
        <CardHeader class="pb-3">
          <div class="flex justify-between items-start gap-4">
            <div class="flex-1 min-w-0 space-y-2">
              <div class="flex items-center gap-3 flex-wrap">
                <CardTitle class="text-base sm:text-lg font-bold text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors break-words">
                  {{ review.site_name }}
                </CardTitle>

                <i
                  v-for="i in 5"
                  :key="i"
                  class="fa-star h-4 w-4"
                  :class="[
                    i <= review.rating
                      ? 'fas text-yellow-400'  /* Llena */
                      : 'far text-gray-400'    /* Borde */
                  ]"
                ></i>
              </div>
              <CardDescription class="dark:text-gray-400 text-xs flex items-center gap-1.5">
                <i class="far fa-calendar text-xs"></i>
                {{ review.date }}
              </CardDescription>
            </div>
            <span :class="`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold shrink-0 ${getStatusColor(review.status)}`">
              <i :class="`fas ${(review.status)} mr-1.5 text-xs`"></i>
              {{ getStatusLabel(review.status) }}
            </span>
          </div>
        </CardHeader>
        <CardContent class="space-y-3 relative">
          <div class="relative pl-4 border-l-2 border-blue-300 dark:border-blue-600/50 py-2">
            <p class="text-sm text-gray-700 dark:text-gray-300 italic line-clamp-2 leading-relaxed">
              "{{ review.excerpt || 'Sin comentario' }}"
            </p>
          </div>
          <div class="flex items-center gap-2 pt-2">
              <button @click="$emit('edit', review)" class="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 text-blue-600 dark:text-blue-400 transition-all hover:scale-105 text-xs font-medium" title="Editar reseña">
                <i class="fas text-xs"></i>
                Editar
              </button>
              <button @click="$emit('delete', review.id)" class="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-rose-50 hover:bg-rose-100 dark:bg-rose-900/30 dark:hover:bg-rose-900/50 text-rose-600 dark:text-rose-400 transition-all hover:scale-105 text-xs font-medium" title="Eliminar reseña">
                <i class="fas text-xs"></i>
                Eliminar
              </button>
          </div>
        </CardContent>
      </Card>
    </div>

    <div v-else class="flex flex-col items-center justify-center py-16 text-center bg-gradient-to-br from-gray-50 to-white dark:from-gray-800/30 dark:to-gray-900/30 rounded-2xl border-2 border-dashed border-gray-300 dark:border-gray-700/50 w-full max-w-md mx-auto backdrop-blur">
      <div class="bg-gradient-to-br from-blue-100 to-blue-200 dark:from-blue-900/40 dark:to-blue-800/30 p-6 rounded-full mb-5 shadow-lg">
        <i class="fas text-blue-600 dark:text-blue-400 text-4xl"></i>
      </div>
      <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">Sin reseñas aún</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6 max-w-[280px]">
        Comparte tu opinión y ayuda a otros exploradores a descubrir nuevos lugares.
      </p>
      <Button class="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white shadow-lg hover:shadow-xl transition-all">
        <i class="fas fa-compass mr-2"></i>
        Explorar Sitios
      </Button>
    </div>
  </div>
</template>
