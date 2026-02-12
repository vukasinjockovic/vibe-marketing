<script setup lang="ts">
import { api } from '../../convex/_generated/api'

const props = defineProps<{
  projectId: string
  product?: any
}>()

const emit = defineEmits<{
  saved: []
}>()

const toast = useToast()
const { mutate: createProduct, loading: createLoading } = useConvexMutation(api.products.create)
const { mutate: updateProduct, loading: updateLoading } = useConvexMutation(api.products.update)

const saving = computed(() => createLoading.value || updateLoading.value)
const isEdit = computed(() => !!props.product)

const showOverrides = ref(
  !!(props.product?.brandVoiceOverride || props.product?.competitorsOverride?.length),
)

const form = reactive({
  name: props.product?.name || '',
  slug: props.product?.slug || '',
  description: props.product?.description || '',
  // Context
  whatItIs: props.product?.context?.whatItIs || '',
  features: [...(props.product?.context?.features || [])],
  pricing: props.product?.context?.pricing || '',
  usps: [...(props.product?.context?.usps || [])],
  targetMarket: props.product?.context?.targetMarket || '',
  productUrl: props.product?.context?.productUrl || '',
  // Overrides (optional — override project-level)
  competitorsOverride: [...(props.product?.competitorsOverride || [])],
  // Brand Voice Override
  tone: props.product?.brandVoiceOverride?.tone || '',
  style: props.product?.brandVoiceOverride?.style || '',
  preferred: [...(props.product?.brandVoiceOverride?.vocabulary?.preferred || [])],
  avoided: [...(props.product?.brandVoiceOverride?.vocabulary?.avoided || [])],
  examples: props.product?.brandVoiceOverride?.examples || '',
  notes: props.product?.brandVoiceOverride?.notes || '',
})

// Auto-generate slug from name (only in create mode)
watch(() => form.name, (name) => {
  if (!isEdit.value) {
    form.slug = name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
  }
})

const errors = reactive<Record<string, string>>({})

function validate(): boolean {
  errors.name = form.name ? '' : 'Name is required'
  errors.slug = form.slug ? '' : 'Slug is required'
  errors.description = form.description ? '' : 'Description is required'
  errors.whatItIs = form.whatItIs ? '' : 'Required'
  errors.targetMarket = form.targetMarket ? '' : 'Required'
  return !Object.values(errors).some(e => !!e)
}

function buildBrandVoiceOverride() {
  if (!form.tone && !form.style) return undefined
  return {
    tone: form.tone,
    style: form.style,
    vocabulary: {
      preferred: form.preferred,
      avoided: form.avoided,
    },
    examples: form.examples || undefined,
    notes: form.notes || undefined,
  }
}

async function submit() {
  if (!validate()) return
  try {
    const context = {
      whatItIs: form.whatItIs,
      features: form.features,
      pricing: form.pricing || undefined,
      usps: form.usps,
      targetMarket: form.targetMarket,
      productUrl: form.productUrl || undefined,
    }
    const competitorsOverride = form.competitorsOverride.length ? form.competitorsOverride : undefined
    const brandVoiceOverride = buildBrandVoiceOverride()

    if (isEdit.value) {
      await updateProduct({
        id: props.product._id,
        name: form.name,
        description: form.description,
        context,
        competitorsOverride,
        brandVoiceOverride,
      })
    } else {
      await createProduct({
        projectId: props.projectId as any,
        name: form.name,
        slug: form.slug,
        description: form.description,
        context,
        competitorsOverride,
        brandVoiceOverride,
      })
    }
    emit('saved')
  } catch (e: any) {
    toast.error(e.message || 'Failed to save product')
  }
}
</script>

<template>
  <form class="space-y-6" @submit.prevent="submit">
    <!-- Basic Info -->
    <div>
      <h3 class="text-sm font-semibold text-foreground uppercase tracking-wide mb-4">Basic Info</h3>
      <div class="space-y-4">
        <VFormField label="Product Name" :error="errors.name" required>
          <input
            v-model="form.name"
            data-field="name"
            type="text"
            placeholder="Enter product name"
            class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          />
        </VFormField>

        <VFormField v-if="!isEdit" label="Slug" :error="errors.slug" required hint="URL-friendly identifier">
          <input
            v-model="form.slug"
            data-field="slug"
            type="text"
            placeholder="product-slug"
            class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          />
        </VFormField>

        <VFormField label="Description" :error="errors.description" required>
          <textarea
            v-model="form.description"
            data-field="description"
            placeholder="Brief description of this product"
            rows="2"
            class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          />
        </VFormField>
      </div>
    </div>

    <!-- Context -->
    <div>
      <h3 class="text-sm font-semibold text-foreground uppercase tracking-wide mb-4">Context</h3>
      <div class="space-y-4">
        <VFormField label="What It Is" :error="errors.whatItIs" required>
          <textarea
            v-model="form.whatItIs"
            data-field="whatItIs"
            placeholder="Describe what this product is"
            rows="2"
            class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          />
        </VFormField>

        <VFormField label="Features">
          <VChipInput v-model="form.features" placeholder="Add features" />
        </VFormField>

        <VFormField label="Pricing">
          <input
            v-model="form.pricing"
            data-field="pricing"
            type="text"
            placeholder="e.g. $29/mo"
            class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          />
        </VFormField>

        <VFormField label="Unique Selling Points (USPs)">
          <VChipInput v-model="form.usps" placeholder="Add USPs" />
        </VFormField>

        <VFormField label="Target Market" :error="errors.targetMarket" required>
          <textarea
            v-model="form.targetMarket"
            data-field="targetMarket"
            rows="2"
            placeholder="Who is this for?"
            class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          />
        </VFormField>

        <VFormField label="Product URL" hint="Landing page or product link">
          <input
            v-model="form.productUrl"
            data-field="productUrl"
            type="url"
            placeholder="https://yoursite.com/product"
            class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          />
        </VFormField>
      </div>
    </div>

    <!-- Project-Level Overrides (collapsible) -->
    <div>
      <button
        type="button"
        class="flex items-center gap-2 text-sm font-semibold text-foreground uppercase tracking-wide"
        @click="showOverrides = !showOverrides"
      >
        <svg
          class="w-4 h-4 transition-transform"
          :class="showOverrides ? 'rotate-90' : ''"
          xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"
        >
          <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
        </svg>
        Project-Level Overrides
      </button>
      <p class="text-xs text-muted-foreground mt-1 mb-4">Only fill these if this product needs different competitors or brand voice than the project defaults.</p>

      <div v-if="showOverrides" class="space-y-6 pl-4 border-l-2 border-primary/20">
        <!-- Competitors Override -->
        <VFormField label="Competitors (overrides project-level)">
          <VChipInput v-model="form.competitorsOverride" placeholder="Add product-specific competitors" />
        </VFormField>

        <!-- Brand Voice Override -->
        <div>
          <h4 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">Brand Voice (overrides project-level)</h4>
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
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
                v-model="form.notes"
                data-field="notes"
                placeholder="Additional brand voice notes"
                rows="2"
                class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              />
            </VFormField>
          </div>
        </div>
      </div>
    </div>

    <!-- Submit -->
    <div class="flex justify-end gap-3 pt-4 border-t border-border">
      <button
        type="submit"
        class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
        :disabled="saving"
      >
        {{ saving ? 'Saving...' : (isEdit ? 'Update Product' : 'Create Product') }}
      </button>
    </div>
  </form>
</template>
