<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Bell, Setting, UserFilled, Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { useNotificationSocket } from '@/features/ai-mention/useNotificationSocket'
import { useCan } from '@/features/auth/useCan'

const router = useRouter()
const authStore = useAuthStore()
const { can, explainDeny } = useCan()

const searchQuery = ref('')
const username = ref('同学')
const unreadCount = ref(0)

const {
  connect: connectNotificationSocket,
  notifications: pushedNotifications,
} = useNotificationSocket()

const canCreateSpace = computed(() => can({ requireAuth: true, permission: 'space.create', minTrust: 3 }))

const unreadBadgeText = computed(() => {
  if (unreadCount.value > 99) return '99+'
  return String(unreadCount.value)
})

const fetchUnreadCount = async () => {
  if (!authStore.isAuthenticated) {
    unreadCount.value = 0
    return
  }

  try {
    const res: any = await request.get('/me/notifications/unread-count')
    unreadCount.value = res.unread_count || 0
  } catch {
    unreadCount.value = 0
  }
}

watch(
  () => pushedNotifications.value.length,
  (next, prev) => {
    if (next > prev) {
      unreadCount.value += next - prev
    }
  },
)

onMounted(async () => {
  if (authStore.user) {
    username.value = authStore.user.nickname || authStore.user.username || '同学'
  }

  if (authStore.isAuthenticated) {
    await fetchUnreadCount()
    const token = (authStore.token || '').trim()
    if (token) {
      void connectNotificationSocket(token)
    }
  }
})

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}

const handleOpenNotifications = () => {
  router.push('/notifications')
}

// Dialog States
const showSpaceDialog = ref(false)
const spaceForm = ref({ name: '', slug: '', description: '', type: 'course', category_id: null as number | null })

const categories = ref<any[]>([])
const openSpaceDialog = async () => {
  if (!canCreateSpace.value) {
    ElMessage.warning(explainDeny({ requireAuth: true, permission: 'space.create', minTrust: 3 }))
    return
  }

  showSpaceDialog.value = true
  spaceForm.value = { name: '', slug: '', description: '', type: 'course', category_id: null }
  
  try {
    const res: any = await request.get('/categories/')
    const allowed = ['学校', '课程', '休闲娱乐', '专业', '探索']
    categories.value = (res || []).filter((c: any) => allowed.includes(c.name))
  } catch (e) {
    console.error(e)
  }
}

const submitSpace = async () => {
  if (!canCreateSpace.value) {
    ElMessage.warning(explainDeny({ requireAuth: true, permission: 'space.create', minTrust: 3 }))
    return
  }

  if (!spaceForm.value.name || !spaceForm.value.category_id) return ElMessage.warning('请填写必填项')
  try {
    await request.post('/spaces/', spaceForm.value)
    ElMessage.success('空间创建成功')
    showSpaceDialog.value = false
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || e.response?.data?.detail || e.message || '创建失败')
  }
}
</script>

<template>
  <header class="h-[88px] bg-white border-b border-[var(--c-navy)] border-opacity-5 flex items-center justify-between px-[80px] sticky top-0 z-40">
    <!-- Left: Logo & Welcome -->
    <div class="flex items-center gap-x-6">
      <div 
        class="w-16 h-16 bg-[var(--c-navy)] rounded-[16px] flex items-center justify-center cursor-pointer overflow-hidden shadow-sm"
        @click="router.push('/home')"
      >
        <span class="font-serif text-[var(--c-fog)] text-xl font-bold tracking-widest pl-1">FRM</span>
      </div>
      <div class="flex flex-col">
        <span class="text-[var(--c-navy)] opacity-60 text-sm mb-0.5">Forum Dashboard</span>
        <span class="text-[var(--c-navy)] font-medium text-lg">欢迎你，{{ username }}</span>
      </div>
    </div>

    <!-- Middle: Search -->
    <div class="w-[320px]">
      <div class="relative flex items-center">
        <el-icon class="absolute left-4 text-[var(--c-navy)] opacity-40 z-10"><Search /></el-icon>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="搜索空间、资料、帖子..."
          class="w-full bg-[var(--c-fog)] rounded-[var(--radius-btn)] pl-11 pr-4 py-2.5 text-[var(--c-navy)] focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)] focus:bg-white transition-all border border-transparent"
        />
      </div>
    </div>

    <!-- Right: Actions -->
    <div class="flex items-center gap-x-5">
      <button 
        class="w-10 h-10 rounded-full flex items-center justify-center hover:bg-[var(--c-fog)] text-[var(--c-navy)] opacity-70 hover:opacity-100 transition-all relative"
        @click="handleOpenNotifications"
      >
        <el-icon :size="20"><Bell /></el-icon>
        <span v-if="unreadCount > 0" class="absolute -top-1 -right-1 min-w-4 h-4 px-1 bg-[var(--c-danger)] text-white text-[10px] leading-4 text-center rounded-full border-2 border-white">
          {{ unreadBadgeText }}
        </span>
      </button>

      <button class="w-10 h-10 rounded-full flex items-center justify-center hover:bg-[var(--c-fog)] text-[var(--c-navy)] opacity-70 hover:opacity-100 transition-all">
        <el-icon :size="20"><Setting /></el-icon>
      </button>

      <!-- Avatar with Dropdown -->
      <el-dropdown trigger="click" placement="bottom-end">
        <div class="ml-2 w-10 h-10 rounded-full bg-[var(--c-fog)] border border-[var(--c-navy)] border-opacity-10 overflow-hidden cursor-pointer flex items-center justify-center text-[var(--c-navy)] opacity-50 hover:opacity-80 transition-opacity">
          <el-icon :size="20"><UserFilled /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu class="min-w-[160px]">
            <el-dropdown-item class="py-2.5" @click="router.push('/profile')">
              个人主页
            </el-dropdown-item>
            <el-dropdown-item class="py-2.5" @click="ElMessage.info('研发中...')">
              修改头像
            </el-dropdown-item>
            <el-dropdown-item class="py-2.5" @click="ElMessage.info('研发中...')">
              修改用户名
            </el-dropdown-item>
            <el-dropdown-item divided class="py-2.5 text-red-500" @click="handleLogout">
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>

  <!-- Create Space Dialog -->
  <el-dialog v-model="showSpaceDialog" title="创建新空间" width="480px" style="border-radius: var(--radius-card)">
    <div class="space-y-4 pt-2">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">所属模块 <span class="text-red-500">*</span></label>
          <el-select v-model="spaceForm.category_id" placeholder="选择模块" class="w-full">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">空间类型</label>
          <el-select v-model="spaceForm.type" placeholder="类型" class="w-full">
            <el-option label="学术/课程" value="course" />
            <el-option label="学校/校区" value="school" />
            <el-option label="兴趣/社团" value="interest" />
          </el-select>
        </div>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">空间名称 <span class="text-red-500">*</span></label>
        <input v-model="spaceForm.name" placeholder="如：高等数学" class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-1 focus:ring-[var(--c-gold)] outline-none" />
      </div>
      <div>
        <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">描述</label>
        <textarea v-model="spaceForm.description" placeholder="空间简介和规则..." rows="3" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-1 focus:ring-[var(--c-gold)] outline-none resize-none"></textarea>
      </div>
    </div>
    <template #footer>
      <div class="flex justify-end gap-x-3">
        <button class="px-5 py-1.5 rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50" @click="showSpaceDialog = false">取消</button>
        <button class="px-5 py-1.5 rounded-lg bg-[var(--c-indigo)] text-white hover:bg-opacity-90" @click="submitSpace">提交创建</button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
/* Scoped styles */
</style>
