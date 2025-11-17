<script setup lang="ts">
import { onMounted, watch, ref, computed, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDebounceFn } from '@vueuse/core'
import { useSitesStore } from '@/stores/sites'
import SiteFilters from '@/components/site/SiteFilters.vue'
import SiteCard from '@/components/site/SiteCard.vue'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'

const route = useRoute()
const router = useRouter()
const store = useSitesStore()

onMounted(async () => {
  store.fromRouteQuery(route.query as Record<string, any>)
  await store.loadFirstPage()
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
  if (store.lat != null && store.long != null) {
    store.page = 1
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

function changeSort(field: 'created_at' | 'name' | 'rating') {
  if (store.sort.field === field) {
    store.sort.dir = store.sort.dir === 'asc' ? 'desc' : 'asc'
  } else {
    store.sort.field = field
    store.sort.dir = 'asc'
  }
  store.loadFirstPage()
}
</script>

<template>
  <section>
    <div class="mb-3 md:mb-4 flex flex-wrap items-center justify-between gap-2">
      <h1 class="text-xl md:text-2xl font-semibold">Sitios históricos</h1>
      <div class="text-sm text-gray-600">{{ store.total }} resultados</div>
    </div>

    <div class="lg:hidden mb-3">
      <Accordion type="single" collapsible>
        <AccordionItem value="filters">
          <AccordionTrigger class="px-3 py-2 border rounded text-sm">Buscar y filtros</AccordionTrigger>
          <AccordionContent class="border rounded p-3 mt-2">
            <SiteFilters />
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-[320px,1fr] gap-4">
      <aside class="hidden lg:block">
        <div class="sticky top-3 border rounded p-3">
          <SiteFilters />
        </div>
      </aside>

      <div class="space-y-3">
        <div class="flex flex-wrap gap-2 items-center justify-between">
          <div class="flex items-center gap-2 text-sm">
            <span class="text-gray-500">Ordenar:</span>
            <Button variant="outline" size="sm" @click="changeSort('created_at')">
              Fecha {{ store.sort.field === 'created_at' ? (store.sort.dir === 'asc' ? '↑' : '↓') : '' }}
            </Button>
            <Button variant="outline" size="sm" @click="changeSort('name')">
              Nombre {{ store.sort.field === 'name' ? (store.sort.dir === 'asc' ? '↑' : '↓') : '' }}
            </Button>
            <Button variant="outline" size="sm" @click="changeSort('rating')">
              Ranking {{ store.sort.field === 'rating' ? (store.sort.dir === 'asc' ? '↑' : '↓') : '' }}
            </Button>
          </div>
        </div>

        <div v-if="store.error" class="p-3 bg-red-50 text-red-700 rounded">
          {{ store.error }}
        </div>

        <div v-if="store.isLoading && !store.items.length" class="grid gap-3" :class="gridCols">
          <div v-for="i in 8" :key="i" class="rounded border p-3 space-y-3">
            <Skeleton class="h-36 w-full" />
            <Skeleton class="h-4 w-2/3" />
            <Skeleton class="h-3 w-1/2" />
          </div>
        </div>

        <template v-else>
          <div v-if="!store.items.length" class="p-6 text-center text-gray-500 border rounded">
            No hay resultados con los filtros actuales.
          </div>
          <div v-else class="grid gap-2 sm:gap-3" :class="gridCols">
            <SiteCard v-for="s in store.items" :key="s.id" :site="s" />
          </div>
        </template>

        <div v-if="store.isNextLoading" class="text-center py-4 text-gray-500">
          Cargando más...
        </div>
        <div ref="sentinel" class="h-1"></div>
      </div>
    </div>
  </section>
</template>
