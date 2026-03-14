import { describe, expect, it, vi, beforeEach } from 'vitest'

vi.mock('@/utils/request', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

import request from '@/utils/request'
import { parseAiPromptFromComment, useAiMentionTrigger } from './useAiMentionTrigger'

describe('parseAiPromptFromComment', () => {
  it('extracts prompt text after @ai mention', () => {
    expect(parseAiPromptFromComment('请帮我 @ai 总结要点')).toBe('总结要点')
    expect(parseAiPromptFromComment('@AI 生成三条结论')).toBe('生成三条结论')
  })

  it('returns null when mention not present or prompt empty', () => {
    expect(parseAiPromptFromComment('普通评论')).toBeNull()
    expect(parseAiPromptFromComment('@ai   ')).toBeNull()
  })
})

describe('useAiMentionTrigger', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates task from comment mention', async () => {
    const mockPost = vi.mocked(request.post)
    mockPost.mockResolvedValueOnce({
      id: 'task-1',
      user_id: 1,
      comment_id: 11,
      post_id: 22,
      space_id: 33,
      prompt: '做一个摘要',
      status: 'queued',
      retry_count: 0,
      created_at: '2026-03-08T10:00:00',
      updated_at: '2026-03-08T10:00:00',
    })

    const trigger = useAiMentionTrigger()
    const task = await trigger.triggerFromComment({
      commentContent: '这里有个请求 @ai 做一个摘要',
      commentId: 11,
      postId: 22,
      spaceId: 33,
    })

    expect(task).not.toBeNull()
    expect(mockPost).toHaveBeenCalledWith('/ai-mention/tasks', {
      comment_id: 11,
      post_id: 22,
      space_id: 33,
      prompt: '做一个摘要',
      comment_content: '这里有个请求 @ai 做一个摘要',
    })
  })

  it('polls until final status', async () => {
    const mockGet = vi.mocked(request.get)
    mockGet
      .mockResolvedValueOnce({
        id: 'task-2',
        status: 'running',
      })
      .mockResolvedValueOnce({
        id: 'task-2',
        status: 'succeeded',
      })

    const trigger = useAiMentionTrigger()
    const task = await trigger.pollTaskUntilFinal('task-2', { intervalMs: 1, timeoutMs: 100 })

    expect(task.status).toBe('succeeded')
    expect(mockGet).toHaveBeenCalledWith('/ai-mention/tasks/task-2')
  })
})
