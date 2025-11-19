<script setup lang="ts">
import { Check } from 'lucide-vue-next'

const props = defineProps<{
  checked: boolean
  id?: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:checked', value: boolean): void
}>()

function handleToggle() {
  if (!props.disabled) {
    emit('update:checked', !props.checked)
  }
}
</script>

<template>
  <div
    :id="id"
    role="checkbox"
    :aria-checked="checked"
    :aria-disabled="disabled"
    tabindex="0"
    @click="handleToggle"
    @keydown.enter.prevent="handleToggle"
    @keydown.space.prevent="handleToggle"
    class="flex items-center justify-center w-4 h-4 border rounded-[4px] cursor-pointer transition-colors shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
    :class="checked
      ? 'bg-primary border-primary dark:bg-primary dark:border-primary'
      : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'"
  >
    <Check v-if="checked" class="w-3.5 h-3.5 text-white" />
  </div>
</template>

