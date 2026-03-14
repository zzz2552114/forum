import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import AiTaskStatusCard from './AiTaskStatusCard.vue'

describe('AiTaskStatusCard', () => {
  it('renders succeeded state and result text', () => {
    const wrapper = mount(AiTaskStatusCard, {
      props: {
        task: {
          id: 'task-1',
          user_id: 1,
          comment_id: 2,
          post_id: 3,
          space_id: 4,
          prompt: '生成摘要',
          status: 'succeeded',
          retry_count: 0,
          result: '摘要完成',
          created_at: '2026-03-08T10:00:00',
          updated_at: '2026-03-08T10:00:01',
        },
      },
    })

    expect(wrapper.text()).toContain('AI 任务状态')
    expect(wrapper.text()).toContain('已完成')
    expect(wrapper.text()).toContain('摘要完成')
  })

  it('renders failed state and error text', () => {
    const wrapper = mount(AiTaskStatusCard, {
      props: {
        task: {
          id: 'task-2',
          user_id: 1,
          comment_id: 2,
          post_id: 3,
          space_id: 4,
          prompt: '生成摘要',
          status: 'failed',
          retry_count: 1,
          error: '执行失败',
          created_at: '2026-03-08T10:00:00',
          updated_at: '2026-03-08T10:00:01',
        },
      },
    })

    expect(wrapper.text()).toContain('失败')
    expect(wrapper.text()).toContain('执行失败')
  })
})
