<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { useDebounceFn, onClickOutside } from '@vueuse/core'
import { useSitesStore } from '@/stores/sites'
import { useAuth } from '@/composables/useAuth'
import { useAlert } from '@/composables/useAlert'
import { fetchFilterOptions, type FilterOptions } from '@/lib/api'
import { Input } from '@/components/ui/input'
import SimpleCheckbox from '@/components/ui/checkbox/SimpleCheckbox.vue'
import { NativeSelect } from '@/components/ui/native-select'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { MapPin, Settings } from 'lucide-vue-next'
import SearchMap from '@/components/map/SearchMap.vue'

const emit = defineEmits<{
  (e: 'apply'): void
  (e: 'reset'): void
}>()

const store = useSitesStore()
const { isAuthenticated, checkAuth, loginWithGoogle } = useAuth()
const { showWarning } = useAlert()

const text = ref(store.text)
const city = ref<string>('')
const province = ref<string>('')
const selectedTags = ref<string[]>(store.tags)
const favoritesOnly = ref(store.favoritesOnly)

const lat = ref<number | null>(typeof store.lat === 'number' ? store.lat : (store.lat && !isNaN(Number(store.lat)) ? Number(store.lat) : null))
const long = ref<number | null>(typeof store.long === 'number' ? store.long : (store.long && !isNaN(Number(store.long)) ? Number(store.long) : null))
const radius = ref<number | string>(typeof store.radius === 'number' ? store.radius : (store.radius && !isNaN(Number(store.radius)) ? Number(store.radius) : 1000))

const radiusForMap = ref<number | null>(
  typeof store.radius === 'number' ? store.radius : (store.radius && !isNaN(Number(store.radius)) ? Number(store.radius) : 1000)
)

watch(radiusForMap, (newVal) => {
  radius.value = newVal ?? 1000
})

const mapAccordionOpen = ref<string | undefined>(undefined)
const radiusDropdownOpen = ref(false)
const radiusDropdownRef = ref<HTMLDivElement | null>(null)

const latError = ref<string | undefined>(undefined)
const longError = ref<string | undefined>(undefined)
const radiusError = ref<string | undefined>(undefined)

const storeLatError = computed(() => store.validationErrors.lat)
const storeLongError = computed(() => store.validationErrors.long)
const storeRadiusError = computed(() => store.validationErrors.radius)

const filterOptions = ref<FilterOptions | null>(null)
const isLoadingOptions = ref(false)

const cityOptions = computed(() => 
  (filterOptions.value?.cities || []).map(c => ({ value: c.name, label: c.name }))
)

const provinceOptions = computed(() => 
  (filterOptions.value?.provinces || []).map(p => ({ value: p.name, label: p.name }))
)

onMounted(async () => {
  isLoadingOptions.value = true
  try {
    filterOptions.value = await fetchFilterOptions()
  } catch (e) {
    console.error('Error al cargar opciones de filtro:', e)
  } finally {
    isLoadingOptions.value = false
  }
  
  if (store.city) city.value = store.city
  if (store.province) province.value = store.province
  favoritesOnly.value = store.favoritesOnly
  
  if (store.validationErrors.lat) latError.value = store.validationErrors.lat
  if (store.validationErrors.long) longError.value = store.validationErrors.long
  if (store.validationErrors.radius) radiusError.value = store.validationErrors.radius
})

onClickOutside(radiusDropdownRef, () => {
  radiusDropdownOpen.value = false
})

function applyTextSearch() {
  store.clearValidationErrors()
  
  store.text = text.value.trim()
  
  store.page = undefined
  store.loadFirstPage()
  emit('apply')
}

