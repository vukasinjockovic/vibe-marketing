<script setup lang="ts">
import draggable from 'vuedraggable'
import { ChevronDown, ChevronRight } from 'lucide-vue-next'
import { api } from '../../convex/_generated/api'

const props = defineProps<{
  category: any
  services: any[]
}>()

const emit = defineEmits<{
  toggle: [service: any]
  configure: [service: any]
  reordered: []
}>()

const { mutate: doReorder } = useConvexMutation(api.services.reorderServices)
const toast = useToast()
const expanded = ref(true)

const activeServices = computed(() =>
  props.services.filter(s => s.isActive).sort((a, b) => a.priority - b.priority)
)

const inactiveServices = computed(() =>
  props.services.filter(s => !s.isActive).sort((a, b) => a.displayName.localeCompare(b.displayName))
)

const dragList = ref<any[]>([])

watch(activeServices, (val) => {
  dragList.value = [...val]
}, { immediate: true })

async function onDragEnd() {
  if (dragList.value.length === 0) return
  const ids = dragList.value.map(s => s._id)
  try {
    await doReorder({ categoryId: props.category._id, serviceIds: ids })
    emit('reordered')
  } catch (e: any) {
    toast.error(e.message || 'Failed to reorder')
  }
}
</script>

<template>
  <div class="rounded-lg border bg-card text-card-foreground shadow-sm">
    <!-- Header -->
    <button
      class="w-full px-4 py-3 border-b flex items-center gap-2 hover:bg-muted/50 transition-colors"
      @click="expanded = !expanded"
    >
      <component :is="expanded ? ChevronDown : ChevronRight" class="h-4 w-4 text-muted-foreground shrink-0" />
      <span class="text-lg">{{ category.icon }}</span>
      <h3 class="font-semibold text-foreground text-sm">{{ category.displayName }}</h3>
      <span class="text-xs text-muted-foreground ml-1">{{ category.description }}</span>
      <span class="ml-auto text-xs text-muted-foreground shrink-0">
        {{ activeServices.length }} active
      </span>
    </button>

    <div v-if="expanded">
      <!-- Active services (draggable) -->
      <div v-if="dragList.length > 0">
        <draggable
          v-model="dragList"
          item-key="_id"
          handle=".cursor-grab"
          ghost-class="opacity-30"
          @end="onDragEnd"
        >
          <template #item="{ element, index }">
            <ServiceRow
              :service="element"
              :rank="index + 1"
              :draggable="true"
              @toggle="emit('toggle', $event)"
              @configure="emit('configure', $event)"
            />
          </template>
        </draggable>
      </div>

      <!-- Inactive divider -->
      <div v-if="inactiveServices.length > 0" class="px-4 py-1.5 bg-muted/30">
        <span class="text-xs text-muted-foreground font-medium">
          {{ activeServices.length > 0 ? 'Inactive' : 'No active providers' }}
          ({{ inactiveServices.length }})
        </span>
      </div>

      <!-- Inactive services -->
      <div v-if="inactiveServices.length > 0" class="divide-y divide-border/50">
        <ServiceRow
          v-for="svc in inactiveServices"
          :key="svc._id"
          :service="svc"
          :draggable="false"
          @toggle="emit('toggle', $event)"
          @configure="emit('configure', $event)"
        />
      </div>

      <!-- Empty state -->
      <div v-if="services.length === 0" class="px-4 py-4 text-sm text-muted-foreground">
        No services configured. Click "Sync Plugins" to discover available services.
      </div>
    </div>
  </div>
</template>
