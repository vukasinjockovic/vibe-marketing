<script setup lang="ts">
import { api } from '../../convex/_generated/api'
import { ChevronDown } from 'lucide-vue-next'

const props = defineProps<{
  projectId: string
  productId: string
  focusGroup?: any
}>()

const emit = defineEmits<{
  saved: []
}>()

const toast = useToast()
const { mutate: createFocusGroup, loading: createLoading } = useConvexMutation(api.focusGroups.create)
const { mutate: updateFocusGroup, loading: updateLoading } = useConvexMutation(api.focusGroups.update)

const saving = computed(() => createLoading.value || updateLoading.value)
const isEdit = computed(() => !!props.focusGroup)

// Accordion state: track which sections are open
const openSections = ref(new Set<string>(['basic']))

function toggleSection(key: string) {
  if (openSections.value.has(key)) {
    if (key !== 'basic') openSections.value.delete(key)
  } else {
    openSections.value.add(key)
  }
}

function isSectionOpen(key: string) {
  return openSections.value.has(key)
}

// Form state
const form = reactive({
  // Basic
  name: props.focusGroup?.name || '',
  nickname: props.focusGroup?.nickname || '',
  number: props.focusGroup?.number || 1,
  category: props.focusGroup?.category || 'fitness',
  overview: props.focusGroup?.overview || '',
  source: props.focusGroup?.source || 'manual',
  transformationPromise: props.focusGroup?.transformationPromise || '',
  // Demographics
  ageRange: props.focusGroup?.demographics?.ageRange || '',
  gender: props.focusGroup?.demographics?.gender || '',
  income: props.focusGroup?.demographics?.income || '',
  lifestyle: props.focusGroup?.demographics?.lifestyle || '',
  triggers: [...(props.focusGroup?.demographics?.triggers || [])],
  // Psychographics
  psychValues: [...(props.focusGroup?.psychographics?.values || [])],
  psychBeliefs: [...(props.focusGroup?.psychographics?.beliefs || [])],
  psychLifestyle: props.focusGroup?.psychographics?.lifestyle || '',
  identity: props.focusGroup?.psychographics?.identity || '',
  // Language & Hooks
  coreDesires: [...(props.focusGroup?.coreDesires || [])],
  painPoints: [...(props.focusGroup?.painPoints || [])],
  fears: [...(props.focusGroup?.fears || [])],
  beliefs: [...(props.focusGroup?.beliefs || [])],
  objections: [...(props.focusGroup?.objections || [])],
  emotionalTriggers: [...(props.focusGroup?.emotionalTriggers || [])],
  languagePatterns: [...(props.focusGroup?.languagePatterns || [])],
  ebookAngles: [...(props.focusGroup?.ebookAngles || [])],
  marketingHooks: [...(props.focusGroup?.marketingHooks || [])],
})

const errors = reactive<Record<string, string>>({})

const categories = ['fitness', 'health', 'wealth', 'relationships']
const sources: Array<'uploaded' | 'researched' | 'manual'> = ['uploaded', 'researched', 'manual']

function validate(): boolean {
  errors.name = form.name ? '' : 'Name is required'
  errors.nickname = form.nickname ? '' : 'Nickname is required'
  errors.overview = form.overview ? '' : 'Overview is required'
  errors.transformationPromise = form.transformationPromise ? '' : 'Required'
  errors.ageRange = form.ageRange ? '' : 'Required'
  errors.gender = form.gender ? '' : 'Required'
  errors.income = form.income ? '' : 'Required'
  errors.lifestyle = form.lifestyle ? '' : 'Required'
  errors.psychLifestyle = form.psychLifestyle ? '' : 'Required'
  errors.identity = form.identity ? '' : 'Required'
  return !Object.values(errors).some(e => !!e)
}

