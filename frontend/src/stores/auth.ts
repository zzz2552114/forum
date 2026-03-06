import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<any>(null)

  const isAuthenticated = computed(() => !!token.value)

  const login = async (data: any) => {
    // Stub implementation
    token.value = 'dummy-token'
    localStorage.setItem('token', token.value)
    user.value = { id: 1, username: 'tester', nickname: 'Test User' }
  }

  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  // Called on app start if token exists
  const fetchMe = async () => {
    if (!token.value) return
    try {
      // user.value = await request.get('/me')
      user.value = { id: 1, username: 'tester', nickname: 'Test User' } // stub for now
    } catch (e) {
      logout()
    }
  }

  return { token, user, isAuthenticated, login, logout, fetchMe }
})
