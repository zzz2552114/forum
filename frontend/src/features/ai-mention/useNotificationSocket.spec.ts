import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { buildNotificationWsUrl, useNotificationSocket } from './useNotificationSocket'

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
  vi.useRealTimers()
})

describe('buildNotificationWsUrl', () => {
  it('injects token query parameter', () => {
    const url = buildNotificationWsUrl('abc123', 'ws://localhost/ws/notifications')
    expect(url).toContain('/ws/notifications')
    expect(url).toContain('token=abc123')
  })
})

describe('useNotificationSocket', () => {
  it('connects and consumes notification events', async () => {
    const client = useNotificationSocket()

    const connected = await client.connect('token-1', 'ws://localhost/ws/notifications')
    expect(connected).toBe(true)
    expect(MockWebSocket.instances).toHaveLength(1)

    MockWebSocket.instances[0].emitOpen()
    expect(client.connectionState.value).toBe('connected')

    MockWebSocket.instances[0].emitMessage(JSON.stringify({
      type: 'notification',
      notification_id: 10,
      task_id: 'task-1',
      task_status: 'succeeded',
      title: 'AI 完成',
      content: 'done',
      target_type: 'post',
      target_id: 5,
      created_at: '2026-03-08T10:00:00',
    }))

    MockWebSocket.instances[0].emitMessage(JSON.stringify({
      type: 'notification',
      notification_id: 10,
      task_id: 'task-1',
      task_status: 'succeeded',
      title: 'AI 完成',
      content: 'done',
      target_type: 'post',
      target_id: 5,
      created_at: '2026-03-08T10:00:00',
    }))

    expect(client.notifications.value).toHaveLength(1)
    expect(client.notifications.value[0].task_id).toBe('task-1')
  })

  it('merges polled notifications with dedupe', async () => {
    const client = useNotificationSocket()
    client.mergeWithPolled([
      {
        type: 'notification',
        notification_id: 1,
        task_id: 'a',
        task_status: 'queued',
        title: '1',
        content: '1',
        created_at: '2026-03-08T10:00:00',
      },
      {
        type: 'notification',
        notification_id: 1,
        task_id: 'a',
        task_status: 'queued',
        title: '1',
        content: '1',
        created_at: '2026-03-08T10:00:00',
      },
    ])

    expect(client.notifications.value).toHaveLength(1)
  })
})
