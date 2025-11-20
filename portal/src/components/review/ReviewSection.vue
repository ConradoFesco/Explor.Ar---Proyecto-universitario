<script setup lang="ts">
import {
  Card,
  CardContent,
} from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Star } from 'lucide-vue-next'

// Datos de muestra para las reseñas
const reviews = [
  {
    id: 'r1',
    name: 'María Contreras',
    initials: 'MC',
    rating: 5.0,
    text: '"Una experiencia inolvidable. El Cabildo superó todas mis expectativas. La historia y la belleza del lugar son impresionantes."',
    date: 'Hace 2 días'
  },
  {
    id: 'r2',
    name: 'Juan Rodríguez',
    initials: 'JR',
    rating: 4.8,
    text: '"Las Ruinas de San Ignacio son simplemente majestuosas. Caminar por donde los jesuitas vivieron hace siglos es una sensación única."',
    date: 'Hace 5 días'
  },
  {
    id: 'r3',
    name: 'Ana López',
    initials: 'AL',
    rating: 5.0,
    text: '"La Quebrada de Humahuaca al atardecer es algo que todos deberían ver al menos una vez en la vida. Absolutamente hermoso."',
    date: 'Hace 1 semana'
  }
]
</script>

<template>
  <section class="py-12 md:py-16 bg-gray-100 dark:bg-gray-800">
    <div class="max-w-7xl mx-auto px-4 md:px-8">

      <!-- Encabezado de la Sección -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h2 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Reseñas Recientes
          </h2>
          <p class="text-gray-600 dark:text-gray-400">
            Lo que dicen nuestros visitantes
          </p>
        </div>
      </div>

      <!-- Grid de Reseñas -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">

        <!-- Iteramos sobre las reseñas -->
        <Card
          v-for="review in reviews"
          :key="review.id"
          class="bg-white dark:bg-gray-900"
        >
          <CardContent class="p-6">
            <!-- Encabezado de la reseña (Avatar y Nombre) -->
            <div class="flex items-center gap-3 mb-4">
              <Avatar>
                <AvatarImage :src="`/avatars/${review.initials}.png`" :alt="review.name" />
                <AvatarFallback class="bg-blue-600 text-white font-semibold">
                  {{ review.initials }}
                </AvatarFallback>
              </Avatar>
              <div>
                <p class="font-semibold text-gray-900 dark:text-gray-100">
                  {{ review.name }}
                </p>
                <div class="flex items-center gap-1">
                  <Star class="w-4 h-4 text-yellow-400 fill-yellow-400" />
                  <span class="text-sm text-gray-600 dark:text-gray-400">
                    {{ review.rating }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Texto de la Reseña -->
            <p class="text-gray-700 dark:text-gray-300 text-sm mb-3">
              {{ review.text }}
            </p>

            <!-- Fecha -->
            <p class="text-xs text-gray-500 dark:text-gray-500">
              {{ review.date }}
            </p>
          </CardContent>
        </Card>

      </div>
    </div>
  </section>
</template>
