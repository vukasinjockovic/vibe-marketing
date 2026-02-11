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
  try {
    await createProject({
      name: form.name,
      slug: form.slug,
      description: form.description || undefined,
      color: form.color,
      icon: form.icon || undefined,
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

    <form class="bg-white rounded-lg shadow p-6 space-y-6" @submit.prevent="submit">
      <VFormField label="Project Name" :error="errors.name" required>
        <input
          v-model="form.name"
          data-field="name"
          type="text"
          placeholder="Enter project name"
          class="w-full border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </VFormField>

      <VFormField label="Slug" :error="errors.slug" required hint="URL-friendly identifier, auto-generated from name">
        <input
          v-model="form.slug"
          data-field="slug"
          type="text"
          placeholder="project-slug"
          class="w-full border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </VFormField>

      <VFormField label="Description">
        <textarea
          v-model="form.description"
          data-field="description"
          placeholder="Brief description of this project"
          rows="3"
          class="w-full border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </VFormField>

      <VFormField label="Color">
        <div class="flex gap-3">
          <button
            v-for="c in colors"
            :key="c"
            type="button"
            class="w-8 h-8 rounded-full border-2 transition-all"
            :class="form.color === c ? 'border-gray-900 scale-110' : 'border-transparent'"
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
          class="w-20 border rounded-md px-3 py-2 text-sm text-center focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </VFormField>

      <div class="flex justify-end gap-3 pt-4 border-t">
        <NuxtLink
          to="/projects"
          class="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
        >
          Cancel
        </NuxtLink>
        <button
          type="submit"
          class="bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors disabled:opacity-50"
          :disabled="saving"
        >
          {{ saving ? 'Creating...' : 'Create Project' }}
        </button>
      </div>
    </form>
  </div>
</template>