function applyMapFilters() {
  latError.value = undefined
  longError.value = undefined
  radiusError.value = undefined
  
  store.clearValidationErrors()
  
  let hasErrors = false
  
  if (lat.value != null) {
    const latResult = store.validateLat(lat.value)
    if (!latResult.valid) {
      latError.value = latResult.error
      hasErrors = true
    } else if (latResult.cleaned !== undefined) {
      lat.value = latResult.cleaned
      store.lat = latResult.cleaned
    } else {
      store.lat = undefined
    }
  } else {
    store.lat = undefined
  }
  
  if (long.value != null) {
    const longResult = store.validateLong(long.value)
    if (!longResult.valid) {
      longError.value = longResult.error
      hasErrors = true
    } else if (longResult.cleaned !== undefined) {
      long.value = longResult.cleaned
      store.long = longResult.cleaned
    } else {
      store.long = undefined
    }
  } else {
    store.long = undefined
  }
  
  const radiusValue = radius.value
  if (radiusValue != null && radiusValue !== '' && radiusValue !== '0') {
    const radiusResult = store.validateRadius(radiusValue)
    if (!radiusResult.valid) {
      radiusError.value = radiusResult.error
      hasErrors = true
    } else if (radiusResult.cleaned !== undefined) {
      radius.value = radiusResult.cleaned
      store.radius = radiusResult.cleaned
    } else {
      store.radius = undefined
    }
  } else {
    store.radius = undefined
  }
  
  if (hasErrors) {
    return
  }
  
  if ((store.lat !== undefined) !== (store.long !== undefined)) {
    if (store.lat !== undefined) {
      longError.value = 'La longitud es requerida cuando se especifica latitud'
      hasErrors = true
    } else {
      latError.value = 'La latitud es requerida cuando se especifica longitud'
      hasErrors = true
    }
  }
  
  if (store.radius !== undefined && (store.lat === undefined || store.long === undefined)) {
    radiusError.value = 'El radio requiere especificar latitud y longitud'
    hasErrors = true
  }
  
  if (hasErrors) {
    return
  }
  
  if (Object.keys(store.validationErrors).length > 0) {
    return
  }
  
  store.page = undefined
  store.loadFirstPage()
  emit('apply')
}

async function applyManualFilters() {
  if (favoritesOnly.value) {
    await checkAuth()
    if (!isAuthenticated.value) {
      favoritesOnly.value = false
      await showWarning(
        'Inicio de sesión requerido',
        'Debe iniciar sesión para ver sus favoritos'
      )
      await loginWithGoogle()
      return
    }
  }
  
  store.clearValidationErrors()
  
  store.city = city.value.trim()
  store.province = province.value.trim()
  store.tags = selectedTags.value
  store.favoritesOnly = favoritesOnly.value === true
  
  if (Object.keys(store.validationErrors).length > 0) {
    return
  }
  
  store.page = undefined
  await store.loadFirstPage()
  emit('apply')
}

const debouncedTextSearch = useDebounceFn(applyTextSearch, 500)

watch([text], debouncedTextSearch)
watch([lat, long, radius], applyMapFilters)

function toggleTag(tagSlug: string) {
  const idx = selectedTags.value.indexOf(tagSlug)
  if (idx >= 0) {
    selectedTags.value.splice(idx, 1)
  } else {
    selectedTags.value.push(tagSlug)
  }
}


function reset() {
  text.value = ''
  city.value = ''
  province.value = ''
  selectedTags.value = []
  favoritesOnly.value = false
  lat.value = null
  long.value = null
  radius.value = 1000
  mapAccordionOpen.value = undefined
  radiusDropdownOpen.value = false
  store.resetFilters()
  store.loadFirstPage()
  emit('reset')
}

function clearMapSelection() {
  lat.value = null
  long.value = null
  radius.value = 1000
  latError.value = undefined
  longError.value = undefined
  radiusError.value = undefined
  store.lat = undefined
  store.long = undefined
  store.radius = undefined
  store.page = undefined
  store.loadFirstPage()
}
</script>

