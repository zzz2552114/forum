export interface NotificationLike {
  target_type?: string
  target_id?: number
  extra_payload?: Record<string, unknown> | null
}

const asNumber = (value: unknown): number | null => {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value
  }
  if (typeof value === 'string' && value.trim()) {
    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
}

export const buildSpacesRouteQuery = (notification: NotificationLike): Record<string, string> => {
  const payload = notification.extra_payload || {}
  const query: Record<string, string> = {}

  const spaceId = asNumber(payload.space_id) ?? (notification.target_type === 'space' ? asNumber(notification.target_id) : null)
  const postId = asNumber(payload.post_id) ?? (notification.target_type === 'post' ? asNumber(notification.target_id) : null)
  const commentId = asNumber(payload.reply_comment_id) ?? asNumber(payload.comment_id) ?? (notification.target_type === 'comment' ? asNumber(notification.target_id) : null)
  const sectionId = asNumber(payload.section_id) ?? (notification.target_type === 'space' ? 2 : null)

  if (spaceId) {
    query.spaceId = String(spaceId)
  }
  if (sectionId) {
    query.sectionId = String(sectionId)
  }
  if (postId) {
    query.postId = String(postId)
  }
  if (commentId) {
    query.commentId = String(commentId)
  }

  if (!query.sectionId && (query.postId || query.commentId)) {
    query.sectionId = '1'
  }

  return query
}