<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const route = useRoute()
const router = useRouter()

// Esta vista será implementada por tu compañero
// Por ahora solo muestra un placeholder
function handleBack() {
  const returnTo = route.query.returnTo as string | undefined
  if (returnTo) {
    router.push(returnTo)
  } else {
    router.push({ name: 'home' })
  }
}
</script>

<template>
  <div class="max-w-md mx-auto mt-8 space-y-6">
    <div class="text-center space-y-2">
      <h1 class="text-2xl font-bold">Iniciar Sesión</h1>
      <p class="text-gray-600">Esta página será implementada próximamente</p>
    </div>
    
    <div class="border rounded-lg p-6 space-y-4 bg-gray-50">
      <p class="text-sm text-gray-500 text-center">
        El formulario de login con Google será implementado aquí.
      </p>
      
      <Button 
        variant="outline" 
        class="w-full"
        @click="handleBack"
      >
        Volver
      </Button>
    </div>
  </div>
</template>

