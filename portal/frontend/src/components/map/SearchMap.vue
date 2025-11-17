<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps<{
  lat: number | null
  long: number | null
  radius: number | null
}>()

const emit = defineEmits<{
  (e: 'update:lat', value: number | null): void
  (e: 'update:long', value: number | null): void
  (e: 'update:radius', value: number | null): void
}>()

const mapEl = ref<HTMLDivElement | null>(null)
let map: L.Map | null = null
let marker: L.Marker | null = null
let circle: L.Circle | null = null

// Fix para iconos de Leaflet en Vite
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png'

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconRetinaUrl: iconRetina,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})
L.Marker.prototype.options.icon = DefaultIcon

function removeLayers() {
  if (marker && map) {
    map.removeLayer(marker)
    marker = null
  }
  if (circle && map) {
    map.removeLayer(circle)
    circle = null
  }
}

function createMarker(latlng: [number, number]) {
  if (!map) return
  
  if (!marker) {
    marker = L.marker(latlng, { draggable: true })
    marker.addTo(map)
    marker.on('dragend', (e: L.DragEndEvent) => {
      const pos = e.target.getLatLng()
      emit('update:lat', pos.lat)
      emit('update:long', pos.lng)
    })
  } else {
    marker.setLatLng(latlng)
  }
}

function createCircle(latlng: [number, number], radiusMeters: number) {
  if (!map) return
  
  if (!circle) {
    circle = L.circle(latlng, {
      radius: radiusMeters,
      color: '#3b82f6',
      fillColor: '#3b82f6',
      fillOpacity: 0.2,
      weight: 2,
    })
    circle.addTo(map)
  } else {
    circle.setLatLng(latlng)
    circle.setRadius(radiusMeters)
  }
}

function updateMarker() {
  if (!map) return

  removeLayers()

  if (props.lat != null && props.long != null) {
    const latlng: [number, number] = [props.lat, props.long]
    const radiusMeters = props.radius ?? 1000
    
    createMarker(latlng)
    createCircle(latlng, radiusMeters)
    
    if (circle) {
      map.fitBounds(circle.getBounds(), { padding: [20, 20] })
    } else {
      map.setView(latlng, Math.max(map.getZoom(), 12))
    }
  }
}

onMounted(() => {
  if (!mapEl.value) return

  map = L.map(mapEl.value, {
    center: [-34.6, -58.4],
    zoom: 6,
    zoomControl: true,
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(map)

  map.on('click', (e: L.LeafletMouseEvent) => {
    const { lat, lng } = e.latlng
    emit('update:lat', lat)
    emit('update:long', lng)
    if (props.radius == null) {
      emit('update:radius', 1000)
    }
  })

  updateMarker()
})

watch([() => props.lat, () => props.long, () => props.radius], updateMarker)

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<template>
  <div
    ref="mapEl"
    class="w-full h-64 sm:h-80 rounded border overflow-hidden bg-gray-100"
    style="z-index: 0;"
  >
    <div v-if="!mapEl" class="h-full flex items-center justify-center text-gray-400 text-sm">
      Cargando mapa...
    </div>
  </div>
</template>
