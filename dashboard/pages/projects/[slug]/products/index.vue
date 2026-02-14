<script setup lang="ts">
import { api } from '../../../../../convex/_generated/api'

const { project } = useCurrentProject()
const toast = useToast()
const projectId = computed(() => project.value?._id)

const { data: products, loading } = useConvexQuery(
  api.products.list,
  computed(() => projectId.value ? { projectId: projectId.value } : 'skip'),
)

const showCreate = ref(false)
const search = ref('')

const filteredProducts = computed(() => {
  if (!products.value) return []
  const q = search.value.toLowerCase().trim()
  if (!q) return products.value
  return products.value.filter((p: any) =>
    p.name?.toLowerCase().includes(q)
    || p.description?.toLowerCase().includes(q)
    || p.context?.usps?.some((u: string) => u.toLowerCase().includes(q))
    || p.context?.targetMarket?.toLowerCase().includes(q),
  )
})

function onCreated() {
  showCreate.value = false
  toast.success('Product created!')
}
</script>

<template>
  <div>
    <VPageHeader title="Products" description="Manage products for this project">
      <template #actions>
        <button
          class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
          @click="showCreate = true"
        >
          New Product
        </button>
      </template>
    </VPageHeader>

    <div v-if="loading" class="text-muted-foreground">Loading...</div>

    <VEmptyState
      v-else-if="!products?.length"
      title="No products yet"
      description="Add your first product to start creating campaigns."
    >
      <template #icon>
        <svg class="w-6 h-6 text-muted-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="m21 7.5-9-5.25L3 7.5m18 0-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" />
        </svg>
      </template>
      <button
        class="inline-block bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
        @click="showCreate = true"
      >
        Add Product
      </button>
    </VEmptyState>

    <template v-else>
      <!-- Search -->
      <div class="mb-4">
        <input
          v-model="search"
          type="text"
          placeholder="Search products..."
          class="flex h-9 w-full max-w-sm rounded-md border border-input bg-background px-3 py-1 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
        />
      </div>

      <div v-if="!filteredProducts.length" class="text-sm text-muted-foreground py-8 text-center">
        No products matching "{{ search }}"
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <NuxtLink
          v-for="product in filteredProducts"
          :key="product._id"
        :to="`/projects/${project?.slug}/products/${product._id}`"
        class="rounded-lg border bg-card shadow-sm p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex items-center justify-between mb-2">
          <h3 class="font-semibold text-foreground">{{ product.name }}</h3>
          <VStatusBadge :status="product.status" size="sm" />
        </div>
        <p class="text-sm text-muted-foreground mb-3">{{ product.description }}</p>
        <div class="flex flex-wrap gap-1">
          <span
            v-for="usp in (product.context?.usps || []).slice(0, 3)"
            :key="usp"
            class="inline-block bg-muted text-muted-foreground text-xs px-2 py-0.5 rounded-full"
          >
            {{ usp }}
          </span>
        </div>
      </NuxtLink>
      </div>
    </template>

    <!-- Create Product Modal -->
    <VModal v-model="showCreate" title="New Product" size="xl" persistent>
      <ProductForm
        v-if="projectId"
        :project-id="projectId"
        @saved="onCreated"
      />
    </VModal>
  </div>
</template>
