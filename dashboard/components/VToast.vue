<script setup lang="ts">
import { X } from 'lucide-vue-next'

const { toasts, dismiss } = useToast()

const typeStyles: Record<string, string> = {
  success: 'bg-green-600',
  error: 'bg-red-600',
  warning: 'bg-yellow-600',
  info: 'bg-primary',
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed bottom-4 right-4 z-[100] space-y-2 w-80">
      <TransitionGroup
        enter-active-class="transition-all duration-300"
        leave-active-class="transition-all duration-300"
        enter-from-class="opacity-0 translate-x-8"
        leave-to-class="opacity-0 translate-x-8"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="rounded-lg px-4 py-3 text-white text-sm shadow-lg flex items-center justify-between"
          :class="typeStyles[toast.type] || typeStyles.info"
        >
          <span>{{ toast.message }}</span>
          <button class="ml-3 opacity-70 hover:opacity-100" @click="dismiss(toast.id)">
            <X :size="14" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