async function submit() {
  if (!validate()) {
    // Open sections with errors
    if (errors.ageRange || errors.gender || errors.income || errors.lifestyle) {
      openSections.value.add('demographics')
    }
    if (errors.psychLifestyle || errors.identity) {
      openSections.value.add('psychographics')
    }
    return
  }

  try {
    if (isEdit.value) {
      await updateFocusGroup({
        id: props.focusGroup._id,
        name: form.name,
        nickname: form.nickname,
        category: form.category,
        overview: form.overview,
        transformationPromise: form.transformationPromise,
        demographics: {
          ageRange: form.ageRange,
          gender: form.gender,
          income: form.income,
          lifestyle: form.lifestyle,
          triggers: form.triggers,
        },
        psychographics: {
          values: form.psychValues,
          beliefs: form.psychBeliefs,
          lifestyle: form.psychLifestyle,
          identity: form.identity,
        },
        coreDesires: form.coreDesires,
        painPoints: form.painPoints,
        fears: form.fears,
        beliefs: form.beliefs,
        objections: form.objections,
        emotionalTriggers: form.emotionalTriggers,
        languagePatterns: form.languagePatterns,
        ebookAngles: form.ebookAngles,
        marketingHooks: form.marketingHooks,
      })
    } else {
      await createFocusGroup({
        projectId: props.projectId as any,
        productId: props.productId as any,
        number: form.number,
        name: form.name,
        nickname: form.nickname,
        category: form.category,
        overview: form.overview,
        source: form.source as 'uploaded' | 'researched' | 'manual',
        transformationPromise: form.transformationPromise,
        demographics: {
          ageRange: form.ageRange,
          gender: form.gender,
          income: form.income,
          lifestyle: form.lifestyle,
          triggers: form.triggers,
        },
        psychographics: {
          values: form.psychValues,
          beliefs: form.psychBeliefs,
          lifestyle: form.psychLifestyle,
          identity: form.identity,
        },
        coreDesires: form.coreDesires,
        painPoints: form.painPoints,
        fears: form.fears,
        beliefs: form.beliefs,
        objections: form.objections,
        emotionalTriggers: form.emotionalTriggers,
        languagePatterns: form.languagePatterns,
        ebookAngles: form.ebookAngles,
        marketingHooks: form.marketingHooks,
      })
    }
    emit('saved')
  } catch (e: any) {
    toast.error(e.message || 'Failed to save focus group')
  }
}

const sections = [
  { key: 'basic', label: 'Basic Info' },
  { key: 'demographics', label: 'Demographics' },
  { key: 'psychographics', label: 'Psychographics' },
  { key: 'language', label: 'Language & Hooks' },
]
</script>

