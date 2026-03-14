<script setup lang="ts">
import { ref, computed, onMounted, watch, markRaw } from 'vue'
import { Plus, ChatDotSquare, Document, ChatLineRound, Location, ShoppingCart, Headset, Star, Setting } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SpaceRealtimeChatPanel from '@/features/realtime-chat/SpaceRealtimeChatPanel.vue'
import ResourceList from '@/features/spaces/ResourceList.vue'
import PostList from '@/features/spaces/PostList.vue'
import PostDetail from '@/features/spaces/PostDetail.vue'
import CreatePostEditor from '@/features/spaces/CreatePostEditor.vue'
import SpaceSidebar from '@/features/spaces/SpaceSidebar.vue'
import SpaceSectionMenu from '@/features/spaces/SpaceSectionMenu.vue'
import HomeHeader from '@/components/HomeHeader.vue'
import { ArrowLeft, CaretTop, CaretBottom, ChatDotRound, StarFilled, MoreFilled, ArrowUpBold, View, Loading } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// State
const categories = ref<any[]>([])
const spaces = ref<any[]>([])
const activeSpaceId = ref<number | null>(null)
const activeSectionId = ref<number>(1) // 1: Posts, 3: Library, 4: Policy, 5: Trade
const isJoinLoading = ref(false)
const posts = ref<any[]>([])
const resources = ref<any[]>([]) // Added to store materials/policies


// Inline Post Detail State (simplified)
const selectedPostId = ref<number | null>(null)

const goBackToPosts = () => {
  selectedPostId.value = null
}



const allowedCategories = ['学校', '课程', '休闲娱乐', '专业', '探索']

const fetchCategories = async () => {
  try {
    const res: any = await request.get('/categories/')
    categories.value = (res || []).filter((c: any) => allowedCategories.includes(c.name))
  } catch (e: any) {
    console.error('Failed to fetch categories', e)
  }
}

// Fetch all spaces
const fetchSpaces = async () => {
  try {
    const res: any = await request.get('/spaces/')
    spaces.value = res || []
    
    if (spaces.value.length > 0 && !activeSpaceId.value) {
      // Find the "学校" category to get its spaces
      const schoolCategory = categories.value.find((c: any) => c.name === '学校')
      const targetSpaces = spaces.value.filter((s: any) => schoolCategory ? s.category_id === schoolCategory.id : true)
      activeSpaceId.value = targetSpaces.length > 0 ? targetSpaces[0].id : spaces.value[0].id
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || e.message || '获取空间列表失败')
  }
}

const fetchPostsForSpace = async () => {
  if (!activeSpaceId.value) return;
  try {
    const params: any = { space_id: activeSpaceId.value };
    if (activeSectionId.value === 5) {
      params.tag_name = "交易";
    }
    const res: any = await request.get(`/posts/`, { params });
    posts.value = res.items || [];
  } catch(e) {
    console.error('Failed to fetch posts', e)
  }
}

const fetchResourcesForSpace = async () => {
  if (!activeSpaceId.value) return;
  try {
    const params: any = { space_id: activeSpaceId.value };
    // If it's a school policy, it might use resource_type='policy' and school_space_id
    // But backend /resources filter checks both space_id and school_space_id
    if (activeSectionId.value === 4) {
      params.resource_type = 'policy';
    }
    const res: any = await request.get(`/resources/`, { params });
    let fetchedResources = res.items || [];
    // 题库区排除政策文件
    if (activeSectionId.value === 3) {
      fetchedResources = fetchedResources.filter((r: any) => r.resource_type !== 'policy')
    }
    // 按照上传时间倒序排列
    resources.value = fetchedResources.sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  } catch(e) {
    console.error('Failed to fetch resources', e)
  }
}




watch(activeSpaceId, () => {
  goBackToPosts()
  if ([1, 2, 5, 6, 7].includes(activeSectionId.value)) {
    fetchPostsForSpace()
  } else if ([3, 4].includes(activeSectionId.value)) {
    fetchResourcesForSpace()
  }
})

watch(activeSectionId, () => {
  goBackToPosts()
  if ([1, 2, 5, 6, 7].includes(activeSectionId.value)) {
    fetchPostsForSpace()
  } else if ([3, 4].includes(activeSectionId.value)) {
    fetchResourcesForSpace()
  }
})

