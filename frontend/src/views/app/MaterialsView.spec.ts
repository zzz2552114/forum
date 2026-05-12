import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import ElementPlus from 'element-plus'

import MaterialsView from './MaterialsView.vue'
import request from '@/utils/request'

vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(async (url: string) => {
      if (url.includes('/categories/')) {
        return [
          { id: 1, name: '学校' },
          { id: 2, name: '课程' },
        ]
      }
      if (url.includes('/spaces/')) {
        return [
          { id: 11, name: 'School A', category_id: 1 },
          { id: 21, name: 'Course A', category_id: 2 },
        ]
      }
      if (url.includes('/search/resources')) {
        return {
          items: [
            {
              id: 101,
              title: 'Course A Notes',
              space_id: 21,
              space_name: 'Course A',
              resource_type: 'notes',
              created_at: '2025-01-01T00:00:00',
              download_count: 0,
              bookmark_count: 0,
            },
          ],
          pagination: { total: 1 },
        }
      }
      return []
    }),
    post: vi.fn(async () => ({})),
  },
}))

describe('MaterialsView.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  const createTestRouter = async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/materials', component: MaterialsView },
        { path: '/search/materials', component: { template: '<div>search</div>' } },
      ],
    })
    await router.push('/materials')
    await router.isReady()
    return router
  }

  const mountView = async () => {
    const router = await createTestRouter()
    const wrapper = mount(MaterialsView, {
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

  it('loads materials via search/resources with materials scope', async () => {
    const { wrapper } = await mountView()
    await new Promise((resolve) => setTimeout(resolve, 40))

    const searchCall = vi
      .mocked(request.get)
      .mock.calls.find((call) => String(call[0]).includes('/search/resources'))
    expect(searchCall).toBeTruthy()
    expect(searchCall?.[1]).toEqual(
      expect.objectContaining({
        params: expect.objectContaining({ scope: 'materials', page_size: 100 }),
      }),
    )
    expect(wrapper.html()).toContain('Course A Notes')
  })

  it('redirects to /search/materials when course filter is empty', async () => {
    const { wrapper, router } = await mountView()
    await new Promise((resolve) => setTimeout(resolve, 40))
    const pushSpy = vi.spyOn(router, 'push')

    const vm = wrapper.vm as any
    vm.selectedCourseId = null
    vm.selectedSchoolId = 11
    vm.searchQuery = 'economics'
    await vm.handleSearch()

    expect(pushSpy).toHaveBeenCalledWith({
      path: '/search/materials',
      query: { keyword: 'economics', schoolSpaceId: '11' },
    })
  })
})
