<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, shallowRef, nextTick } from 'vue'

// ---------------------------------------------------------------------------
// One Dark Pro theme definition (ported from BusinessPress page-builder)
// ---------------------------------------------------------------------------
const ONE_DARK_PRO_THEME = {
  base: 'vs-dark' as const,
  inherit: true,
  rules: [
    { token: '', foreground: 'abb2bf', background: '282c34' },
    { token: 'comment', foreground: '5c6370', fontStyle: 'italic' },
    { token: 'keyword', foreground: 'c678dd' },
    { token: 'string', foreground: '98c379' },
    { token: 'number', foreground: 'd19a66' },
    { token: 'variable', foreground: 'e06c75' },
    { token: 'type', foreground: 'e5c07b' },
    { token: 'function', foreground: '61afef' },
    { token: 'tag', foreground: 'e06c75' },
    { token: 'attribute.name', foreground: 'd19a66' },
    { token: 'attribute.value', foreground: '98c379' },
    { token: 'delimiter', foreground: 'abb2bf' },
    { token: 'delimiter.html', foreground: 'abb2bf' },
    { token: 'delimiter.twig', foreground: '56b6c2' },
    { token: 'tag.twig', foreground: 'c678dd' },
    { token: 'variable.twig', foreground: 'e06c75' },
    { token: 'string.twig', foreground: '98c379' },
    { token: 'number.twig', foreground: 'd19a66' },
    { token: 'keyword.twig', foreground: 'c678dd' },
    { token: 'metatag', foreground: 'e06c75' },
    { token: 'metatag.content', foreground: '98c379' },
  ],
  colors: {
    'editor.background': '#282c34',
    'editor.foreground': '#abb2bf',
    'editor.lineHighlightBackground': '#2c313c',
    'editor.selectionBackground': '#3e4451',
    'editorCursor.foreground': '#528bff',
    'editorWhitespace.foreground': '#3b4048',
    'editorIndentGuide.background': '#3b4048',
    'editorIndentGuide.activeBackground': '#c8c8c859',
    'editor.selectionHighlightBackground': '#3e445180',
    'editorBracketMatch.background': '#3e4451',
    'editorBracketMatch.border': '#528bff',
    'editorLineNumber.foreground': '#495162',
    'editorLineNumber.activeForeground': '#abb2bf',
    'editorGutter.background': '#282c34',
    'editorWidget.background': '#21252b',
    'editorWidget.border': '#3a3f4b',
    'input.background': '#1d1f23',
    'input.border': '#3a3f4b',
    'focusBorder': '#528bff',
    'list.activeSelectionBackground': '#2c313c',
    'list.hoverBackground': '#2c313c50',
    'scrollbarSlider.background': '#4e566680',
    'scrollbarSlider.hoverBackground': '#5a637580',
    'scrollbarSlider.activeBackground': '#747d9180',
  },
}

// ---------------------------------------------------------------------------
// Monaco CDN configuration
// ---------------------------------------------------------------------------
const MONACO_VERSION = '0.52.0'
const MONACO_CDN = `https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/${MONACO_VERSION}/min`

// ---------------------------------------------------------------------------
// Props & emits
// ---------------------------------------------------------------------------
const props = withDefaults(
  defineProps<{
    value?: string
    language?: string
    theme?: string
    options?: Record<string, any>
  }>(),
  {
    value: '',
    language: 'plaintext',
    theme: 'one-dark-pro',
    options: () => ({}),
  },
)

const emit = defineEmits<{
  change: [value: string]
}>()

// ---------------------------------------------------------------------------
// Refs
// ---------------------------------------------------------------------------
const containerRef = ref<HTMLDivElement | null>(null)
const editorInstance = shallowRef<any>(null)
const monacoRef = shallowRef<any>(null)
const isLoading = ref(true)
const loadFailed = ref(false)
const cursorLine = ref(1)
const cursorColumn = ref(1)
const selectionCount = ref(0)
const lineCount = ref(0)
const wordWrapOn = ref(true)
const minimapOn = ref(false)
let resizeObserver: ResizeObserver | null = null
let isUpdatingFromExternal = false

