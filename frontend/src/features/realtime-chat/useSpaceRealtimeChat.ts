import { computed, getCurrentInstance, onBeforeUnmount, ref } from 'vue'

import {
  normalizeRoomEvent,
  type RealtimeConnectionState,
  type RealtimeRoomEvent,
} from './format'

const MAX_CONTENT_LENGTH = 500
const MAX_STORED_MESSAGES = 200
const BASE_RECONNECT_DELAY_MS = 500
const MAX_RECONNECT_DELAY_MS = 8000
const HEARTBEAT_INTERVAL_MS = 15000
const NON_RETRIABLE_CLOSE_CODES = new Set([1008])

export interface SpaceRealtimeChatOptions {
  spaceId: number
  sectionId: number
  username: string
  token?: string
  endpoint?: string
  autoReconnect?: boolean
}

interface ConnectOptions {
  lastEventId?: number
}

interface MutableContext {
  spaceId: number
  sectionId: number
  username: string
  token: string
  endpoint: string
  autoReconnect: boolean
}

const isAbsoluteWsUrl = (value: string): boolean => value.startsWith('ws://') || value.startsWith('wss://')

export const buildRoomWebSocketUrl = (
  options: {
    spaceId: number
    sectionId: number
    username: string
    token?: string
    endpoint?: string
    lastEventId?: number
  },
): string => {
  const endpoint = options.endpoint || '/ws/chat'
  const baseUrl = isAbsoluteWsUrl(endpoint)
    ? new URL(endpoint)
    : new URL(`${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`)

  const normalizedPath = baseUrl.pathname.replace(/\/$/, '')
  baseUrl.pathname = `${normalizedPath}/${options.spaceId}/${options.sectionId}`
  baseUrl.searchParams.set('username', options.username.trim())

  const token = (options.token || '').trim()
  if (token) {
    baseUrl.searchParams.set('token', token)
  }

  if (typeof options.lastEventId === 'number' && Number.isFinite(options.lastEventId) && options.lastEventId > 0) {
    baseUrl.searchParams.set('last_event_id', String(options.lastEventId))
  }

  return baseUrl.toString()
}

