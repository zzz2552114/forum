import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ElementPlus from 'element-plus'

import ExploreSpacesView from './ExploreSpacesView.vue'
import router from '@/router'
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
    post: vi.fn(),
  },
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    isAuthenticated: true,
    user: { id: 1, username: 'tester' },
    authorizationLoaded: true,
    fetchAuthorization: vi.fn(),
    fetchMe: vi.fn(),
    hasTrustLevel: vi.fn(() => true),
    hasPermission: vi.fn(() => true),
  })),
}))

describe('ExploreSpacesView.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  const mountView = () =>
    mount(ExploreSpacesView, {
      global: {
        plugins: [createPinia(), router, ElementPlus],
        stubs: {
          HomeHeader: true,
          'el-dialog': { template: '<div><slot /><slot name="footer" /></div>' },
        },
      },
    })

  it('loads explore resources through search/resources with explore scope', async () => {
    const wrapper = mountView()
    await new Promise((resolve) => setTimeout(resolve, 40))

    const calls = vi.mocked(request.get).mock.calls
    const searchCall = calls.find((call) => String(call[0]).includes('/search/resources'))
    expect(searchCall).toBeTruthy()
    expect(searchCall?.[1]).toEqual(
      expect.objectContaining({
        params: expect.objectContaining({ scope: 'explore' }),
      }),
    )
    expect(wrapper.html()).toContain('Policy Document')
  })

  it('renders school filter and explore button', async () => {
    const wrapper = mountView()
    await new Promise((resolve) => setTimeout(resolve, 40))

    expect(wrapper.html()).toContain('学校筛选')
    expect(wrapper.html()).toContain('探索')
  })
})
