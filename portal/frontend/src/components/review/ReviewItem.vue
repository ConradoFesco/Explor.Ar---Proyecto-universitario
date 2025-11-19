<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Review } from '@/lib/api'
import { useReviewsStore } from '@/stores/reviews'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Star, Pencil, Trash2, MoreVertical } from 'lucide-vue-next'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

const props = defineProps<{ review: Review }>()
const emit = defineEmits<{ (e: 'edit'): void; (e: 'delete-success'): void }>()

const reviewsStore = useReviewsStore()
const isDeleting = ref(false)

const authorName = computed(() => props.review.user.name || 'Anónimo')
const authorInitials = computed(() =>
  (props.review.user.name?.substring(0, 1) || 'U').toUpperCase()
)

async function onDelete() {
  if (!confirm('¿Eliminar esta reseña?')) return
  isDeleting.value = true
  try {
    await reviewsStore.deleteReview(props.review.id)
    emit('delete-success')
  } catch (error) {
    console.error(error)
    alert('Error al eliminar')
  } finally {
    isDeleting.value = false
  }
}
</script>

<template>
  <Card class="bg-white dark:bg-gray-800 dark:border-gray-700 transition-colors">
    <CardContent class="p-6">
      <div class="flex justify-between items-start">
        <div class="flex items-center gap-3">
          <Avatar>
            <AvatarImage src="" /> <!-- No hay avatar en la API -->
            <AvatarFallback class="bg-blue-100 text-blue-700">
              {{ authorInitials }}
            </AvatarFallback>
          </Avatar>

          <div>
            <p class="text-sm font-semibold text-gray-900 dark:text-gray-100">
              {{ authorName }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ review.created_at || 'Reciente' }}
            </p>
          </div>
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button variant="ghost" size="icon" class="h-8 w-8 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700">
              <MoreVertical class="h-4 w-4 text-gray-500 dark:text-gray-400" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" class="dark:bg-gray-800 dark:border-gray-700">
            <DropdownMenuItem @click="$emit('edit')" class="cursor-pointer dark:text-gray-200">
              <Pencil class="mr-2 h-4 w-4" /> Editar
            </DropdownMenuItem>
            <DropdownMenuItem @click="onDelete" class="cursor-pointer text-red-600" :disabled="isDeleting">
              <Trash2 class="mr-2 h-4 w-4" /> Eliminar
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <div class="flex items-center gap-1 mt-3 mb-2">
        <Star v-for="i in 5" :key="i" class="w-4 h-4"
          :class="i <= review.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300 dark:text-gray-600'" />
      </div>

      <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
        {{ review.content }}
      </p>
    </CardContent>
  </Card>
</template>
