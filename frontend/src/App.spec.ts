import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import App from './App.vue'
import router from './router'
import pinia from './stores'
import ElementPlus from 'element-plus'

describe('App.vue', () => {
  it('renders correctly', async () => {
    router.push('/')
    await router.isReady()
    
    const wrapper = mount(App, {
      global: {
        plugins: [router, pinia, ElementPlus]
      }
    })
    
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.html()).toContain('Welcome to Forum')
  })
})
