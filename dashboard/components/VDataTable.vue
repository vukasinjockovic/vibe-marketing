<script setup lang="ts">
import { LoaderCircle } from 'lucide-vue-next'

defineProps<{
  columns: Array<{
    key: string
    label: string
    class?: string
  }>
  rows: any[]
  loading?: boolean
  emptyMessage?: string
}>()
</script>

<template>
  <div class="rounded-lg border bg-card text-card-foreground shadow-sm overflow-x-auto">
    <div v-if="loading" class="p-8 text-center text-muted-foreground">
      <LoaderCircle class="animate-spin h-5 w-5 mx-auto mb-2 text-muted-foreground" />
      Loading...
    </div>
    <div v-else-if="rows.length === 0" class="p-8 text-center text-muted-foreground">
      {{ emptyMessage || 'No data found.' }}
    </div>
    <table v-else class="w-full min-w-[600px]">
      <thead class="border-b bg-muted/50">
        <tr>
          <th
            v-for="col in columns"
            :key="col.key"
            class="text-left px-4 py-3 text-sm font-medium text-muted-foreground"
            :class="col.class"
          >
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-border">
        <tr v-for="(row, idx) in rows" :key="row._id || idx" class="hover:bg-muted/50 transition-colors">
          <td v-for="col in columns" :key="col.key" class="px-4 py-3 text-sm" :class="col.class">
            <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
              {{ row[col.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
