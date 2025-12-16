<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useAuth } from '@/composables/useAuth'
import { getApiBaseUrl } from '@/lib/api'
import { useRouter } from 'vue-router'
import { useAlert } from '@/composables/useAlert'
import UserProfileHeader from '../components/profile/UserProfileHeader.vue'
import ListReviewUser from '@/components/profile/ListReviewUser.vue'
import ListFavoritesUser from '@/components/profile/ListFavoritesUser.vue'
import SortButton from '@/components/profile/SortButton.vue'
import Pagination from '@/components/profile/Pagination.vue'

const { user: authUser } = useAuth()

const currentUser = computed(() => {
  if (authUser.value) {
    return {
      name: authUser.value.name || 'Usuario',
      email: authUser.value.mail || '',
      avatar_url: authUser.value.avatar_url || ''
    }
  }
  return { name: 'Cargando...', email: '...', avatar_url: '' }
})

const { showConfirm, showSuccess, showError } = useAlert()
const loading = ref(false)
const activeTab = ref('reviews')
const sortOrder = ref<'asc' | 'desc'>('desc')
const page = ref(1)
const totalPages = ref(1)
const reviews = ref<Array<{
  id: any
  site_name: string
  rating: number
  date: string
  excerpt: string
}>>([])
const favorites = ref<Array<{
  id: any
  site_name: string
  image_url: any
  location: string
  added_at: string
}>>([])

const router = useRouter()

const fetchData = async () => {
  if (!authUser.value?.id) return

  loading.value = true

  reviews.value = []
  favorites.value = []

  try {
    const base = getApiBaseUrl()
    const params = new URLSearchParams()
    if (page.value !== undefined && page.value !== null) {
      params.set('page', page.value.toString())
    }
    if (sortOrder.value) {
      params.set('sort', sortOrder.value)
    }

    if (activeTab.value === 'reviews') {
      const url = `${base}/me/reviews?${params.toString()}`
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include'
      })

      if (!response.ok) {
        console.error(`Error al cargar reviews: HTTP ${response.status}`, await response.text())
        throw new Error(`Error al cargar reviews del backend.`)
      }

      const data = await response.json()
      reviews.value = (data.items || []).map((r: any) => ({
        id: r.id,
        site_id: r.site_id,
        site_name: r.site_name || 'Sitio sin nombre',
        rating: Number(r.rating),
        date: r.inserted_at ? new Date(r.inserted_at).toLocaleDateString('es-AR') : '',
        excerpt: (r.comment || '') ? ((r.comment || '').length > 100 ? (r.comment || '').substring(0, 100) + '...' : (r.comment || '')) : '',
        status: r.status || 'pending'
      }))
      totalPages.value = data.pagination?.pages || 1
    } else {
      const url = `${base}/me/favorites?${params.toString()}`
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include'
      })

      if (!response.ok) {
        console.error(`Error al cargar favorites: HTTP ${response.status}`, await response.text())
        throw new Error(`Error al cargar favorites del backend.`)
      }

      const payload = await response.json()
      const items: any[] = payload.data || []
      const meta = payload.meta || {}

      favorites.value = items.map((item: any) => ({
        id: item.id,
        site_name: item.name || 'Sitio sin nombre',
        image_url: item.cover_image_url || item.cover_image?.url_publica,
        location: item.city ? `${item.city}${item.province ? ', ' + item.province : ''}` : 'Ubicación no disponible',
        added_at: item.inserted_at ? new Date(item.inserted_at).toLocaleDateString('es-AR') : ''
      }))
      const perPage = meta.per_page ?? 25
      const total = meta.total ?? items.length
      totalPages.value = Math.max(1, Math.ceil(total / perPage))
    }

    if (totalPages.value < 1) {
      totalPages.value = 1
    }

  } catch (error) {
    console.error("Error fetching data:", error)
    reviews.value = []
    favorites.value = []
    totalPages.value = 1
  } finally {
    loading.value = false
  }
}

const changePage = (delta: number) => {
  const newPage = page.value + delta
  if (newPage >= 1 && newPage <= totalPages.value) {
    page.value = newPage
    fetchData()
  }
}

const handleEditReview = (review: any) => {
  router.push({
    name: 'SiteDetail',
    params: { id: review.site_id },
    query: { editReview: review.id }
  })
}

const handleDeleteReview = async (reviewId: number) => {
  const result = await showConfirm(
    'Eliminar reseña',
    '¿Está seguro de que desea eliminar su reseña? Esta acción no se puede deshacer.'
  )

  if (!result.isConfirmed) {
    return
  }

  try {
    const base = getApiBaseUrl()
    await fetch(`${base}/me/reviews/${reviewId}`, {
      method: 'DELETE',
      credentials: 'include'
    })
    await showSuccess(
      'Reseña eliminada',
      'Su reseña ha sido eliminada correctamente.'
    )
    fetchData()
  } catch (e) {
    console.error('Error eliminando reseña', e)
    await showError(
      'Error',
      'No se pudo eliminar la reseña. Por favor, intente nuevamente.'
    )
  }
}

onMounted(() => { if (authUser.value) fetchData() })
watch(authUser, (newVal) => { if (newVal) fetchData() })
watch(sortOrder, () => { page.value = 1; fetchData() })
watch(activeTab, () => { page.value = 1; fetchData() })
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-950 pb-20 transition-colors duration-300 flex flex-col items-center">

    <UserProfileHeader :user="currentUser" />

    <div class="w-full max-w-6xl px-4 sm:px-6 lg:px-8 pt-8 relative z-10">

      <Tabs v-model="activeTab" class="w-full">

        <div class="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 mb-6 sm:mb-8 w-full">

          <div class="bg-white dark:bg-gray-800 p-1.5 rounded-full shadow-lg border border-gray-200 dark:border-gray-700 flex">

            <TabsList class="bg-transparent inline-flex space-x-0">

              <TabsTrigger
                value="reviews"
                class="rounded-full px-5 py-2 text-sm font-medium transition-all text-center whitespace-nowrap
                       data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-md
                       data-[state=inactive]:text-gray-700 dark:data-[state=inactive]:text-gray-100 dark:data-[state=inactive]:bg-transparent hover:text-blue-600 dark:hover:text-blue-400"
              >
                Mis Reseñas
              </TabsTrigger>

              <TabsTrigger
                value="favorites"
                class="rounded-full px-5 py-2 text-sm font-medium transition-all text-center whitespace-nowrap
                       data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-md
                       data-[state=inactive]:text-gray-700 dark:data-[state=inactive]:text-gray-100 dark:data-[state=inactive]:bg-transparent hover:text-blue-600 dark:hover:text-blue-400"
              >
                Favoritos
              </TabsTrigger>
            </TabsList>
          </div>

          <SortButton v-model="sortOrder" label="Fecha" />
        </div>

        <TabsContent value="reviews" class="mt-0 focus-visible:outline-none w-full">
          <ListReviewUser :reviews="reviews"
                          :loading="loading"
                          @edit="handleEditReview"
                          @delete="handleDeleteReview" />
        </TabsContent>

        <TabsContent value="favorites" class="mt-0 focus-visible:outline-none w-full">
          <ListFavoritesUser :favorites="favorites" :loading="loading" @favorite-removed="fetchData" />
        </TabsContent>

      </Tabs>

      <Pagination
        :current-page="page"
        :total-pages="totalPages"
        :disabled="loading || (reviews.length === 0 && favorites.length === 0)"
        @change-page="changePage"
      />

    </div>
  </div>
</template>
