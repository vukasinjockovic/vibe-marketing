/**
 * Proxy dispatch requests to the host dispatcher service.
 * POST /api/dispatch — { taskId, agentName }
 */
export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  if (!body?.taskId || !body?.agentName) {
    throw createError({ statusCode: 400, message: 'Missing taskId or agentName' })
  }

  try {
    const res = await $fetch('http://127.0.0.1:3212/dispatch', {
      method: 'POST',
      body: { taskId: body.taskId, agentName: body.agentName },
    })
    return res
  } catch (err: any) {
    throw createError({
      statusCode: 502,
      message: `Dispatcher unavailable: ${err.message}`,
    })
  }
})
