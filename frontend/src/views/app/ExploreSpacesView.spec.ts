import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ElementPlus from 'element-plus'
import ExploreSpacesView from './ExploreSpacesView.vue'
import router from '@/router'

// Mock request module
vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(async (url) => {
      if (url.includes('/categories/')) return [{ id: 1, name: '学校' }]
      if (url.includes('/spaces/')) return [{ id: 10, name: 'Test University', category_id: 1 }]
      if (url.includes('/resources/')) return { items: [{ id: 100, title: 'Policy Document', space_id: 10 }] }
      return []
    }),
    post: vi.fn()
  }
}))

// Mock auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    isAuthenticated: true,
    user: { id: 1, username: 'testuser' }
  }))
}))

import request from '@/utils/request'

describe('ExploreSpacesView.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  const mountView = () => {
    return mount(ExploreSpacesView, {
      global: {
        plugins: [createPinia(), router, ElementPlus],
        stubs: {
          'HomeHeader': true,
          'Upload': true,
          'el-dialog': { template: '<div class="mock-dialog" v-if="modelValue"><slot /><slot name="footer" /></div>', props: ['modelValue'] },
        }
      }
    })
  }

  it('fetches categories, spaces, and policies on mount', async () => {
    const mockGet = vi.mocked(request.get)
    const wrapper = mountView()
    await new Promise(resolve => setTimeout(resolve, 50))
    
    expect(mockGet).toHaveBeenCalledWith('/categories/')
    expect(mockGet).toHaveBeenCalledWith('/spaces/')
    expect(mockGet).toHaveBeenCalledWith('/resources/', expect.anything())
    
    expect(wrapper.html()).toContain('Policy Document')
  })

  it('switches sections when clicking on the sidebar', async () => {
    const wrapper = mountView()
    await new Promise(resolve => setTimeout(resolve, 50))
    
    const tabs = wrapper.findAll('.cursor-pointer') // Sidebar items
    // Click the second tab (大学生优惠合集)
    await tabs[1].trigger('click')
    
    expect(wrapper.html()).toContain('大学生优惠合集')
    // As per logic, materials are only fetched for section 1 right now in our implementation
  })
})
