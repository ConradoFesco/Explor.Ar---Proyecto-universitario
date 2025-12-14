<script setup lang="ts">
import { onMounted, watch, ref, computed, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDebounceFn } from '@vueuse/core'
import { useSitesStore } from '@/stores/sites'
import SiteFilters from '@/components/site/SiteFilters.vue'
import SiteCard from '@/components/site/SiteCard.vue'
import { Skeleton } from '@/components/ui/skeleton'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import SortButton from '@/components/profile/SortButton.vue'

const route = useRoute()
const router = useRouter()
const store = useSitesStore()

onMounted(async () => {
  store.fromRouteQuery(route.query as Record<string, any>)
  if (Object.keys(store.validationErrors).length === 0) {
    await store.loadFirstPage()
  }
  await nextTick()
  setupInfiniteScroll()
})

watch(
  () => ({ ...store.queryParams }),
  (qp) => {
    router.replace({ query: { ...qp } })
  },
  { deep: true }
)

const debouncedMapSearch = useDebounceFn(() => {
  if (store.lat != null && store.long != null && Object.keys(store.validationErrors).length === 0) {
    store.loadFirstPage()
  }
}, 300)

watch([() => store.lat, () => store.long, () => store.radius], debouncedMapSearch)

const gridCols = computed(() => 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4')
const sentinel = ref<HTMLDivElement | null>(null)
let io: IntersectionObserver | null = null

function setupInfiniteScroll() {
  if (io) {
    io.disconnect()
    io = null
  }
  if (!sentinel.value) return
  io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (e.isIntersecting) {
        store.loadNextPage()
      }
    }
  }, { rootMargin: '400px' })
  io.observe(sentinel.value)
}

onBeforeUnmount(() => {
  if (io) io.disconnect()
})

function handleSortChange(field: string, dir: 'asc' | 'desc') {
  store.sort = { field: field as 'created_at' | 'name' | 'rating', dir }
  store.loadFirstPage()
}
</script>

<template>
  <div class="w-full">
    <div class="w-full px-4 sm:px-6 lg:px-8 xl:px-12 py-12">
      <div class="mb-3 md:mb-4 flex flex-col sm:flex-row flex-wrap items-start sm:items-center justify-between gap-2">
        <h1 class="text-lg sm:text-xl md:text-2xl font-semibold text-gray-900 dark:text-gray-100">Sitios históricos</h1>
        <div class="text-xs sm:text-sm text-gray-600 dark:text-gray-400">{{ store.total }} resultados</div>
      </div>

      <div class="lg:hidden mb-3">
        <Accordion type="single" collapsible>
          <AccordionItem value="filters">
            <AccordionTrigger class="px-3 py-2 border border-gray-200 dark:border-gray-700 rounded text-sm text-gray-900 dark:text-gray-100">Buscar y filtros</AccordionTrigger>
            <AccordionContent class="border border-gray-200 dark:border-gray-700 rounded p-3 mt-2 bg-white dark:bg-gray-800">
              <SiteFilters />
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-[320px,1fr] gap-4 lg:gap-6">
        <aside class="hidden lg:block">
          <div class="sticky top-3 border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800 shadow-sm">
            <SiteFilters />
          </div>
        </aside>

        <div class="space-y-3 min-w-0">
        <div class="flex flex-col sm:flex-row flex-wrap gap-2 sm:gap-3 items-start sm:items-center justify-between">
          <div class="flex flex-wrap items-center gap-2 text-xs sm:text-sm">
            <span class="text-gray-500 dark:text-gray-400 shrink-0">Ordenar:</span>
            <SortButton
              field="created_at"
              :current-field="typeof store.sort === 'object' && store.sort ? store.sort.field : undefined"
              :current-dir="typeof store.sort === 'object' && store.sort ? store.sort.dir : undefined"
              label="Fecha"
              @sort-change="handleSortChange"
            />
            <SortButton
              field="name"
              :current-field="typeof store.sort === 'object' && store.sort ? store.sort.field : undefined"
              :current-dir="typeof store.sort === 'object' && store.sort ? store.sort.dir : undefined"
              label="Nombre"
              @sort-change="handleSortChange"
            />
            <SortButton
              field="rating"
              :current-field="typeof store.sort === 'object' && store.sort ? store.sort.field : undefined"
              :current-dir="typeof store.sort === 'object' && store.sort ? store.sort.dir : undefined"
              label="Ranking"
              @sort-change="handleSortChange"
            />
          </div>
        </div>

        <div v-if="store.error" class="p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded mb-3">
          <p class="font-medium">Error al cargar sitios:</p>
          <p>{{ store.error }}</p>
        </div>
        
        <div v-if="Object.keys(store.validationErrors).length > 0" class="p-3 bg-yellow-50 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400 rounded mb-3">
          <p class="font-medium mb-2">⚠️ Errores de validación en los filtros:</p>
          <ul class="list-disc list-inside space-y-1 text-sm">
            <li v-if="store.validationErrors.lat">{{ store.validationErrors.lat }}</li>
            <li v-if="store.validationErrors.long">{{ store.validationErrors.long }}</li>
            <li v-if="store.validationErrors.radius">{{ store.validationErrors.radius }}</li>
            <li v-if="store.validationErrors.page">{{ store.validationErrors.page }}</li>
            <li v-if="store.validationErrors.perPage">{{ store.validationErrors.perPage }}</li>
            <li v-if="store.validationErrors.sort">{{ store.validationErrors.sort }}</li>
          </ul>
          <p class="text-xs mt-2">Por favor, corrige estos errores en los filtros.</p>
        </div>

        <div v-if="store.isLoading && !store.items.length" class="grid gap-3" :class="gridCols">
          <div v-for="i in 8" :key="i" class="rounded border border-gray-200 dark:border-gray-700 p-3 space-y-3">
            <Skeleton class="h-36 w-full" />
            <Skeleton class="h-4 w-2/3" />
            <Skeleton class="h-3 w-1/2" />
          </div>
        </div>

        <template v-else>
          <div v-if="!store.items.length" class="p-6 text-center text-gray-500 dark:text-gray-400 border border-gray-200 dark:border-gray-700 rounded">
            No hay resultados con los filtros actuales.
          </div>
          <div v-else class="grid gap-2 sm:gap-3 mx-auto" :class="gridCols">
            <SiteCard v-for="s in store.items" :key="s.id" :site="s" />
          </div>
        </template>

        <div v-if="store.isNextLoading" class="text-center py-4 text-gray-500 dark:text-gray-400">
          Cargando más...
        </div>
        <div ref="sentinel" class="h-1"></div>
        </div>
      </div>
    </div>
  </div>
</template>
