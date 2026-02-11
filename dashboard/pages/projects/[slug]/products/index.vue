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
          class="bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
          @click="showCreate = true"
        >
          New Product
        </button>
      </template>
    </VPageHeader>

    <div v-if="loading" class="text-gray-500">Loading...</div>

    <VEmptyState
      v-else-if="!products?.length"
      icon="i-heroicons-cube"
      title="No products yet"
      description="Add your first product to start creating campaigns."
    >
      <button
        class="inline-block bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
        @click="showCreate = true"
      >
        Add Product
      </button>
    </VEmptyState>

    <div v-else class="grid grid-cols-3 gap-6">
      <NuxtLink
        v-for="product in products"
        :key="product._id"
        :to="`/projects/${project?.slug}/products/${product._id}`"
        class="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex items-center justify-between mb-2">
          <h3 class="font-semibold text-gray-900">{{ product.name }}</h3>
          <VStatusBadge :status="product.status" size="sm" />
        </div>
        <p class="text-sm text-gray-600 mb-3">{{ product.description }}</p>
        <div class="flex flex-wrap gap-1">
          <span
            v-for="usp in (product.context?.usps || []).slice(0, 3)"
            :key="usp"
            class="inline-block bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded-full"
          >
            {{ usp }}
          </span>
        </div>
      </NuxtLink>
    </div>

    <!-- Create Product Modal -->
    <VModal v-model="showCreate" title="New Product" size="xl">
      <ProductForm
        v-if="projectId"
        :project-id="projectId"
        @saved="onCreated"
      />
    </VModal>
  </div>
</template>
