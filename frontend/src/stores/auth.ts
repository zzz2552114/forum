import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import request from '@/utils/request'

export type SessionMode = 'auth' | 'guest' | 'anonymous'

export interface AuthorizationSnapshot {
  auth_state: 'auth' | 'guest'
  role: 'super_root' | 'admin' | 'user' | 'guest'
  trust_level: number
  permissions: string[]
  space_permissions: Record<string, string[]>
}

const SESSION_MODE_KEY = 'session_mode'

const createGuestSnapshot = (): AuthorizationSnapshot => ({
  auth_state: 'guest',
  role: 'guest',
  trust_level: 0,
  permissions: [],
  space_permissions: {},
})

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<any>(null)

  const sessionMode = ref<SessionMode>('anonymous')
  const authorization = ref<AuthorizationSnapshot>(createGuestSnapshot())
  const authorizationLoaded = ref(false)

  const initializeSession = () => {
    if (token.value) {
      sessionMode.value = 'auth'
      sessionStorage.setItem(SESSION_MODE_KEY, 'auth')
      return
    }

    const cachedMode = (sessionStorage.getItem(SESSION_MODE_KEY) || 'anonymous') as SessionMode
    sessionMode.value = cachedMode === 'guest' ? 'guest' : 'anonymous'
  }

  initializeSession()

  const isAuthenticated = computed(() => sessionMode.value === 'auth' && !!token.value)
  const isGuest = computed(() => sessionMode.value === 'guest')

  const setSessionMode = (mode: SessionMode) => {
    sessionMode.value = mode
    sessionStorage.setItem(SESSION_MODE_KEY, mode)
  }

  const hasPermission = (permission: string, spaceId?: number): boolean => {
    if (!authorizationLoaded.value) {
      return false
    }

    if (authorization.value.permissions.includes(permission)) {
      return true
    }

    if (spaceId !== undefined) {
      const scoped = authorization.value.space_permissions[String(spaceId)] || []
      if (scoped.includes(permission)) {
        return true
      }

      const wildcard = authorization.value.space_permissions['*'] || []
      if (wildcard.includes(permission)) {
        return true
      }
    }

    return false
  }

  const hasTrustLevel = (minTrust: number): boolean => {
    if (!authorizationLoaded.value) {
      return false
    }

    if (authorization.value.role === 'admin' || authorization.value.role === 'super_root') {
      return true
    }

    return Number(authorization.value.trust_level || 0) >= minTrust
  }

  const fetchAuthorization = async () => {
    try {
      const snapshot = await request.get('/me/authorization')
      authorization.value = snapshot as AuthorizationSnapshot
      authorizationLoaded.value = true
      return authorization.value
    } catch {
      if (sessionMode.value === 'auth') {
        logout()
      }
      authorization.value = createGuestSnapshot()
      authorizationLoaded.value = true
      return authorization.value
    }
  }

  const fetchMe = async () => {
    if (!isAuthenticated.value) return
    try {
      user.value = await request.get('/me/')
    } catch {
      logout()
    }
  }

  const login = async (data: any) => {
    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)

    const res: any = await request.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })

    token.value = res.access_token
    localStorage.setItem('token', token.value)
    setSessionMode('auth')

    await fetchMe()
    await fetchAuthorization()
  }

  const register = async (data: any) => {
    await request.post('/auth/register', data)
  }

  const enterGuestSession = async () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    setSessionMode('guest')

    authorization.value = createGuestSnapshot()
    authorizationLoaded.value = true
    await fetchAuthorization()
  }

  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    setSessionMode('anonymous')

    authorization.value = createGuestSnapshot()
    authorizationLoaded.value = false
  }

  return {
    token,
    user,
    sessionMode,
    authorization,
    authorizationLoaded,
    isAuthenticated,
    isGuest,
    login,
    register,
    logout,
    enterGuestSession,
    fetchMe,
    fetchAuthorization,
    hasPermission,
    hasTrustLevel,
  }
})
