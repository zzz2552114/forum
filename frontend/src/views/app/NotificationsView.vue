<template>
  <div class="max-w-4xl mx-auto py-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-slate-800 flex items-center gap-2">
        <el-icon class="text-blue-600"><Bell /></el-icon> 消息中心
      </h1>
      <el-button @click="markAllAsRead" type="primary" plain :disabled="!hasUnread">全部标记为已读</el-button>
    </div>

    <el-card shadow="never" class="border-none rounded-2xl p-2" v-loading="loading">
      <el-tabs v-model="activeTab" class="w-full">
        <el-tab-pane label="全部消息" name="all">
          <div class="space-y-2">
            <div v-for="notification in notifications" :key="notification.id" 
                 class="p-4 rounded-xl border flex gap-4 transition-colors relative cursor-pointer hover:bg-slate-50"
                 :class="{'bg-blue-50/30 border-blue-100': !notification.is_read, 'bg-white border-slate-100': notification.is_read}"
                 @click="handleNotificationClick(notification)">
              
              <!-- Icon based on type -->
              <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
                   :class="getIconClass(notification.type)">
                <el-icon class="text-lg"><component :is="getIconComponent(notification.type)" /></el-icon>
              </div>

              <div class="flex-1">
                <div class="flex justify-between items-start mb-1">
                  <h4 class="font-bold text-slate-800">{{ notification.title }}</h4>
                  <span class="text-xs text-slate-400 whitespace-nowrap ml-4">{{ new Date(notification.created_at).toLocaleString() }}</span>
                </div>
                <p class="text-sm text-slate-600">{{ notification.content }}</p>
              </div>

              <!-- Unread dot -->
              <div v-if="!notification.is_read" class="absolute top-5 right-4 w-2 h-2 rounded-full bg-blue-500"></div>
            </div>

            <el-empty v-if="notifications.length === 0" description="暂无新消息" />
          </div>
          
          <div class="mt-6 flex justify-center" v-if="total > 0">
            <el-pagination v-model:current-page="page" :page-size="pageSize" layout="prev, pager, next" :total="total" @current-change="fetchNotifications" />
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="系统通知" name="system">
          <el-empty description="此分类下暂无内容" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, ChatDotRound, Star, User, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const activeTab = ref('all')
const loading = ref(false)
const notifications = ref<any[]>([])
const page = ref(1)
const pageSize = ref(15)
const total = ref(0)

const hasUnread = computed(() => notifications.value.some(n => !n.is_read))

const getIconClass = (type: string) => {
  const map: Record<string, string> = {
    'comment': 'bg-green-100 text-green-600',
    'mention': 'bg-blue-100 text-blue-600',
    'like': 'bg-red-100 text-red-600',
    'system': 'bg-orange-100 text-orange-600'
  }
  return map[type] || 'bg-slate-100 text-slate-600'
}

const getIconComponent = (type: string) => {
  const map: Record<string, any> = {
    'comment': ChatDotRound,
    'mention': User,
    'like': Star,
    'system': InfoFilled
  }
  return map[type] || Bell
}

const fetchNotifications = async () => {
  loading.value = true
  try {
    const res: any = await request.get('/me/notifications', {
      params: { page: page.value, page_size: pageSize.value }
    })
    notifications.value = res.items || []
    total.value = res.pagination?.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const markAllAsRead = async () => {
  try {
    await request.post('/me/notifications/read', { notification_ids: [] })
    notifications.value.forEach(n => n.is_read = true)
    ElMessage.success('已全部标记为已读')
  } catch (e) {
    console.error(e)
  }
}

const handleNotificationClick = async (notification: any) => {
  if (!notification.is_read) {
    try {
      await request.post('/me/notifications/read', { notification_ids: [notification.id] })
      notification.is_read = true
    } catch (e) {
      console.error(e)
    }
  }
  
  if (notification.target_type === 'post' && notification.target_id) {
    router.push(`/posts/${notification.target_id}`)
  }
}

onMounted(() => {
  fetchNotifications()
})
</script>
