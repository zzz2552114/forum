import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'

import ExploreAllSpacesView from './ExploreAllSpacesView.vue'
import request from '@/utils/request'

vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(async (url: string, options?: any) => {
      if (url.includes('/categories/')) {
        return [{ id: 1, name: '学校' }]
      }
      if (url.includes('/spaces/')) {
        return [
          { id: 10, name: '数学分析', category_id: 1 },
          { id: 11, name: '会计学基础', category_id: 1 },
        ]
      }
      if (url.includes('/search/spaces')) {
        const keyword = String(options?.params?.keyword || '').toLowerCase()
        if (keyword.includes('math') || keyword.includes('数学')) {
          return { items: [{ id: 10, name: '数学分析', category_id: 1 }], pagination: { total: 1 } }
        }
        if (keyword.includes('account') || keyword.includes('会计')) {
          return { items: [{ id: 11, name: '会计学基础', category_id: 1 }], pagination: { total: 1 } }
        }
        return { items: [], pagination: { total: 0 } }
      }
      return []
    }),
  },
}))

describe('ExploreAllSpacesView.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const createTestRouter = async (initialPath = '/explore-spaces') => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/explore-spaces', component: ExploreAllSpacesView }],
    })
    await router.push(initialPath)
    await router.isReady()
    return router
  }

  const mountView = async (initialPath = '/explore-spaces') => {
    const router = await createTestRouter(initialPath)
    const wrapper = mount(ExploreAllSpacesView, {
      global: {
        plugins: [createPinia(), router, ElementPlus],
        stubs: { HomeHeader: true },
      },
    })
    await new Promise((resolve) => setTimeout(resolve, 40))
    return { wrapper, router }
  }

  it('requires module selection before search', async () => {
    const { wrapper } = await mountView()
    const vm = wrapper.vm as any
    vm.searchQuery = 'Test'
    await vm.performSpaceSearch()

    const searchCalls = vi
      .mocked(request.get)
      .mock.calls.filter((call) => String(call[0]).includes('/search/spaces'))
    expect(searchCalls.length).toBe(0)
  })

  it('requires keyword before searching', async () => {
    const { wrapper } = await mountView()
    const vm = wrapper.vm as any
    vm.selectedCategoryId = 1
    vm.searchQuery = '   '
    await vm.performSpaceSearch()

    const searchCalls = vi
      .mocked(request.get)
      .mock.calls.filter((call) => String(call[0]).includes('/search/spaces'))
    expect(searchCalls.length).toBe(0)
  })

  it('searches spaces when category and keyword are set', async () => {
    const { wrapper } = await mountView()
    const vm = wrapper.vm as any
    vm.selectedCategoryId = 1
    vm.searchQuery = 'math'
    await vm.performSpaceSearch()

    const searchCall = vi
      .mocked(request.get)
      .mock.calls.find((call) => String(call[0]).includes('/search/spaces'))
    expect(searchCall).toBeTruthy()
    expect(searchCall?.[1]).toEqual(
      expect.objectContaining({
        params: expect.objectContaining({ category_id: 1, keyword: 'math' }),
      }),
    )
  })

  it('re-fetches when same route query changes', async () => {
    const { wrapper, router } = await mountView('/explore-spaces?keyword=math&categoryId=1')
    await new Promise((resolve) => setTimeout(resolve, 40))

    let searchCalls = vi
      .mocked(request.get)
      .mock.calls.filter((call) => String(call[0]).includes('/search/spaces'))
    expect(searchCalls.length).toBe(1)
    expect((searchCalls[0]?.[1] as any)?.params?.keyword).toBe('math')
    expect((wrapper.vm as any).searchResultIds).toEqual([10])

    await router.push('/explore-spaces?keyword=account&categoryId=1')
    await new Promise((resolve) => setTimeout(resolve, 40))

    searchCalls = vi
      .mocked(request.get)
      .mock.calls.filter((call) => String(call[0]).includes('/search/spaces'))
    expect(searchCalls.length).toBe(2)
    expect((searchCalls[1]?.[1] as any)?.params?.keyword).toBe('account')
    expect((wrapper.vm as any).searchResultIds).toEqual([11])
  })

  it('does not request and clears stale result when query is incomplete', async () => {
    const { wrapper, router } = await mountView('/explore-spaces?keyword=math&categoryId=1')
    await new Promise((resolve) => setTimeout(resolve, 40))
    expect((wrapper.vm as any).searchResultIds).toEqual([10])

    await router.push('/explore-spaces?categoryId=1')
    await new Promise((resolve) => setTimeout(resolve, 40))

    const searchCalls = vi
      .mocked(request.get)
      .mock.calls.filter((call) => String(call[0]).includes('/search/spaces'))
    expect(searchCalls.length).toBe(1)
    expect((wrapper.vm as any).searchResultIds).toEqual([])
  })

  it('writes query through router.replace when submiting sub search', async () => {
    const { wrapper, router } = await mountView()
    const replaceSpy = vi.spyOn(router, 'replace')
    const vm = wrapper.vm as any
    vm.selectedCategoryId = 1
    vm.searchQuery = 'math'

    await vm.handleSearchSubmit()
    expect(replaceSpy).toHaveBeenCalledWith({
      path: '/explore-spaces',
      query: { keyword: 'math', categoryId: '1' },
    })
  })
})
