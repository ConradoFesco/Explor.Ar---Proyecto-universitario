<script setup lang="ts">
import { ref, watch } from 'vue'
import { useSitesStore } from '@/stores/sites'
import { Input } from '@/components/ui/input'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import { Button } from '@/components/ui/button'

const emit = defineEmits<{
  (e: 'apply'): void
  (e: 'reset'): void
}>()

const store = useSitesStore()

const text = ref(store.text)
const city = ref(store.city)
const province = ref(store.province)
const tagsInput = ref(store.tags.join(', '))
const favoritesOnly = ref(store.favoritesOnly)

const lat = ref(store.lat)
const long = ref(store.long)
const radius = ref(store.radius ?? 1000)

watch([text, city, province, tagsInput, favoritesOnly, lat, long, radius], () => {
  // no-op reactive
})

function parseTags(input: string): string[] {
  return input
    .split(',')
    .map(t => t.trim())
    .filter(Boolean)
}

function apply() {
  store.text = text.value.trim()
  store.city = city.value.trim()
  store.province = province.value.trim()
  store.tags = parseTags(tagsInput.value)
  store.favoritesOnly = !!favoritesOnly.value
  store.lat = lat.value != null ? Number(lat.value) : null
  store.long = long.value != null ? Number(long.value) : null
  store.radius = radius.value != null ? Number(radius.value) : null
  store.page = 1
  emit('apply')
}

function reset() {
  text.value = ''
  city.value = ''
  province.value = ''
  tagsInput.value = ''
  favoritesOnly.value = false
  lat.value = null
  long.value = null
  radius.value = 1000
  store.resetFilters()
  emit('reset')
}
</script>

<template>
  <form @submit.prevent="apply" class="space-y-3">
    <div>
      <label class="block text-sm font-medium mb-1">Buscar</label>
      <Input v-model="text" type="search" placeholder="Nombre o descripción" />
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
      <div>
        <label class="block text-sm font-medium mb-1">Ciudad</label>
        <Input v-model="city" type="text" placeholder="Ciudad" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Provincia</label>
        <Input v-model="province" type="text" placeholder="Provincia" />
      </div>
    </div>

    <div>
      <label class="block text-sm font-medium mb-1">Tags</label>
      <Input v-model="tagsInput" type="text" placeholder="tag1, tag2, tag3" />
      <p class="text-xs text-gray-500 mt-1">Separá por comas. Máximo 5 se muestran en tarjetas.</p>
    </div>

    <div class="flex items-center gap-2">
      <Checkbox id="fav" v-model:checked="favoritesOnly" />
      <label for="fav" class="text-sm select-none">Favoritos</label>
    </div>

    <Accordion type="single" collapsible>
      <AccordionItem value="map">
        <AccordionTrigger class="text-sm">Búsqueda por mapa (punto + radio)</AccordionTrigger>
        <AccordionContent>
          <div class="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label class="block text-sm font-medium mb-1">Latitud</label>
              <Input v-model.number="lat" type="number" step="any" placeholder="-34.6" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Longitud</label>
              <Input v-model.number="long" type="number" step="any" placeholder="-58.4" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Radio (m)</label>
              <Input v-model.number="radius" type="number" min="10" step="10" />
            </div>
          </div>
          <p class="text-xs text-gray-500 mt-2">Sugerencia: podés tocar el mapa en la vista para completar estos campos.</p>
        </AccordionContent>
      </AccordionItem>
    </Accordion>

    <div class="flex flex-wrap gap-2">
      <Button type="submit">Aplicar</Button>
      <Button type="button" variant="outline" @click="reset">Limpiar</Button>
    </div>
  </form>
</template>


