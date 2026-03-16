import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'

import SearchMaterialsView from './SearchMaterialsView.vue'
import request from '@/utils/request'

vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(async () => ({
      items: [{ id: 1, title: 'Material A', created_at: '2025-01-01T00:00:00' }],
      pagination: { total: 1 },
    })),
    post: vi.fn(async () => ({ bookmarked: true })),
  },
}))

describe('SearchMaterialsView.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('requests material scope results', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/search/materials', component: SearchMaterialsView }],
    })
    await router.push('/search/materials?keyword=econ')
    await router.isReady()

    mount(SearchMaterialsView, {
      global: {
        plugins: [createPinia(), router, ElementPlus],
        stubs: { HomeHeader: true },
      },
    })

    await new Promise((resolve) => setTimeout(resolve, 30))

    expect(vi.mocked(request.get)).toHaveBeenCalledWith(
      '/search/resources',
      expect.objectContaining({
        params: expect.objectContaining({ scope: 'materials', keyword: 'econ' }),
      }),
    )
  })
})
