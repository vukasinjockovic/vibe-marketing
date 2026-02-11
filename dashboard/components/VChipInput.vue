<script setup lang="ts">
import { ref } from 'vue'
import { X } from 'lucide-vue-next'

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
  <div class="flex h-auto min-h-10 w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm ring-offset-background focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 flex-wrap gap-1.5 items-center">
    <span
      v-for="(chip, idx) in modelValue"
      :key="idx"
      class="inline-flex items-center gap-1 bg-primary/10 text-primary text-xs px-2 py-0.5 rounded-full font-medium"
    >
      {{ chip }}
      <button type="button" class="hover:text-primary/70" @click="remove(idx)">
        <X :size="12" />
      </button>
    </span>
    <input
      v-model="inputValue"
      :placeholder="modelValue.length === 0 ? (placeholder || 'Type and press Enter') : ''"
      class="flex-1 min-w-[120px] text-sm outline-none bg-transparent placeholder:text-muted-foreground"
      @keydown="onKeydown"
    />
  </div>
</template>
