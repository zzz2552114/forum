import { vi } from 'vitest'

// Mock generic request utility since our components depend on it heavily
vi.mock('@/utils/request', () => {
  return {
    default: {
      get: vi.fn((url: string) => {
        if (url.includes('/categories/')) {
          return Promise.resolve([{ id: 1, name: '学校' }, { id: 2, name: '探索' }])
        }
        if (url.includes('/spaces/')) {
          return Promise.resolve([{ id: 1, name: '测试空间', category_id: 1 }])
        }
        if (url.includes('/posts/') || url.includes('/resources/') || url.includes('/search/resources')) {
          return Promise.resolve({ items: [], pagination: { total: 0 } })
        }
        if (url.includes('/me/subscriptions/spaces')) {
          return Promise.resolve([])
        }
        return Promise.resolve([])
      }),
      post: vi.fn(() => Promise.resolve({})),
      put: vi.fn(() => Promise.resolve({})),
      delete: vi.fn(() => Promise.resolve({}))
    }
  }
})

// Optional mock for ElMessage
vi.mock('element-plus', async () => {
  const original = await vi.importActual('element-plus')
  return {
    ...original,
    ElMessage: {
      success: vi.fn(),
      warning: vi.fn(),
      error: vi.fn(),
      info: vi.fn()
    }
  }
})
