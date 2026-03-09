<template>
  <div class="min-h-screen bg-slate-50 pb-12 font-sans">
    <HomeHeader />

    <main class="max-w-4xl mx-auto pt-28 px-4">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-3xl font-extrabold text-slate-800 flex items-center gap-3 tracking-tight">
            <div class="p-2 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center"><el-icon><Bell /></el-icon></div>
            消息中心
          </h1>
          <p class="text-slate-500 mt-2">查看您的所有互动和系统通知</p>
        </div>
        <el-button @click="markAllAsRead" type="primary" round size="large" class="shadow-md hover:shadow-lg transition-shadow" :disabled="!hasUnread">全部标记为已读</el-button>
      </div>

      <el-card shadow="never" class="border-none rounded-3xl p-4 shadow-sm bg-white" v-loading="loading">
        <el-tabs v-model="activeTab" class="w-full">
          <el-tab-pane label="全部消息" name="all">
            <div class="space-y-4 mt-2">
              <div v-for="notification in notifications" :key="notification.id" 
                   class="p-5 rounded-2xl border flex gap-5 transition-all duration-300 relative cursor-pointer hover:shadow-md hover:-translate-y-0.5"
                   :class="{'bg-blue-50/40 border-blue-100': !notification.is_read, 'bg-white border-slate-100': notification.is_read}"
                   @click="handleNotificationClick(notification)">
                
                <!-- Icon based on type -->
                <div class="w-12 h-12 rounded-full flex items-center justify-center shrink-0 shadow-sm"
                     :class="getIconClass(notification.type)">
                  <el-icon class="text-xl"><component :is="getIconComponent(notification.type)" /></el-icon>
                </div>

                <div class="flex-1 pt-1">
                  <div class="flex justify-between items-start mb-2">
                    <h4 class="font-bold text-slate-800 text-lg leading-tight">{{ notification.title }}</h4>
                    <span class="text-xs text-slate-400 whitespace-nowrap ml-4 font-medium">{{ new Date(notification.created_at).toLocaleString() }}</span>
                  </div>
                  <p class="text-slate-600 leading-relaxed">{{ notification.content }}</p>
                </div>

                <!-- Unread dot -->
                <div v-if="!notification.is_read" class="absolute top-6 right-6 w-3 h-3 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]"></div>
              </div>

              <el-empty v-if="notifications.length === 0" description="暂无新消息" class="py-12" />
            </div>
            
            <div class="mt-8 flex justify-center pb-4" v-if="total > 0">
              <el-pagination v-model:current-page="page" :page-size="pageSize" layout="prev, pager, next" :total="total" @current-change="fetchNotifications" background />
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="系统通知" name="system">
            <el-empty description="此分类下暂无内容" class="py-12" />
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, ChatDotRound, Star, User, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import HomeHeader from '@/components/HomeHeader.vue'

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
