import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ElementPlus from 'element-plus'
import SpacesView from './SpacesView.vue'
import router from '@/router'

// Mock request module
vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(async (url) => {
      if (url.includes('/categories/')) return [{ id: 1, name: 'Test Cat' }]
      if (url.includes('/spaces/')) return [{ id: 42, name: 'Math', color: 'bg-blue-500', category_id: 1 }]
      if (url.includes('/posts/')) return { items: [], pagination: { total: 0 } }
      return []
    }),
    post: vi.fn(),
    put: vi.fn(),
  }
}))

import request from '@/utils/request'

describe('SpacesView.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  const mountView = () => {
    return mount(SpacesView, {
      global: {
        plugins: [createPinia(), router, ElementPlus],
      }
    })
  }

  it('calls GET /spaces on mount', async () => {
    const mockGet = vi.mocked(request.get)
    
    mountView()
    // Wait for onMounted async call
    await new Promise(resolve => setTimeout(resolve, 10))
    
    expect(mockGet).toHaveBeenCalledWith('/spaces/')
  })

  it('renders the spaces sidebar structure', async () => {
    const wrapper = mountView()
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.html()).toContain('已加入空间')
  })

  it('submits a new trade post with correct tag_names', async () => {
    const mockPost = vi.mocked(request.post)
    const wrapper = mountView()
    await new Promise(resolve => setTimeout(resolve, 10))

    const vm = wrapper.vm as any
    vm.activeSpaceId = 42
    vm.newPostForm = { title: 'Sell Book', content: 'Details' }
    vm.isTradePost = true
    
    await vm.submitPost()
    
    expect(mockPost).toHaveBeenCalledWith('/posts/', expect.objectContaining({
      title: 'Sell Book',
      content: 'Details',
      space_id: 42,
      tag_names: ['交易']
    }))
  })
})
