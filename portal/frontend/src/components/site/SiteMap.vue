<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps<{
  latitude: number
  longitude: number
  siteName: string
  siteDescription?: string
}>()

const mapContainer = ref<HTMLDivElement | null>(null)
let map: L.Map | null = null
let marker: L.Marker | null = null
let tileLayer: L.TileLayer | null = null

// Configurar iconos de Leaflet (solo una vez)
if (typeof window !== 'undefined' && !(L.Icon.Default.prototype as any)._getIconUrl) {
  delete (L.Icon.Default.prototype as any)._getIconUrl
  L.Icon.Default.mergeOptions({
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  })
}

function createPopupContent(): string {
  const description = props.siteDescription 
    ? `<p class="text-sm mt-1">${escapeHtml(props.siteDescription)}</p>` 
    : ''
  return `
    <div class="p-2">
      <strong>${escapeHtml(props.siteName)}</strong>
      ${description}
    </div>
  `
}

function escapeHtml(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

function initMap() {
  if (!mapContainer.value || map) return

  // Crear mapa
  map = L.map(mapContainer.value, {
    center: [props.latitude, props.longitude],
    zoom: 13,
    zoomControl: true,
  })

  // Agregar tiles de OpenStreetMap
  tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  })
  tileLayer.addTo(map)

  // Agregar marcador
  marker = L.marker([props.latitude, props.longitude])
    .addTo(map)
    .bindPopup(createPopupContent())
    .openPopup()
}

function updateMap() {
  if (!map || !marker) return
  
  const newCenter: [number, number] = [props.latitude, props.longitude]
  map.setView(newCenter, 13)
  marker.setLatLng(newCenter)
  marker.setPopupContent(createPopupContent())
}

function cleanup() {
  if (marker) {
    marker.remove()
    marker = null
  }
  if (tileLayer) {
    tileLayer.remove()
    tileLayer = null
  }
  if (map) {
    map.remove()
    map = null
  }
}

// Watchers
watch([() => props.latitude, () => props.longitude], () => {
  if (map) {
    updateMap()
  }
})

watch([() => props.siteName, () => props.siteDescription], () => {
  if (marker) {
    marker.setPopupContent(createPopupContent())
  }
})

// Lifecycle
onMounted(async () => {
  await nextTick()
  initMap()
})

onBeforeUnmount(() => {
  cleanup()
})
</script>

<template>
  <div 
    ref="mapContainer" 
    class="w-full h-64 md:h-80 lg:h-96 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm"
    role="img"
    :aria-label="`Mapa mostrando la ubicación de ${siteName}`"
  ></div>
</template>