<template>
  <form @submit.prevent="applyManualFilters" class="space-y-3">
    <div>
      <label class="block text-xs sm:text-sm font-medium mb-1 text-gray-900 dark:text-gray-100">Buscar</label>
      <Input v-model="text" type="search" placeholder="Nombre o descripción" class="text-sm" />
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
      <div class="min-w-0">
        <label class="block text-xs sm:text-sm font-medium mb-1 text-gray-900 dark:text-gray-100">Ciudad</label>
        <div v-if="isLoadingOptions" class="text-xs text-gray-500 dark:text-gray-400 py-2">Cargando ciudades...</div>
        <NativeSelect
          v-else
          v-model="city"
          :disabled="isLoadingOptions"
          placeholder="Todas las ciudades"
          :options="cityOptions"
        />
        <p v-if="!isLoadingOptions && filterOptions" class="text-xs text-gray-400 dark:text-gray-300 mt-1">
          {{ filterOptions.cities?.length || 0 }} ciudades disponibles
        </p>
      </div>
      <div class="min-w-0">
        <label class="block text-xs sm:text-sm font-medium mb-1 text-gray-900 dark:text-gray-100">Provincia</label>
        <div v-if="isLoadingOptions" class="text-xs text-gray-500 dark:text-gray-400 py-2">Cargando provincias...</div>
        <NativeSelect
          v-else
          v-model="province"
          :disabled="isLoadingOptions"
          placeholder="Todas las provincias"
          :options="provinceOptions"
        />
        <p v-if="!isLoadingOptions && filterOptions" class="text-xs text-gray-400 dark:text-gray-300 mt-1">
          {{ filterOptions.provinces?.length || 0 }} provincias disponibles
        </p>
      </div>
    </div>

    <div>
      <label class="block text-xs sm:text-sm font-medium mb-1 text-gray-900 dark:text-gray-100">Tags</label>
      <div v-if="isLoadingOptions" class="text-xs text-gray-500 dark:text-gray-400">Cargando tags...</div>
      <div v-else class="flex flex-wrap gap-2">
        <Badge
          v-for="tag in filterOptions?.tags || []"
          :key="tag.id"
          :variant="selectedTags.includes(tag.slug) ? 'default' : 'outline'"
          class="cursor-pointer"
          @click="toggleTag(tag.slug)"
        >
          {{ tag.name }}
        </Badge>
      </div>
      <p v-if="selectedTags.length" class="text-xs text-gray-500 dark:text-gray-400 mt-2">
        Seleccionados: {{ selectedTags.length }}
      </p>
    </div>

    <div class="flex items-center gap-2">
      <SimpleCheckbox 
        id="fav" 
        :checked="favoritesOnly"
        @update:checked="(value: boolean) => favoritesOnly = value"
      />
      <label for="fav" class="text-xs sm:text-sm select-none cursor-pointer text-gray-900 dark:text-gray-100">Favoritos</label>
    </div>

    <Accordion v-model="mapAccordionOpen" type="single" collapsible class="w-full">
      <AccordionItem value="map" class="border border-gray-200 dark:border-gray-700 rounded">
        <AccordionTrigger class="px-3 py-2 text-sm text-gray-900 dark:text-gray-100">
          <div class="flex items-center gap-2">
            <MapPin class="h-4 w-4" />
            <span>Búsqueda por mapa</span>
          </div>
        </AccordionTrigger>
        <AccordionContent class="px-3 pb-3 pt-0">
          <div class="space-y-3 mt-3">
            <div class="w-full">
              <SearchMap
                v-model:lat="lat"
                v-model:long="long"
                v-model:radius="radiusForMap"
              />
            </div>
            <div class="flex items-center justify-between">
              <div v-if="lat != null && long != null" class="text-xs text-gray-600 dark:text-gray-300">
                <p class="font-medium">Punto seleccionado:</p>
                <p>{{ typeof lat === 'number' ? lat.toFixed(5) : lat }}, {{ typeof long === 'number' ? long.toFixed(5) : long }}</p>
                <p v-if="radius != null && radius !== ''" class="mt-1">Radio: {{ radius }} m</p>
                <p v-if="latError || storeLatError" class="text-red-600 dark:text-red-400 mt-1 font-medium">
                  ⚠️ {{ latError || storeLatError }}
                </p>
                <p v-if="longError || storeLongError" class="text-red-600 dark:text-red-400 mt-1 font-medium">
                  ⚠️ {{ longError || storeLongError }}
                </p>
              </div>
              <div v-else class="text-xs text-gray-500 dark:text-gray-400">
                Hacé clic en el mapa para seleccionar un punto
              </div>
              <div class="flex gap-2 items-center">
                <div ref="radiusDropdownRef" class="relative">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    @click="radiusDropdownOpen = !radiusDropdownOpen"
                  >
                    <Settings class="h-4 w-4 mr-2" />
                    Radio
                  </Button>
                  <div
                    v-if="radiusDropdownOpen"
                    class="absolute right-0 bottom-full mb-2 w-64 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-50 p-3"
                  >
                    <label class="block text-sm font-medium mb-1 text-gray-900 dark:text-gray-100">Radio de búsqueda (metros)</label>
                    <Input
                      v-model="radius"
                      type="number"
                      min="100"
                      max="50000"
                      step="100"
                      placeholder="1000"
                      :class="['mb-2', (radiusError || storeRadiusError) && 'border-red-500 dark:border-red-500']"
                      @blur="applyMapFilters"
                    />
                    <p v-if="radiusError || storeRadiusError" class="text-xs text-red-600 dark:text-red-400 mb-2 font-medium">
                      {{ radiusError || storeRadiusError }}
                    </p>
                    <p v-else class="text-xs text-gray-500 dark:text-gray-400">
                      El radio se aplicará desde el punto seleccionado en el mapa (100-50000 metros).
                    </p>
                  </div>
                </div>
                <Button
                  v-if="lat != null && long != null"
                  type="button"
                  variant="outline"
                  size="sm"
                  @click="clearMapSelection"
                >
                  Limpiar
                </Button>
              </div>
            </div>
          </div>
        </AccordionContent>
      </AccordionItem>
    </Accordion>

    <div class="flex items-center justify-end gap-2 pt-2 border-t border-gray-200 dark:border-gray-700">
      <Button type="button" variant="outline" size="sm" @click="reset">
        Limpiar
      </Button>
      <Button type="submit" size="sm">
        Aplicar
      </Button>
    </div>
  </form>
</template>
