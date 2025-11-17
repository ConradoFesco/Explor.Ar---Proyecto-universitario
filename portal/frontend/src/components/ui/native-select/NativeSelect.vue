<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'
import { ChevronDown } from 'lucide-vue-next'

interface NativeSelectProps {
  modelValue?: string
  placeholder?: string
  disabled?: boolean
  class?: HTMLAttributes['class']
  options: Array<{ value: string; label: string }>
}

const props = withDefaults(defineProps<NativeSelectProps>(), {
  modelValue: '',
  placeholder: 'Seleccionar...',
  disabled: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

function handleChange(event: Event) {
  const target = event.target as HTMLSelectElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="relative">
    <select
      :value="modelValue"
      @change="handleChange"
      :disabled="disabled"
      :class="cn(
        'appearance-none w-full h-9 rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs transition-[color,box-shadow] outline-none',
        'focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]',
        'disabled:cursor-not-allowed disabled:opacity-50',
        'pr-8',
        props.class
      )"
    >
      <option v-if="placeholder" value="">{{ placeholder }}</option>
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>
    <ChevronDown
      class="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 opacity-50 pointer-events-none"
    />
  </div>
</template>

