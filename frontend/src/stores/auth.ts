import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<any>(null)

  const isAuthenticated = computed(() => !!token.value)

  const login = async (data: any) => {
    // API requires application/x-www-form-urlencoded for OAuth2
    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)

    const res: any = await request.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    token.value = res.access_token
    localStorage.setItem('token', token.value)
    
    // Fetch user profile immediately
    await fetchMe()
  }

  const register = async (data: any) => {
    await request.post('/auth/register', data)
  }

  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  const fetchMe = async () => {
    if (!token.value) return
    try {
      user.value = await request.get('/me')
    } catch (e) {
      logout()
    }
  }

  return { token, user, isAuthenticated, login, register, logout, fetchMe }
})
