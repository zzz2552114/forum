import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import ElementPlus from 'element-plus'

import HomeHeader from '../HomeHeader.vue'

vi.mock('@/features/ai-mention/useNotificationSocket', () => ({
  useNotificationSocket: () => ({
    connect: vi.fn(),
    notifications: { value: [] },
  }),
}))

vi.mock('@/features/auth/useCan', () => ({
  useCan: () => ({
    can: () => true,
    explainDeny: () => '',
  }),
}))

vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(async () => 0),
    post: vi.fn(async () => ({})),
  },
}))

const createTestRouter = () =>
  createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div>Landing</div>' } },
      { path: '/home', component: { template: '<div>Home</div>' } },
      { path: '/spaces', component: { template: '<div>Spaces</div>' } },
      { path: '/explore-spaces', component: { template: '<div>Explore spaces</div>' } },
      { path: '/search/posts', component: { template: '<div>Search posts</div>' } },
      { path: '/search/materials', component: { template: '<div>Search materials</div>' } },
      { path: '/search/explore', component: { template: '<div>Search explore</div>' } },
      { path: '/notifications', component: { template: '<div>Notifications</div>' } },
      { path: '/profile', component: { template: '<div>Profile</div>' } },
    ],
  })

describe('HomeHeader.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders correctly', async () => {
    const router = createTestRouter()
    await router.push('/home')
    await router.isReady()

    const wrapper = mount(HomeHeader, {
      global: {
        plugins: [createPinia(), router, ElementPlus],
      },
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('FRM')
    expect(wrapper.text()).toContain('Forum Dashboard')
  })

  it('navigates to global post search', async () => {
    const router = createTestRouter()
    await router.push('/home')
    await router.isReady()
    const pushSpy = vi.spyOn(router, 'push')

    const wrapper = mount(HomeHeader, {
      global: {
        plugins: [createPinia(), router, ElementPlus],
      },
    })

    const vm = wrapper.vm as any
    vm.globalSearchType = 'posts'
    vm.searchQuery = 'economics'
    vm.handleSearch()

    expect(pushSpy).toHaveBeenCalledWith({
      path: '/search/posts',
      query: { keyword: 'economics' },
    })
  })

  it('navigates to space policy search with space context', async () => {
    const router = createTestRouter()
    await router.push('/spaces')
    await router.isReady()
    const pushSpy = vi.spyOn(router, 'push')

    const wrapper = mount(HomeHeader, {
      props: {
        spaceId: 12,
        spaceName: 'Macro Space',
        spaceSectionId: 4,
      },
      global: {
        plugins: [createPinia(), router, ElementPlus],
      },
    })

    const vm = wrapper.vm as any
    vm.spaceSearchType = 'space_policy'
    vm.searchQuery = 'policy'
    vm.handleSearch()

    expect(pushSpy).toHaveBeenCalledWith({
      path: '/search/explore',
      query: {
        keyword: 'policy',
        spaceId: '12',
        source: 'spaces',
      },
    })
  })
})
