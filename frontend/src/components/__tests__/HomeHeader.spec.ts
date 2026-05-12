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
    get: vi.fn(async (url: string) => {
      if (String(url).includes('/categories/')) {
        return [
          { id: 1, name: '学校' },
          { id: 2, name: '课程' },
        ]
      }
      return 0
    }),
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
    const input = wrapper.find('[data-testid="home-global-search-input"]')
    expect(input.exists()).toBe(true)
    await input.setValue('economics')
    expect((wrapper.vm as any).searchQuery).toBe('economics')
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

  it('navigates to space search with category and keyword', async () => {
    const router = createTestRouter()
    await router.push('/home')
    await router.isReady()
    const pushSpy = vi.spyOn(router, 'push')

    const wrapper = mount(HomeHeader, {
      global: {
        plugins: [createPinia(), router, ElementPlus],
      },
    })

    await new Promise((resolve) => setTimeout(resolve, 20))
    const vm = wrapper.vm as any
    vm.globalSearchType = 'spaces'
    vm.selectedSpaceCategoryId = 1
    vm.searchQuery = '山东'
    vm.handleSearch()

    expect(pushSpy).toHaveBeenCalledWith({
      path: '/explore-spaces',
      query: { keyword: '山东', categoryId: '1' },
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
