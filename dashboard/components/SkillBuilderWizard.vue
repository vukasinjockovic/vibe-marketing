<script setup lang="ts">
import { Upload, FileText, Settings, Eye, Loader2, X, Check } from 'lucide-vue-next'
import { api } from '../../convex/_generated/api'

const props = defineProps<{
  categories: any[]
}>()

const emit = defineEmits<{
  close: []
}>()

const toast = useToast()

// Wizard step
const step = ref(1)
const totalSteps = 4

// Step 1: Sources
const uploadedFiles = ref<{ name: string; path: string; size: number }[]>([])
const uploading = ref(false)

async function handleFileUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return

  uploading.value = true
  const buildId = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 15)
  form.buildId = buildId

  for (const file of Array.from(input.files)) {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('targetDir', `.claude/skill-builds/${buildId}/sources`)

      const result = await $fetch('/api/file-upload', {
        method: 'POST',
        body: formData,
      })
      uploadedFiles.value.push({
        name: file.name,
        path: (result as any).path || `.claude/skill-builds/${buildId}/sources/${file.name}`,
        size: file.size,
      })
    } catch (e: any) {
      toast.error(`Upload failed: ${file.name} — ${e.message}`)
    }
  }
  uploading.value = false
  input.value = ''
}

function removeFile(index: number) {
  uploadedFiles.value.splice(index, 1)
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// Step 2: Configure
const form = reactive({
  buildId: '',
  skillName: '',
  author: '',
  targetLayer: '' as string,
  category: '' as string,
  type: 'mbook' as 'mbook' | 'procedure' | 'community' | 'custom',
})

// Auto-generate skill name
watch(() => [form.author, form.targetLayer], () => {
  if (form.author && form.type === 'mbook') {
    const authorSlug = form.author.toLowerCase().replace(/[^a-z0-9]/g, '')
    form.skillName = `mbook-${authorSlug}-skill`
  }
})

// Auto-fill category from layer
watch(() => form.targetLayer, (layer) => {
  const layerMap: Record<string, string> = {
    L1: 'L1_audience',
    L2: 'L2_offer',
    L3: 'L3_persuasion',
    L4: 'L4_craft',
  }
  if (layerMap[layer]) {
    form.category = layerMap[layer]
    form.type = 'mbook'
  }
})

// Step 3: Prompt
const promptTemplates: Record<string, { label: string; template: string }> = {
  mbook: {
    label: 'Extract marketing book frameworks',
    template: `You are building a skill from a marketing book. Read all source files in .claude/skill-builds/{build_id}/sources/.

Extract:
1. Core frameworks, models, and mental models
2. Step-by-step processes and decision trees
3. Key principles with examples
4. Application rules (when to use, when not to)

Create a SKILL.md at .claude/skills/{skill_name}/SKILL.md following the mbook skill format:
- YAML frontmatter with: displayName, description, tagline, category, type: mbook, isAutoActive, isCampaignSelectable
- Decision routing logic (if applicable)
- Framework details with actionable instructions
- Examples of application to marketing copy

The skill should be usable by an AI writing agent to improve marketing content.`,
  },
  cro: {
    label: 'Create CRO optimization skill',
    template: `Read the source files and create a CRO optimization skill.

Create .claude/skills/{skill_name}/SKILL.md with:
- Conversion optimization frameworks
- Testing hypotheses templates
- Element-by-element optimization checklist
- Before/after examples`,
  },
  procedure: {
    label: 'Create procedure SOP from docs',
    template: `Read the source files and create a standard operating procedure (SOP) skill.

Create .claude/skills/{skill_name}/SKILL.md with:
- Step-by-step workflow
- Decision points and branching logic
- Quality checks and validation rules
- Output format specifications`,
  },
  custom: {
    label: 'Custom (blank)',
    template: `Read all source files in .claude/skill-builds/{build_id}/sources/.

Create a skill at .claude/skills/{skill_name}/SKILL.md.

[Describe what the skill should do, what frameworks to extract, and how agents should use it.]`,
  },
}

const selectedTemplate = ref('mbook')
const prompt = ref(promptTemplates.mbook.template)

watch(selectedTemplate, (key) => {
  prompt.value = promptTemplates[key]?.template || ''
})

// Step 4: Submit
const submitting = ref(false)
const submitted = ref(false)

function resolvedPrompt(): string {
  return prompt.value
    .replace(/\{build_id\}/g, form.buildId)
    .replace(/\{skill_name\}/g, form.skillName)
    .replace(/\{target_layer\}/g, form.targetLayer)
}

async function submit() {
  submitting.value = true
  try {
    // Create a dispatch request for the skill-builder agent
    await $fetch('/api/dispatch', {
      method: 'POST',
      body: {
        agent: 'skill-builder',
        prompt: resolvedPrompt(),
        metadata: {
          buildId: form.buildId,
          skillName: form.skillName,
          category: form.category,
          type: form.type,
          sourceCount: uploadedFiles.value.length,
        },
      },
    })
    submitted.value = true
    toast.success('Skill build dispatched! Check Tasks for progress.')
  } catch (e: any) {
    toast.error(e.message || 'Failed to dispatch skill build')
  } finally {
    submitting.value = false
  }
}

function canProceed(): boolean {
  switch (step.value) {
    case 1: return uploadedFiles.value.length > 0
    case 2: return !!form.skillName && !!form.category
    case 3: return prompt.value.trim().length > 20
    case 4: return true
    default: return false
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Step indicator -->
    <div class="flex items-center gap-2 mb-6">
      <template v-for="s in totalSteps" :key="s">
        <div
          class="flex items-center justify-center w-8 h-8 rounded-full text-xs font-medium transition-colors"
          :class="s === step
            ? 'bg-primary text-primary-foreground'
            : s < step
              ? 'bg-primary/20 text-primary'
              : 'bg-muted text-muted-foreground'"
        >
          <Check v-if="s < step" :size="14" />
          <span v-else>{{ s }}</span>
        </div>
        <div v-if="s < totalSteps" class="flex-1 h-px" :class="s < step ? 'bg-primary/40' : 'bg-border'" />
      </template>
    </div>

    <!-- Step 1: Upload Sources -->
    <div v-if="step === 1">
      <h3 class="text-sm font-semibold text-foreground mb-1">Upload Source Files</h3>
      <p class="text-xs text-muted-foreground mb-4">Upload ebooks, PDFs, markdown, or text files to extract skill frameworks from.</p>

      <label
        class="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer hover:border-primary/50 transition-colors"
        :class="uploading ? 'opacity-50 pointer-events-none' : 'border-border'"
      >
        <div class="flex flex-col items-center gap-2 text-muted-foreground">
          <Upload v-if="!uploading" :size="24" />
          <Loader2 v-else :size="24" class="animate-spin" />
          <span class="text-sm">{{ uploading ? 'Uploading...' : 'Click to upload or drag files here' }}</span>
          <span class="text-xs">Supports .epub, .pdf, .md, .txt</span>
        </div>
        <input type="file" class="hidden" multiple accept=".epub,.pdf,.md,.txt,.json" @change="handleFileUpload" />
      </label>

      <div v-if="uploadedFiles.length" class="mt-4 space-y-2">
        <div
          v-for="(file, i) in uploadedFiles"
          :key="i"
          class="flex items-center justify-between rounded-md border bg-muted/50 px-3 py-2"
        >
          <div class="flex items-center gap-2 min-w-0">
            <FileText :size="14" class="text-muted-foreground shrink-0" />
            <span class="text-sm text-foreground truncate">{{ file.name }}</span>
            <span class="text-xs text-muted-foreground md:shrink-0">{{ formatSize(file.size) }}</span>
          </div>
          <button class="text-muted-foreground hover:text-destructive" @click="removeFile(i)">
            <X :size="14" />
          </button>
        </div>
      </div>
    </div>

    <!-- Step 2: Configure -->
    <div v-if="step === 2">
      <h3 class="text-sm font-semibold text-foreground mb-1">Configure Skill</h3>
      <p class="text-xs text-muted-foreground mb-4">Set the skill name, layer, and category.</p>

      <div class="space-y-4">
        <VFormField label="Skill Name" required hint="e.g. mbook-author-shortname">
          <input
            v-model="form.skillName"
            type="text"
            required
            placeholder="mbook-author-shortname"
            class="w-full rounded-md border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </VFormField>

        <VFormField label="Author" hint="For mbook skills">
          <input
            v-model="form.author"
            type="text"
            placeholder="e.g. Cialdini"
            class="w-full rounded-md border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </VFormField>

        <VFormField label="Target Layer">
          <div class="flex gap-3">
            <label
              v-for="layer in ['L1', 'L2', 'L3', 'L4', 'Other']"
              :key="layer"
              class="flex items-center gap-1.5 cursor-pointer"
            >
              <input
                type="radio"
                :value="layer"
                v-model="form.targetLayer"
                class="text-primary"
              />
              <span class="text-sm text-foreground">{{ layer }}</span>
            </label>
          </div>
        </VFormField>

        <VFormField label="Category" required>
          <select
            v-model="form.category"
            required
            class="w-full rounded-md border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="">Select category...</option>
            <option v-for="cat in categories" :key="cat.key" :value="cat.key">
              {{ cat.displayName }}
            </option>
          </select>
        </VFormField>

        <VFormField label="Type">
          <select
            v-model="form.type"
            class="w-full rounded-md border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="mbook">Book (mbook)</option>
            <option value="procedure">Procedure (SOP)</option>
            <option value="community">Community</option>
            <option value="custom">Custom</option>
          </select>
        </VFormField>
      </div>
    </div>

    <!-- Step 3: Prompt -->
    <div v-if="step === 3">
      <h3 class="text-sm font-semibold text-foreground mb-1">Build Prompt</h3>
      <p class="text-xs text-muted-foreground mb-4">Claude will use this prompt to read your files and create the skill.</p>

      <VFormField label="Template">
        <select
          v-model="selectedTemplate"
          class="w-full rounded-md border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option v-for="(tmpl, key) in promptTemplates" :key="key" :value="key">
            {{ tmpl.label }}
          </option>
        </select>
      </VFormField>

      <VFormField label="Prompt" required class="mt-4">
        <textarea
          v-model="prompt"
          rows="12"
          required
          class="w-full rounded-md border bg-background px-3 py-2 text-sm text-foreground font-mono focus:outline-none focus:ring-2 focus:ring-ring resize-y"
        />
      </VFormField>

      <p class="text-xs text-muted-foreground mt-2">
        Placeholders: <code class="bg-muted px-1 rounded">{build_id}</code>, <code class="bg-muted px-1 rounded">{skill_name}</code>, <code class="bg-muted px-1 rounded">{target_layer}</code>
      </p>
    </div>

    <!-- Step 4: Review -->
    <div v-if="step === 4">
      <h3 class="text-sm font-semibold text-foreground mb-1">Review & Submit</h3>
      <p class="text-xs text-muted-foreground mb-4">Confirm everything looks correct before building.</p>

      <div v-if="submitted" class="text-center py-8">
        <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-500/10 text-green-400 mb-3">
          <Check :size="24" />
        </div>
        <h3 class="text-lg font-semibold text-foreground">Build Dispatched!</h3>
        <p class="text-sm text-muted-foreground mt-1">The skill-builder agent will process your files. Check Tasks for progress.</p>
        <p class="text-sm text-muted-foreground mt-1">After completion, click "Sync Now" on the Skills page to import the new skill.</p>
        <button class="mt-4 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground" @click="emit('close')">
          Done
        </button>
      </div>

      <div v-else class="rounded-lg border bg-muted/30 p-4 space-y-3">
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span class="text-muted-foreground">Skill Name:</span>
            <span class="ml-2 text-foreground font-medium">{{ form.skillName }}</span>
          </div>
          <div>
            <span class="text-muted-foreground">Type:</span>
            <span class="ml-2 text-foreground font-medium">{{ form.type }}</span>
          </div>
          <div>
            <span class="text-muted-foreground">Category:</span>
            <span class="ml-2 text-foreground font-medium">{{ form.category }}</span>
          </div>
          <div>
            <span class="text-muted-foreground">Source Files:</span>
            <span class="ml-2 text-foreground font-medium">{{ uploadedFiles.length }}</span>
          </div>
        </div>
        <div>
          <span class="text-xs text-muted-foreground">Prompt preview:</span>
          <pre class="mt-1 text-xs text-foreground font-mono bg-muted rounded p-2 max-h-32 overflow-y-auto whitespace-pre-wrap">{{ resolvedPrompt().slice(0, 500) }}{{ resolvedPrompt().length > 500 ? '...' : '' }}</pre>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <div v-if="!submitted" class="flex items-center justify-between pt-4 border-t">
      <button
        v-if="step > 1"
        type="button"
        class="rounded-md px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        @click="step--"
      >
        Back
      </button>
      <div v-else />

      <div class="flex gap-3">
        <button
          type="button"
          class="rounded-md px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          @click="emit('close')"
        >
          Cancel
        </button>
        <button
          v-if="step < totalSteps"
          type="button"
          :disabled="!canProceed()"
          class="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
          @click="step++"
        >
          Next
        </button>
        <button
          v-else
          type="button"
          :disabled="submitting"
          class="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
          @click="submit"
        >
          {{ submitting ? 'Building...' : 'Build Skill' }}
        </button>
      </div>
    </div>
  </div>
</template>
