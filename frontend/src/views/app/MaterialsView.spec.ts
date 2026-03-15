import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ElementPlus from 'element-plus'

import MaterialsView from './MaterialsView.vue'
import router from '@/router'
import request from '@/utils/request'

vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(async (url, config) => {
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
    post: vi.fn(),
  },
}))

describe('MaterialsView.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  const mountView = () =>
    mount(MaterialsView, {
      global: {
        plugins: [createPinia(), router, ElementPlus],
        stubs: {
          'el-dialog': { template: '<div><slot /><slot name="footer" /></div>' },
        },
      },
    })

  it('loads materials via search/resources with materials scope', async () => {
    const wrapper = mountView()
    await new Promise((resolve) => setTimeout(resolve, 30))

    const calls = vi.mocked(request.get).mock.calls
    const searchCall = calls.find((call) => String(call[0]).includes('/search/resources'))
    expect(searchCall).toBeTruthy()
    expect(searchCall?.[1]).toEqual(
      expect.objectContaining({
        params: expect.objectContaining({ scope: 'materials' }),
      }),
    )
    expect(wrapper.html()).toContain('Course A Notes')
  })

  it('renders search controls and upload entry', async () => {
    const wrapper = mountView()
    await new Promise((resolve) => setTimeout(resolve, 30))

    expect(wrapper.html()).toContain('搜索库')
    expect(wrapper.html()).toContain('上传资料')
    expect(wrapper.html()).toContain('学校筛选')
    expect(wrapper.html()).toContain('课程筛选')
  })
})
