<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchSiteDetail, type HistoricSiteDetail, type HistoricSite } from '@/lib/api'
import { useSitesStore } from '@/stores/sites'
import { useAuth } from '@/composables/useAuth'
import { useReviews } from '@/composables/useReviews'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { ArrowLeft } from 'lucide-vue-next'
import SiteMap from '@/components/site/SiteMap.vue'
import SiteGallery from '@/components/site/SiteGallery.vue'
import SiteHeader from '@/components/site/SiteHeader.vue'
import SiteDescription from '@/components/site/SiteDescription.vue'
import SiteTags from '@/components/site/SiteTags.vue'
import ReviewsSection from '@/components/site/ReviewsSection.vue'
import ReviewForm from '@/components/site/ReviewForm.vue'

const route = useRoute()
const router = useRouter()
const sitesStore = useSitesStore()

// Composables
const siteId = computed(() => Number(route.params.id))
const { isAuthenticated, checkAuth, redirectToLogin } = useAuth()
const reviews = useReviews(() => siteId.value)

// State
const site = ref<HistoricSiteDetail | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)
const showReviewForm = ref(false)
const isSubmittingReview = ref(false)

// Computed
const allImages = computed(() => {
  if (!site.value) return []
  
  const images = [...(site.value.images || [])]
  
  // Agregar imagen de portada si no está en la lista
  if (site.value.cover_image) {
    const coverImage = site.value.cover_image
    const coverExists = images.some(img => img.id === coverImage.id)
    if (!coverExists) {
      images.unshift(coverImage)
    }
  }
  
  // Ordenar: portada primero, luego por orden
  return images.sort((a, b) => {
    if (a.es_portada) return -1
    if (b.es_portada) return 1
    return a.orden - b.orden
  })
})

// Functions
async function loadSite() {
  if (isLoading.value) return
  
  isLoading.value = true
  error.value = null
  
  try {
    await checkAuth()
    site.value = await fetchSiteDetail(siteId.value, isAuthenticated.value)
    await reviews.loadReviews(1)
  } catch (e: unknown) {
    const message = e instanceof Error ? e.message : 'Error al cargar el sitio'
    error.value = message
    console.error('Error loading site:', e)
  } finally {
    isLoading.value = false
  }
}

function handleFavoriteUpdate(newState: boolean) {
  if (site.value) {
    site.value = { ...site.value, is_favorite: newState }
  }
  // Actualizar en el store si el sitio está en la lista
  const idx = sitesStore.items.findIndex(s => s.id === site.value?.id)
  if (idx >= 0 && site.value) {
    sitesStore.items[idx] = { ...sitesStore.items[idx], is_favorite: newState } as HistoricSite
  }
}

async function handleWriteReview() {
  if (!isAuthenticated.value) {
    redirectToLogin()
    return
  }
  showReviewForm.value = true
}

async function handleSubmitReview(rating: number, content: string) {
  if (!site.value || isSubmittingReview.value) return
  
  isSubmittingReview.value = true
  
  try {
    await reviews.submitReview(rating, content)
    showReviewForm.value = false
  } catch {
    // El error ya fue manejado en useReviews
  } finally {
    isSubmittingReview.value = false
  }
}

function handleTagClick(tagSlug: string) {
  sitesStore.tags = [tagSlug]
  sitesStore.page = 1
  router.push({ name: 'SitesList', query: sitesStore.queryParams })
}

function handleBack() {
  router.push({ name: 'SitesList', query: sitesStore.queryParams })
}

// Watchers
watch(() => route.params.id, (newId) => {
  if (newId && Number(newId) !== site.value?.id) {
    loadSite()
  }
})

// Lifecycle
onMounted(() => {
  loadSite()
})
</script>

<template>
  <div class="w-full px-4 sm:px-6 lg:px-10 xl:px-20 2xl:px-32 py-6">
    <div class="max-w-[1600px] mx-auto space-y-6">
    <!-- Botón Volver -->
    <Button variant="outline" size="sm" @click="handleBack" class="flex items-center gap-2">
      <ArrowLeft class="h-4 w-4" />
      Volver al listado
    </Button>

    <!-- Loading State -->
    <div v-if="isLoading" class="space-y-6">
      <div class="space-y-3">
        <Skeleton class="h-8 w-3/4" />
        <Skeleton class="h-4 w-1/2" />
      </div>
      <Skeleton class="h-64 w-full" />
      <Skeleton class="h-4 w-full" />
      <Skeleton class="h-4 w-3/4" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="p-4 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded border border-red-200 dark:border-red-800">
      <p class="font-semibold">Error</p>
      <p>{{ error }}</p>
      <Button variant="outline" size="sm" @click="loadSite" class="mt-3">
        Reintentar
      </Button>
    </div>

    <!-- Site Content -->
    <div v-else-if="site" class="space-y-6">
      <!-- Encabezado -->
      <SiteHeader
        :site="site"
        :reviews-total="reviews.reviewsTotal.value"
        @favorite-update="handleFavoriteUpdate"
      />

      <!-- Galería de Imágenes -->
      <SiteGallery 
        v-if="allImages.length > 0" 
        :images="allImages" 
        :site-name="site.name" 
      />

      <!-- Descripción -->
      <SiteDescription :site="site" />

      <!-- Tags -->
      <SiteTags :tags="site.tags" @tag-click="handleTagClick" />

      <!-- Mapa -->
      <section v-if="site.latitude && site.longitude" class="space-y-2">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Ubicación</h2>
        <SiteMap
          :latitude="site.latitude"
          :longitude="site.longitude"
          :site-name="site.name"
          :site-description="site.brief_description || ''"
        />
      </section>

      <!-- Reseñas -->
      <ReviewsSection
        :reviews="reviews.reviews.value"
        :is-loading="reviews.isLoadingReviews.value"
        :current-page="reviews.reviewsPage.value"
        :total-pages="reviews.reviewsTotalPages.value"
        :is-authenticated="isAuthenticated"
        @write-review="handleWriteReview"
        @page-change="reviews.loadReviews"
      />
    </div>

    <!-- Modal de Formulario de Reseña -->
    <ReviewForm
      v-if="showReviewForm && site"
      :site-id="site.id"
      :site-name="site.name"
      @submit="handleSubmitReview"
      @close="showReviewForm = false"
    />
    </div>
  </div>
</template>
