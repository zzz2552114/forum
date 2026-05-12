import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { ref } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'

const pushedNotifications = ref<any[]>([])
const connectMock = vi.fn()

vi.mock('@/features/ai-mention/useNotificationSocket', () => ({
  useNotificationSocket: () => ({
    connect: connectMock,
    notifications: pushedNotifications,
  }),
}))

vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
  },
}))

import request from '@/utils/request'
import NotificationsView from './NotificationsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>home</div>' } },
    { path: '/notifications', component: NotificationsView },
    { path: '/spaces', component: { template: '<div>spaces</div>' } },
  ],
})

describe('NotificationsView.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    pushedNotifications.value = []
    connectMock.mockReset()
    vi.clearAllMocks()
  })

  const mountView = () => mount(NotificationsView, {
    global: {
      plugins: [createPinia(), router, ElementPlus],
    },
  })

  it('loads notifications on mount', async () => {
    const mockGet = vi.mocked(request.get)
    mockGet.mockResolvedValueOnce({
      items: [
        {
          id: 1,
          type: 'post_like',
          title: 'Like',
          content: 'someone liked your post',
          is_read: false,
          created_at: '2026-03-08T10:00:00',
        },
      ],
      pagination: { total: 1 },
    })

    const wrapper = mountView()
    await flushPromises()

    expect(mockGet).toHaveBeenCalledWith('/me/notifications', {
      params: { page: 1, page_size: 15 },
    })
    expect(wrapper.text()).toContain('Like')
  })

  it('marks all as read', async () => {
    const mockGet = vi.mocked(request.get)
    const mockPatch = vi.mocked(request.patch)

    mockGet.mockResolvedValueOnce({
      items: [
        {
          id: 2,
          type: 'post_bookmark',
          title: 'Bookmark',
          content: 'bookmarked',
          is_read: false,
          created_at: '2026-03-08T10:00:00',
        },
      ],
      pagination: { total: 1 },
    })
    mockPatch.mockResolvedValueOnce({ updated: 1 })

    const wrapper = mountView()
    await flushPromises()

    const button = wrapper.find('button')
    await button.trigger('click')

    expect(mockPatch).toHaveBeenCalledWith('/me/notifications/read', { notification_ids: [] })
  })

  it('merges pushed websocket notifications', async () => {
    const mockGet = vi.mocked(request.get)
    mockGet.mockResolvedValueOnce({ items: [], pagination: { total: 0 } })

    const wrapper = mountView()
    await flushPromises()

    pushedNotifications.value = [
      {
        type: 'notification',
        notification_id: 9,
        notification_type: 'chat_mention',
        title: 'Mention',
        content: 'you were mentioned',
        created_at: '2026-03-08T10:00:00',
      },
    ]

    await flushPromises()
    expect(wrapper.text()).toContain('Mention')
  })
})
