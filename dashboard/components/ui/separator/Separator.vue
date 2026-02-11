<script setup lang="ts">
import { Separator as SeparatorPrimitive } from 'radix-vue'
import { cn } from '~/lib/utils'

const props = withDefaults(defineProps<{
  orientation?: 'horizontal' | 'vertical'
  decorative?: boolean
  class?: any
}>(), {
  orientation: 'horizontal',
  decorative: true,
})
</script>

<template>
  <SeparatorPrimitive
    :orientation="orientation"
    :decorative="decorative"
    :class="cn(
      'shrink-0 bg-border',
      orientation === 'horizontal' ? 'h-[1px] w-full' : 'h-full w-[1px]',
      props.class,
    )"
  />
</template>
