<script setup lang="ts">
import { api } from '../../convex/_generated/api'

const props = defineProps<{
  skill: any
  categories: any[]
  agents: any[]
}>()

const emit = defineEmits<{
  saved: []
  cancel: []
}>()

const { mutate: updateSkill } = useConvexMutation(api.skills.update)
const { mutate: updateAgentSkills } = useConvexMutation(api.agents.updateSkills)
const toast = useToast()

// Form state
const form = reactive({
  displayName: props.skill.displayName || '',
  tagline: props.skill.tagline || '',
  description: props.skill.description || '',
  dashboardDescription: props.skill.dashboardDescription || '',
  category: props.skill.category || '',
  type: props.skill.type || 'custom',
  isAutoActive: props.skill.isAutoActive || false,
  isCampaignSelectable: props.skill.isCampaignSelectable || false,
  subSelections: props.skill.subSelections || [],
})

// Agent assignments - which agents have this skill as static
const assignedAgentIds = ref<string[]>(
  props.agents
    .filter((a: any) => a.staticSkillIds?.includes(props.skill._id))
    .map((a: any) => a._id)
)

const saving = ref(false)

// Sub-selection management
function addSubSelection() {
  form.subSelections.push({ key: '', label: '', description: '' })
}

function removeSubSelection(index: number) {
  form.subSelections.splice(index, 1)
}

