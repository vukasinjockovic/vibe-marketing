<script setup lang="ts">
import { api } from '../../../convex/_generated/api'

const { data: pipelines, loading } = useConvexQuery(api.pipelines.list, {})
const { mutate: forkPipeline } = useConvexMutation(api.pipelines.fork)
const toast = useToast()

const forking = ref<string | null>(null)

async function fork(p: any) {
  forking.value = p._id
  try {
    const newSlug = `${p.slug}-copy-${Date.now().toString(36)}`
    await forkPipeline({
      pipelineId: p._id,
      newName: `${p.name} (Copy)`,
      newSlug: newSlug,
    })
    toast.success('Pipeline forked successfully!')
  } catch (e: any) {
    toast.error(e.message || 'Failed to fork pipeline')
  } finally {
    forking.value = null
  }
}
</script>

<template>
  <div>
    <VPageHeader title="Pipeline Templates" description="Content production pipeline templates and custom forks" />

    <div v-if="loading" class="text-gray-500">Loading pipelines...</div>

    <VEmptyState
      v-else-if="!pipelines?.length"
      icon="i-heroicons-arrow-path-rounded-square"
      title="No pipelines"
      description="Pipeline templates will appear here once created."
    />

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="p in pipelines"
        :key="p._id"
        class="bg-white rounded-lg shadow hover:shadow-md transition-shadow"
      >
        <div class="p-6">
          <div class="flex items-center justify-between mb-3">
            <NuxtLink
              :to="`/pipelines/${p.slug}`"
              class="font-semibold text-gray-900 hover:text-primary-600 transition-colors"
            >
              {{ p.name }}
            </NuxtLink>
            <span
              class="text-xs font-medium px-2 py-0.5 rounded-full"
              :class="p.type === 'preset'
                ? 'bg-blue-100 text-blue-700'
                : 'bg-purple-100 text-purple-700'"
            >
              {{ p.type }}
            </span>
          </div>

          <p v-if="p.description" class="text-sm text-gray-600 mb-4 line-clamp-2">
            {{ p.description }}
          </p>

          <!-- Step preview -->
          <div class="flex items-center gap-1 mb-4">
            <div
              v-for="(s, i) in (p.mainSteps || []).slice(0, 7)"
              :key="i"
              class="flex items-center"
            >
              <div
                class="w-6 h-6 rounded-full bg-gray-100 text-gray-500 flex items-center justify-center text-xs font-medium"
                :title="s.label"
              >
                {{ i + 1 }}
              </div>
              <div
                v-if="i < Math.min((p.mainSteps || []).length, 7) - 1"
                class="w-3 h-0.5 bg-gray-200"
              />
            </div>
            <span v-if="(p.mainSteps || []).length > 7" class="text-xs text-gray-400 ml-1">
              +{{ (p.mainSteps || []).length - 7 }}
            </span>
          </div>

          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3 text-xs text-gray-500">
              <span>{{ (p.mainSteps || []).length }} steps</span>
              <span v-if="p.parallelBranches?.length">
                {{ p.parallelBranches.length }} branches
              </span>
            </div>
            <div class="flex items-center gap-2">
              <NuxtLink
                :to="`/pipelines/${p.slug}`"
                class="text-xs text-primary-600 hover:text-primary-700 font-medium"
              >
                View
              </NuxtLink>
              <button
                class="text-xs text-gray-500 hover:text-gray-700 font-medium disabled:opacity-50"
                :disabled="forking === p._id"
                @click="fork(p)"
              >
                {{ forking === p._id ? 'Forking...' : 'Fork' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
