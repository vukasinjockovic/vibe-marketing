<script setup lang="ts">
import { api } from '../../convex/_generated/api'

const props = defineProps<{
  modelValue: boolean
  projectId: string
  productId: string
  product: any
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  created: []
}>()

const toast = useToast()
const { mutate: createTask } = useConvexMutation(api.tasks.create)
const { data: pipeline } = useConvexQuery(
  api.pipelines.getBySlug,
  { slug: 'audience-discovery' },
)

const includeReddit = ref(true)
const includeCompetitors = ref(true)
const autoEnrich = ref(true)
const submitting = ref(false)

function close() {
  emit('update:modelValue', false)
}

async function submit() {
  submitting.value = true
  try {
    // Build pipeline steps from the pipeline template
    const pipelineSteps = pipeline.value?.mainSteps?.map((s: any) => ({
      step: s.order,
      status: s.order === 1 ? 'in_progress' : 'pending',
      agent: s.agent,
      model: s.model,
      description: s.description || s.label,
      outputDir: s.outputDir,
    })) || [
      { step: 1, status: 'in_progress', agent: 'vibe-audience-researcher', description: 'Research and discover audience segments' },
    ]

    await createTask({
      projectId: props.projectId as any,
      title: `Research audiences for ${props.product?.name || 'product'}`,
      description: `Discover target audience segments through research. Reddit: ${includeReddit.value}, Competitors: ${includeCompetitors.value}, Auto-enrich: ${autoEnrich.value}`,
      pipeline: pipelineSteps,
      priority: 'medium',
      createdBy: 'dashboard',
      contentType: 'audience_research',
      metadata: {
        productId: props.productId,
        includeReddit: includeReddit.value,
        includeCompetitors: includeCompetitors.value,
        autoEnrich: autoEnrich.value,
      },
    })

    toast.success('Audience research task created!')
    emit('created')
    close()
  } catch (e: any) {
    toast.error(e.message || 'Failed to create research task')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <VModal :model-value="modelValue" title="Research Audiences" size="lg" @update:model-value="$emit('update:modelValue', $event)">
    <div class="space-y-5">
      <!-- Product Context (read-only) -->
      <div class="bg-gray-50 rounded-lg p-4 space-y-3">
        <h4 class="text-sm font-semibold text-gray-900">Product Context</h4>
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span class="text-xs font-medium text-gray-500 uppercase">What It Is</span>
            <p class="text-gray-900 mt-0.5">{{ product?.context?.whatItIs || 'Not set' }}</p>
          </div>
          <div>
            <span class="text-xs font-medium text-gray-500 uppercase">Target Market</span>
            <p class="text-gray-900 mt-0.5">{{ product?.context?.targetMarket || 'Not set' }}</p>
          </div>
          <div>
            <span class="text-xs font-medium text-gray-500 uppercase">Website</span>
            <p class="text-gray-900 mt-0.5">{{ product?.context?.website || 'Not set' }}</p>
          </div>
          <div v-if="product?.context?.competitors?.length">
            <span class="text-xs font-medium text-gray-500 uppercase">Competitors</span>
            <div class="flex flex-wrap gap-1 mt-0.5">
              <span
                v-for="c in product.context.competitors"
                :key="c"
                class="bg-gray-200 text-gray-700 text-xs px-2 py-0.5 rounded-full"
              >
                {{ c }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Research Options -->
      <div class="space-y-3">
        <h4 class="text-sm font-semibold text-gray-900">Research Options</h4>
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            v-model="includeReddit"
            type="checkbox"
            class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span class="text-sm text-gray-700">Include Reddit research</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            v-model="includeCompetitors"
            type="checkbox"
            class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span class="text-sm text-gray-700">Include competitor scraping</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            v-model="autoEnrich"
            type="checkbox"
            class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span class="text-sm text-gray-700">Auto-enrich after discovery</span>
        </label>
      </div>
    </div>

    <template #footer>
      <button
        class="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
        @click="close"
      >
        Cancel
      </button>
      <button
        class="px-4 py-2 text-sm text-white bg-primary-600 hover:bg-primary-700 rounded-md transition-colors disabled:opacity-50"
        :disabled="submitting"
        @click="submit"
      >
        {{ submitting ? 'Starting...' : 'Start Research' }}
      </button>
    </template>
  </VModal>
</template>