// ---------------------------------------------------------------------------
// Toolbar actions
// ---------------------------------------------------------------------------
function editorAction(action: string) {
  editorInstance.value?.getAction(action)?.run()
}

function undo() {
  editorInstance.value?.trigger('toolbar', 'undo')
}

function redo() {
  editorInstance.value?.trigger('toolbar', 'redo')
}

function openSearch() {
  editorAction('actions.find')
}

function openReplace() {
  editorAction('editor.action.startFindReplaceAction')
}

function toggleWordWrap() {
  wordWrapOn.value = !wordWrapOn.value
  editorInstance.value?.updateOptions({ wordWrap: wordWrapOn.value ? 'on' : 'off' })
}

function toggleMinimap() {
  minimapOn.value = !minimapOn.value
  editorInstance.value?.updateOptions({ minimap: { enabled: minimapOn.value } })
}

// ---------------------------------------------------------------------------
// CDN loader (singleton pattern, same as the Alpine component)
// ---------------------------------------------------------------------------
let monacoLoadPromise: Promise<any> | null = null

function loadMonacoFromCDN(): Promise<any> {
  if (monacoLoadPromise) return monacoLoadPromise

  monacoLoadPromise = new Promise((resolve, reject) => {
    // If already loaded (shared across instances)
    if ((window as any).monaco) {
      resolve((window as any).monaco)
      return
    }

    // Check if the AMD loader script is already on the page
    const existingScript = document.querySelector('script[data-monaco-loader]')
    const loaderReady = typeof (window as any).require !== 'undefined'
      && typeof (window as any).require.config === 'function'

    const configureAndLoad = () => {
      const require = (window as any).require

      require.config({
        paths: { vs: `${MONACO_CDN}/vs` },
      })

      // Web worker proxy so Monaco workers load from CDN
      const workerBlob = new Blob(
        [
          `self.MonacoEnvironment = { baseUrl: '${MONACO_CDN}' };
          importScripts('${MONACO_CDN}/vs/base/worker/workerMain.js');`,
        ],
        { type: 'text/javascript' },
      )
      const workerUrl = URL.createObjectURL(workerBlob)
      ;(window as any).MonacoEnvironment = {
        getWorkerUrl: () => workerUrl,
      }

      require(['vs/editor/editor.main'], () => {
        resolve((window as any).monaco)
      })
    }

    if (loaderReady) {
      configureAndLoad()
      return
    }

    // Load the AMD loader script
    const script = document.createElement('script')
    script.src = `${MONACO_CDN}/vs/loader.min.js`
    script.setAttribute('data-monaco-loader', 'true')
    script.onload = () => {
      // Poll until require.config is available (may take a tick)
      const poll = setInterval(() => {
        if (
          typeof (window as any).require !== 'undefined'
          && typeof (window as any).require.config === 'function'
        ) {
          clearInterval(poll)
          configureAndLoad()
        }
      }, 10)
    }
    script.onerror = () => reject(new Error('Failed to load Monaco loader script'))
    document.head.appendChild(script)
  })

  return monacoLoadPromise
}

