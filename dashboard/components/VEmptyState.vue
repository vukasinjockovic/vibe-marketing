<script setup lang="ts">
defineProps<{
  icon?: string
  title: string
  description?: string
}>()
</script>

<template>
  <div class="bg-white rounded-lg shadow p-12 text-center">
    <span v-if="icon" :class="icon" class="text-4xl text-gray-300 mb-4 block" />
    <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
    <p v-if="description" class="text-gray-500 mt-1">{{ description }}</p>
    <div v-if="$slots.default" class="mt-4">
      <slot />
    </div>
  </div>
</template>
