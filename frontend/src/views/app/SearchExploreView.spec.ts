import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'

import SearchExploreView from './SearchExploreView.vue'
import request from '@/utils/request'

vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(async () => ({
      items: [{ id: 1, title: 'Explore A', created_at: '2025-01-01T00:00:00' }],
      pagination: { total: 1 },
    })),
    post: vi.fn(async () => ({ bookmarked: true })),
  },
}))

describe('SearchExploreView.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('requests explore scope results', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/search/explore', component: SearchExploreView }],
    })
    await router.push('/search/explore?keyword=policy')
    await router.isReady()

    mount(SearchExploreView, {
      global: {
        plugins: [createPinia(), router, ElementPlus],
        stubs: { HomeHeader: true },
      },
    })

    await new Promise((resolve) => setTimeout(resolve, 30))

    expect(vi.mocked(request.get)).toHaveBeenCalledWith(
      '/search/resources',
      expect.objectContaining({
        params: expect.objectContaining({ scope: 'explore', keyword: 'policy' }),
      }),
    )
  })
})
