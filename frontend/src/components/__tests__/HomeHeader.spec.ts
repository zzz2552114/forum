import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import HomeHeader from '../HomeHeader.vue'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/login', component: { template: '<div>Login</div>' } }
  ]
})

describe('HomeHeader.vue', () => {
  it('renders correctly', async () => {
    setActivePinia(createPinia())
    const wrapper = mount(HomeHeader, {
      global: {
        plugins: [router],
        stubs: {
          'el-input': true,
          'el-dropdown': true,
          'el-dropdown-menu': true,
          'el-dropdown-item': true,
          'el-avatar': true,
          'el-button': true,
          'el-icon': true,
          'el-dialog': true,
          'el-select': true,
          'el-option': true,
          'Search': true,
          'Bell': true,
          'Setting': true,
          'UserFilled': true,
          'Plus': true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('FRMForum Dashboard')
  })
})