onMounted(() => {
  fetchCategories()
  fetchSpaces().then(() => {
    if ([1, 2, 5, 6, 7].includes(activeSectionId.value)) {
      fetchPostsForSpace()
    } else if ([3, 4].includes(activeSectionId.value)) {
      fetchResourcesForSpace()
    }
  })
})

const handleJoinSpace = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录再操作')
    return
  }
  if (!activeSpaceId.value) return
  isJoinLoading.value = true
  try {
    await request.put(`/spaces/${activeSpaceId.value}/subscriptions/me/`)
    ElMessage.success('已加入空间！')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || e.response?.data?.detail || e.message || '加入失败')
  } finally {
    isJoinLoading.value = false
  }
}

const showCreatePostEditor = ref(false)

const handleOpenEditor = () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录再发布帖子')
    router.push('/?showLogin=true')
    return
  }
  showCreatePostEditor.value = true
}



const activeSpace = computed(() => {
  return spaces.value.find((s: any) => s.id === activeSpaceId.value)
})

const activeSection = computed(() => {
  return sections.value.find((s: any) => s.id === activeSectionId.value)
})

// Create Post State
const newComment = ref('')
const replyToId = ref<number | null>(null)
const isSubmittingComment = ref(false)

const downloadFile = (mat: any) => {
  if (!mat) return;
  const token = localStorage.getItem('token');
  if (!token) {
    ElMessage.warning('请先登录再下载');
    return;
  }
  window.open(`/api/v1/resources/${mat.id}/download?token=${encodeURIComponent(token)}`, '_blank');
  mat.download_count = (mat.download_count || 0) + 1;
}

const sections = ref([
  { id: 1, name: '发帖区', icon: markRaw(ChatDotSquare), unread: 0 },
  { id: 2, name: '即时聊天区', icon: markRaw(ChatLineRound), unread: 0 },
  { id: 3, name: '题库区', icon: markRaw(Document), unread: 0 },
  { id: 4, name: '学校政策区', icon: markRaw(Location), unread: 0 },
  { id: 5, name: '交易专区', icon: markRaw(ShoppingCart), unread: 0 },
  { id: 6, name: '课程评价区', icon: markRaw(Star), unread: 0 },
  { id: 7, name: '教师评价区', icon: markRaw(Headset), unread: 0 },
])
</script>