<template>
  <form class="space-y-2" @submit.prevent="submit">
    <!-- Accordion sections -->
    <div v-for="section in sections" :key="section.key" class="border border-border rounded-lg overflow-hidden">
      <button
        type="button"
        data-section
        class="w-full flex items-center justify-between px-4 py-3 bg-muted/50 hover:bg-muted transition-colors cursor-pointer"
        @click="toggleSection(section.key)"
      >
        <span class="text-sm font-semibold text-foreground">{{ section.label }}</span>
        <ChevronDown
          class="w-4 h-4 text-muted-foreground/60 transition-transform"
          :class="{ 'rotate-180': isSectionOpen(section.key) }"
        />
      </button>

      <!-- Basic Info -->
      <div v-if="section.key === 'basic' && isSectionOpen('basic')" class="p-4 space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <VFormField label="Name" :error="errors.name" required>
            <input
              v-model="form.name"
              data-field="name"
              type="text"
              placeholder="Focus group name"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            />
          </VFormField>

          <VFormField label="Nickname" :error="errors.nickname" required>
            <input
              v-model="form.nickname"
              data-field="nickname"
              type="text"
              placeholder="Short identifier"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            />
          </VFormField>
        </div>

        <div class="grid grid-cols-3 gap-4">
          <VFormField label="Number">
            <input
              v-model.number="form.number"
              data-field="number"
              type="number"
              min="1"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            />
          </VFormField>

          <VFormField label="Category">
            <select
              v-model="form.category"
              data-field="category"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            >
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </VFormField>

          <VFormField label="Source">
            <select
              v-model="form.source"
              data-field="source"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            >
              <option v-for="src in sources" :key="src" :value="src">{{ src }}</option>
            </select>
          </VFormField>
        </div>

        <VFormField label="Overview" :error="errors.overview" required>
          <textarea
            v-model="form.overview"
            data-field="overview"
            placeholder="Describe this focus group"
            rows="3"
            class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          />
        </VFormField>

        <VFormField label="Transformation Promise" :error="errors.transformationPromise" required>
          <input
            v-model="form.transformationPromise"
            data-field="transformationPromise"
            type="text"
            placeholder="e.g. From novice to advanced lifter in 12 weeks"
            class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          />
        </VFormField>
      </div>

      <!-- Demographics -->
      <div v-if="section.key === 'demographics' && isSectionOpen('demographics')" class="p-4 space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <VFormField label="Age Range" :error="errors.ageRange" required>
            <input
              v-model="form.ageRange"
              data-field="ageRange"
              type="text"
              placeholder="e.g. 25-40"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            />
          </VFormField>

          <VFormField label="Gender" :error="errors.gender" required>
            <input
              v-model="form.gender"
              data-field="gender"
              type="text"
              placeholder="e.g. Male, Female, All"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            />
          </VFormField>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <VFormField label="Income" :error="errors.income" required>
            <input
              v-model="form.income"
              data-field="income"
              type="text"
              placeholder="e.g. $50k-80k"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            />
          </VFormField>

          <VFormField label="Lifestyle" :error="errors.lifestyle" required>
            <input
              v-model="form.lifestyle"
              data-field="demographicsLifestyle"
              type="text"
              placeholder="e.g. Active, Sedentary"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            />
          </VFormField>
        </div>

        <VFormField label="Triggers">
          <VChipInput v-model="form.triggers" placeholder="Add purchase triggers" />
        </VFormField>
      </div>

      <!-- Psychographics -->
      <div v-if="section.key === 'psychographics' && isSectionOpen('psychographics')" class="p-4 space-y-4">
        <VFormField label="Values">
          <VChipInput v-model="form.psychValues" placeholder="Add values" />
        </VFormField>

        <VFormField label="Beliefs">
          <VChipInput v-model="form.psychBeliefs" placeholder="Add beliefs" />
        </VFormField>

        <div class="grid grid-cols-2 gap-4">
          <VFormField label="Lifestyle" :error="errors.psychLifestyle" required>
            <input
              v-model="form.psychLifestyle"
              data-field="psychLifestyle"
              type="text"
              placeholder="e.g. Gym 5x/week"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            />
          </VFormField>

          <VFormField label="Identity" :error="errors.identity" required>
            <input
              v-model="form.identity"
              data-field="identity"
              type="text"
              placeholder="e.g. Athlete, Yogi"
              class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            />
          </VFormField>
        </div>
      </div>

      <!-- Language & Hooks -->
      <div v-if="section.key === 'language' && isSectionOpen('language')" class="p-4 space-y-4">
        <VFormField label="Core Desires">
          <VChipInput v-model="form.coreDesires" placeholder="Add core desires" />
        </VFormField>

        <VFormField label="Pain Points">
          <VChipInput v-model="form.painPoints" placeholder="Add pain points" />
        </VFormField>

        <VFormField label="Fears">
          <VChipInput v-model="form.fears" placeholder="Add fears" />
        </VFormField>

        <VFormField label="Beliefs">
          <VChipInput v-model="form.beliefs" placeholder="Add beliefs" />
        </VFormField>

        <VFormField label="Objections">
          <VChipInput v-model="form.objections" placeholder="Add common objections" />
        </VFormField>

        <VFormField label="Emotional Triggers">
          <VChipInput v-model="form.emotionalTriggers" placeholder="Add emotional triggers" />
        </VFormField>

        <VFormField label="Language Patterns">
          <VChipInput v-model="form.languagePatterns" placeholder="Add phrases they use" />
        </VFormField>

        <VFormField label="Ebook Angles">
          <VChipInput v-model="form.ebookAngles" placeholder="Add ebook angles" />
        </VFormField>

        <VFormField label="Marketing Hooks">
          <VChipInput v-model="form.marketingHooks" placeholder="Add marketing hooks" />
        </VFormField>
      </div>
    </div>

    <!-- Submit -->
    <div class="flex justify-end gap-3 pt-4">
      <button
        type="submit"
        class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
        :disabled="saving"
      >
        {{ saving ? 'Saving...' : (isEdit ? 'Update Focus Group' : 'Create Focus Group') }}
      </button>
    </div>
  </form>
</template>
