<script setup lang="ts">
import { api } from '../../convex/_generated/api'

const props = defineProps<{
  projectId: string
  channel?: any // Pass existing channel for edit mode
}>()

const emit = defineEmits<{
  created: []
  saved: []
}>()

const isEdit = computed(() => !!props.channel)

const { mutate: createChannel } = useConvexMutation(api.channels.create)
const { mutate: updateChannel } = useConvexMutation(api.channels.update)
const toast = useToast()

const form = reactive({
  name: '',
  slug: '',
  platform: 'facebook' as 'facebook' | 'x' | 'linkedin' | 'tiktok' | 'instagram',
  description: '',
  username: '',
  pageUrl: '',
  postsPerDay: 3,
  timezone: 'Europe/London',
})

const platforms = [
  { value: 'facebook', label: 'Facebook' },
  { value: 'x', label: 'X (Twitter)' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'tiktok', label: 'TikTok' },
  { value: 'instagram', label: 'Instagram' },
]

// Populate form when editing
watch(() => props.channel, (ch) => {
  if (ch) {
    form.name = ch.name || ''
    form.slug = ch.slug || ''
    form.platform = ch.platform || 'facebook'
    form.description = ch.description || ''
    form.username = ch.platformConfig?.username || ''
    form.pageUrl = ch.platformConfig?.pageUrl || ''
    form.postsPerDay = ch.postingConfig?.postsPerDay || 3
    form.timezone = ch.postingConfig?.timezone || 'Europe/London'
  }
}, { immediate: true })

// Auto-generate slug from name (only in create mode)
watch(() => form.name, (name) => {
  if (!isEdit.value) {
    form.slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
  }
})

const submitting = ref(false)

async function submit() {
  if (!form.name || !form.slug) return
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateChannel({
        id: props.channel._id,
        name: form.name,
        description: form.description || undefined,
        platformConfig: {
          username: form.username || undefined,
          pageUrl: form.pageUrl || undefined,
        },
        postingConfig: {
          postsPerDay: form.postsPerDay,
          timezone: form.timezone,
        },
      })
      toast.success(`Channel "${form.name}" updated!`)
      emit('saved')
    } else {
      await createChannel({
        projectId: props.projectId as any,
        name: form.name,
        slug: form.slug,
        platform: form.platform,
        description: form.description || undefined,
        platformConfig: {
          username: form.username || undefined,
          pageUrl: form.pageUrl || undefined,
        },
        postingConfig: {
          postsPerDay: form.postsPerDay,
          timezone: form.timezone,
        },
      })
      toast.success(`Channel "${form.name}" created!`)
      emit('created')
    }
  } catch (e: any) {
    toast.error(e.message || `Failed to ${isEdit.value ? 'update' : 'create'} channel`)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <VFormField label="Platform">
      <select
        v-model="form.platform"
        :disabled="isEdit"
        class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm disabled:opacity-50"
      >
        <option v-for="p in platforms" :key="p.value" :value="p.value">{{ p.label }}</option>
      </select>
    </VFormField>

    <VFormField label="Channel Name" required>
      <input
        v-model="form.name"
        type="text"
        class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
        placeholder="Our Forever Stories"
      />
    </VFormField>

    <VFormField v-if="!isEdit" label="Slug">
      <input
        v-model="form.slug"
        type="text"
        class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-muted-foreground"
      />
    </VFormField>

    <VFormField label="Description">
      <textarea
        v-model="form.description"
        rows="2"
        class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
        placeholder="What this channel is about..."
      />
    </VFormField>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <VFormField label="Username">
        <input
          v-model="form.username"
          type="text"
          class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          placeholder="@ourforeverstories"
        />
      </VFormField>

      <VFormField label="Page URL">
        <input
          v-model="form.pageUrl"
          type="text"
          class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          placeholder="https://facebook.com/..."
        />
      </VFormField>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <VFormField label="Posts per Day">
        <input
          v-model.number="form.postsPerDay"
          type="number"
          min="1"
          max="10"
          class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
        />
      </VFormField>

      <VFormField label="Timezone">
        <input
          v-model="form.timezone"
          type="text"
          class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          placeholder="Europe/London"
        />
      </VFormField>
    </div>

    <div class="flex justify-end gap-2 pt-2">
      <button
        type="submit"
        :disabled="submitting || !form.name"
        class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
      >
        {{ submitting ? (isEdit ? 'Saving...' : 'Creating...') : (isEdit ? 'Save Changes' : 'Create Channel') }}
      </button>
    </div>
  </form>
</template>