<template>
  <div class="min-h-screen bg-[var(--c-fog)] flex flex-col h-screen overflow-hidden">
    <!-- Header: Shrink 0 to keep constant height -->
    <div class="shrink-0">
      <HomeHeader />
    </div>

    <div class="flex-1 flex overflow-hidden">
      <!-- Left Column: Spaces List (2 Cols ~ 16.6%) -->
      <SpaceSidebar 
        :categories="categories" 
        :spaces="spaces" 
        v-model:active-space-id="activeSpaceId" 
      />

      <!-- Middle Column: Sections (3 Cols ~ 25%) -->
      <SpaceSectionMenu 
        :active-space-name="activeSpace?.name || ''"
        :sections="sections"
        v-model:active-section-id="activeSectionId"
      />
      <!-- Right Column: Content Area (7 Cols ~ 58.3%) -->
      <div class="flex-1 h-full min-w-0 bg-white flex flex-col relative">
        <!-- Content Header -->
        <div class="h-16 flex items-center justify-between px-8 border-b border-[var(--c-navy)] border-opacity-10 shrink-0 bg-white z-10 sticky top-0">
          <div class="flex items-center gap-x-3">
            <template v-if="selectedPostId">
              <button @click="goBackToPosts" class="w-8 h-8 rounded-full hover:bg-[var(--c-fog)] flex items-center justify-center text-[var(--c-navy)]/60 hover:text-[var(--c-navy)] transition-colors mr-2">
                <el-icon :size="20"><ArrowLeft /></el-icon>
              </button>
              <h3 class="text-lg font-bold text-[var(--c-navy)]">帖子详情</h3>
            </template>
            <template v-else>
              <h3 class="text-lg font-bold text-[var(--c-navy)]"># {{ activeSection?.name }}</h3>
              <span
                class="text-xs px-2 py-0.5 rounded-full bg-[var(--c-fog)] text-[var(--c-navy)]/60 font-medium line-clamp-1 border border-[var(--c-navy)]/5"
              >
                来自 {{ activeSpace?.name }}
              </span>
            </template>
          </div>
          
          <div class="flex items-center gap-x-4">
            <button v-if="activeSpace" @click="handleJoinSpace" :disabled="isJoinLoading" class="px-4 py-1.5 rounded-full bg-[var(--c-gold)] text-white text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50">
              {{ isJoinLoading ? '加入中...' : '加入空间' }}
            </button>
            <button
              class="w-8 h-8 rounded hover:bg-[var(--c-fog)] flex items-center justify-center text-[var(--c-navy)]/60 hover:text-[var(--c-navy)] transition-colors"
            >
              <el-icon :size="20"><Setting /></el-icon>
            </button>
          </div>
        </div>

        <!-- Scrollable Content -->
        <div
          class="flex-1 overflow-y-auto px-6 py-6 custom-scrollbar bg-[var(--c-fog)]/30"
        >
          <!-- Empty State Mockup (only for sections with no implemented content yet) -->
          <div
            v-if="[6, 7].includes(activeSectionId)"
            class="h-full flex flex-col items-center justify-center text-[var(--c-navy)]/40 mt-20"
          >
            <div
              class="w-20 h-20 mb-4 rounded-full bg-[var(--c-navy)]/5 flex items-center justify-center"
            >
              <el-icon :size="32"
                ><component
                  :is="activeSection?.icon"
              /></el-icon>
            </div>
            <p class="text-lg font-medium">还没有内容</p>
            <p class="text-sm mt-1">成为第一个在这里发布的人吧！</p>
          </div>

          <!-- Realtime Chat State -->
          <div v-else-if="activeSectionId === 2" class="h-[calc(100vh-[var(--header-height,64px)]-8rem)] min-h-[500px] w-full">
             <SpaceRealtimeChatPanel 
               v-if="activeSpaceId" 
               :key="activeSpaceId + '-' + activeSectionId"
               :space-id="activeSpaceId" 
               :section-id="2"
               :username="authStore.user?.nickname || authStore.user?.username || `用户${authStore.user?.id || '?'}`"
               :token="authStore.token || undefined"
               class="h-full bg-white rounded-2xl shadow-sm border border-[var(--c-navy)]/5 overflow-hidden" 
             />
          </div>

          <!-- Inline Post Detail State -->
          <div v-else-if="selectedPostId" class="w-full">
            <PostDetail :post-id="selectedPostId" @back="goBackToPosts" />
          </div>

          <!-- List State (for posts) -->
          <div v-else-if="[1, 2, 5, 6, 7].includes(activeSectionId)" class="max-w-[800px] mx-auto pb-24">
            <PostList :posts="posts" @read="id => selectedPostId = id" />
          </div>
          
          <!-- Library / Policy State (for resources) -->
          <div v-else-if="[3, 4].includes(activeSectionId)" class="max-w-[800px] mx-auto pb-24">
            <ResourceList :resources="resources" :active-space-name="activeSpace?.name || ''" @download="downloadFile" />
          </div>
        </div>

        <!-- Floating Action Button -->
        <button 
          v-if="activeSectionId === 1 && !selectedPostId"
          class="absolute bottom-8 right-8 w-14 h-14 bg-[var(--c-indigo)] text-white rounded-full flex items-center justify-center shadow-user transition-all hover:-translate-y-1 hover:shadow-xl z-20 group"
          @click="handleOpenEditor"
        >
          <el-icon :size="24"><Plus /></el-icon>
        </button>
      </div>
    </div>

    <!-- Inline Post Editor Overlay -->
    <CreatePostEditor 
      v-model:visible="showCreatePostEditor" 
      :space-id="activeSpaceId" 
      :space-name="activeSpace?.name || ''"
      @success="fetchPostsForSpace" 
    />
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
}

.bg-white .custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(15, 27, 45, 0.1);
}
.bg-white .custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: rgba(15, 27, 45, 0.2);
}
</style>
