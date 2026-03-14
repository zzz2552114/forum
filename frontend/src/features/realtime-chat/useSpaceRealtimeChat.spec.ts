import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { buildRoomWebSocketUrl, useSpaceRealtimeChat } from './useSpaceRealtimeChat'

class MockWebSocket {
  static instances: MockWebSocket[] = []
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  url: string
  sent: string[] = []
  readyState = MockWebSocket.CONNECTING

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
    this.emitClose()
  }

  emitClose(options?: { code?: number; reason?: string }): void {
    this.readyState = MockWebSocket.CLOSED
    this.onclose?.(new CloseEvent('close', {
      code: options?.code,
      reason: options?.reason,
    }))
  }

  emitOpen(): void {
    this.readyState = MockWebSocket.OPEN
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
  vi.useRealTimers()
  vi.unstubAllGlobals()
})

describe('buildRoomWebSocketUrl', () => {
  it('builds path params and query correctly', () => {
    const url = buildRoomWebSocketUrl({
      spaceId: 7,
      sectionId: 21,
      username: 'alice',
      endpoint: 'ws://localhost/ws/chat',
      lastEventId: 33,
    })

    expect(url).toContain('/ws/chat/7/21')
    expect(url).toContain('username=alice')
    expect(url).toContain('last_event_id=33')
  })
})

describe('useSpaceRealtimeChat', () => {
  it('connects and receives room events', async () => {
    const chat = useSpaceRealtimeChat({
      spaceId: 1,
      sectionId: 2,
      username: 'alice',
      endpoint: 'ws://localhost/ws/chat',
    })

    await chat.connect()
    expect(MockWebSocket.instances).toHaveLength(1)
    expect(MockWebSocket.instances[0].url).toContain('/ws/chat/1/2')

    MockWebSocket.instances[0].emitOpen()
    expect(chat.isConnected.value).toBe(true)
    expect(chat.connectionState.value).toBe('connected')

    MockWebSocket.instances[0].emitMessage(JSON.stringify({
      event_id: 1,
      type: 'chat',
      room: '1:2',
      message: 'hello',
      content: 'hello',
      username: 'alice',
      online_count: 3,
      timestamp: '2026-03-08T10:10:00',
      display_time: '03-08 10:10',
    }))

    expect(chat.messages.value).toHaveLength(1)
    expect(chat.messages.value[0].content).toBe('hello')
    expect(chat.onlineCount.value).toBe(3)
  })

  it('replays history payload and de-duplicates by event_id', async () => {
    const chat = useSpaceRealtimeChat({
      spaceId: 5,
      sectionId: 6,
      username: 'bob',
      endpoint: 'ws://localhost/ws/chat',
    })

    await chat.connect()
    const socket = MockWebSocket.instances[0]
    socket.emitOpen()

    socket.emitMessage(JSON.stringify({
      event_id: 10,
      type: 'history',
      room: '5:6',
      message: 'history replay',
      content: 'history replay',
      payload: {
        events: [
          {
            event_id: 8,
            type: 'chat',
            room: '5:6',
            message: 'm1',
            content: 'm1',
            username: 'a',
            timestamp: '2026-03-08T10:00:00',
            display_time: '03-08 10:00',
          },
          {
            event_id: 9,
            type: 'chat',
            room: '5:6',
            message: 'm2',
            content: 'm2',
            username: 'b',
            timestamp: '2026-03-08T10:01:00',
            display_time: '03-08 10:01',
          },
        ],
      },
      timestamp: '2026-03-08T10:02:00',
      display_time: '03-08 10:02',
    }))

    socket.emitMessage(JSON.stringify({
      event_id: 9,
      type: 'chat',
      room: '5:6',
      message: 'm2-duplicate',
      content: 'm2-duplicate',
      username: 'b',
      timestamp: '2026-03-08T10:03:00',
      display_time: '03-08 10:03',
    }))

    expect(chat.messages.value.map((item) => item.event_id)).toEqual([8, 9, 10])
  })

  it('queues message and flushes after reconnect', async () => {
    vi.useFakeTimers()

    const chat = useSpaceRealtimeChat({
      spaceId: 9,
      sectionId: 9,
      username: 'eve',
      endpoint: 'ws://localhost/ws/chat',
    })

    await chat.connect()
    const firstSocket = MockWebSocket.instances[0]
    firstSocket.emitOpen()

    firstSocket.close()
    expect(chat.connectionState.value).toBe('reconnecting')

    const queued = chat.sendMessage('queued-message')
    expect(queued).toBe(true)
    expect(chat.outboundQueue.value).toHaveLength(1)

    vi.advanceTimersByTime(500)
    expect(MockWebSocket.instances).toHaveLength(2)

    const secondSocket = MockWebSocket.instances[1]
    secondSocket.emitOpen()

    expect(secondSocket.sent).toContain('{"content":"queued-message"}')
    expect(chat.outboundQueue.value).toHaveLength(0)
  })


  it('does not reconnect when server rejects the socket', async () => {
    vi.useFakeTimers()

    const chat = useSpaceRealtimeChat({
      spaceId: 3,
      sectionId: 4,
      username: 'mallory',
      endpoint: 'ws://localhost/ws/chat',
    })

    await chat.connect()
    const socket = MockWebSocket.instances[0]
    socket.emitOpen()
    socket.emitClose({ code: 1008, reason: 'invalid token or username mismatch' })

    expect(chat.connectionState.value).toBe('offline')
    expect(chat.errorMessage.value).toBe('invalid token or username mismatch')

    vi.advanceTimersByTime(5000)
    expect(MockWebSocket.instances).toHaveLength(1)
  })
})