async function save() {
  saving.value = true
  try {
    // Update skill in Convex
    await updateSkill({
      id: props.skill._id,
      displayName: form.displayName,
      description: form.description,
      category: form.category,
      type: form.type as any,
      isAutoActive: form.isAutoActive,
      isCampaignSelectable: form.isCampaignSelectable,
      tagline: form.tagline || undefined,
      dashboardDescription: form.dashboardDescription || undefined,
      subSelections: form.subSelections.length > 0
        ? form.subSelections.filter((s: any) => s.key && s.label)
        : undefined,
    })

    // Write back to SKILL.md
    try {
      await $fetch('/api/skills/write-back', {
        method: 'POST',
        body: {
          skillId: props.skill._id,
          updatedFields: {
            displayName: form.displayName,
            description: form.description,
            category: form.category,
            type: form.type,
            isAutoActive: form.isAutoActive,
            isCampaignSelectable: form.isCampaignSelectable,
            tagline: form.tagline,
            dashboardDescription: form.dashboardDescription,
          },
        },
      })
    } catch {
      // Non-fatal: Convex is updated, file write-back failed
      toast.error('Saved to database but SKILL.md write-back failed')
    }

    // Update agent assignments
    const originalAgentIds = props.agents
      .filter((a: any) => a.staticSkillIds?.includes(props.skill._id))
      .map((a: any) => a._id)

    const added = assignedAgentIds.value.filter((id) => !originalAgentIds.includes(id))
    const removed = originalAgentIds.filter((id: string) => !assignedAgentIds.value.includes(id))

    for (const agentId of added) {
      const agent = props.agents.find((a: any) => a._id === agentId)
      if (agent) {
        const newIds = [...(agent.staticSkillIds || []), props.skill._id]
        await updateAgentSkills({ id: agentId as any, staticSkillIds: newIds })
      }
    }

    for (const agentId of removed) {
      const agent = props.agents.find((a: any) => a._id === agentId)
      if (agent) {
        const newIds = (agent.staticSkillIds || []).filter((id: string) => id !== props.skill._id)
        await updateAgentSkills({ id: agentId as any, staticSkillIds: newIds })
      }
    }

    emit('saved')
  } catch (e: any) {
    toast.error(e.message || 'Failed to save skill')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <form @submit.prevent="save" class="space-y-4">
    <div class="grid grid-cols-2 gap-4">
      <VFormField label="Display Name" required>
        <input
          v-model="form.displayName"
          type="text"
          required
          class="w-full rounded-md border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </VFormField>

      <VFormField label="Slug">
        <input
          :value="skill.slug"
          type="text"
          disabled
          class="w-full rounded-md border bg-muted px-3 py-2 text-sm text-muted-foreground"
        />
      </VFormField>
    </div>

    <VFormField label="Tagline" hint="Short one-liner for cards">
      <input
        v-model="form.tagline"
        type="text"
        class="w-full rounded-md border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
      />
    </VFormField>

    <VFormField label="Description" required>
      <textarea
        v-model="form.description"
        rows="3"
        required
        class="w-full rounded-md border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-y"
      />
    </VFormField>

    <VFormField label="Dashboard Description" hint="Shown on cards instead of full description">
      <textarea
        v-model="form.dashboardDescription"
        rows="2"
        class="w-full rounded-md border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-y"
      />
    </VFormField>

    <div class="grid grid-cols-2 gap-4">
      <VFormField label="Category" required>
        <select
          v-model="form.category"
          required
          class="w-full rounded-md border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option v-for="cat in categories" :key="cat.key" :value="cat.key">
            {{ cat.displayName }}
          </option>
        </select>
      </VFormField>

      <VFormField label="Type" required>
        <select
          v-model="form.type"
          required
          class="w-full rounded-md border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="mbook">Book (mbook)</option>
          <option value="procedure">Procedure (SOP)</option>
          <option value="community">Community</option>
          <option value="custom">Custom</option>
        </select>
      </VFormField>
    </div>

    <div class="flex items-center gap-6">
      <label class="flex items-center gap-2 cursor-pointer">
        <input type="checkbox" v-model="form.isAutoActive" class="rounded border-border" />
        <span class="text-sm text-foreground">Auto-active</span>
        <span class="text-xs text-muted-foreground">(always applied)</span>
      </label>
      <label class="flex items-center gap-2 cursor-pointer">
        <input type="checkbox" v-model="form.isCampaignSelectable" class="rounded border-border" />
        <span class="text-sm text-foreground">Campaign-selectable</span>
        <span class="text-xs text-muted-foreground">(available in Writing Strategy)</span>
      </label>
    </div>

    <!-- Sub-selections -->
    <div>
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-foreground">Sub-selections</span>
        <button type="button" class="text-xs text-primary hover:underline" @click="addSubSelection">+ Add</button>
      </div>
      <div v-if="form.subSelections.length === 0" class="text-xs text-muted-foreground">
        No sub-selections. Add specific principles, triggers, or tactics that can be individually toggled.
      </div>
      <div v-for="(sub, i) in form.subSelections" :key="i" class="flex items-center gap-2 mb-2">
        <input
          v-model="sub.key"
          placeholder="key"
          class="w-24 rounded-md border bg-background px-2 py-1 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
        />
        <input
          v-model="sub.label"
          placeholder="Label"
          class="flex-1 rounded-md border bg-background px-2 py-1 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
        />
        <input
          v-model="sub.description"
          placeholder="Description (optional)"
          class="flex-1 rounded-md border bg-background px-2 py-1 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
        />
        <button type="button" class="text-xs text-destructive hover:underline" @click="removeSubSelection(i)">Remove</button>
      </div>
    </div>

    <!-- Agent assignments -->
    <VFormField label="Assigned Agents" hint="Agents permanently using this skill (staticSkillIds)">
      <div class="flex flex-wrap gap-2">
        <label
          v-for="agent in agents"
          :key="agent._id"
          class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs cursor-pointer transition-colors"
          :class="assignedAgentIds.includes(agent._id)
            ? 'bg-primary/10 border-primary/30 text-primary'
            : 'border-border text-muted-foreground hover:border-primary/20'"
        >
          <input
            type="checkbox"
            :value="agent._id"
            v-model="assignedAgentIds"
            class="sr-only"
          />
          {{ agent.displayName }}
        </label>
      </div>
    </VFormField>

    <!-- Actions -->
    <div class="flex justify-end gap-3 pt-4 border-t">
      <button
        type="button"
        class="rounded-md px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        @click="emit('cancel')"
      >
        Cancel
      </button>
      <button
        type="submit"
        :disabled="saving"
        class="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
      >
        {{ saving ? 'Saving...' : 'Save Changes' }}
      </button>
    </div>
  </form>
</template>
