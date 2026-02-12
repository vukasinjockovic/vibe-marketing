<script setup lang="ts">
const props = defineProps<{
  label: string
  value: any
  filled: boolean
  confidence?: string
}>()

const isObject = computed(() => typeof props.value === 'object' && props.value !== null)
const isString = computed(() => typeof props.value === 'string')

// Extract arrays and scalar fields from an object value
const objectArrays = computed(() => {
  if (!isObject.value || Array.isArray(props.value)) return []
  const result: { key: string, values: string[] }[] = []
  for (const [key, val] of Object.entries(props.value)) {
    if (Array.isArray(val) && val.length) {
      result.push({ key: formatKey(key), values: val as string[] })
    }
  }
  return result
})

const objectScalars = computed(() => {
  if (!isObject.value || Array.isArray(props.value)) return []
  const result: { key: string, value: string }[] = []
  for (const [key, val] of Object.entries(props.value)) {
    if (!Array.isArray(val) && val !== null && val !== undefined) {
      result.push({ key: formatKey(key), value: String(val) })
    }
  }
  return result
})

function formatKey(key: string): string {
  return key.replace(/([A-Z])/g, ' $1').replace(/^./, s => s.toUpperCase()).trim()
}
</script>

<template>
  <div class="flex items-start gap-2">
    <span
      data-testid="field-status-indicator"
      class="mt-1 w-2 h-2 rounded-full flex-shrink-0"
      :class="filled ? 'bg-green-500' : 'bg-muted-foreground/30'"
    />
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2">
        <span class="text-xs font-medium text-muted-foreground">{{ label }}</span>
        <span
          v-if="confidence"
          data-testid="confidence-badge"
          class="text-xs px-1.5 py-0.5 rounded-full"
          :class="{
            'bg-green-100 text-green-700': confidence === 'high',
            'bg-yellow-100 text-yellow-700': confidence === 'medium',
            'bg-red-100 text-red-700': confidence === 'low',
          }"
        >
          {{ confidence }}
        </span>
      </div>

      <!-- Not filled -->
      <p v-if="!filled" class="text-sm text-muted-foreground/70 italic mt-0.5">Not yet enriched</p>

      <!-- Simple string value -->
      <p v-else-if="isString" class="text-sm text-foreground mt-0.5">{{ value }}</p>

      <!-- Object value — render structured -->
      <div v-else-if="isObject" class="mt-1 space-y-2">
        <!-- Scalar fields as a grid -->
        <div v-if="objectScalars.length" class="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
          <div v-for="s in objectScalars" :key="s.key">
            <span class="text-muted-foreground text-xs">{{ s.key }}:</span>
            <span class="ml-1 text-foreground">{{ s.value }}</span>
          </div>
        </div>
        <!-- Array fields as pill groups -->
        <div v-for="arr in objectArrays" :key="arr.key">
          <span class="text-xs text-muted-foreground">{{ arr.key }}:</span>
          <div class="flex flex-wrap gap-1 mt-0.5">
            <span
              v-for="item in arr.values"
              :key="item"
              class="bg-muted text-foreground text-xs px-2 py-0.5 rounded-full"
            >{{ item }}</span>
          </div>
        </div>
      </div>

      <!-- Fallback -->
      <p v-else class="text-sm text-foreground mt-0.5">{{ value }}</p>
    </div>
  </div>
</template>
