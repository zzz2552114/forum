import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { formatDisplayTime, normalizeIncomingMessage } from './format'
import { useRealtimeChat } from './useRealtimeChat'

class MockWebSocket {
  static instances: MockWebSocket[] = []

  url: string
  sent: string[] = []
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent<string>) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null

  constructor(url: string) {
    this.url = url
    MockWebSocket.instances.push(this)
  }

  send(payload: string): void {
    this.sent.push(payload)
  }

  close(): void {
    this.onclose?.(new CloseEvent('close'))
  }

  emitOpen(): void {
    this.onopen?.(new Event('open'))
  }

  emitMessage(payload: string): void {
    this.onmessage?.(new MessageEvent('message', { data: payload }))
  }
}

beforeEach(() => {
  MockWebSocket.instances = []
  vi.stubGlobal('WebSocket', MockWebSocket as unknown as typeof WebSocket)
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('useRealtimeChat', () => {
  it('connects and tracks connection state', () => {
    const chat = useRealtimeChat()

    const connected = chat.connect('alice', 'ws://localhost/ws/chat')
    expect(connected).toBe(true)
    expect(MockWebSocket.instances).toHaveLength(1)
    expect(MockWebSocket.instances[0].url).toContain('username=alice')

    MockWebSocket.instances[0].emitOpen()
    expect(chat.isConnected.value).toBe(true)
    expect(chat.isConnecting.value).toBe(false)
  })

  it('queues incoming messages and updates online count', () => {
    const chat = useRealtimeChat()
    chat.connect('alice', 'ws://localhost/ws/chat')
    const socket = MockWebSocket.instances[0]

    socket.emitOpen()
    socket.emitMessage(JSON.stringify({
      type: 'system',
      content: 'alice joined',
      online_count: 1,
      timestamp: '2026-03-07T21:45:00',
      display_time: '03-07 21:45',
    }))
    socket.emitMessage(JSON.stringify({
      type: 'chat',
      username: 'alice',
      content: 'hello',
      timestamp: '2026-03-07T21:46:00',
      display_time: '03-07 21:46',
    }))

    expect(chat.messages.value).toHaveLength(2)
    expect(chat.onlineCount.value).toBe(1)
    expect(chat.messages.value[1].username).toBe('alice')
    expect(chat.messages.value[1].content).toBe('hello')
  })

  it('validates outgoing message before sending', () => {
    const chat = useRealtimeChat()

    expect(chat.sendMessage('hello')).toBe(false)
    expect(chat.connect('alice', 'ws://localhost/ws/chat')).toBe(true)

    const socket = MockWebSocket.instances[0]
    socket.emitOpen()

    expect(chat.sendMessage('   ')).toBe(false)
    expect(chat.sendMessage('x'.repeat(501))).toBe(false)
    expect(chat.sendMessage('hello world')).toBe(true)
    expect(socket.sent[0]).toBe('{"content":"hello world"}')
  })
})

describe('format helpers', () => {
  it('formats display time in MM-DD HH:mm', () => {
    const display = formatDisplayTime(new Date('2026-03-07T13:05:00'))
    expect(display).toMatch(/^\d{2}-\d{2} \d{2}:\d{2}$/)
  })

  it('normalizes valid incoming payload', () => {
    const normalized = normalizeIncomingMessage({
      type: 'chat',
      username: 'bob',
      content: 'hey',
      timestamp: '2026-03-07T21:46:00',
      display_time: '03-07 21:46',
    })

    expect(normalized).not.toBeNull()
    expect(normalized?.type).toBe('chat')
    expect(normalized?.username).toBe('bob')
  })

  it('rejects malformed payload', () => {
    const normalized = normalizeIncomingMessage({ type: 'chat', content: '   ' })
    expect(normalized).toBeNull()
  })
})
