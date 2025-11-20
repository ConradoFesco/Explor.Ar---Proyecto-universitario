<script setup lang="ts">
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'

interface Props {
  user: {
    name: string
    email: string
    avatar_url: string
  }
}

defineProps<Props>()
</script>

<template>
  <div class="w-full bg-gradient-to-b from-gray-900 to-gray-950 dark:from-gray-900 dark:to-gray-950 border-b border-gray-800 dark:border-gray-800 pb-14 pt-10 px-4 transition-colors duration-300 flex justify-center">
    <div class="w-full max-w-4xl flex flex-col items-center text-center">

      <div class="relative mb-6 group">
        <div class="absolute inset-0 bg-blue-500 rounded-full blur-xl opacity-30 group-hover:opacity-50 transition-opacity duration-500"></div>

        <Avatar class="h-28 w-28 border-4 border-gray-800 dark:border-gray-700 shadow-2xl relative z-10 ring-2 ring-blue-500/20">
          <AvatarImage :src="user.avatar_url" :alt="user.name" class="object-cover" />
          <AvatarFallback class="bg-gradient-to-br from-blue-500 to-blue-600 text-3xl font-bold text-white">
            {{ user.name ? user.name.charAt(0).toUpperCase() : 'U' }}
          </AvatarFallback>
        </Avatar>

        <Badge class="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-green-500 text-white border-2 border-gray-900 dark:border-gray-800 px-3 py-0.5 shadow-lg z-20 whitespace-nowrap">
          <i class="fab fa-google mr-1.5 text-xs"></i> Conectado
        </Badge>
      </div>

      <h1 class="text-3xl font-extrabold tracking-tight text-white mb-1">
        {{ user.name }}
      </h1>
      <p class="text-sm text-gray-400 font-medium">
        {{ user.email }}
      </p>

    </div>
  </div>
</template>