export const useSpaceRealtimeChat = (initialOptions: SpaceRealtimeChatOptions) => {
  const socket = ref<WebSocket | null>(null)
  const connectionState = ref<RealtimeConnectionState>('offline')
  const messages = ref<RealtimeRoomEvent[]>([])
  const onlineCount = ref(0)
  const errorMessage = ref('')
  const currentEventId = ref(0)

  const reconnectAttempts = ref(0)
  const outboundQueue = ref<string[]>([])

  const context = ref<MutableContext>({
    spaceId: initialOptions.spaceId,
    sectionId: initialOptions.sectionId,
    username: initialOptions.username,
    token: initialOptions.token || '',
    endpoint: initialOptions.endpoint || '/ws/chat',
    autoReconnect: initialOptions.autoReconnect ?? true,
  })

  const seenEventIds = new Set<number>()

  let manualClose = false
  let reconnectTimer: number | null = null
  let heartbeatTimer: number | null = null

  const isConnected = computed(() => connectionState.value === 'connected' && socket.value !== null)
  const canSend = computed(() => isConnected.value)

  const clearReconnectTimer = (): void => {
    if (reconnectTimer !== null) {
      window.clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  const stopHeartbeat = (): void => {
    if (heartbeatTimer !== null) {
      window.clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  const appendEvent = (event: RealtimeRoomEvent): void => {
    if (event.event_id > 0) {
      if (seenEventIds.has(event.event_id)) {
        return
      }
      seenEventIds.add(event.event_id)
      currentEventId.value = Math.max(currentEventId.value, event.event_id)
    }

    if (typeof event.online_count === 'number') {
      onlineCount.value = event.online_count
    }

    const next = [...messages.value, event]
    messages.value = next.slice(Math.max(0, next.length - MAX_STORED_MESSAGES))
  }

  const handleIncomingPayload = (data: string): void => {
    let raw: unknown
    try {
      raw = JSON.parse(data) as unknown
    } catch {
      errorMessage.value = 'Received invalid message payload.'
      return
    }

    const event = normalizeRoomEvent(raw)
    if (!event) {
      errorMessage.value = 'Received unknown room event.'
      return
    }

    if (event.type === 'history' && event.payload && Array.isArray(event.payload.events)) {
      const replayEvents = event.payload.events
        .map((item) => normalizeRoomEvent(item))
        .filter((item): item is RealtimeRoomEvent => item !== null)
      replayEvents.forEach((item) => appendEvent(item))
      appendEvent(event)
      return
    }

    appendEvent(event)
  }

  const flushOutboundQueue = (): void => {
    if (!socket.value || socket.value.readyState !== WebSocket.OPEN || outboundQueue.value.length === 0) {
      return
    }

    const queued = [...outboundQueue.value]
    outboundQueue.value = []
    queued.forEach((payload) => socket.value?.send(payload))
  }

  const startHeartbeat = (): void => {
    stopHeartbeat()
    heartbeatTimer = window.setInterval(() => {
      if (!socket.value || socket.value.readyState !== WebSocket.OPEN) {
        return
      }
      socket.value.send(JSON.stringify({ type: 'ping' }))
    }, HEARTBEAT_INTERVAL_MS)
  }

  const scheduleReconnect = (): void => {
    if (!context.value.autoReconnect || manualClose) {
      return
    }

    clearReconnectTimer()
    reconnectAttempts.value += 1
    connectionState.value = 'reconnecting'
    const delay = Math.min(BASE_RECONNECT_DELAY_MS * (2 ** (reconnectAttempts.value - 1)), MAX_RECONNECT_DELAY_MS)

    reconnectTimer = window.setTimeout(() => {
      void connect({ lastEventId: currentEventId.value })
    }, delay)
  }

  const disconnect = (): void => {
    manualClose = true
    clearReconnectTimer()
    stopHeartbeat()

    if (socket.value) {
      socket.value.close()
      socket.value = null
    }

    connectionState.value = 'offline'
  }

  const connect = async (options?: ConnectOptions): Promise<boolean> => {
    const username = context.value.username.trim()
    if (!username) {
      errorMessage.value = 'Username is required.'
      return false
    }

    manualClose = false
    clearReconnectTimer()
    stopHeartbeat()

    if (socket.value) {
      socket.value.close()
      socket.value = null
    }

    errorMessage.value = ''
    if (connectionState.value !== 'reconnecting') {
      connectionState.value = 'connecting'
    }

    const nextSocket = new WebSocket(buildRoomWebSocketUrl({
      spaceId: context.value.spaceId,
      sectionId: context.value.sectionId,
      username,
      token: context.value.token,
      endpoint: context.value.endpoint,
      lastEventId: options?.lastEventId,
    }))

    socket.value = nextSocket

    nextSocket.onopen = () => {
      reconnectAttempts.value = 0
      connectionState.value = 'connected'
      startHeartbeat()
      flushOutboundQueue()
    }

    nextSocket.onmessage = (event: MessageEvent<string>) => {
      handleIncomingPayload(event.data)
    }

    nextSocket.onerror = () => {
      errorMessage.value = '即时聊天连接失败，请确认后端服务和 /ws 代理是否可用。'
    }

    nextSocket.onclose = (event: CloseEvent) => {
      stopHeartbeat()
      socket.value = null

      if (event.reason) {
        errorMessage.value = event.reason
      } else if (event.code === 1008) {
        errorMessage.value = '即时聊天连接被服务器拒绝，请重新登录后再试。'
      }

      if (!manualClose && !NON_RETRIABLE_CLOSE_CODES.has(event.code)) {
        scheduleReconnect()
      } else {
        connectionState.value = 'offline'
      }
    }

    return true
  }

  const reconfigure = async (next: Partial<SpaceRealtimeChatOptions>): Promise<boolean> => {
    context.value = {
      ...context.value,
      spaceId: next.spaceId ?? context.value.spaceId,
      sectionId: next.sectionId ?? context.value.sectionId,
      username: next.username ?? context.value.username,
      token: next.token ?? context.value.token,
      endpoint: next.endpoint ?? context.value.endpoint,
      autoReconnect: next.autoReconnect ?? context.value.autoReconnect,
    }

    seenEventIds.clear()
    messages.value = []
    currentEventId.value = 0

    return connect()
  }

  const sendMessage = (content: string): boolean => {
    const trimmed = content.trim()
    if (!trimmed) {
      errorMessage.value = 'Message cannot be empty.'
      return false
    }

    if (trimmed.length > MAX_CONTENT_LENGTH) {
      errorMessage.value = `Message too long (max ${MAX_CONTENT_LENGTH} chars).`
      return false
    }

    const payload = JSON.stringify({ content: trimmed })

    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      socket.value.send(payload)
      return true
    }

    outboundQueue.value.push(payload)
    if (connectionState.value === 'offline') {
      void connect({ lastEventId: currentEventId.value })
    }
    return true
  }

  const clearMessages = (): void => {
    messages.value = []
    seenEventIds.clear()
    currentEventId.value = 0
  }

  if (getCurrentInstance()) {
    onBeforeUnmount(() => {
      disconnect()
    })
  }

  return {
    canSend,
    clearMessages,
    connect,
    connectionState,
    currentEventId,
    disconnect,
    errorMessage,
    isConnected,
    messages,
    onlineCount,
    outboundQueue,
    reconfigure,
    sendMessage,
  }
}
