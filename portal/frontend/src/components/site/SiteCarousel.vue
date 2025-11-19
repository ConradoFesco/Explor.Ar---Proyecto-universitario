<template>
  <section class="mb-10">
    <div class="flex justify-between items-center mb-3">
      <h2 class="text-2xl font-semibold">{{ title }}</h2>
      <button class="text-blue-600 font-medium">Ver todos →</button>
    </div>

    <div class="flex gap-4 overflow-x-auto pb-2">
      <SiteCard v-for="item in items" :key="item.id" :site="item" />
    </div>
  </section>
</template>

<script setup lang="ts">
import SiteCard from "@/components/site/SiteCard.vue";

defineProps<{
  title: string;
  items: Array<any>;
}>();
</script>

<style scoped>
::-webkit-scrollbar {
  display: none;
}
</style>
