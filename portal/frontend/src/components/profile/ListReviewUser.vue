<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

interface Review {
  id: number
  site_name: string
  rating: number
  date: string
  excerpt: string
}

interface Props {
  reviews: Review[]
  loading: boolean
}

defineProps<Props>()
</script>

<template>
  <div class="w-full">

    <!-- Loading state -->
    <div v-if="loading" class="space-y-4">
      <Card v-for="i in 3" :key="i" class="dark:bg-gray-900 dark:border-gray-800">
        <CardHeader>
          <div class="flex gap-4">
            <Skeleton class="h-12 w-12 rounded-full shrink-0 dark:bg-gray-800" />
            <div class="space-y-3 flex-1">
              <Skeleton class="h-5 w-[40%] dark:bg-gray-800" />
              <Skeleton class="h-4 w-full dark:bg-gray-800" />
            </div>
          </div>
        </CardHeader>
      </Card>
    </div>

    <!-- Reviews list -->
    <div v-else-if="reviews.length > 0" class="grid gap-4">
      <Card v-for="review in reviews" :key="review.id" class="group overflow-hidden hover:shadow-lg transition-all duration-300 dark:bg-gray-900 dark:border-gray-800">
        <CardHeader class="pb-3">
          <div class="flex justify-between items-start gap-4">
            <div class="flex-1 min-w-0">
              <CardTitle class="text-lg font-bold text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors truncate">
                {{ review.site_name }}
              </CardTitle>
              <CardDescription class="dark:text-gray-400 text-xs">{{ review.date }}</CardDescription>
            </div>
            <div class="flex text-yellow-400 text-sm gap-0.5 bg-yellow-50 dark:bg-yellow-900/20 px-2.5 py-1 rounded-full shrink-0">
              <i v-for="n in 5" :key="n" class="fas fa-star text-xs" :class="n <= review.rating ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'"></i>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div class="relative pl-4 border-l-2 border-blue-200 dark:border-blue-900">
            <p class="text-sm text-gray-600 dark:text-gray-300 italic line-clamp-2">
              "{{ review.excerpt }}"
            </p>
          </div>
        </CardContent>
        <CardFooter class="pt-0 flex justify-end">
          <Button variant="ghost" size="sm" class="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/20">
            Leer completa <i class="fas fa-arrow-right ml-2 text-xs"></i>
          </Button>
        </CardFooter>
      </Card>
    </div>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center py-16 text-center bg-white dark:bg-gray-900/50 rounded-2xl border-2 border-dashed border-gray-300 dark:border-gray-700 mx-auto max-w-md">
      <div class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 p-5 rounded-full mb-5">
        <i class="fas fa-pencil-alt text-blue-500 dark:text-blue-400 text-3xl"></i>
      </div>
      <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">Sin reseñas aún</h3>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-6 max-w-[280px]">
        Comparte tu opinión y ayuda a otros exploradores.
      </p>
      <Button class="bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg transition-all">
        <i class="fas fa-compass mr-2"></i>
        Explorar Sitios
      </Button>
    </div>
  </div>
</template>
