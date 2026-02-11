<script setup lang="ts">
defineProps<{
  label: string
  error?: string
  required?: boolean
  hint?: string
}>()
</script>

<template>
  <div class="space-y-1.5">
    <label class="block text-sm font-medium text-foreground">
      {{ label }}
      <span v-if="required" class="text-destructive">*</span>
    </label>
    <slot />
    <p v-if="hint && !error" class="text-xs text-muted-foreground">{{ hint }}</p>
    <p v-if="error" class="text-xs text-destructive">{{ error }}</p>
  </div>
</template>
