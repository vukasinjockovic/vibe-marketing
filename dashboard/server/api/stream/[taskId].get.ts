import { createReadStream, existsSync, readdirSync, statSync } from 'fs'
import { createInterface } from 'readline'
import { join } from 'path'

const STREAM_DIR = '/tmp/vibe-streams'

export default defineEventHandler(async (event) => {
  const taskId = getRouterParam(event, 'taskId')
  if (!taskId || !/^[a-zA-Z0-9_-]+$/.test(taskId)) {
    throw createError({ statusCode: 400, message: 'Invalid taskId' })
  }

  // Find all stream files matching this taskId (main + branch files)
  const streamFiles = findStreamFiles(taskId)

  setResponseHeaders(event, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Accel-Buffering': 'no',
  })

  const stream = new ReadableStream({
    start(controller) {
      const encoder = new TextEncoder()
      // Track file read positions for tailing
      const positions: Record<string, number> = {}
      let closed = false

      function sendEvent(data: string, source?: string) {
        if (closed) return
        const payload = source ? JSON.stringify({ ...JSON.parse(data), _source: source }) : data
        controller.enqueue(encoder.encode(`data: ${payload}\n\n`))
      }

      // Read existing content + tail for new content
      async function tailFile(filePath: string, source: string) {
        positions[filePath] = 0

        // Read existing lines
        if (existsSync(filePath)) {
          const stat = statSync(filePath)
          if (stat.size > 0) {
            const rl = createInterface({ input: createReadStream(filePath) })
            for await (const line of rl) {
              if (closed) return
              if (line.trim()) {
                sendEvent(line.trim(), source)
              }
            }
            positions[filePath] = stat.size
          }
        }
      }

      // Initial read of all existing files
      const initialRead = Promise.all(
        streamFiles.map(({ path, source }) => tailFile(path, source)),
      )

      // Poll for new content every 500ms
      const interval = setInterval(() => {
        if (closed) return

        // Re-scan for new branch files that may have appeared
        const currentFiles = findStreamFiles(taskId)

        for (const { path, source } of currentFiles) {
          if (!existsSync(path)) {
            // File was cleaned up — agent finished
            if (positions[path] !== undefined) {
              sendEvent(JSON.stringify({ type: 'stream_end', source }), source)
              delete positions[path]
            }
            continue
          }

          const stat = statSync(path)
          const pos = positions[path] ?? 0

          if (stat.size > pos) {
            // Read new bytes
            const rs = createReadStream(path, { start: pos })
            const rl = createInterface({ input: rs })
            let newPos = stat.size
            rl.on('line', (line: string) => {
              if (closed) return
              if (line.trim()) {
                sendEvent(line.trim(), source)
              }
            })
            rl.on('close', () => {
              positions[path] = newPos
            })
          }

          // If file existed before but is now gone (race condition check)
          if (positions[path] === undefined) {
            positions[path] = 0
          }
        }

        // If no files exist at all, send a heartbeat to keep connection alive
        if (currentFiles.length === 0 && Object.keys(positions).length === 0) {
          controller.enqueue(encoder.encode(`: heartbeat\n\n`))
        }
      }, 500)

      // Clean up on client disconnect
      event.node.req.on('close', () => {
        closed = true
        clearInterval(interval)
        controller.close()
      })
    },
  })

  return sendStream(event, stream)
})

function findStreamFiles(taskId: string): { path: string, source: string }[] {
  if (!existsSync(STREAM_DIR)) return []

  const files: { path: string, source: string }[] = []

  try {
    const entries = readdirSync(STREAM_DIR)
    for (const entry of entries) {
      if (!entry.startsWith(taskId) || !entry.endsWith('.jsonl')) continue

      const path = join(STREAM_DIR, entry)
      // Main stream: {taskId}.jsonl → source = "main"
      // Branch stream: {taskId}-{model}.jsonl → source = model name
      const suffix = entry.slice(taskId.length, -'.jsonl'.length)
      const source = suffix ? suffix.slice(1) : 'main' // Remove leading dash

      files.push({ path, source })
    }
  } catch {}

  return files
}
