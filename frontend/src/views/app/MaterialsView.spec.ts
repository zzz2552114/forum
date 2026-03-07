import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ElementPlus from 'element-plus'
import MaterialsView from './MaterialsView.vue'
import router from '@/router'

// Mock request module
vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
  }
}))

import request from '@/utils/request'

describe('MaterialsView.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  const mountView = () => {
    return mount(MaterialsView, {
      global: {
        plugins: [createPinia(), router, ElementPlus],
        stubs: {
          'el-dialog': { template: '<div class="mock-dialog"><slot /><slot name="footer" /></div>', props: ['modelValue'] },
        }
      }
    })
  }

  it('calls GET /resources and GET /spaces on mount', async () => {
    const mockGet = vi.mocked(request.get)
    mockGet.mockResolvedValue({ items: [] })
    
    mountView()
    await vi.dynamicImportSettled()
    
    expect(mockGet).toHaveBeenCalledWith('/resources/')
    expect(mockGet).toHaveBeenCalledWith('/spaces/')
  })

  it('renders the search bar and subject filter', async () => {
    const mockGet = vi.mocked(request.get)
    mockGet.mockResolvedValue({ items: [] })
    
    const wrapper = mountView()
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.html()).toContain('搜索高校')
    expect(wrapper.html()).toContain('上传资料')
    expect(wrapper.html()).toContain('全部')
    expect(wrapper.html()).toContain('高等数学')
  })

  it('filteredMaterials filters by subject correctly', async () => {
    const mockGet = vi.mocked(request.get)
    mockGet.mockImplementation(async (url: string) => {
      if (url === '/resources/') {
        return {
          items: [
            { id: 1, title: 'Math Paper', subject: '高等数学', school: '清华', created_at: '2024-01-01' },
            { id: 2, title: 'Physics Notes', subject: '大学物理', school: '北大', created_at: '2024-01-02' },
          ]
        }
      }
      return []
    })
    
    const wrapper = mountView()
    await vi.dynamicImportSettled()
    
    const vm = wrapper.vm as any
    // Default is '全部', should show all
    expect(vm.filteredMaterials.length).toBe(2)
    
    // Filter by subject
    vm.activeSubject = '高等数学'
    expect(vm.filteredMaterials.length).toBe(1)
    expect(vm.filteredMaterials[0].title).toBe('Math Paper')
  })
})
