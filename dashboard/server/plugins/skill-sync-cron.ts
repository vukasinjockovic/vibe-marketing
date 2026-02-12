export default defineNitroPlugin((nitro) => {
  const SYNC_INTERVAL = 10 * 60 * 1000 // 10 minutes
  const INITIAL_DELAY = 5000 // 5 seconds after server start

  let timer: ReturnType<typeof setInterval> | null = null

  async function runSync() {
    try {
      const res = await $fetch('/api/skills/sync', { method: 'POST', baseURL: 'http://localhost:3000' })
      const r = res as any
      console.log(`[skill-sync] ${r.synced} synced, ${r.unchanged} unchanged, ${r.skipped} skipped, ${r.missing} missing`)
    } catch (e: any) {
      console.error('[skill-sync] Failed:', e.message)
    }
  }

  // Initial sync after short delay
  setTimeout(() => {
    runSync()
    // Then every 10 minutes
    timer = setInterval(runSync, SYNC_INTERVAL)
  }, INITIAL_DELAY)

  // Cleanup on close
  nitro.hooks.hook('close', () => {
    if (timer) clearInterval(timer)
  })
})
