<script setup lang="ts">
import {
  FileText, MessageSquare, Mail, Image, Video,
  Search, FileEdit, Megaphone, Layout, Bookmark,
  BarChart3, Palette, MailPlus, Sparkles,
} from 'lucide-vue-next'

const props = defineProps<{
  type: string
  size?: number
}>()

const iconMap: Record<string, any> = {
  research_material: Search,
  brief: FileEdit,
  article: FileText,
  landing_page: Layout,
  ad_copy: Megaphone,
  social_post: MessageSquare,
  email_sequence: MailPlus,
  email_excerpt: Mail,
  image_prompt: Sparkles,
  image: Image,
  video_script: Video,
  lead_magnet: Bookmark,
  report: BarChart3,
  brand_asset: Palette,
}

const colorMap: Record<string, string> = {
  research_material: 'text-blue-500',
  brief: 'text-indigo-500',
  article: 'text-emerald-500',
  landing_page: 'text-violet-500',
  ad_copy: 'text-orange-500',
  social_post: 'text-pink-500',
  email_sequence: 'text-cyan-500',
  email_excerpt: 'text-teal-500',
  image_prompt: 'text-amber-500',
  image: 'text-rose-500',
  video_script: 'text-purple-500',
  lead_magnet: 'text-lime-500',
  report: 'text-sky-500',
  brand_asset: 'text-fuchsia-500',
}

const icon = computed(() => iconMap[props.type] || FileText)
const color = computed(() => colorMap[props.type] || 'text-muted-foreground')
</script>

<template>
  <component :is="icon" :size="size || 16" :class="color" />
</template>
