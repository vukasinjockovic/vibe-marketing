<script setup lang="ts">
import { api } from '../../../convex/_generated/api'

const toast = useToast()
const { mutate: createProject, loading: saving } = useConvexMutation(api.projects.create)

const form = reactive({
  name: '',
  slug: '',
  description: '',
  color: '#0ea5e9',
  icon: '',
  website: '',
  competitors: [] as string[],
  // Brand Voice
  tone: '',
  style: '',
  preferred: [] as string[],
  avoided: [] as string[],
  examples: '',
  voiceNotes: '',
})

const colors = ['#0ea5e9', '#8b5cf6', '#f43f5e', '#10b981', '#f59e0b', '#6366f1']

watch(() => form.name, (name) => {
  form.slug = name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
})

const errors = reactive<Record<string, string>>({})

async function submit() {
  errors.name = form.name ? '' : 'Name is required'
  errors.slug = form.slug ? '' : 'Slug is required'
  if (errors.name || errors.slug) return

  const hasBrandVoice = form.tone || form.style
  try {
    await createProject({
      name: form.name,
      slug: form.slug,
      description: form.description || undefined,
      color: form.color,
      icon: form.icon || undefined,
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
    toast.success('Project created!')
    navigateTo(`/projects/${form.slug}`)
  } catch (e: any) {
    toast.error(e.message || 'Failed to create project')
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <VPageHeader title="New Project" description="Create a new marketing project" />

    <form class="rounded-lg border bg-card text-card-foreground shadow-sm p-6 space-y-6" @submit.prevent="submit">
      <!-- Basic Info -->
      <div>
        <h3 class="text-sm font-semibold text-foreground uppercase tracking-wide mb-4">Basic Info</h3>
        <div class="space-y-4">
          <VFormField label="Project Name" :error="errors.name" required>
            <input
              v-model="form.name"
              data-field="name"
              type="text"
              placeholder="Enter project name"
              class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
          </VFormField>

          <VFormField label="Slug" :error="errors.slug" required hint="URL-friendly identifier, auto-generated from name">
            <input
              v-model="form.slug"
              data-field="slug"
              type="text"
              placeholder="project-slug"
              class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
          </VFormField>

          <VFormField label="Description">
            <textarea
              v-model="form.description"
              data-field="description"
              placeholder="Brief description of this project"
              rows="3"
              class="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
          </VFormField>

          <VFormField label="Website">
            <input
              v-model="form.website"
              data-field="website"
              type="url"
              placeholder="https://yourproject.com"
              class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
          </VFormField>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
                data-field="icon"
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
      <div>
        <h3 class="text-sm font-semibold text-foreground uppercase tracking-wide mb-4">Competitors</h3>
        <VFormField label="Competitor Names / URLs">
          <VChipInput v-model="form.competitors" placeholder="Add competitor names or URLs" />
        </VFormField>
      </div>

      <!-- Brand Voice -->
      <div>
        <h3 class="text-sm font-semibold text-foreground uppercase tracking-wide mb-4">Brand Voice</h3>
        <p class="text-xs text-muted-foreground -mt-2 mb-4">Applies to all products in this project. Can be overridden per product.</p>
        <div class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <VFormField label="Tone">
              <textarea
                v-model="form.tone"
                data-field="tone"
                rows="2"
                placeholder="e.g. Motivational, Friendly"
                class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              />
            </VFormField>

            <VFormField label="Style">
              <textarea
                v-model="form.style"
                data-field="style"
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
              data-field="examples"
              placeholder="Example copy or voice samples"
              rows="2"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            />
          </VFormField>

          <VFormField label="Notes">
            <textarea
              v-model="form.voiceNotes"
              data-field="voiceNotes"
              placeholder="Additional brand voice notes"
              rows="2"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            />
          </VFormField>
        </div>
      </div>

      <div class="flex justify-end gap-3 pt-4 border-t">
        <NuxtLink
          to="/projects"
          class="px-4 py-2 text-sm text-muted-foreground hover:bg-muted rounded-md transition-colors"
        >
          Cancel
        </NuxtLink>
        <button
          type="submit"
          class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
          :disabled="saving"
        >
          {{ saving ? 'Creating...' : 'Create Project' }}
        </button>
      </div>
    </form>
  </div>
</template>
