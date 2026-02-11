<script setup lang="ts">
import { api } from '../../../convex/_generated/api'
import { ArrowLeft, HardDriveDownload } from 'lucide-vue-next'

const route = useRoute()
const slug = computed(() => route.params.slug as string)

const { data: pipeline, loading } = useConvexQuery(
  api.pipelines.getBySlug,
  computed(() => slug.value ? { slug: slug.value } : 'skip'),
)

const { mutate: forkPipeline } = useConvexMutation(api.pipelines.fork)
const toast = useToast()
const forking = ref(false)

async function fork() {
  if (!pipeline.value) return
  forking.value = true
  try {
    const newSlug = `${pipeline.value.slug}-copy-${Date.now().toString(36)}`
    await forkPipeline({
      pipelineId: pipeline.value._id,
      newName: `${pipeline.value.name} (Copy)`,
      newSlug: newSlug,
    })
    toast.success('Pipeline forked!')
    navigateTo(`/pipelines/${newSlug}`)
  } catch (e: any) {
    toast.error(e.message || 'Failed to fork pipeline')
  } finally {
    forking.value = false
  }
}
</script>

<template>
  <div>
    <div v-if="loading" class="text-muted-foreground">Loading pipeline...</div>

    <div v-else-if="!pipeline" class="text-muted-foreground">Pipeline not found.</div>

    <template v-else>
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <div class="flex items-center gap-3">
            <NuxtLink
              to="/pipelines"
              class="text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft :size="18" />
            </NuxtLink>
            <h1 class="text-2xl font-bold text-foreground">{{ pipeline.name }}</h1>
            <span
              class="text-xs font-medium px-2 py-0.5 rounded-full"
              :class="pipeline.type === 'preset'
                ? 'bg-blue-100 text-blue-700'
                : 'bg-purple-100 text-purple-700'"
            >
              {{ pipeline.type }}
            </span>
          </div>
          <p v-if="pipeline.description" class="text-sm text-muted-foreground mt-1 ml-9">
            {{ pipeline.description }}
          </p>
        </div>
        <button
          class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
          :disabled="forking"
          @click="fork"
        >
          {{ forking ? 'Forking...' : 'Fork Pipeline' }}
        </button>
      </div>

      <!-- Summary cards -->
      <div class="grid grid-cols-3 gap-4 mb-8">
        <div class="rounded-lg border bg-card shadow-sm p-4">
          <h3 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">Main Steps</h3>
          <p class="text-2xl font-bold text-foreground">{{ pipeline.mainSteps?.length || 0 }}</p>
        </div>
        <div class="rounded-lg border bg-card shadow-sm p-4">
          <h3 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">Parallel Branches</h3>
          <p class="text-2xl font-bold text-foreground">{{ pipeline.parallelBranches?.length || 0 }}</p>
        </div>
        <div class="rounded-lg border bg-card shadow-sm p-4">
          <h3 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">On Complete</h3>
          <div class="flex gap-2 mt-1">
            <span
              v-if="pipeline.onComplete?.telegram"
              class="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded"
            >
              Telegram
            </span>
            <span
              v-if="pipeline.onComplete?.summary"
              class="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded"
            >
              Summary
            </span>
            <span
              v-if="pipeline.onComplete?.generateManifest"
              class="text-xs bg-purple-50 text-purple-700 px-2 py-0.5 rounded"
            >
              Manifest
            </span>
          </div>
        </div>
      </div>

      <!-- Main pipeline flow -->
      <div class="rounded-lg border bg-card shadow-sm p-6 mb-6">
        <h2 class="text-lg font-semibold text-foreground mb-6">Main Pipeline</h2>

        <div class="relative">
          <div
            v-for="(step, idx) in pipeline.mainSteps"
            :key="idx"
            class="flex items-start gap-4 pb-8 last:pb-0"
          >
            <!-- Timeline line -->
            <div class="flex flex-col items-center">
              <div class="w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center text-sm font-bold flex-shrink-0">
                {{ step.order ?? idx + 1 }}
              </div>
              <div
                v-if="idx < (pipeline.mainSteps?.length || 0) - 1"
                class="w-0.5 flex-1 bg-primary/20 mt-2 min-h-8"
              />
            </div>

            <!-- Step content -->
            <div class="flex-1 pt-1.5">
              <div class="flex items-center gap-3 mb-1">
                <h3 class="font-semibold text-foreground">{{ step.label }}</h3>
              </div>
              <p v-if="step.description" class="text-sm text-muted-foreground mb-2">{{ step.description }}</p>
              <div class="flex flex-wrap gap-2">
                <span v-if="step.agent" class="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full">
                  {{ step.agent }}
                </span>
                <span v-if="step.model" class="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full">
                  {{ step.model }}
                </span>
                <span v-if="step.outputDir" class="text-xs bg-amber-50 text-amber-700 px-2 py-0.5 rounded-full">
                  {{ step.outputDir }}/
                </span>
              </div>

              <!-- Show parallel branches that trigger after this step -->
              <div
                v-if="pipeline.parallelBranches?.filter((b: any) => b.triggerAfterStep === (step.order ?? idx + 1)).length"
                class="mt-3 ml-4 pl-4 border-l-2 border-dashed border-purple-300"
              >
                <p class="text-xs text-purple-600 font-medium mb-2">Parallel Branches</p>
                <div
                  v-for="(branch, bIdx) in pipeline.parallelBranches.filter((b: any) => b.triggerAfterStep === (step.order ?? idx + 1))"
                  :key="bIdx"
                  class="bg-purple-50 rounded-md p-3 mb-2"
                >
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-sm font-medium text-purple-800">{{ branch.label }}</span>
                  </div>
                  <p v-if="branch.description" class="text-xs text-purple-600 mb-1">{{ branch.description }}</p>
                  <div class="flex gap-2">
                    <span class="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">
                      {{ branch.agent }}
                    </span>
                    <span v-if="branch.model" class="text-xs bg-purple-100 text-purple-600 px-2 py-0.5 rounded-full">
                      {{ branch.model }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Convergence point -->
          <div v-if="pipeline.convergenceStep" class="flex items-start gap-4 pt-4 border-t border-dashed mt-4">
            <div class="w-10 h-10 rounded-full bg-green-100 text-green-700 flex items-center justify-center flex-shrink-0">
              <HardDriveDownload :size="18" />
            </div>
            <div class="pt-1.5">
              <h3 class="font-semibold text-foreground">Convergence Point</h3>
              <p class="text-sm text-muted-foreground">
                All parallel branches merge back at step {{ pipeline.convergenceStep }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Forked from info -->
      <div v-if="pipeline.forkedFrom" class="text-sm text-muted-foreground text-center">
        Forked from another pipeline template
      </div>
    </template>
  </div>
</template>
