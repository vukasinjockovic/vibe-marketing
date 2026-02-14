<script setup lang="ts">
import { api } from '../../convex/_generated/api'
import { ArrowUp, ArrowDown, Link2 } from 'lucide-vue-next'

const props = defineProps<{
  resourceId: any
}>()

const emit = defineEmits<{
  navigate: [resourceId: string]
}>()

const { data: relationships, loading } = useConvexQuery(
  api.resources.listRelated,
  computed(() => props.resourceId ? { resourceId: props.resourceId } : 'skip'),
)
</script>

<template>
  <div>
    <div v-if="loading" class="p-4 text-center text-muted-foreground text-sm">Loading relationships...</div>

    <div v-else-if="!relationships?.parent && !relationships?.children?.length && !relationships?.related?.length"
         class="p-4 text-center text-muted-foreground text-sm">
      No relationships
    </div>

    <div v-else class="space-y-4 p-4">
      <!-- Parent -->
      <div v-if="relationships?.parent">
        <h4 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2 flex items-center gap-1">
          <ArrowUp :size="12" /> Parent
        </h4>
        <div
          class="flex items-center gap-2 p-2 rounded-md border cursor-pointer hover:bg-muted/50 transition-colors"
          @click="emit('navigate', relationships.parent._id)"
        >
          <ResourceTypeIcon :type="relationships.parent.resourceType" :size="16" />
          <span class="text-sm font-medium">{{ relationships.parent.title }}</span>
          <span class="text-xs text-muted-foreground ml-auto">{{ relationships.parent.resourceType.replace('_', ' ') }}</span>
        </div>
      </div>

      <!-- Children -->
      <div v-if="relationships?.children?.length">
        <h4 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2 flex items-center gap-1">
          <ArrowDown :size="12" /> Children ({{ relationships.children.length }})
        </h4>
        <div class="space-y-1">
          <div
            v-for="child in relationships.children"
            :key="child._id"
            class="flex items-center gap-2 p-2 rounded-md border cursor-pointer hover:bg-muted/50 transition-colors"
            @click="emit('navigate', child._id)"
          >
            <ResourceTypeIcon :type="child.resourceType" :size="16" />
            <span class="text-sm font-medium">{{ child.title }}</span>
            <span class="text-xs text-muted-foreground ml-auto">{{ child.status }}</span>
          </div>
        </div>
      </div>

      <!-- Related -->
      <div v-if="relationships?.related?.length">
        <h4 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2 flex items-center gap-1">
          <Link2 :size="12" /> Related ({{ relationships.related.length }})
        </h4>
        <div class="space-y-1">
          <div
            v-for="rel in relationships.related"
            :key="rel._id"
            class="flex items-center gap-2 p-2 rounded-md border cursor-pointer hover:bg-muted/50 transition-colors"
            @click="emit('navigate', rel._id)"
          >
            <ResourceTypeIcon :type="rel.resourceType" :size="16" />
            <span class="text-sm font-medium">{{ rel.title }}</span>
            <span class="text-xs text-muted-foreground ml-auto">{{ rel.resourceType.replace('_', ' ') }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
