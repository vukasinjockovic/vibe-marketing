<script setup lang="ts">
import { api } from '../../../../../convex/_generated/api'

const route = useRoute()
const toast = useToast()
const { project } = useCurrentProject()

const productId = computed(() => route.params.id as string)

const { data: product, loading } = useConvexQuery(
  api.products.get,
  computed(() => productId.value ? { id: productId.value as any } : 'skip'),
)

const { data: focusGroups } = useConvexQuery(
  api.focusGroups.listByProduct,
  computed(() => productId.value ? { productId: productId.value as any } : 'skip'),
)

const { mutate: archiveProduct } = useConvexMutation(api.products.archive)

const showEdit = ref(false)
const showArchiveConfirm = ref(false)

const activeTab = ref<'details' | 'audiences'>('details')

function onSaved() {
  showEdit.value = false
  toast.success('Product updated!')
}

async function confirmArchive() {
  try {
    await archiveProduct({ id: productId.value as any })
    toast.success('Product archived')
    showArchiveConfirm.value = false
    navigateTo(`/projects/${project.value?.slug}/products`)
  } catch (e: any) {
    toast.error(e.message || 'Failed to archive')
  }
}
</script>

<template>
  <div>
    <div v-if="loading" class="text-gray-500">Loading...</div>

    <template v-else-if="product">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <div class="flex items-center gap-3">
            <h2 class="text-xl font-bold text-gray-900">{{ product.name }}</h2>
            <VStatusBadge :status="product.status" />
          </div>
          <p class="text-sm text-gray-500 mt-1">{{ product.description }}</p>
        </div>
        <div class="flex gap-2">
          <button
            class="px-3 py-1.5 text-sm border rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
            @click="showEdit = true"
          >
            <span class="i-heroicons-pencil-square text-sm mr-1" />
            Edit
          </button>
          <button
            class="px-3 py-1.5 text-sm border border-red-200 rounded-md text-red-600 hover:bg-red-50 transition-colors"
            @click="showArchiveConfirm = true"
          >
            Archive
          </button>
        </div>
      </div>

      <!-- Tab toggle -->
      <div class="flex gap-1 mb-6 border-b border-gray-200">
        <button
          class="px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px"
          :class="activeTab === 'details' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
          @click="activeTab = 'details'"
        >
          Details
        </button>
        <button
          class="px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px"
          :class="activeTab === 'audiences' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
          @click="activeTab = 'audiences'"
        >
          Audiences ({{ focusGroups?.length || 0 }})
        </button>
      </div>

      <!-- Details Tab -->
      <div v-if="activeTab === 'details'" class="space-y-6">
        <!-- Context Section -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="font-semibold text-gray-900 mb-4">Product Context</h3>
          <div class="space-y-4">
            <div>
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">What It Is</p>
              <p class="text-sm text-gray-900 mt-1">{{ product.context?.whatItIs }}</p>
            </div>

            <div v-if="product.context?.features?.length">
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Features</p>
              <div class="flex flex-wrap gap-1.5 mt-1">
                <span
                  v-for="f in product.context.features"
                  :key="f"
                  class="inline-block bg-blue-50 text-blue-700 text-xs px-2 py-0.5 rounded-full"
                >
                  {{ f }}
                </span>
              </div>
            </div>

            <div v-if="product.context?.pricing">
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Pricing</p>
              <p class="text-sm text-gray-900 mt-1">{{ product.context.pricing }}</p>
            </div>

            <div v-if="product.context?.usps?.length">
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Unique Selling Points</p>
              <div class="flex flex-wrap gap-1.5 mt-1">
                <span
                  v-for="u in product.context.usps"
                  :key="u"
                  class="inline-block bg-green-50 text-green-700 text-xs px-2 py-0.5 rounded-full"
                >
                  {{ u }}
                </span>
              </div>
            </div>

            <div>
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Target Market</p>
              <p class="text-sm text-gray-900 mt-1">{{ product.context?.targetMarket }}</p>
            </div>

            <div v-if="product.context?.website">
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Website</p>
              <a :href="product.context.website" target="_blank" class="text-sm text-primary-600 hover:underline">
                {{ product.context.website }}
              </a>
            </div>

            <div v-if="product.context?.competitors?.length">
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Competitors</p>
              <div class="flex flex-wrap gap-1.5 mt-1">
                <span
                  v-for="c in product.context.competitors"
                  :key="c"
                  class="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-0.5 rounded-full"
                >
                  {{ c }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Brand Voice Section -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="font-semibold text-gray-900 mb-4">Brand Voice</h3>
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Tone</p>
                <p class="text-sm text-gray-900 mt-1">{{ product.brandVoice?.tone }}</p>
              </div>
              <div>
                <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Style</p>
                <p class="text-sm text-gray-900 mt-1">{{ product.brandVoice?.style }}</p>
              </div>
            </div>

            <div v-if="product.brandVoice?.vocabulary?.preferred?.length">
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Preferred Words</p>
              <div class="flex flex-wrap gap-1.5 mt-1">
                <span
                  v-for="w in product.brandVoice.vocabulary.preferred"
                  :key="w"
                  class="inline-block bg-green-50 text-green-700 text-xs px-2 py-0.5 rounded-full"
                >
                  {{ w }}
                </span>
              </div>
            </div>

            <div v-if="product.brandVoice?.vocabulary?.avoided?.length">
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Avoided Words</p>
              <div class="flex flex-wrap gap-1.5 mt-1">
                <span
                  v-for="w in product.brandVoice.vocabulary.avoided"
                  :key="w"
                  class="inline-block bg-red-50 text-red-700 text-xs px-2 py-0.5 rounded-full"
                >
                  {{ w }}
                </span>
              </div>
            </div>

            <div v-if="product.brandVoice?.examples">
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Examples</p>
              <p class="text-sm text-gray-900 mt-1">{{ product.brandVoice.examples }}</p>
            </div>

            <div v-if="product.brandVoice?.notes">
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Notes</p>
              <p class="text-sm text-gray-900 mt-1">{{ product.brandVoice.notes }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Audiences Tab -->
      <div v-if="activeTab === 'audiences'">
        <VEmptyState
          v-if="!focusGroups?.length"
          icon="i-heroicons-user-group"
          title="No audiences"
          description="Add focus groups to define your target audiences."
        />
        <div v-else class="grid grid-cols-2 gap-4">
          <NuxtLink
            v-for="fg in focusGroups"
            :key="fg._id"
            :to="`/projects/${project?.slug}/products/${productId}/audiences`"
            class="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow"
          >
            <div class="flex items-center justify-between mb-2">
              <h4 class="font-medium text-gray-900">{{ fg.name }}</h4>
              <span class="text-xs text-gray-500">{{ fg.category }}</span>
            </div>
            <p class="text-xs text-gray-500 mb-1">{{ fg.nickname }}</p>
            <p class="text-sm text-gray-600 line-clamp-2">{{ fg.overview }}</p>
          </NuxtLink>
        </div>
      </div>

      <!-- Edit Modal -->
      <VModal v-model="showEdit" title="Edit Product" size="xl">
        <ProductForm
          :project-id="product.projectId"
          :product="product"
          @saved="onSaved"
        />
      </VModal>

      <!-- Archive Confirm -->
      <VConfirmDialog
        v-model="showArchiveConfirm"
        title="Archive Product"
        message="Are you sure you want to archive this product? This will hide it from active lists."
        confirm-label="Archive"
        confirm-class="bg-red-600 hover:bg-red-700"
        @confirm="confirmArchive"
      />
    </template>

    <VEmptyState
      v-else
      icon="i-heroicons-exclamation-triangle"
      title="Product not found"
      description="This product doesn't exist or has been archived."
    >
      <NuxtLink
        v-if="project"
        :to="`/projects/${project.slug}/products`"
        class="inline-block bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
      >
        Back to Products
      </NuxtLink>
    </VEmptyState>
  </div>
</template>
