<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  modelValue: string[]
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const inputValue = ref('')

function add() {
  const val = inputValue.value.trim()
  if (val && !props.modelValue.includes(val)) {
    emit('update:modelValue', [...props.modelValue, val])
  }
  inputValue.value = ''
}

function remove(index: number) {
  emit('update:modelValue', props.modelValue.filter((_, i) => i !== index))
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    e.preventDefault()
    add()
  }
  if (e.key === 'Backspace' && !inputValue.value && props.modelValue.length) {
    remove(props.modelValue.length - 1)
  }
}
</script>

<template>
  <div class="border rounded-md px-2 py-1.5 flex flex-wrap gap-1.5 items-center focus-within:ring-2 focus-within:ring-primary-500 focus-within:border-primary-500 bg-white min-h-[38px]">
    <span
      v-for="(chip, idx) in modelValue"
      :key="idx"
      class="inline-flex items-center gap-1 bg-primary-100 text-primary-800 text-xs px-2 py-0.5 rounded-full"
    >
      {{ chip }}
      <button type="button" class="hover:text-primary-600" @click="remove(idx)">
        <span class="i-heroicons-x-mark text-xs" />
      </button>
    </span>
    <input
      v-model="inputValue"
      :placeholder="modelValue.length === 0 ? (placeholder || 'Type and press Enter') : ''"
      class="flex-1 min-w-[120px] text-sm outline-none bg-transparent"
      @keydown="onKeydown"
    />
  </div>
</template>
