<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search, Bell, Setting, UserFilled } from '@element-plus/icons-vue'
import { ElMessage, ElNotification } from 'element-plus'
import { useNotificationSocket } from '@/features/ai-mention/useNotificationSocket'
import { useCan } from '@/features/auth/useCan'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'

type GlobalSearchType = 'spaces' | 'posts' | 'materials' | 'explore' | 'users'
type SpaceSearchType = 'space_posts' | 'space_materials' | 'space_policy'

type SearchCategory = {
  id: number
  name: string
  slug?: string | null
}

const props = withDefaults(
  defineProps<{
    spaceId?: number | null
    spaceName?: string
    spaceSectionId?: number | null
  }>(),
  {
    spaceId: null,
    spaceName: '',
    spaceSectionId: null,
  },
)

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { can, explainDeny } = useCan()

const searchQuery = ref('')
const globalSearchType = ref<GlobalSearchType>('spaces')
const spaceSearchType = ref<SpaceSearchType>('space_posts')
const selectedSpaceCategoryId = ref<number | null>(null)
const isSearchFocused = ref(false)

const username = ref('同学')
const unreadCount = ref(0)

const searchCategories = ref<SearchCategory[]>([])

const { connect: connectNotificationSocket, notifications: pushedNotifications } = useNotificationSocket()

const canCreateSpace = computed(() => can({ requireAuth: true, permission: 'space.create', minTrust: 3 }))
const isSpacesRoute = computed(() => route.path === '/spaces')
const hasValidSpaceContext = computed(() => Number.isFinite(Number(props.spaceId)) && Number(props.spaceId) > 0)
const shouldShowSpacePrefix = computed(
  () => isSpacesRoute.value && hasValidSpaceContext.value && isSearchFocused.value && Boolean(props.spaceName?.trim()),
)

const activeSearchType = computed({
  get: () => (isSpacesRoute.value ? spaceSearchType.value : globalSearchType.value),
  set: (value: string) => {
    if (isSpacesRoute.value) {
      spaceSearchType.value = value as SpaceSearchType
      return
    }
    globalSearchType.value = value as GlobalSearchType
  },
})

const searchTypeOptions = computed(() => {
  if (isSpacesRoute.value) {
    return [
      { label: '帖子', value: 'space_posts' as const },
      { label: '题库', value: 'space_materials' as const },
      { label: '学校政策', value: 'space_policy' as const },
    ]
  }
  return [
    { label: '空间', value: 'spaces' as const },
    { label: '帖子', value: 'posts' as const },
    { label: '题库', value: 'materials' as const },
    { label: '其他资料', value: 'explore' as const },
    { label: '用户', value: 'users' as const },
  ]
})

const normalizedCategoryName = (category: SearchCategory): string => String(category.name || '').trim().toLowerCase()
const normalizedCategorySlug = (category: SearchCategory): string => String(category.slug || '').trim().toLowerCase()

const categoryNameAlias = new Set(['学校', '课程', '休闲娱乐', '专业', '探索'])
const categorySlugAlias = new Set(['school', 'course', 'entertainment', 'major', 'explore'])

const spaceCategoryOptions = computed(() =>
  searchCategories.value.filter((category) => {
    if (categoryNameAlias.has(normalizedCategoryName(category))) return true
    return categorySlugAlias.has(normalizedCategorySlug(category))
  }),
)

const shouldShowSpaceCategorySelect = computed(
  () => !isSpacesRoute.value && globalSearchType.value === 'spaces',
)

const searchPlaceholder = computed(() => {
  if (isSpacesRoute.value) {
    if (spaceSearchType.value === 'space_posts') return '在当前空间搜索帖子关键词...'
    if (spaceSearchType.value === 'space_materials') return '在当前空间搜索题库关键词...'
    return '在当前空间搜索政策关键词...'
  }

  if (globalSearchType.value === 'spaces') return '请输入空间关键词（如：山东、经济）'
  if (globalSearchType.value === 'posts') return '请输入帖子关键词'
  if (globalSearchType.value === 'materials') return '请输入题库关键词'
  if (globalSearchType.value === 'explore') return '请输入其他资料关键词'
  return '用户搜索开发中'
})

const unreadBadgeText = computed(() => {
  if (unreadCount.value > 99) return '99+'
  return String(unreadCount.value)
})

