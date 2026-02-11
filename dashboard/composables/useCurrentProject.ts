import { computed } from 'vue'
import { api } from '../../convex/_generated/api'

export function useCurrentProject() {
  const route = useRoute()
  const slug = computed(() => route.params.slug as string)

  const { data: project, loading, error } = useConvexQuery(
    api.projects.getBySlug,
    computed(() => slug.value ? { slug: slug.value } : 'skip' as const),
  )

  return { project, loading, error, slug }
}
