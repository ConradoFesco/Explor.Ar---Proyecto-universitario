<template>
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-2xl font-bold text-gray-800">
      {{ title }}
    </h2>

    <button
      class="text-blue-600 hover:underline"
      @click="$emit('see-all')"
    >
      Ver todos →
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
}>();
</script>