// ---------------------------------------------------------------------------
// Lifecycle
// ---------------------------------------------------------------------------
onMounted(async () => {
  if (!containerRef.value) return

  try {
    const monaco = await loadMonacoFromCDN()
    monacoRef.value = monaco

    // Register the One Dark Pro theme (idempotent -- defineTheme overwrites)
    monaco.editor.defineTheme('one-dark-pro', ONE_DARK_PRO_THEME)

    // Merge default editor options with caller overrides
    const defaultOptions: Record<string, any> = {
      value: props.value,
      language: props.language,
      theme: props.theme,
      minimap: { enabled: false },
      wordWrap: 'on',
      fontSize: 14,
      tabSize: 2,
      scrollBeyondLastLine: false,
      fontFamily:
        "'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace",
      fontLigatures: true,
      renderWhitespace: 'selection',
      bracketPairColorization: { enabled: true },
      guides: { bracketPairs: true, indentation: true },
      padding: { top: 10, bottom: 10 },
      smoothScrolling: true,
      cursorBlinking: 'smooth',
      cursorSmoothCaretAnimation: 'on',
      formatOnPaste: true,
      autoClosingBrackets: 'always',
      autoClosingQuotes: 'always',
      autoIndent: 'full',
      stickyScroll: { enabled: false },
      folding: true,
      showFoldingControls: 'mouseover',
      lineNumbers: 'on',
      // NOTE: we deliberately omit `automaticLayout: true` because we handle
      // resize ourselves via ResizeObserver (more reliable in flex layouts).
    }

    // Deep merge: props.options wins for top-level keys
    const mergedOptions = { ...defaultOptions, ...props.options }

    editorInstance.value = monaco.editor.create(containerRef.value, mergedOptions)

    // Content change -> emit
    editorInstance.value.onDidChangeModelContent(() => {
      if (isUpdatingFromExternal) return
      const currentValue = editorInstance.value.getValue()
      emit('change', currentValue)
      lineCount.value = editorInstance.value.getModel()?.getLineCount() ?? 0
    })

    // Cursor position tracking
    editorInstance.value.onDidChangeCursorPosition((e: any) => {
      cursorLine.value = e.position.lineNumber
      cursorColumn.value = e.position.column
    })

    editorInstance.value.onDidChangeCursorSelection((e: any) => {
      const sel = e.selection
      if (sel.isEmpty()) {
        selectionCount.value = 0
      } else {
        const model = editorInstance.value.getModel()
        if (model) {
          selectionCount.value = model.getValueInRange(sel).length
        }
      }
    })

    // Initial line count
    lineCount.value = editorInstance.value.getModel()?.getLineCount() ?? 0

    // ResizeObserver for automatic layout
    setupResizeObserver()

    isLoading.value = false
  } catch (err) {
    console.warn('Monaco editor failed to load:', err)
    loadFailed.value = true
    isLoading.value = false
  }
})

// ---------------------------------------------------------------------------
// Watchers
// ---------------------------------------------------------------------------

// External value changes
watch(
  () => props.value,
  (newValue) => {
    const editor = editorInstance.value
    if (!editor) return
    const currentValue = editor.getValue()
    if (currentValue === newValue) return

    isUpdatingFromExternal = true

    // Use pushEditOperations to preserve undo stack
    const model = editor.getModel()
    if (model) {
      const fullRange = model.getFullModelRange()
      editor.executeEdits('external-sync', [
        {
          range: fullRange,
          text: newValue ?? '',
          forceMoveMarkers: true,
        },
      ])
    }

    nextTick(() => {
      isUpdatingFromExternal = false
    })
  },
)

// Language changes
watch(
  () => props.language,
  (newLang) => {
    const editor = editorInstance.value
    const monaco = monacoRef.value
    if (!editor || !monaco) return
    const model = editor.getModel()
    if (model) {
      monaco.editor.setModelLanguage(model, newLang)
    }
  },
)

// Theme changes
watch(
  () => props.theme,
  (newTheme) => {
    const monaco = monacoRef.value
    if (!monaco) return
    monaco.editor.setTheme(newTheme)
  },
)

// Options changes (shallow comparison of the object reference)
watch(
  () => props.options,
  (newOptions) => {
    const editor = editorInstance.value
    if (!editor) return
    editor.updateOptions(newOptions)
  },
  { deep: true },
)

// ---------------------------------------------------------------------------
// ResizeObserver
// ---------------------------------------------------------------------------
function setupResizeObserver() {
  if (!containerRef.value || !editorInstance.value) return

  resizeObserver = new ResizeObserver(() => {
    editorInstance.value?.layout()
  })
  resizeObserver.observe(containerRef.value)
}

// ---------------------------------------------------------------------------
// Cleanup
// ---------------------------------------------------------------------------
onBeforeUnmount(() => {
  // Disconnect resize observer
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }

  // Dispose the editor
  if (editorInstance.value) {
    editorInstance.value.dispose()
    editorInstance.value = null
  }
})

// ---------------------------------------------------------------------------
// Textarea fallback handler
// ---------------------------------------------------------------------------
function onTextareaInput(e: Event) {
  const target = e.target as HTMLTextAreaElement
  emit('change', target.value)
}
</script>

