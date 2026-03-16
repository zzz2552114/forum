import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import ElementPlus from 'element-plus'

import ExploreSpacesView from './ExploreSpacesView.vue'
import request from '@/utils/request'

vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(async (url: string) => {
      if (url.includes('/categories/')) {
        return [{ id: 1, name: '学校' }]
      }
      if (url.includes('/spaces/')) {
        return [{ id: 10, name: 'Test University', category_id: 1 }]
      }
      if (url.includes('/search/resources')) {
        return {
          items: [
            {
              id: 100,
              title: 'Policy Document',
              school_space_id: 10,
              school_space_name: 'Test University',
              resource_type: 'policy',
              created_at: '2025-01-01T00:00:00',
            },
          ],
          pagination: { total: 1 },
        }
      }
      return []
    }),
    post: vi.fn(async () => ({ bookmarked: true })),
  },
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    isAuthenticated: true,
    user: { id: 1, username: 'tester' },
  })),
}))

describe('ExploreSpacesView.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  const createTestRouter = async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/explore', component: ExploreSpacesView },
        { path: '/search/explore', component: { template: '<div>search</div>' } },
      ],
    })
    await router.push('/explore')
    await router.isReady()
    return router
  }

  const mountView = async () => {
    const router = await createTestRouter()
    const wrapper = mount(ExploreSpacesView, {
      global: {
        plugins: [createPinia(), router, ElementPlus],
        stubs: {
          HomeHeader: true,
          'el-dialog': { template: '<div><slot /><slot name="footer" /></div>' },
        },
      },
    })
    return { wrapper, router }
  }

  it('loads explore resources through search/resources with explore scope', async () => {
    const { wrapper } = await mountView()
    await new Promise((resolve) => setTimeout(resolve, 40))

    const searchCall = vi
      .mocked(request.get)
      .mock.calls.find((call) => String(call[0]).includes('/search/resources'))
    expect(searchCall).toBeTruthy()
    expect(searchCall?.[1]).toEqual(
      expect.objectContaining({
        params: expect.objectContaining({ scope: 'explore', page_size: 100 }),
      }),
    )
    expect(wrapper.html()).toContain('Policy Document')
  })

  it('redirects to /search/explore when school filter is empty', async () => {
    const { wrapper, router } = await mountView()
    await new Promise((resolve) => setTimeout(resolve, 40))
    const pushSpy = vi.spyOn(router, 'push')

    const vm = wrapper.vm as any
    vm.selectedSchoolId = null
    vm.searchQuery = 'policy'
    await vm.handleSearch()

    expect(pushSpy).toHaveBeenCalledWith({
      path: '/search/explore',
      query: { keyword: 'policy' },
    })
  })
})
