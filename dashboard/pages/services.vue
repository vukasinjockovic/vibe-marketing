<script setup lang="ts">
import { api } from '../../convex/_generated/api'

const { data: categories, loading: catsLoading } = useConvexQuery(api.services.listCategories, {})

const servicesByCategory = ref<Record<string, any[]>>({})
const svcsLoading = ref(true)

const loading = computed(() => catsLoading.value || svcsLoading.value)

// When categories load/change, fetch services per category
const client = useConvex()
watch(categories, async (cats) => {
  if (!cats || cats.length === 0) {
    svcsLoading.value = false
    return
  }
  svcsLoading.value = true
  const map: Record<string, any[]> = {}
  try {
    for (const cat of cats) {
      map[cat._id] = await client.query(api.services.listByCategory, { categoryId: cat._id })
    }
    servicesByCategory.value = map
  } catch (e) {
    console.error('Failed to load services:', e)
  } finally {
    svcsLoading.value = false
  }
}, { immediate: true })

const { mutate: doToggle } = useConvexMutation(api.services.toggleActive)
const toast = useToast()

async function toggleActive(svc: any) {
  try {
    await doToggle({ id: svc._id })
    toast.success(`${svc.displayName} ${svc.isActive ? 'deactivated' : 'activated'}`)
    // Refetch services for this category
    const catServices = await client.query(api.services.listByCategory, { categoryId: svc.categoryId })
    servicesByCategory.value = { ...servicesByCategory.value, [svc.categoryId]: catServices }
  } catch (e: any) {
    toast.error(e.message || 'Failed to update service')
  }
}
</script>

<template>
  <div>
    <VPageHeader title="Service Registry" description="Manage external service integrations" />

    <div v-if="loading" class="text-muted-foreground">Loading...</div>

    <div v-else class="space-y-6">
      <div v-for="cat in categories" :key="cat._id" class="rounded-lg border bg-card text-card-foreground shadow-sm">
        <div class="px-6 py-4 border-b flex items-center gap-2">
          <span class="text-lg">{{ cat.icon }}</span>
          <h3 class="font-semibold text-foreground">{{ cat.displayName }}</h3>
          <span class="text-sm text-muted-foreground ml-2">{{ cat.description }}</span>
        </div>
        <div v-if="servicesByCategory[cat._id]?.length" class="divide-y divide-border">
          <div
            v-for="svc in servicesByCategory[cat._id]"
            :key="svc._id"
            class="px-6 py-3 flex items-center justify-between"
          >
            <div>
              <span class="font-medium text-foreground">{{ svc.displayName }}</span>
              <span class="text-sm text-muted-foreground ml-2">{{ svc.costInfo }}</span>
            </div>
            <div class="flex items-center gap-3">
              <VStatusBadge :status="svc.apiKeyConfigured ? 'configured' : 'needs_key'" />
              <button
                class="px-3 py-1 text-xs rounded-full font-medium transition-colors"
                :class="svc.isActive
                  ? 'bg-green-100 text-green-700 hover:bg-green-200'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'"
                @click="toggleActive(svc)"
              >
                {{ svc.isActive ? 'Active' : 'Inactive' }}
              </button>
            </div>
          </div>
        </div>
        <div v-else class="px-6 py-4 text-sm text-muted-foreground">
          No services configured for this category.
        </div>
      </div>
    </div>
  </div>
</template>
