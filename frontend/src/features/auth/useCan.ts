import { computed } from 'vue'

import { useAuthStore } from '@/stores/auth'

const TRUST_LABELS: Record<number, string> = {
  1: 'BASIC',
  2: 'VERIFIED',
  3: 'CONTRIBUTOR',
}

export const useCan = () => {
  const authStore = useAuthStore()

  const can = (
    opts: {
      permission?: string
      minTrust?: number
      spaceId?: number
      requireAuth?: boolean
    } = {},
  ): boolean => {
    const { permission, minTrust, spaceId, requireAuth } = opts

    if (requireAuth && !authStore.isAuthenticated) {
      return false
    }

    if (permission && !authStore.hasPermission(permission, spaceId)) {
      return false
    }

    if (typeof minTrust === 'number' && !authStore.hasTrustLevel(minTrust)) {
      return false
    }

    return true
  }

  const explainDeny = (
    opts: {
      permission?: string
      minTrust?: number
      requireAuth?: boolean
    } = {},
  ): string => {
    const { permission, minTrust, requireAuth } = opts

    if (requireAuth && !authStore.isAuthenticated) {
      return '请先登录'
    }

    if (typeof minTrust === 'number' && !authStore.hasTrustLevel(minTrust)) {
      return `需要信任等级 ${TRUST_LABELS[minTrust] || minTrust}`
    }

    if (permission && !authStore.hasPermission(permission)) {
      return `缺少权限：${permission}`
    }

    return '权限不足'
  }

  const isGuest = computed(() => authStore.isGuest)

  return {
    can,
    explainDeny,
    isGuest,
  }
}
