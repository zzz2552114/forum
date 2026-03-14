import { computed, getCurrentInstance, onBeforeUnmount, ref } from 'vue'

import type { AiNotificationEvent } from './types'

export type NotificationConnectionState = 'connecting' | 'connected' | 'reconnecting' | 'offline'

const BASE_RECONNECT_DELAY_MS = 500
const MAX_RECONNECT_DELAY_MS = 8000

export const buildNotificationWsUrl = (token: string, endpoint = '/ws/notifications'): string => {
  const baseUrl = endpoint.startsWith('ws://') || endpoint.startsWith('wss://')
    ? new URL(endpoint)
    : new URL(`${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`)

  baseUrl.searchParams.set('token', token)
  return baseUrl.toString()
}

export const useNotificationSocket = () => {
  const socket = ref<WebSocket | null>(null)
  const connectionState = ref<NotificationConnectionState>('offline')
  const notifications = ref<AiNotificationEvent[]>([])
  const errorMessage = ref('')

  const reconnectAttempts = ref(0)
  const seenNotificationIds = new Set<number>()

  let manualClose = false
  let reconnectTimer: number | null = null
  let tokenCache = ''
  let endpointCache = '/ws/notifications'

  const isConnected = computed(() => connectionState.value === 'connected' && socket.value !== null)

  const clearReconnect = (): void => {
    if (reconnectTimer !== null) {
      window.clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  const appendNotification = (event: AiNotificationEvent): void => {
    if (seenNotificationIds.has(event.notification_id)) {
      return
    }
    seenNotificationIds.add(event.notification_id)

    notifications.value = [event, ...notifications.value]
  }

  const scheduleReconnect = (): void => {
    if (manualClose || !tokenCache) {
      return
    }

    clearReconnect()
    reconnectAttempts.value += 1
    connectionState.value = 'reconnecting'

    const delay = Math.min(BASE_RECONNECT_DELAY_MS * (2 ** (reconnectAttempts.value - 1)), MAX_RECONNECT_DELAY_MS)
    reconnectTimer = window.setTimeout(() => {
      void connect(tokenCache, endpointCache)
    }, delay)
  }

  const connect = async (token: string, endpoint = '/ws/notifications'): Promise<boolean> => {
    if (!token.trim()) {
      errorMessage.value = 'token is required'
      return false
    }

    tokenCache = token.trim()
    endpointCache = endpoint
    manualClose = false
    clearReconnect()

    if (socket.value) {
      socket.value.close()
      socket.value = null
    }

    connectionState.value = connectionState.value === 'reconnecting' ? 'reconnecting' : 'connecting'
    errorMessage.value = ''

    const nextSocket = new WebSocket(buildNotificationWsUrl(tokenCache, endpointCache))
    socket.value = nextSocket

    nextSocket.onopen = () => {
      reconnectAttempts.value = 0
      connectionState.value = 'connected'
    }

    nextSocket.onmessage = (event: MessageEvent<string>) => {
      try {
        const raw = JSON.parse(event.data) as unknown
        if (!raw || typeof raw !== 'object') {
          return
        }

        const parsed = raw as Partial<AiNotificationEvent>
        if (parsed.type !== 'notification') {
          return
        }

        if (!parsed.notification_id || !parsed.title || !parsed.content || !parsed.created_at) {
          return
        }

        appendNotification(parsed as AiNotificationEvent)
      } catch {
        errorMessage.value = 'Received invalid notification payload.'
      }
    }

    nextSocket.onerror = () => {
      errorMessage.value = 'Notification socket error.'
    }

    nextSocket.onclose = () => {
      socket.value = null
      if (!manualClose) {
        scheduleReconnect()
      } else {
        connectionState.value = 'offline'
      }
    }

    return true
  }

  const mergeWithPolled = (items: AiNotificationEvent[]): void => {
    items.forEach((item) => appendNotification(item))
  }

  const disconnect = (): void => {
    manualClose = true
    clearReconnect()
    if (socket.value) {
      socket.value.close()
      socket.value = null
    }
    connectionState.value = 'offline'
  }

  if (getCurrentInstance()) {
    onBeforeUnmount(() => {
      disconnect()
    })
  }

  return {
    connect,
    connectionState,
    disconnect,
    errorMessage,
    isConnected,
    mergeWithPolled,
    notifications,
  }
}