<template>
  <!-- Loading state -->
  <div
    v-if="isLoading && !loadFailed"
    class="w-full h-full min-h-[200px] bg-[#282c34] flex items-center justify-center rounded-lg border border-[#3a3f4b]"
  >
    <div class="flex items-center gap-2 text-[#6b717d]">
      <svg
        class="animate-spin h-5 w-5"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <span class="text-sm">Loading editor...</span>
    </div>
  </div>

  <!-- Textarea fallback when Monaco fails to load -->
  <div v-else-if="loadFailed" class="w-full h-full min-h-[200px] p-0">
    <textarea
      :value="value"
      class="w-full h-full bg-[#282c34] text-[#abb2bf] font-mono text-sm p-4 resize-none border border-[#3a3f4b] rounded-lg outline-none focus:border-[#528bff]"
      spellcheck="false"
      @input="onTextareaInput"
    />
  </div>

  <!-- Monaco editor + toolbar + status bar -->
  <div
    v-show="!isLoading && !loadFailed"
    class="w-full h-full min-h-[200px] flex flex-col"
  >
    <!-- Toolbar -->
    <div class="flex items-center px-2 py-1 bg-[#21252b] border-b border-[#3a3f4b] shrink-0 select-none">
      <div class="flex items-center gap-1">
        <!-- Undo -->
        <button
          type="button"
          class="p-1.5 text-[#6b717d] hover:text-[#abb2bf] hover:bg-[#2c313c] rounded transition-colors"
          title="Undo"
          @click="undo"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a5 5 0 015 5v2M3 10l4-4m-4 4l4 4" />
          </svg>
        </button>

        <!-- Redo -->
        <button
          type="button"
          class="p-1.5 text-[#6b717d] hover:text-[#abb2bf] hover:bg-[#2c313c] rounded transition-colors"
          title="Redo"
          @click="redo"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 10H11a5 5 0 00-5 5v2m15-7l-4-4m4 4l-4 4" />
          </svg>
        </button>

        <div class="w-px h-4 bg-[#3b4048] mx-1" />

        <!-- Search -->
        <button
          type="button"
          class="p-1.5 text-[#6b717d] hover:text-[#abb2bf] hover:bg-[#2c313c] rounded transition-colors"
          title="Search (Ctrl+F)"
          @click="openSearch"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </button>

        <!-- Replace -->
        <button
          type="button"
          class="p-1.5 text-[#6b717d] hover:text-[#abb2bf] hover:bg-[#2c313c] rounded transition-colors"
          title="Search & Replace (Ctrl+H)"
          @click="openReplace"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
        </button>

        <div class="w-px h-4 bg-[#3b4048] mx-1" />

        <!-- Word Wrap Toggle -->
        <button
          type="button"
          class="p-1.5 rounded transition-colors"
          :class="wordWrapOn ? 'text-[#61afef] bg-[#2c313c]' : 'text-[#6b717d] hover:text-[#abb2bf] hover:bg-[#2c313c]'"
          title="Toggle Word Wrap"
          @click="toggleWordWrap"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h10m-10 6h16" />
          </svg>
        </button>

        <!-- Minimap Toggle -->
        <button
          type="button"
          class="p-1.5 rounded transition-colors"
          :class="minimapOn ? 'text-[#61afef] bg-[#2c313c]' : 'text-[#6b717d] hover:text-[#abb2bf] hover:bg-[#2c313c]'"
          title="Toggle Minimap"
          @click="toggleMinimap"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Editor -->
    <div ref="containerRef" class="flex-1 min-h-0" />
    <!-- Status bar -->
    <div class="flex items-center justify-between px-3 py-1 bg-[#21252b] text-[#6b717d] text-[11px] font-mono border-t border-[#3a3f4b] shrink-0 select-none">
      <div class="flex items-center gap-4">
        <span>Ln {{ cursorLine }}, Col {{ cursorColumn }}</span>
        <span v-if="selectionCount > 0">({{ selectionCount }} selected)</span>
      </div>
      <div class="flex items-center gap-4">
        <span>{{ lineCount }} lines</span>
        <span class="uppercase">{{ language }}</span>
        <span>UTF-8</span>
      </div>
    </div>
  </div>
</template>
