import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ElementPlus from 'element-plus'

import SpacesView from './SpacesView.vue'
import router from '@/router'
import request from '@/utils/request'
import { useAuthStore } from '@/stores/auth'

vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(async (url) => {
      if (url.includes('/me/authorization')) {
        return {
          auth_state: 'guest',
          role: 'guest',
          trust_level: 0,
          permissions: [],
          space_permissions: {},
        }
      }
      if (url.includes('/categories/')) return [{ id: 1, name: 'Test Cat' }]
      if (url.includes('/spaces/')) return [{ id: 42, name: 'Math', color: 'bg-blue-500', category_id: 1 }]
      if (url.includes('/posts/')) {
        return {
          items: [
            { id: 1, title: 'Micro economics notes', summary: 'summary', created_at: '2025-01-01T00:00:00' },
            { id: 2, title: 'Linear algebra', summary: 'summary', created_at: '2025-01-01T00:00:00' },
          ],
          pagination: { total: 2 },
        }
      }
      if (url.includes('/resources/')) {
        return {
          items: [
            { id: 11, title: 'School policy A', resource_type: 'policy', created_at: '2025-01-01T00:00:00' },
            { id: 12, title: 'Question bank micro', resource_type: 'notes', created_at: '2025-01-01T00:00:00' },
          ],
          pagination: { total: 2 },
        }
      }
      return []
    }),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

describe('SpacesView.vue', () => {
  beforeEach(() => {
    sessionStorage.clear()
    localStorage.clear()
    vi.clearAllMocks()
  })

  const mountView = () => {
    const pinia = createPinia()
    setActivePinia(pinia)

    return {
      wrapper: mount(SpacesView, {
        global: {
          plugins: [pinia, router, ElementPlus],
        },
      }),
      authStore: useAuthStore(),
    }
  }

  it('calls GET /spaces on mount', async () => {
    const mockGet = vi.mocked(request.get)

    mountView()
    await new Promise((resolve) => setTimeout(resolve, 10))

    expect(mockGet).toHaveBeenCalledWith('/spaces/')
  })

  it('renders the spaces sidebar structure', async () => {
    const { wrapper } = mountView()
    expect(wrapper.exists()).toBe(true)
    // SpaceSidebar is now a child component, we just check if it was mounted
    expect(wrapper.findComponent({ name: 'SpaceSidebar' }).exists()).toBe(true)
  })

  it('guest cannot join space', async () => {
    const mockPut = vi.mocked(request.put)
    const { wrapper, authStore } = mountView()

    authStore.sessionMode = 'guest'
    authStore.authorizationLoaded = true
    authStore.authorization = {
      auth_state: 'guest',
      role: 'guest',
      trust_level: 0,
      permissions: [],
      space_permissions: {},
    }

    await new Promise((resolve) => setTimeout(resolve, 10))

    const vm = wrapper.vm as any
    vm.activeSpaceId = 42
    await vm.handleJoinSpace()

    expect(mockPut).not.toHaveBeenCalled()
  })

  it('basic authenticated user can join space', async () => {
    const mockPut = vi.mocked(request.put)
    mockPut.mockResolvedValueOnce({})

    const { wrapper, authStore } = mountView()

    authStore.sessionMode = 'auth'
    authStore.token = 'mock-token'
    authStore.user = { id: 1, username: 'tester' }
    authStore.authorizationLoaded = true
    authStore.authorization = {
      auth_state: 'auth',
      role: 'user',
      trust_level: 1,
      permissions: ['space.subscribe'],
      space_permissions: {},
    }

    await new Promise((resolve) => setTimeout(resolve, 10))

    const vm = wrapper.vm as any
    vm.activeSpaceId = 42
    await vm.handleJoinSpace()

    expect(mockPut).toHaveBeenCalledWith('/spaces/42/subscriptions/me')
  })

  it('filters current section list by keyword and resets on blank keyword', async () => {
    const { wrapper } = mountView()
    await new Promise((resolve) => setTimeout(resolve, 20))
    expect(wrapper.find('[data-testid="space-section-search"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="space-section-search-input"]').exists()).toBe(true)

    const vm = wrapper.vm as any
    vm.posts = [
      { id: 1, title: 'Micro economics notes', summary: 'summary', created_at: '2025-01-01T00:00:00' },
      { id: 2, title: 'Linear algebra', summary: 'summary', created_at: '2025-01-01T00:00:00' },
    ]
    vm.activeSectionId = 1
    vm.currentSectionSearchKeyword = 'micro'

    expect(vm.filteredPosts.length).toBe(1)
    expect(vm.filteredPosts[0].title).toContain('Micro')

    vm.currentSectionSearchKeyword = '   '
    expect(vm.filteredPosts.length).toBe(2)
  })
})
