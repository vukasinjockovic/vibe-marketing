import { exec } from 'node:child_process'
import { promisify } from 'node:util'

const execAsync = promisify(exec)

export default defineEventHandler(async () => {
  try {
    const { stdout, stderr } = await execAsync(
      'python3 scripts/sync_services.py',
      { cwd: '/var/www/vibe-marketing', timeout: 60000 }
    )

    // Parse summary from last lines
    const lines = stdout.trim().split('\n')
    return {
      success: true,
      output: stdout,
      summary: lines.slice(-3).join('\n'),
    }
  } catch (error: any) {
    return {
      success: false,
      error: error.message || 'Sync failed',
      output: error.stdout || '',
      stderr: error.stderr || '',
    }
  }
})
