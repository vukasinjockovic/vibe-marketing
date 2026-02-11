<script setup lang="ts">
const props = defineProps<{
  modelValue: boolean
  title: string
  message: string
  confirmLabel?: string
  confirmClass?: string
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: []
}>()

function close() {
  emit('update:modelValue', false)
}
</script>

<template>
  <VModal :model-value="modelValue" :title="title" @update:model-value="$emit('update:modelValue', $event)">
    <p class="text-muted-foreground">{{ message }}</p>
    <template #footer>
      <button class="px-4 py-2 text-sm text-muted-foreground hover:bg-muted rounded-md transition-colors" @click="close">
        Cancel
      </button>
      <button
        class="px-4 py-2 text-sm text-white rounded-md transition-colors disabled:opacity-50"
        :class="confirmClass || 'bg-primary hover:bg-primary/90'"
        :disabled="loading"
        @click="$emit('confirm')"
      >
        {{ confirmLabel || 'Confirm' }}
      </button>
    </template>
  </VModal>
</template>
