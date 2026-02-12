<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, shallowRef } from 'vue'
import { loader } from '@guolao/vue-monaco-editor'

const props = withDefaults(defineProps<{
  value?: string
  language?: string
  theme?: string
  options?: Record<string, any>
}>(), {
  value: '',
  language: 'plaintext',
  theme: 'vs-dark',
  options: () => ({}),
})

const emit = defineEmits<{
  change: [value: string]
}>()

const containerRef = ref<HTMLDivElement | null>(null)
const editorInstance = shallowRef<any>(null)
const monacoRef = shallowRef<any>(null)
const loadFailed = ref(false)

onMounted(async () => {
  if (!containerRef.value) return

  try {
    // Use the @monaco-editor/loader which loads from CDN by default
    // This avoids all Vite/Rollup worker bundling issues
    const monaco = await loader.init()
    monacoRef.value = monaco

    editorInstance.value = monaco.editor.create(containerRef.value, {
      value: props.value,
      language: props.language,
      theme: props.theme,
      ...props.options,
    })

    editorInstance.value.onDidChangeModelContent(() => {
      const currentValue = editorInstance.value.getValue()
      emit('change', currentValue)
    })
  } catch (err) {
    console.warn('Monaco editor failed to load:', err)
    loadFailed.value = true
  }
})

// Watch for external value changes
watch(() => props.value, (newValue) => {
  if (editorInstance.value) {
    const currentValue = editorInstance.value.getValue()
    if (currentValue !== newValue) {
      editorInstance.value.setValue(newValue)
    }
  }
})

// Watch for language changes
watch(() => props.language, (newLang) => {
  if (editorInstance.value && monacoRef.value) {
    const model = editorInstance.value.getModel()
    if (model) {
      monacoRef.value.editor.setModelLanguage(model, newLang)
    }
  }
})

// Watch for theme changes
watch(() => props.theme, (newTheme) => {
  if (monacoRef.value) {
    monacoRef.value.editor.setTheme(newTheme)
  }
})

onUnmounted(() => {
  if (editorInstance.value) {
    editorInstance.value.dispose()
    editorInstance.value = null
  }
})

function onTextareaInput(e: Event) {
  const target = e.target as HTMLTextAreaElement
  emit('change', target.value)
}
</script>

<template>
  <div v-if="loadFailed" class="w-full h-full min-h-[200px] p-0">
    <textarea
      :value="value"
      class="w-full h-full bg-[#1e1e1e] text-[#d4d4d4] font-mono text-sm p-4 resize-none border-0 outline-none"
      spellcheck="false"
      @input="onTextareaInput"
    />
  </div>
  <div v-else ref="containerRef" class="w-full h-full min-h-[200px]" />
</template>
