<script setup lang="ts">
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselPrevious,
  CarouselNext,
} from "@/components/ui/carousel";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface HistoricSite {
  id: number;
  name: string;
  city: string;
  province?: string;
  cover_image_url?: string;
  tags?: string[];
  rating?: number;
}

interface Props {
  title: string;
  sites: HistoricSite[];
  loading: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: "open-details", id: number): void;
}>();

function formatTags(tags: any[] | undefined) {
  return Array.isArray(tags) ? tags.slice(0, 5) : [];
}
</script>

<template>
  <section>
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold text-gray-800">{{ title }}</h2>
    </div>

    <Carousel class="w-full">
      <CarouselContent class="flex gap-4">
        <!-- LOADING -->
        <div
          v-if="loading"
          class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 w-full"
        >
          <div
            class="h-48 bg-gray-200 animate-pulse rounded-xl"
            v-for="n in 4"
            :key="n"
          ></div>
        </div>

        <!-- ITEMS -->
        <CarouselItem
          v-for="site in sites"
          :key="site.id"
          class="basis-4/5 sm:basis-1/2 md:basis-1/3 lg:basis-1/4 cursor-pointer"
        >
          <Card
            class="shadow hover:shadow-lg transition rounded-xl"
            @click="emit('open-details', site.id)"
          >
            <img
              :src="
                site.cover_image_url ||
                'https://via.placeholder.com/300x200?text=No+Image'
              "
              alt="Site image"
              class="w-full h-40 object-cover rounded-t-xl"
            />

            <CardHeader>
              <CardTitle class="text-lg font-semibold">{{ site.name }}</CardTitle>
            </CardHeader>

            <CardContent class="space-y-2">
              <p class="text-gray-600 text-sm">
                {{ site.city }}
                <span v-if="site.province">– {{ site.province }}</span>
              </p>

              <div class="flex flex-wrap gap-2">
                <Badge
                  v-for="tag in formatTags(site.tags)"
                  :key="tag"
                  class="text-xs bg-blue-100 text-blue-700"
                >
                  {{ tag }}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </CarouselItem>
      </CarouselContent>

      <CarouselPrevious />
      <CarouselNext />
    </Carousel>
  </section>
</template>

<style scoped></style>
