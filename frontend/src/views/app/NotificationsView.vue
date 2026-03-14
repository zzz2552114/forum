<template>
  <div class="max-w-4xl mx-auto py-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-slate-800 flex items-center gap-2">
        <el-icon class="text-blue-600"><Bell /></el-icon>
        通知中心
      </h1>
      <el-button @click="markAllAsRead" type="primary" plain :disabled="!hasUnread">全部标记为已读</el-button>
    </div>

    <el-card shadow="never" class="border-none rounded-2xl p-2" v-loading="loading">
      <div class="space-y-2">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="p-4 rounded-xl border flex gap-4 transition-colors relative cursor-pointer hover:bg-slate-50"
          :class="{ 'bg-blue-50/30 border-blue-100': !notification.is_read, 'bg-white border-slate-100': notification.is_read }"
          @click="handleNotificationClick(notification)"
        >
          <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0" :class="getIconClass(notification.type)">
            <el-icon class="text-lg"><component :is="getIconComponent(notification.type)" /></el-icon>
          </div>

          <div class="flex-1">
            <div class="flex justify-between items-start mb-1">
              <h4 class="font-bold text-slate-800">{{ notification.title }}</h4>
              <span class="text-xs text-slate-400 whitespace-nowrap ml-4">{{ new Date(notification.created_at).toLocaleString() }}</span>
            </div>
            <p class="text-sm text-slate-600">{{ notification.content }}</p>
          </div>

          <div v-if="!notification.is_read" class="absolute top-5 right-4 w-2 h-2 rounded-full bg-blue-500"></div>
        </div>

        <el-empty v-if="notifications.length === 0" description="ææ éç¥" />
      </div>

      <div class="mt-6 flex justify-center" v-if="total > 0">
        <el-pagination v-model:current-page="page" :page-size="pageSize" layout="prev, pager, next" :total="total" @current-change="fetchNotifications" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, ChatDotRound, Star, User, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import { useNotificationSocket } from '@/features/ai-mention/useNotificationSocket'
import { buildSpacesRouteQuery } from '@/features/notifications/navigation'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const notifications = ref<any[]>([])
const page = ref(1)
const pageSize = ref(15)
const total = ref(0)

const {
  connect: connectNotificationSocket,
  notifications: pushedNotifications,
} = useNotificationSocket()

const hasUnread = computed(() => notifications.value.some((n) => !n.is_read))

const typeClassMap: Record<string, string> = {
  comment_reply: 'bg-green-100 text-green-600',
  post_like: 'bg-red-100 text-red-600',
  post_bookmark: 'bg-orange-100 text-orange-600',
  chat_mention: 'bg-blue-100 text-blue-600',
  ai_reply: 'bg-indigo-100 text-indigo-600',
}

const typeIconMap: Record<string, any> = {
  comment_reply: ChatDotRound,
  post_like: Star,
  post_bookmark: Star,
  chat_mention: User,
  ai_reply: InfoFilled,
}

const getIconClass = (type: string) => typeClassMap[type] || 'bg-slate-100 text-slate-600'
const getIconComponent = (type: string) => typeIconMap[type] || Bell

const normalizeSocketNotification = (item: any) => ({
  id: item.notification_id,
  type: item.notification_type || 'system',
  title: item.title,
  content: item.content,
  is_read: false,
  target_type: item.target_type,
  target_id: item.target_id,
  extra_payload: item.extra_payload || null,
  created_at: item.created_at,
})

const upsertNotification = (item: any) => {
  const existing = notifications.value.find((x) => x.id === item.id)
  if (existing) {
    Object.assign(existing, item)
    return
  }
  notifications.value = [item, ...notifications.value]
  total.value += 1
}

const fetchNotifications = async () => {
  loading.value = true
  try {
    const res: any = await request.get('/me/notifications', {
      params: { page: page.value, page_size: pageSize.value },
    })
    notifications.value = res.items || []
    total.value = res.pagination?.total || 0
  } finally {
    loading.value = false
  }
}

const markAllAsRead = async () => {
  try {
    await request.patch('/me/notifications/read', { notification_ids: [] })
    notifications.value.forEach((n) => {
      n.is_read = true
    })
    ElMessage.success('已全部标记为已读')
  } catch {
    ElMessage.error('标记已读失败')
  }
}

const resolveNotificationQuery = async (notification: any): Promise<Record<string, string>> => {
  const directQuery = buildSpacesRouteQuery(notification)
  if (directQuery.spaceId) {
    return directQuery
  }

  if (notification.target_type === 'space' && notification.target_id) {
    return {
      spaceId: String(notification.target_id),
      sectionId: '2',
    }
  }

  if (notification.target_type === 'post' && notification.target_id) {
    const postContext: any = await request.get(`/posts/${notification.target_id}/context`)
    return {
      spaceId: String(postContext.space_id),
      sectionId: '1',
      postId: String(postContext.id),
    }
  }

  if (notification.target_type === 'comment' && notification.target_id) {
    const commentContext: any = await request.get(`/comments/${notification.target_id}/context`)
    return {
      spaceId: String(commentContext.space_id),
      sectionId: '1',
      postId: String(commentContext.post_id),
      commentId: String(commentContext.id),
    }
  }

  return directQuery
}

const handleNotificationClick = async (notification: any) => {
  if (!notification.is_read) {
    try {
      await request.patch(`/me/notifications/${notification.id}/read`)
      notification.is_read = true
    } catch {
      notification.is_read = true
    }
  }

  try {
    const query = await resolveNotificationQuery(notification)
    if (Object.keys(query).length > 0) {
      router.push({ path: '/spaces', query })
      return
    }
  } catch {
    ElMessage.error('通知跳转失败')
  }

  router.push('/spaces')
}

watch(
  () => pushedNotifications.value.length,
  () => {
    pushedNotifications.value
      .map((item) => normalizeSocketNotification(item))
      .forEach(upsertNotification)
  },
)

onMounted(async () => {
  await fetchNotifications()

  const token = (authStore.token || '').trim()
  if (token) {
    void connectNotificationSocket(token)
  }
})
</script>
