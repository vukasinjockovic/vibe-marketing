<script setup lang="ts">
import { computed, watch, onUnmounted } from 'vue'
import { X } from 'lucide-vue-next'

const props = defineProps<{
  modelValue: boolean
  title: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  persistent?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const sizeClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'max-w-md'
    case 'lg': return 'max-w-2xl'
    case 'xl': return 'max-w-4xl'
    default: return 'max-w-lg'
  }
})

function close() {
  emit('update:modelValue', false)
}

function onBackdrop(e: MouseEvent) {
  if (!props.persistent && e.target === e.currentTarget) close()
}

function onKeydown(e: KeyboardEvent) {
  if (!props.persistent && e.key === 'Escape') close()
}

watch(() => props.modelValue, (open) => {
  if (open) {
    document.addEventListener('keydown', onKeydown)
    document.body.style.overflow = 'hidden'
  } else {
    document.removeEventListener('keydown', onKeydown)
    document.body.style.overflow = ''
  }
}, { immediate: true })

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200"
      leave-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 overflow-y-auto" @click="onBackdrop">
        <div class="bg-background rounded-lg shadow-xl w-full my-auto border max-h-[calc(100vh-2rem)] flex flex-col" :class="sizeClass" @click.stop>
          <div class="flex items-center justify-between px-6 py-4 border-b shrink-0">
            <h2 class="text-lg font-semibold text-foreground">{{ title }}</h2>
            <button class="text-muted-foreground hover:text-foreground transition-colors rounded-sm opacity-70 hover:opacity-100" @click="close">
              <X :size="18" />
            </button>
          </div>
          <div class="px-6 py-4 overflow-y-auto flex-1">
            <slot />
          </div>
          <div v-if="$slots.footer" class="px-6 py-3 border-t bg-muted/50 rounded-b-lg flex justify-end gap-3 shrink-0">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
