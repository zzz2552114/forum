export type AiMentionTaskStatus = 'queued' | 'running' | 'succeeded' | 'failed' | 'timeout'

export interface AiMentionTask {
  id: string
  user_id: number
  comment_id: number
  post_id: number
  space_id: number
  prompt: string
  status: AiMentionTaskStatus
  retry_count: number
  result?: string
  error?: string
  created_at: string
  updated_at: string
  finished_at?: string
  reply_comment_id?: number
}

export interface AiNotificationEvent {
  type: 'notification'
  notification_id: number
  notification_type?: string
  task_id?: string
  task_status?: AiMentionTaskStatus
  title: string
  content: string
  is_read?: boolean
  target_type?: string
  target_id?: number
  extra_payload?: Record<string, unknown> | null
  created_at: string
  [key: string]: unknown
}