<script setup lang="ts">
import { api } from '../../../../../convex/_generated/api'
import { ArrowLeft, Trash2 } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const slug = computed(() => route.params.slug as string)
const resourceId = computed(() => route.params.id as string)

const { data: resource } = useConvexQuery(
  api.resources.get,
  computed(() => resourceId.value ? { id: resourceId.value as any } : 'skip'),
)

const { mutate: deleteResource } = useConvexMutation(api.resources.remove)

const showDeleteConfirm = ref(false)
const deleteError = ref('')

async function handleDelete() {
  if (!resource.value) return
  try {
    await deleteResource({
      id: resource.value._id,
      deletedBy: 'dashboard',
    })
    router.push(`/projects/${slug.value}/resources`)
  } catch (e: any) {
    deleteError.value = e.message || 'Failed to delete'
  }
}

function handleNavigate(id: string) {
  router.push(`/projects/${slug.value}/resources/${id}`)
}
</script>

<template>
  <div class="space-y-4">
    <!-- Back link + actions -->
    <div class="flex items-center justify-between">
      <NuxtLink
        :to="`/projects/${slug}/resources`"
        class="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft :size="14" />
        Back to Resources
      </NuxtLink>

      <button
        v-if="resource"
        class="flex items-center gap-1 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-md transition-colors"
        @click="showDeleteConfirm = true"
      >
        <Trash2 :size="14" />
        Delete
      </button>
    </div>

    <!-- Resource detail -->
    <div class="rounded-lg border bg-card shadow-sm">
      <ResourceDetailPanel
        :resource-id="resourceId"
        @navigate="handleNavigate"
        @close="router.push(`/projects/${slug}/resources`)"
      />
    </div>

    <!-- Delete confirmation -->
    <Teleport to="body">
      <div
        v-if="showDeleteConfirm"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
        @click.self="showDeleteConfirm = false"
      >
        <div class="bg-card border rounded-lg shadow-lg p-6 max-w-sm w-full mx-4">
          <h3 class="text-lg font-semibold text-foreground mb-2">Delete Resource</h3>
          <p class="text-sm text-muted-foreground mb-4">
            Are you sure you want to delete "{{ resource?.title }}"? This action cannot be undone.
          </p>
          <p v-if="deleteError" class="text-sm text-red-600 mb-3">{{ deleteError }}</p>
          <div class="flex justify-end gap-2">
            <button
              class="px-3 py-1.5 text-sm rounded-md border hover:bg-muted transition-colors"
              @click="showDeleteConfirm = false"
            >
              Cancel
            </button>
            <button
              class="px-3 py-1.5 text-sm rounded-md bg-red-600 text-white hover:bg-red-700 transition-colors"
              @click="handleDelete"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
