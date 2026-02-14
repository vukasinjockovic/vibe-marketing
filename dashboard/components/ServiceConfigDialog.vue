<script setup lang="ts">
import { X, ExternalLink, Copy, Check } from 'lucide-vue-next'
import { api } from '../../convex/_generated/api'

const props = defineProps<{
  service: any | null
  open: boolean
}>()

const emit = defineEmits<{
  close: []
  updated: []
}>()

const { mutate: doUpdate } = useConvexMutation(api.services.update)
const toast = useToast()

const apiKeyValue = ref('')
const extraConfig = ref('')
const saving = ref(false)
const copied = ref(false)

watch(() => props.service, (svc) => {
  if (svc) {
    apiKeyValue.value = svc.apiKeyValue || ''
    extraConfig.value = svc.extraConfig || ''
  }
})

async function save() {
  if (!props.service) return
  saving.value = true
  try {
    await doUpdate({
      id: props.service._id,
      apiKeyConfigured: !!apiKeyValue.value,
      apiKeyValue: apiKeyValue.value || undefined,
      extraConfig: extraConfig.value || undefined,
    })
    toast.success(`${props.service.displayName} configuration saved`)
    emit('updated')
    emit('close')
  } catch (e: any) {
    toast.error(e.message || 'Failed to save')
  } finally {
    saving.value = false
  }
}

function copyEnvVar() {
  if (props.service?.apiKeyEnvVar) {
    navigator.clipboard.writeText(props.service.apiKeyEnvVar)
    copied.value = true
    setTimeout(() => copied.value = false, 2000)
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="open && service" class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/50" @click.self="emit('close')">
        <div class="bg-card rounded-lg shadow-xl w-full max-w-lg max-h-[calc(100vh-1.5rem)] sm:max-h-[calc(100vh-2rem)] flex flex-col">
          <!-- Header -->
          <div class="relative px-4 sm:px-6 pr-12 py-4 border-b shrink-0 overflow-hidden">
            <h3 class="font-semibold text-lg text-foreground truncate">{{ service.displayName }}</h3>
            <p class="text-sm text-muted-foreground truncate mt-0.5">{{ service.description }}</p>
            <button class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center justify-center w-8 h-8 rounded-md hover:bg-muted transition-colors" @click="emit('close')">
              <X class="h-5 w-5" />
            </button>
          </div>

          <!-- Body -->
          <div class="px-4 sm:px-6 py-4 space-y-4 overflow-y-auto flex-1">
            <!-- Info row -->
            <div class="flex flex-wrap gap-2 text-sm">
              <span class="px-2 py-1 rounded bg-muted text-muted-foreground">{{ service.integrationType || 'script' }}</span>
              <span class="px-2 py-1 rounded bg-muted text-muted-foreground">{{ service.costInfo }}</span>
              <span v-if="service.freeTier" class="px-2 py-1 rounded bg-emerald-100 text-emerald-700">Free tier</span>
              <ServiceHealthDot :status="service.lastHealthStatus" />
            </div>

            <!-- Self-hosted info -->
            <div v-if="service.selfHostedConfig" class="rounded-md bg-blue-50 p-3 text-sm text-blue-800">
              <p class="font-medium">Self-hosted service</p>
              <p v-if="service.selfHostedConfig.healthCheckUrl" class="mt-1">
                Health: <code class="text-xs">{{ service.selfHostedConfig.healthCheckUrl }}</code>
              </p>
              <p v-if="service.selfHostedConfig.defaultPort" class="mt-1">
                Port: {{ service.selfHostedConfig.defaultPort }}
              </p>
            </div>

            <!-- API Key -->
            <div v-if="service.apiKeyEnvVar">
              <label class="block text-sm font-medium text-foreground mb-1">
                API Key
                <button class="ml-2 text-xs text-muted-foreground hover:text-foreground inline-flex items-center gap-1" @click="copyEnvVar">
                  <component :is="copied ? Check : Copy" class="h-3 w-3" />
                  {{ service.apiKeyEnvVar }}
                </button>
              </label>
              <input
                v-model="apiKeyValue"
                type="password"
                class="w-full px-3 py-2 rounded-md border bg-background text-sm"
                :placeholder="`Enter ${service.apiKeyEnvVar}`"
              />
            </div>

            <!-- Extra config -->
            <div>
              <label class="block text-sm font-medium text-foreground mb-1">Extra Configuration (JSON)</label>
              <textarea
                v-model="extraConfig"
                rows="3"
                class="w-full px-3 py-2 rounded-md border bg-background text-sm font-mono"
                placeholder='{"key": "value"}'
              />
            </div>

            <!-- Docs link -->
            <a
              v-if="service.docsUrl"
              :href="service.docsUrl"
              target="_blank"
              class="inline-flex items-center gap-1 text-sm text-primary hover:underline"
            >
              <ExternalLink class="h-3.5 w-3.5" />
              Documentation
            </a>
          </div>

          <!-- Footer -->
          <div class="flex justify-end gap-2 px-4 sm:px-6 py-4 border-t shrink-0">
            <button class="px-4 py-2 text-sm rounded-md hover:bg-muted" @click="emit('close')">Cancel</button>
            <button
              class="px-4 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
              :disabled="saving"
              @click="save"
            >
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
