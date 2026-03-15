import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'

import ExploreAllSpacesView from './ExploreAllSpacesView.vue'
import request from '@/utils/request'

vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(async (url) => {
      if (url.includes('/categories/')) {
        return [{ id: 1, name: '学校' }]
      }
      if (url.includes('/spaces/')) {
        return [{ id: 10, name: 'Test University', category_id: 1 }]
      }
      if (url.includes('/search/spaces')) {
        return { items: [{ id: 10, name: 'Test University', category_id: 1 }], pagination: { total: 1 } }
      }
      return []
    }),
  },
}))

describe('ExploreAllSpacesView.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const createTestRouter = async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/explore-spaces', component: ExploreAllSpacesView }],
    })
    await router.push('/explore-spaces')
    await router.isReady()
    return router
  }

  it('requires module selection before normal search', async () => {
    const router = await createTestRouter()
    const wrapper = mount(ExploreAllSpacesView, {
      global: {
        plugins: [createPinia(), router, ElementPlus],
        stubs: { HomeHeader: true },
      },
    })
    await new Promise((resolve) => setTimeout(resolve, 40))

    const vm = wrapper.vm as any
    vm.searchQuery = 'Test'
    await vm.performSpaceSearch()

    const searchCalls = vi.mocked(request.get).mock.calls.filter((call) => String(call[0]).includes('/search/spaces'))
    expect(searchCalls.length).toBe(0)
  })

  it('searches spaces when category is selected', async () => {
    const router = await createTestRouter()
    const wrapper = mount(ExploreAllSpacesView, {
      global: {
        plugins: [createPinia(), router, ElementPlus],
        stubs: { HomeHeader: true },
      },
    })
    await new Promise((resolve) => setTimeout(resolve, 40))

    const vm = wrapper.vm as any
    vm.selectedCategoryId = 1
    vm.searchQuery = 'Test'
    await vm.performSpaceSearch()

    const searchCall = vi.mocked(request.get).mock.calls.find((call) => String(call[0]).includes('/search/spaces'))
    expect(searchCall).toBeTruthy()
    expect(searchCall?.[1]).toEqual(
      expect.objectContaining({
        params: expect.objectContaining({ category_id: 1, keyword: 'Test' }),
      }),
    )
  })
})
