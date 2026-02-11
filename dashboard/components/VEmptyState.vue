<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div class="rounded-lg border bg-card text-card-foreground shadow-sm p-12 text-center">
    <div v-if="$slots.icon" class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-muted">
      <slot name="icon" />
    </div>
    <h3 class="text-lg font-medium text-foreground">{{ title }}</h3>
    <p v-if="description" class="text-muted-foreground mt-1 text-sm">{{ description }}</p>
    <div v-if="$slots.default" class="mt-4">
      <slot />
    </div>
  </div>
</template>
