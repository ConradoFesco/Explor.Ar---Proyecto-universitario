<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useAuth } from '@/composables/useAuth'
import UserProfileHeader from '../components/profile/UserProfileHeader.vue'
import ListReviewUser from '@/components/profile/ListReviewUser.vue'
import ListFavoritesUser from '@/components/profile/ListFavoritesUser.vue'

const { user: authUser } = useAuth()

const currentUser = computed(() => {
  if (authUser.value) {
    return {
      name: authUser.value.name || 'Usuario',
      email: authUser.value.email || '',
      avatar_url: authUser.value.avatar_url || ''
    }
  }
  return { name: 'Cargando...', email: '...', avatar_url: '' }
})

const loading = ref(false)
const activeTab = ref('reviews')
const sortOrder = ref('desc')
const page = ref(1)
const totalPages = ref(1)
const reviews = ref([])
const favorites = ref([])

const fetchData = async () => {
  if (!authUser.value?.id) return

  loading.value = true

  reviews.value = []
  favorites.value = []

  try {
    const userId = authUser.value.id
    const resource = activeTab.value === 'reviews' ? 'reviews' : 'favorites'

    // CORRECCIÓN CLAVE: Devolvemos el userId a la URL, asumiendo que Flask lo necesita.
    let url = `/api/users/${userId}/${resource}`

    const params = new URLSearchParams({
      page: page.value.toString(),
      per_page: '5',
      sort: sortOrder.value
    })

    const response = await fetch(`${url}?${params.toString()}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })

    if (!response.ok) {
        console.error(`Error al cargar ${resource}: HTTP ${response.status}`, await response.text());
        throw new Error(`Error al cargar ${resource} del backend.`);
    }

    const data = await response.json()

    if (activeTab.value === 'reviews') {
      reviews.value = data.items || data
    } else {
      favorites.value = data.items || data
    }

    totalPages.value = data.pages || 1

    if ((activeTab.value === 'reviews' && reviews.value.length === 0) ||
        (activeTab.value === 'favorites' && favorites.value.length === 0)) {
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

onMounted(() => { if (authUser.value) fetchData() })
watch(authUser, (newVal) => { if (newVal) fetchData() })
watch(sortOrder, () => { page.value = 1; fetchData() })
watch(activeTab, () => { page.value = 1; fetchData() })
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-950 pb-20 transition-colors duration-300">

    <UserProfileHeader :user="currentUser" />

    <div class="container max-w-3xl mx-auto px-4 -mt-8 relative z-10">

      <Tabs v-model="activeTab" class="w-full">

        <!-- CONTROLES: Asegura el centrado del bloque completo (Pestañas + Ordenar) -->
        <div class="flex flex-col md:flex-row items-center justify-center gap-3 mb-8">

          <!-- PESTAÑAS -->
          <div class="bg-white dark:bg-gray-800 p-1.5 rounded-full shadow-lg border border-gray-200 dark:border-gray-700 flex">

            <TabsList class="bg-transparent inline-flex space-x-0">

              <!-- Trigger Reviews -->
              <TabsTrigger
                value="reviews"
                class="rounded-full px-5 py-2 text-sm font-medium transition-all text-center whitespace-nowrap
                       data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-md
                       data-[state=inactive]:text-gray-700 dark:data-[state=inactive]:text-gray-100 dark:data-[state=inactive]:bg-transparent hover:text-blue-600 dark:hover:text-blue-400"
              >
                Mis Reseñas
              </TabsTrigger>

              <!-- Trigger Favoritos -->
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

          <!-- ORDENAR -->
          <div class="flex items-center gap-2 bg-white dark:bg-gray-800 px-4 py-2 rounded-full shadow-lg border border-gray-200 dark:border-gray-700">
            <span class="text-xs font-medium text-gray-500 dark:text-gray-400 whitespace-nowrap">Ordenar:</span>
            <Select v-model="sortOrder">
              <SelectTrigger class="w-[120px] h-auto bg-transparent border-0 focus:ring-0 text-sm font-semibold text-gray-800 dark:text-gray-200">
                <SelectValue placeholder="Ordenar" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="desc">Más recientes</SelectItem>
                <SelectItem value="asc">Más antiguos</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <!-- CONTENIDO -->
        <TabsContent value="reviews" class="mt-0 focus-visible:outline-none">
          <ListReviewUser :reviews="reviews" :loading="loading" />
        </TabsContent>

        <TabsContent value="favorites" class="mt-0 focus-visible:outline-none">
          <ListFavoritesUser :favorites="favorites" :loading="loading" />
        </TabsContent>

      </Tabs>

      <!-- Paginación -->
      <div v-if="!loading && (reviews.length > 0 || favorites.length > 0)" class="flex items-center justify-center gap-3 mt-10">
        <Button
          variant="outline"
          size="sm"
          @click="changePage(-1)"
          :disabled="page === 1"
          class="rounded-full px-5 shadow-sm hover:shadow-md transition-all disabled:opacity-50"
        >
          <i class="fas fa-chevron-left mr-2 text-xs"></i>
          Anterior
        </Button>
        <span class="text-sm font-medium text-gray-700 dark:text-gray-300 px-4 py-1.5 bg-white dark:bg-gray-800 rounded-full shadow-sm border border-gray-200 dark:border-gray-700">
          {{ page }} / {{ totalPages }}
        </span>
        <Button
          variant="outline"
          size="sm"
          @click="changePage(1)"
          :disabled="page === totalPages"
          class="rounded-full px-5 shadow-sm hover:shadow-md transition-all disabled:opacity-50"
        >
          Siguiente
          <i class="fas fa-chevron-right ml-2 text-xs"></i>
        </Button>
      </div>

    </div>
  </div>
</template>