watch(
  () => props.spaceSectionId,
  (sectionId) => {
    if (!isSpacesRoute.value || sectionId == null) return
    if (sectionId === 3) {
      spaceSearchType.value = 'space_materials'
      return
    }
    if (sectionId === 4) {
      spaceSearchType.value = 'space_policy'
      return
    }
    spaceSearchType.value = 'space_posts'
  },
  { immediate: true },
)

watch(globalSearchType, (next) => {
  if (next !== 'spaces') selectedSpaceCategoryId.value = null
})

watch(
  () => pushedNotifications.value.length,
  (next, prev) => {
    if (next > prev) unreadCount.value += next - prev
  },
)

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
      // Show popup for latest AI reply notification
      const latest = pushedNotifications.value[0]
      if (latest && latest.notification_type === 'ai_reply') {
        ElNotification({
          title: 'AI 回复已完成',
          message: '请在通知里查阅 AI 的回复。',
          type: 'success',
          duration: 5000,
          position: 'top-right',
          onClick: () => router.push('/notifications'),
        })
      }
    }
  },
)

const fetchSearchCategories = async () => {
  try {
    const res: any = await request.get('/categories/')
    searchCategories.value = Array.isArray(res) ? res : []
  } catch {
    searchCategories.value = []
  }
}

onMounted(async () => {
  if (authStore.user) {
    username.value = authStore.user.nickname || authStore.user.username || '同学'
  }
  if (authStore.isAuthenticated) {
    await fetchUnreadCount()
    const token = (authStore.token || '').trim()
    if (token) void connectNotificationSocket(token)
  }
  await fetchSearchCategories()
})

const handleSearch = () => {
  const keyword = searchQuery.value.trim()

  if (isSpacesRoute.value) {
    if (!hasValidSpaceContext.value) {
      ElMessage.warning('请先在空间页选择一个空间')
      return
    }
    if (!keyword) {
      ElMessage.warning('请输入关键词后再搜索')
      return
    }
    const commonQuery = {
      keyword,
      spaceId: String(props.spaceId),
      source: 'spaces',
    }
    if (spaceSearchType.value === 'space_posts') {
      router.push({ path: '/search/posts', query: commonQuery })
      return
    }
    if (spaceSearchType.value === 'space_materials') {
      router.push({ path: '/search/materials', query: commonQuery })
      return
    }
    router.push({ path: '/search/explore', query: commonQuery })
    return
  }

  if (globalSearchType.value === 'users') {
    ElMessage.info('用户搜索功能开发中')
    return
  }

  if (!keyword) {
    ElMessage.warning('请输入关键词后再搜索')
    return
  }

  if (globalSearchType.value === 'spaces') {
    if (!selectedSpaceCategoryId.value) {
      ElMessage.warning('请选择空间子标签（模块）')
      return
    }
    router.push({
      path: '/explore-spaces',
      query: { keyword, categoryId: String(selectedSpaceCategoryId.value) },
    })
    return
  }

  if (globalSearchType.value === 'posts') {
    router.push({ path: '/search/posts', query: { keyword } })
    return
  }
  if (globalSearchType.value === 'materials') {
    router.push({ path: '/search/materials', query: { keyword } })
    return
  }
  router.push({ path: '/search/explore', query: { keyword } })
}


const handleOpenNotifications = () => {
  router.push('/notifications')
}

const showSpaceDialog = ref(false)
const spaceForm = ref({
  name: '',
  slug: '',
  description: '',
  type: 'course',
  category_id: null as number | null,
})
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
    categories.value = (res || []).filter((item: any) => {
      const name = String(item.name || '').trim().toLowerCase()
      const slug = String(item.slug || '').trim().toLowerCase()
      return categoryNameAlias.has(name) || categorySlugAlias.has(slug)
    })
  } catch {
    categories.value = []
  }
}

const submitSpace = async () => {
  if (!canCreateSpace.value) {
    ElMessage.warning(explainDeny({ requireAuth: true, permission: 'space.create', minTrust: 3 }))
    return
  }
  if (!spaceForm.value.name || !spaceForm.value.category_id) {
    ElMessage.warning('请填写必填项')
    return
  }
  try {
    await request.post('/spaces/', spaceForm.value)
    ElMessage.success('空间创建成功')
    showSpaceDialog.value = false
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || error.response?.data?.detail || error.message || '创建失败')
  }
}
</script>

