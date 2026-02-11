<script setup lang="ts">
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
  <div class="bg-white rounded-lg shadow overflow-hidden">
    <div v-if="loading" class="p-8 text-center text-gray-500">
      <span class="i-heroicons-arrow-path animate-spin text-2xl mb-2 block" />
      Loading...
    </div>
    <div v-else-if="rows.length === 0" class="p-8 text-center text-gray-500">
      {{ emptyMessage || 'No data found.' }}
    </div>
    <table v-else class="w-full">
      <thead class="bg-gray-50 border-b">
        <tr>
          <th
            v-for="col in columns"
            :key="col.key"
            class="text-left px-4 py-3 text-sm font-medium text-gray-500"
            :class="col.class"
          >
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y">
        <tr v-for="(row, idx) in rows" :key="row._id || idx" class="hover:bg-gray-50 transition-colors">
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
