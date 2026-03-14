export type RealtimeEventType = 'chat' | 'system'

export interface RealtimeMessage {
  type: RealtimeEventType
  username?: string
  content: string
  timestamp: string
  display_time: string
  online_count?: number
}

export type RealtimeRoomEventType = 'system' | 'chat' | 'history' | 'error' | 'presence'

export type RealtimeConnectionState = 'connecting' | 'connected' | 'reconnecting' | 'offline'

export interface RealtimeRoomEvent {
  event_id: number
  type: RealtimeRoomEventType
  room: string
  message: string
  content: string
  timestamp: string
  display_time: string
  username?: string
  online_count?: number
  payload?: Record<string, unknown>
}

const ROOM_EVENT_TYPES = new Set<RealtimeRoomEventType>(['system', 'chat', 'history', 'error', 'presence'])
const DISPLAY_TIME_REGEX = /^\d{2}-\d{2} \d{2}:\d{2}$/

const pad = (value: number): string => value.toString().padStart(2, '0')

export const formatDisplayTime = (date: Date): string => {
  return `${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

export const isDisplayTimeValid = (value: string): boolean => DISPLAY_TIME_REGEX.test(value)

export const fallbackDisplayTime = (timestamp?: string): string => {
  const date = timestamp ? new Date(timestamp) : new Date()
  if (Number.isNaN(date.getTime())) {
    return formatDisplayTime(new Date())
  }
  return formatDisplayTime(date)
}

export const normalizeIncomingMessage = (payload: unknown): RealtimeMessage | null => {
  if (!payload || typeof payload !== 'object') {
    return null
  }

  const raw = payload as Record<string, unknown>
  const type = raw.type
  const content = raw.content

  if (type !== 'chat' && type !== 'system') {
    return null
  }
  if (typeof content !== 'string' || !content.trim()) {
    return null
  }

  const timestamp = typeof raw.timestamp === 'string' && raw.timestamp ? raw.timestamp : new Date().toISOString()
  const display_time = typeof raw.display_time === 'string' && isDisplayTimeValid(raw.display_time)
    ? raw.display_time
    : fallbackDisplayTime(timestamp)

  const message: RealtimeMessage = {
    type,
    content: content.trim(),
    timestamp,
    display_time,
  }

  if (typeof raw.username === 'string' && raw.username.trim()) {
    message.username = raw.username.trim()
  }

  if (typeof raw.online_count === 'number' && Number.isFinite(raw.online_count)) {
    message.online_count = raw.online_count
  }

  return message
}

export const normalizeRoomEvent = (payload: unknown): RealtimeRoomEvent | null => {
  if (!payload || typeof payload !== 'object') {
    return null
  }

  const raw = payload as Record<string, unknown>
  const type = raw.type
  const room = raw.room

  if (typeof type !== 'string' || !ROOM_EVENT_TYPES.has(type as RealtimeRoomEventType)) {
    return null
  }
  if (typeof room !== 'string' || !room.trim()) {
    return null
  }

  const messageCandidate = typeof raw.message === 'string' ? raw.message : raw.content
  if (typeof messageCandidate !== 'string' || !messageCandidate.trim()) {
    return null
  }

  const event_id = typeof raw.event_id === 'number' && Number.isFinite(raw.event_id)
    ? raw.event_id
    : 0
  const timestamp = typeof raw.timestamp === 'string' && raw.timestamp
    ? raw.timestamp
    : new Date().toISOString()
  const display_time = typeof raw.display_time === 'string' && isDisplayTimeValid(raw.display_time)
    ? raw.display_time
    : fallbackDisplayTime(timestamp)

  const event: RealtimeRoomEvent = {
    event_id,
    type: type as RealtimeRoomEventType,
    room: room.trim(),
    message: messageCandidate.trim(),
    content: messageCandidate.trim(),
    timestamp,
    display_time,
  }

  if (typeof raw.username === 'string' && raw.username.trim()) {
    event.username = raw.username.trim()
  }

  if (typeof raw.online_count === 'number' && Number.isFinite(raw.online_count)) {
    event.online_count = raw.online_count
  }

  if (raw.payload && typeof raw.payload === 'object') {
    event.payload = raw.payload as Record<string, unknown>
  }

  return event
}
