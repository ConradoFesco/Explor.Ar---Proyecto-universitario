<script setup lang="ts">
import { onMounted, ref } from 'vue'

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

onMounted(() => {
  // Minimal placeholder: click-to-select point on a simple static map placeholder.
  // You can replace with Leaflet for full UX; emits lat/long from click.
  if (!mapEl.value) return
  mapEl.value.addEventListener('click', (ev: MouseEvent) => {
    const rect = (ev.currentTarget as HTMLDivElement).getBoundingClientRect()
    const x = ev.clientX - rect.left
    const y = ev.clientY - rect.top
    // Fake projection to lat/long just to allow UI wiring in environments without map libs.
    const lat = +(90 - (y / rect.height) * 180).toFixed(5)
    const long = +(-180 + (x / rect.width) * 360).toFixed(5)
    emit('update:lat', lat)
    emit('update:long', long)
    if (props.radius == null) emit('update:radius', 1000)
  })
})
</script>

<template>
  <div
    ref="mapEl"
    class="w-full h-64 rounded border bg-gray-100 relative cursor-crosshair"
    title="Hacé clic para seleccionar un punto aproximado"
  >
    <div class="absolute inset-0 flex items-center justify-center pointer-events-none text-gray-400 text-sm">
      Mapa (placeholder)
    </div>
    <div v-if="lat != null && long != null" class="absolute right-2 bottom-2 bg-white/90 text-xs px-2 py-1 rounded shadow">
      {{ lat }}, {{ long }} <span v-if="radius">· {{ radius }} m</span>
    </div>
  </div>
</template>


