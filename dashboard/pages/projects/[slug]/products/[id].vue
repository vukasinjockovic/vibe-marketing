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
    <div v-if="loading" class="text-muted-foreground">Loading...</div>

    <template v-else-if="product">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <div class="flex items-center gap-3 flex-wrap">
            <h2 class="text-xl font-bold text-foreground">{{ product.name }}</h2>
            <VStatusBadge :status="product.status" />
          </div>
          <p class="text-sm text-muted-foreground mt-1">{{ product.description }}</p>
        </div>
        <div class="flex gap-2">
          <button
            class="px-3 py-1.5 text-sm border border-border rounded-md text-muted-foreground hover:bg-muted transition-colors"
            @click="showEdit = true"
          >
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
      <div class="flex gap-1 mb-6 border-b border-border">
        <button
          class="px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px"
          :class="activeTab === 'details' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'"
          @click="activeTab = 'details'"
        >
          Details
        </button>
        <button
          class="px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px"
          :class="activeTab === 'audiences' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'"
          @click="activeTab = 'audiences'"
        >
          Audiences ({{ focusGroups?.length || 0 }})
        </button>
      </div>

      <!-- Details Tab -->
      <div v-if="activeTab === 'details'" class="space-y-6">
        <!-- Context Section -->
        <div class="rounded-lg border bg-card shadow-sm p-6">
          <h3 class="font-semibold text-foreground mb-4">Product Context</h3>
          <div class="space-y-4">
            <div>
              <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">What It Is</p>
              <p class="text-sm text-foreground mt-1">{{ product.context?.whatItIs }}</p>
            </div>

            <div v-if="product.context?.features?.length">
              <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Features</p>
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
              <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Pricing</p>
              <p class="text-sm text-foreground mt-1">{{ product.context.pricing }}</p>
            </div>

            <div v-if="product.context?.usps?.length">
              <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Unique Selling Points</p>
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
              <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Target Market</p>
              <p class="text-sm text-foreground mt-1">{{ product.context?.targetMarket }}</p>
            </div>

            <div v-if="product.context?.productUrl">
              <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Product URL</p>
              <a :href="product.context.productUrl" target="_blank" class="text-sm text-primary hover:underline">
                {{ product.context.productUrl }}
              </a>
            </div>

            <div v-if="product.competitorsOverride?.length">
              <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Competitors <span class="text-primary/70">(product override)</span></p>
              <div class="flex flex-wrap gap-1.5 mt-1">
                <span
                  v-for="c in product.competitorsOverride"
                  :key="c"
                  class="inline-block bg-muted text-muted-foreground text-xs px-2 py-0.5 rounded-full"
                >
                  {{ c }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Brand Voice Override Section -->
        <div v-if="product.brandVoiceOverride" class="rounded-lg border bg-card shadow-sm p-6">
          <h3 class="font-semibold text-foreground mb-1">Brand Voice <span class="text-xs font-normal text-primary/70">(product override)</span></h3>
          <p class="text-xs text-muted-foreground mb-4">This overrides the project-level brand voice for this product.</p>
          <div class="space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Tone</p>
                <p class="text-sm text-foreground mt-1">{{ product.brandVoiceOverride.tone }}</p>
              </div>
              <div>
                <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Style</p>
                <p class="text-sm text-foreground mt-1">{{ product.brandVoiceOverride.style }}</p>
              </div>
            </div>

            <div v-if="product.brandVoiceOverride.vocabulary?.preferred?.length">
              <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Preferred Words</p>
              <div class="flex flex-wrap gap-1.5 mt-1">
                <span
                  v-for="w in product.brandVoiceOverride.vocabulary.preferred"
                  :key="w"
                  class="inline-block bg-green-50 text-green-700 text-xs px-2 py-0.5 rounded-full"
                >
                  {{ w }}
                </span>
              </div>
            </div>

            <div v-if="product.brandVoiceOverride.vocabulary?.avoided?.length">
              <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Avoided Words</p>
              <div class="flex flex-wrap gap-1.5 mt-1">
                <span
                  v-for="w in product.brandVoiceOverride.vocabulary.avoided"
                  :key="w"
                  class="inline-block bg-red-50 text-red-700 text-xs px-2 py-0.5 rounded-full"
                >
                  {{ w }}
                </span>
              </div>
            </div>

            <div v-if="product.brandVoiceOverride.examples">
              <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Examples</p>
              <p class="text-sm text-foreground mt-1">{{ product.brandVoiceOverride.examples }}</p>
            </div>

            <div v-if="product.brandVoiceOverride.notes">
              <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Notes</p>
              <p class="text-sm text-foreground mt-1">{{ product.brandVoiceOverride.notes }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Audiences Tab -->
      <div v-if="activeTab === 'audiences'">
        <VEmptyState
          v-if="!focusGroups?.length"
          title="No audiences"
          description="Add focus groups to define your target audiences."
        />
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <NuxtLink
            v-for="fg in focusGroups"
            :key="fg._id"
            :to="`/projects/${project?.slug}/products/${productId}/audiences`"
            class="rounded-lg border bg-card shadow-sm p-4 hover:shadow-md transition-shadow"
          >
            <div class="flex items-center justify-between mb-2">
              <h4 class="font-medium text-foreground">{{ fg.name }}</h4>
              <span class="text-xs text-muted-foreground">{{ fg.category }}</span>
            </div>
            <p class="text-xs text-muted-foreground mb-1">{{ fg.nickname }}</p>
            <p class="text-sm text-muted-foreground line-clamp-2">{{ fg.overview }}</p>
          </NuxtLink>
        </div>
      </div>

      <!-- Edit Modal -->
      <VModal v-model="showEdit" title="Edit Product" size="xl" persistent>
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
      title="Product not found"
      description="This product doesn't exist or has been archived."
    >
      <NuxtLink
        v-if="project"
        :to="`/projects/${project.slug}/products`"
        class="inline-block bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
      >
        Back to Products
      </NuxtLink>
    </VEmptyState>
  </div>
</template>
