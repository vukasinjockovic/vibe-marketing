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
  website: props.product?.context?.website || '',
  competitors: [...(props.product?.context?.competitors || [])],
  // Brand Voice
  tone: props.product?.brandVoice?.tone || '',
  style: props.product?.brandVoice?.style || '',
  preferred: [...(props.product?.brandVoice?.vocabulary?.preferred || [])],
  avoided: [...(props.product?.brandVoice?.vocabulary?.avoided || [])],
  examples: props.product?.brandVoice?.examples || '',
  notes: props.product?.brandVoice?.notes || '',
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
  errors.tone = form.tone ? '' : 'Required'
  errors.style = form.style ? '' : 'Required'
  return !Object.values(errors).some(e => !!e)
}

async function submit() {
  if (!validate()) return
  try {
    if (isEdit.value) {
      await updateProduct({
        id: props.product._id,
        name: form.name,
        description: form.description,
        context: {
          whatItIs: form.whatItIs,
          features: form.features,
          pricing: form.pricing || undefined,
          usps: form.usps,
          targetMarket: form.targetMarket,
          website: form.website || undefined,
          competitors: form.competitors,
        },
        brandVoice: {
          tone: form.tone,
          style: form.style,
          vocabulary: {
            preferred: form.preferred,
            avoided: form.avoided,
          },
          examples: form.examples || undefined,
          notes: form.notes || undefined,
        },
      })
    } else {
      await createProduct({
        projectId: props.projectId as any,
        name: form.name,
        slug: form.slug,
        description: form.description,
        context: {
          whatItIs: form.whatItIs,
          features: form.features,
          pricing: form.pricing || undefined,
          usps: form.usps,
          targetMarket: form.targetMarket,
          website: form.website || undefined,
          competitors: form.competitors,
        },
        brandVoice: {
          tone: form.tone,
          style: form.style,
          vocabulary: {
            preferred: form.preferred,
            avoided: form.avoided,
          },
          examples: form.examples || undefined,
          notes: form.notes || undefined,
        },
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
          <input
            v-model="form.targetMarket"
            data-field="targetMarket"
            type="text"
            placeholder="Who is this for?"
            class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          />
        </VFormField>

        <VFormField label="Website">
          <input
            v-model="form.website"
            data-field="website"
            type="url"
            placeholder="https://..."
            class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          />
        </VFormField>

        <VFormField label="Competitors">
          <VChipInput v-model="form.competitors" placeholder="Add competitor names" />
        </VFormField>
      </div>
    </div>

    <!-- Brand Voice -->
    <div>
      <h3 class="text-sm font-semibold text-foreground uppercase tracking-wide mb-4">Brand Voice</h3>
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <VFormField label="Tone" :error="errors.tone" required>
            <input
              v-model="form.tone"
              data-field="tone"
              type="text"
              placeholder="e.g. Motivational, Friendly"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            />
          </VFormField>

          <VFormField label="Style" :error="errors.style" required>
            <input
              v-model="form.style"
              data-field="style"
              type="text"
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
