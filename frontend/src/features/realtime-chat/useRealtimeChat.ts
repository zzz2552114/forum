import { computed, getCurrentInstance, onBeforeUnmount, ref } from 'vue'

import { normalizeIncomingMessage, type RealtimeMessage } from './format'

const MAX_CONTENT_LENGTH = 500
const MAX_STORED_MESSAGES = 100

export const buildWebSocketUrl = (username: string, endpoint = '/ws/chat'): string => {
  const url = endpoint.startsWith('ws://') || endpoint.startsWith('wss://')
    ? new URL(endpoint)
    : new URL(
      `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`,
    )

  url.searchParams.set('username', username)
  return url.toString()
}

export const useRealtimeChat = () => {
  const socket = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const currentUsername = ref('')
  const messages = ref<RealtimeMessage[]>([])
  const onlineCount = ref(0)
  const errorMessage = ref('')

  const canSend = computed(() => isConnected.value && socket.value !== null)

  const appendMessage = (message: RealtimeMessage): void => {
    const nextMessages = [...messages.value, message]
    messages.value = nextMessages.slice(Math.max(0, nextMessages.length - MAX_STORED_MESSAGES))

    if (typeof message.online_count === 'number') {
      onlineCount.value = message.online_count
    }
  }

  const disconnect = (): void => {
    if (socket.value) {
      socket.value.close()
      socket.value = null
    }
    isConnected.value = false
    isConnecting.value = false
  }

  const connect = (username: string, endpoint = '/ws/chat'): boolean => {
    const trimmedName = username.trim()
    if (!trimmedName) {
      errorMessage.value = 'Username is required.'
      return false
    }

    disconnect()
    errorMessage.value = ''
    currentUsername.value = trimmedName
    isConnecting.value = true

    const nextSocket = new WebSocket(buildWebSocketUrl(trimmedName, endpoint))
    socket.value = nextSocket

    nextSocket.onopen = () => {
      isConnected.value = true
      isConnecting.value = false
    }

    nextSocket.onmessage = (event: MessageEvent<string>) => {
      try {
        const raw = JSON.parse(event.data) as unknown
        const message = normalizeIncomingMessage(raw)
        if (message) {
          appendMessage(message)
        }
      } catch {
        errorMessage.value = 'Received invalid message payload.'
      }
    }

    nextSocket.onerror = () => {
      errorMessage.value = 'WebSocket connection error.'
    }

    nextSocket.onclose = () => {
      isConnected.value = false
      isConnecting.value = false
      socket.value = null
    }

    return true
  }

  const sendMessage = (content: string): boolean => {
    if (!canSend.value || !socket.value) {
      errorMessage.value = 'Socket is not connected.'
      return false
    }

    const trimmedContent = content.trim()
    if (!trimmedContent) {
      errorMessage.value = 'Message cannot be empty.'
      return false
    }

    if (trimmedContent.length > MAX_CONTENT_LENGTH) {
      errorMessage.value = `Message too long (max ${MAX_CONTENT_LENGTH} chars).`
      return false
    }

    socket.value.send(JSON.stringify({ content: trimmedContent }))
    return true
  }

  if (getCurrentInstance()) {
    onBeforeUnmount(disconnect)
  }

  return {
    canSend,
    connect,
    currentUsername,
    disconnect,
    errorMessage,
    isConnected,
    isConnecting,
    messages,
    onlineCount,
    sendMessage,
  }
}