<template>
  <header class="h-[88px] bg-white border-b border-[var(--c-navy)] border-opacity-5 flex items-center justify-between px-[80px] sticky top-0 z-40">
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

    <div class="w-[600px] shrink-0">
      <div class="relative flex items-center gap-2 min-w-0">
        <el-select
          v-model="activeSearchType"
          class="header-search-select-main shrink-0"
          style="width: 92px; min-width: 92px; max-width: 92px; flex: 0 0 92px"
          size="large"
          popper-class="header-search-popper"
        >
          <el-option
            v-for="option in searchTypeOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>

        <el-select
          v-if="shouldShowSpaceCategorySelect"
          v-model="selectedSpaceCategoryId"
          class="header-search-select-sub shrink-0"
          style="width: 112px; min-width: 112px; max-width: 112px; flex: 0 0 112px"
          size="large"
          popper-class="header-search-popper"
          placeholder="模块"
        >
          <el-option
            v-for="option in spaceCategoryOptions"
            :key="option.id"
            :label="option.name"
            :value="option.id"
          />
        </el-select>

        <div class="relative z-[1] flex-1 min-w-[220px] h-11 bg-[var(--c-fog)] rounded-[var(--radius-btn)] border border-transparent focus-within:border-[var(--c-gold)] focus-within:bg-white transition-all flex items-center px-3 gap-2">
          <el-icon class="text-[var(--c-navy)] opacity-50"><Search /></el-icon>
          <span
            v-if="shouldShowSpacePrefix"
            class="text-xs font-semibold text-[var(--c-indigo)] bg-[var(--c-indigo)]/10 px-2 py-1 rounded-full whitespace-nowrap"
          >
            {{ props.spaceName }}:
          </span>
          <input
            v-model="searchQuery"
            data-testid="home-global-search-input"
            type="text"
            :placeholder="searchPlaceholder"
            class="w-full bg-transparent text-[var(--c-navy)] focus:outline-none text-sm"
            @focus="isSearchFocused = true"
            @blur="isSearchFocused = false"
            @keyup.enter="handleSearch"
          />
        </div>

        <button
          class="h-11 px-5 bg-[var(--c-indigo)] text-white rounded-[var(--radius-btn)] hover:bg-opacity-90 transition-all text-sm font-medium shrink-0"
          @click="handleSearch"
        >
          搜索
        </button>
      </div>
    </div>

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

      <button class="w-10 h-10 rounded-full flex items-center justify-center hover:bg-[var(--c-fog)] text-[var(--c-navy)] opacity-70 hover:opacity-100 transition-all" @click="openSpaceDialog">
        <el-icon :size="20"><Setting /></el-icon>
      </button>

      <!-- Avatar → /me/overview -->
      <div
        class="ml-2 w-10 h-10 rounded-full bg-[var(--c-fog)] border border-[var(--c-navy)] border-opacity-10 overflow-hidden cursor-pointer flex items-center justify-center text-[var(--c-navy)] opacity-50 hover:opacity-80 transition-opacity"
        @click="router.push('/me/overview')"
      >
        <img v-if="authStore.user?.avatar_url" :src="authStore.user.avatar_url" class="w-full h-full object-cover" />
        <el-icon v-else :size="20"><UserFilled /></el-icon>
      </div>
    </div>
  </header>

  <el-dialog v-model="showSpaceDialog" title="创建新空间" width="480px" style="border-radius: var(--radius-card)">
    <div class="space-y-4 pt-2">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">所属模块 <span class="text-red-500">*</span></label>
          <el-select v-model="spaceForm.category_id" placeholder="选择模块" class="w-full">
            <el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" />
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
:deep(.header-search-select-main.el-select) {
  width: 92px !important;
  min-width: 92px;
  max-width: 92px;
  flex: 0 0 92px;
}

:deep(.header-search-select-sub.el-select) {
  width: 112px !important;
  min-width: 112px;
  max-width: 112px;
  flex: 0 0 112px;
}

:deep(.header-search-select-main .el-select__wrapper),
:deep(.header-search-select-sub .el-select__wrapper) {
  border-radius: var(--radius-btn);
  box-shadow: none;
  border: 1px solid rgba(15, 27, 45, 0.08);
  padding-left: 8px;
  padding-right: 8px;
}
</style>
