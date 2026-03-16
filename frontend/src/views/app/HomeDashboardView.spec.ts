import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import HomeDashboardView from './HomeDashboardView.vue'
import router from '@/router'

// Mock request module
vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(async (url) => {
      if (url.includes('/spaces/me/subscriptions')) {
        return [{ id: 1, name: 'Real School Space' }, { id: 2, name: 'Course Space' }]
      }
      if (url.includes('/resources/')) {
        return { items: [{ id: 1, title: 'Real Material', downloads: 10, created_at: '2025-01-01T00:00:00' }] }
      }
      return []
    })
  }
}))

import request from '@/utils/request'

describe('HomeDashboardView.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
  })

  const mountView = () => {
    return mount(HomeDashboardView, {
      global: {
        plugins: [createPinia(), router],
        stubs: {
          'HomeHeader': true,
          'FeatureCard': {
            template: '<div><slot></slot></div>',
            props: ['title', 'subtitle', 'targetRoute']
          }
        }
      }
    })
  }

  it('fetches and renders real spaces and materials', async () => {
    const mockGet = vi.mocked(request.get)
    localStorage.setItem('token', 'mock-token')
    
    const wrapper = mountView()
    await new Promise(resolve => setTimeout(resolve, 50)) // Wait for onMounted
    
    expect(mockGet).toHaveBeenCalledWith('/spaces/me/subscriptions')
    expect(mockGet).toHaveBeenCalledWith('/resources/', expect.objectContaining({ params: { page: 1, page_size: 5 } }))
    
    // Check if the DOM has been updated with mocked fetch results
    expect(wrapper.html()).toContain('Real School Space')
    expect(wrapper.html()).toContain('Real Material')
  })
})
