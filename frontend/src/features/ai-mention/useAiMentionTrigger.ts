import { ref } from 'vue'

import request from '@/utils/request'

import type { AiMentionTask, AiMentionTaskStatus } from './types'

const FINAL_STATUSES = new Set<AiMentionTaskStatus>(['succeeded', 'failed', 'timeout'])

const sleep = (ms: number): Promise<void> => new Promise((resolve) => {
  window.setTimeout(resolve, ms)
})

export const parseAiPromptFromComment = (content: string): string | null => {
  const matched = content.match(/@ai\b/i)
  if (!matched || matched.index === undefined) {
    return null
  }

  const prompt = content.slice(matched.index + matched[0].length).trim()
  return prompt || null
}

export const useAiMentionTrigger = () => {
  const isSubmitting = ref(false)
  const latestTask = ref<AiMentionTask | null>(null)
  const errorMessage = ref('')

  const createTask = async (payload: {
    comment_id: number
    post_id: number
    space_id: number
    prompt?: string
    comment_content?: string
  }): Promise<AiMentionTask> => {
    isSubmitting.value = true
    errorMessage.value = ''

    try {
      const task = await request.post('/ai-mention/tasks', payload)
      latestTask.value = (task as unknown) as AiMentionTask
      return (task as unknown) as AiMentionTask
    } catch (error: unknown) {
      errorMessage.value = error instanceof Error ? error.message : 'Failed to create AI mention task.'
      throw error
    } finally {
      isSubmitting.value = false
    }
  }

  const triggerFromComment = async (input: {
    commentContent: string
    commentId: number
    postId: number
    spaceId: number
  }): Promise<AiMentionTask | null> => {
    const prompt = parseAiPromptFromComment(input.commentContent)
    if (!prompt) {
      return null
    }

    return createTask({
      comment_id: input.commentId,
      post_id: input.postId,
      space_id: input.spaceId,
      prompt,
      comment_content: input.commentContent,
    })
  }

  const fetchTask = async (taskId: string): Promise<AiMentionTask> => {
    const task = await request.get(`/ai-mention/tasks/${taskId}`)
    latestTask.value = (task as unknown) as AiMentionTask
    return (task as unknown) as AiMentionTask
  }

  const pollTaskUntilFinal = async (
    taskId: string,
    options?: { intervalMs?: number; timeoutMs?: number },
  ): Promise<AiMentionTask> => {
    const intervalMs = options?.intervalMs ?? 1200
    const timeoutMs = options?.timeoutMs ?? 120000
    const start = Date.now()

    while (Date.now() - start < timeoutMs) {
      const task = await fetchTask(taskId)
      if (FINAL_STATUSES.has(task.status)) {
        return task
      }
      await sleep(intervalMs)
    }

    throw new Error('Polling AI task timed out.')
  }

  return {
    createTask,
    errorMessage,
    fetchTask,
    isSubmitting,
    latestTask,
    pollTaskUntilFinal,
    triggerFromComment,
  }
}
