<script setup lang="ts">
import { api } from '../../convex/_generated/api'
import { Settings, RotateCcw } from 'lucide-vue-next'

const props = defineProps<{
  campaignId?: string
  contentBatchId?: string
}>()

const { data: health } = useConvexQuery(
  api.services.getCampaignServiceHealth,
  computed(() => props.campaignId ? { campaignId: props.campaignId as any } : 'skip'),
)

const { data: overrides } = useConvexQuery(
  api.services.listChainOverrides,
  computed(() => {
    if (props.contentBatchId) return { contentBatchId: props.contentBatchId as any }
    if (props.campaignId) return { campaignId: props.campaignId as any }
    return 'skip'
  }),
)

const { mutate: doRemoveOverride } = useConvexMutation(api.services.removeChainOverride)
const toast = useToast()

const overallBadgeClass = computed(() => {
  switch (health.value?.overallStatus) {
    case 'ready': return 'bg-green-100 text-green-700'
    case 'degraded': return 'bg-yellow-100 text-yellow-700'
    case 'blocked': return 'bg-red-100 text-red-700'
    default: return 'bg-muted text-muted-foreground'
  }
})

async function removeOverride(id: string) {
  try {
    await doRemoveOverride({ id: id as any })
    toast.success('Override removed — reverting to global chain')
  } catch (e: any) {
    toast.error(e.message || 'Failed to remove override')
  }
}
</script>

<template>
  <div class="space-y-4">
    <!-- Overall status -->
    <div v-if="health" class="flex items-center gap-3">
      <span class="text-sm font-medium text-foreground">Pipeline Status:</span>
      <span class="px-2.5 py-1 text-xs font-semibold rounded-full uppercase" :class="overallBadgeClass">
        {{ health.overallStatus }}
      </span>
    </div>

    <!-- Agent breakdown -->
    <div v-if="health?.agents?.length" class="space-y-3">
      <div
        v-for="agent in health.agents"
        :key="agent.agentName"
        class="rounded-lg border bg-card p-4"
      >
        <div class="flex items-center justify-between mb-2">
          <span class="font-medium text-sm text-foreground">{{ agent.agentName }}</span>
          <VStatusBadge :status="agent.status" size="sm" />
        </div>

        <div class="space-y-1">
          <div
            v-for="cap in agent.capabilities"
            :key="cap.capability"
            class="flex items-center gap-2 text-xs"
          >
            <span class="text-muted-foreground w-32 truncate" :title="cap.capability">
              {{ cap.capability }}:
            </span>
            <span v-if="cap.providers.length > 0" class="text-foreground">
              {{ cap.providers.join(' → ') }}
            </span>
            <span v-else class="text-red-600 font-medium">
              No active provider!
            </span>
            <span v-if="!cap.required" class="text-muted-foreground/60 italic ml-1">(optional)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Active overrides -->
    <div v-if="overrides?.length" class="space-y-2">
      <h4 class="text-sm font-medium text-foreground">Active Overrides</h4>
      <div
        v-for="ov in overrides"
        :key="ov._id"
        class="flex items-center justify-between rounded border px-3 py-2 text-sm"
      >
        <span class="text-muted-foreground">
          {{ ov.categoryId }} — {{ ov.serviceChain.length }} services
        </span>
        <button
          class="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
          @click="removeOverride(ov._id)"
        >
          <RotateCcw class="h-3 w-3" />
          Reset
        </button>
      </div>
    </div>

    <!-- Empty -->
    <div v-if="!health" class="text-sm text-muted-foreground py-4">
      Loading service health...
    </div>
  </div>
</template>
