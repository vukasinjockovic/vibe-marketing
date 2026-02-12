<script setup lang="ts">
import { api } from '../../../../convex/_generated/api'

const { project } = useCurrentProject()
const toast = useToast()
const { mutate: updateProject, loading: saving } = useConvexMutation(api.projects.update)

const form = reactive({
  name: '',
  description: '',
  website: '',
  color: '#0ea5e9',
  icon: '',
  competitors: [] as string[],
  tone: '',
  style: '',
  preferred: [] as string[],
  avoided: [] as string[],
  examples: '',
  voiceNotes: '',
})

const colors = ['#0ea5e9', '#8b5cf6', '#f43f5e', '#10b981', '#f59e0b', '#6366f1']

// Populate form when project loads
watch(project, (p) => {
  if (!p) return
  form.name = p.name || ''
  form.description = p.description || ''
  form.website = p.website || ''
  form.color = p.appearance?.color || '#0ea5e9'
  form.icon = p.appearance?.icon || ''
  form.competitors = [...(p.competitors || [])]
  form.tone = p.brandVoice?.tone || ''
  form.style = p.brandVoice?.style || ''
  form.preferred = [...(p.brandVoice?.vocabulary?.preferred || [])]
  form.avoided = [...(p.brandVoice?.vocabulary?.avoided || [])]
  form.examples = p.brandVoice?.examples || ''
  form.voiceNotes = p.brandVoice?.notes || ''
}, { immediate: true })

const errors = reactive<Record<string, string>>({})

async function submit() {
  errors.name = form.name ? '' : 'Name is required'
  if (errors.name) return

  const hasBrandVoice = form.tone || form.style
  try {
    await updateProject({
      id: project.value!._id,
      name: form.name,
      description: form.description || undefined,
      icon: form.icon || undefined,
      color: form.color,
      website: form.website || undefined,
      competitors: form.competitors.length ? form.competitors : undefined,
      brandVoice: hasBrandVoice
        ? {
            tone: form.tone,
            style: form.style,
            vocabulary: {
              preferred: form.preferred,
              avoided: form.avoided,
            },
            examples: form.examples || undefined,
            notes: form.voiceNotes || undefined,
          }
        : undefined,
    })
    toast.success('Project updated!')
  } catch (e: any) {
    toast.error(e.message || 'Failed to update project')
  }
}
</script>

<template>
  <div class="max-w-2xl">
    <form class="space-y-6" @submit.prevent="submit">
      <!-- Basic Info -->
      <div class="rounded-lg border bg-card shadow-sm p-6">
        <h3 class="font-semibold text-foreground mb-4">General</h3>
        <div class="space-y-4">
          <VFormField label="Project Name" :error="errors.name" required>
            <input
              v-model="form.name"
              type="text"
              placeholder="Enter project name"
              class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
          </VFormField>

          <VFormField label="Description">
            <textarea
              v-model="form.description"
              placeholder="Brief description of this project"
              rows="3"
              class="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
          </VFormField>

          <VFormField label="Website">
            <input
              v-model="form.website"
              type="url"
              placeholder="https://yourproject.com"
              class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
          </VFormField>

          <div class="grid grid-cols-2 gap-4">
            <VFormField label="Color">
              <div class="flex gap-3">
                <button
                  v-for="c in colors"
                  :key="c"
                  type="button"
                  class="w-8 h-8 rounded-full border-2 transition-all"
                  :class="form.color === c ? 'border-foreground scale-110' : 'border-transparent'"
                  :style="{ backgroundColor: c }"
                  @click="form.color = c"
                />
              </div>
            </VFormField>

            <VFormField label="Icon" hint="Optional emoji or single character">
              <input
                v-model="form.icon"
                type="text"
                placeholder="e.g. rocket emoji"
                maxlength="2"
                class="flex h-10 w-20 rounded-md border border-input bg-background px-3 py-2 text-sm text-center ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
            </VFormField>
          </div>
        </div>
      </div>

      <!-- Competitors -->
      <div class="rounded-lg border bg-card shadow-sm p-6">
        <h3 class="font-semibold text-foreground mb-4">Competitors</h3>
        <VFormField label="Competitor Names / URLs">
          <VChipInput v-model="form.competitors" placeholder="Add competitor names or URLs" />
        </VFormField>
      </div>

      <!-- Brand Voice -->
      <div class="rounded-lg border bg-card shadow-sm p-6">
        <h3 class="font-semibold text-foreground mb-1">Brand Voice</h3>
        <p class="text-xs text-muted-foreground mb-4">Applies to all products. Can be overridden per product.</p>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <VFormField label="Tone">
              <textarea
                v-model="form.tone"
                rows="2"
                placeholder="e.g. Motivational, Friendly"
                class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              />
            </VFormField>

            <VFormField label="Style">
              <textarea
                v-model="form.style"
                rows="2"
                placeholder="e.g. Bold, Casual"
                class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              />
            </VFormField>
          </div>

          <VFormField label="Preferred Vocabulary">
            <VChipInput v-model="form.preferred" placeholder="Words to use" />
          </VFormField>

          <VFormField label="Avoided Vocabulary">
            <VChipInput v-model="form.avoided" placeholder="Words to avoid" />
          </VFormField>

          <VFormField label="Examples">
            <textarea
              v-model="form.examples"
              placeholder="Example copy or voice samples"
              rows="2"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            />
          </VFormField>

          <VFormField label="Notes">
            <textarea
              v-model="form.voiceNotes"
              placeholder="Additional brand voice notes"
              rows="2"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            />
          </VFormField>
        </div>
      </div>

      <!-- Save -->
      <div class="flex justify-end">
        <button
          type="submit"
          class="bg-primary text-primary-foreground px-6 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
          :disabled="saving"
        >
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </form>
  </div>
</template>
