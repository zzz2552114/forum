import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'

import SearchPostsView from './SearchPostsView.vue'
import request from '@/utils/request'

vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(async () => ({
      items: [{ id: 1, title: 'Economics Post', summary: 'summary', space_id: 9, created_at: '2025-01-01T00:00:00', like_count: 0, comment_count: 0, view_count: 0, author: { id: 1, username: 'u' } }],
      pagination: { total: 1 },
    })),
  },
}))

describe('SearchPostsView.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('requests /search/posts with keyword and space filter', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/search/posts', component: SearchPostsView },
        { path: '/spaces', component: { template: '<div />' } },
      ],
    })
    await router.push('/search/posts?keyword=economics&spaceId=9')
    await router.isReady()

    mount(SearchPostsView, {
      global: {
        plugins: [createPinia(), router, ElementPlus],
        stubs: {
          HomeHeader: true,
          PostList: { template: '<div>post list</div>', props: ['posts'] },
        },
      },
    })

    await new Promise((resolve) => setTimeout(resolve, 30))

    expect(vi.mocked(request.get)).toHaveBeenCalledWith(
      '/search/posts',
      expect.objectContaining({
        params: expect.objectContaining({ keyword: 'economics', space_id: 9 }),
      }),
    )
  })
})
