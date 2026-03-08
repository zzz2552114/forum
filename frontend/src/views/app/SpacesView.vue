<script setup lang="ts">
import { ref, computed, onMounted, watch, markRaw } from 'vue'
import { Plus, ChatDotSquare, Document, ChatLineRound, Location, ShoppingCart, Headset, Star, Setting } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import HomeHeader from '@/components/HomeHeader.vue'

const router = useRouter()

// State
const categories = ref<any[]>([])
const spaces = ref<any[]>([])
const activeSpaceId = ref<number | null>(null)
const activeSectionId = ref(1)
const expandedCategories = ref<number[]>([])

const isJoinLoading = ref(false)
const posts = ref<any[]>([])

const fetchCategories = async () => {
  try {
    const res: any = await request.get('/categories/')
    categories.value = res || []
    if (categories.value.length > 0) {
      expandedCategories.value = [categories.value[0].id]
    }
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
      activeSpaceId.value = spaces.value[0].id
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || e.message || '获取空间列表失败')
  }
}

const fetchPostsForSpace = async () => {
  if (!activeSpaceId.value) return;
  try {
    const res: any = await request.get(`/posts/`, { params: { space_id: activeSpaceId.value } });
    posts.value = res.items || [];
  } catch(e) {
    console.error('Failed to fetch posts', e)
  }
}

watch(activeSpaceId, () => {
  if (activeSectionId.value === 1) fetchPostsForSpace()
})

watch(activeSectionId, () => {
  if (activeSectionId.value === 1) fetchPostsForSpace()
})

onMounted(() => {
  fetchCategories()
  fetchSpaces().then(() => {
    if (activeSectionId.value === 1) fetchPostsForSpace()
  })
})

const handleJoinSpace = async () => {
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

const toggleCategory = (id: number) => {
  if (expandedCategories.value.includes(id)) {
    expandedCategories.value = expandedCategories.value.filter(cid => cid !== id)
  } else {
    expandedCategories.value.push(id)
  }
}

const activeSpace = computed(() => {
  return spaces.value.find((s: any) => s.id === activeSpaceId.value)
})

const activeSection = computed(() => {
  return sections.value.find((s: any) => s.id === activeSectionId.value)
})

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
      <div
        class="w-[84px] sm:w-[240px] shrink-0 bg-[#0F1522] flex flex-col items-center sm:items-stretch py-6 border-r border-black/10 z-10 transition-all"
      >
        <div
          class="px-6 mb-4 hidden sm:block text-white/50 text-xs font-bold tracking-wider"
        >
          已加入空间
        </div>

        <div class="flex-1 overflow-y-auto custom-scrollbar pt-2 space-y-4">
          <div v-for="category in categories" :key="category.id" class="mb-2">
            <!-- Category Title (Drawer Header) -->
            <div 
              class="px-5 py-2 flex items-center justify-between text-white/50 text-xs font-bold tracking-wider cursor-pointer hover:text-white/80 transition-colors"
              @click="toggleCategory(category.id)"
            >
              <span>{{ category.name }}</span>
              <span>{{ expandedCategories.includes(category.id) ? '▼' : '▶' }}</span>
            </div>
            
            <!-- Category Spaces List -->
            <div v-show="expandedCategories.includes(category.id)" class="px-3 space-y-2 mt-1">
              <div
                v-for="space in spaces.filter(s => s.category_id === category.id)"
                :key="space.id"
                class="group flex items-center gap-x-3 p-2 rounded-[16px] cursor-pointer transition-all relative"
                :class="activeSpaceId === space.id ? 'bg-white/10' : 'hover:bg-white/5'"
                @click="activeSpaceId = space.id"
              >
                <!-- Active Indicator Line -->
                <div
                  class="absolute left-[-12px] w-1 bg-white rounded-r-md transition-all duration-300"
                  :class="
                    activeSpaceId === space.id
                      ? 'h-8 opacity-100'
                      : 'h-0 opacity-0 group-hover:h-4 group-hover:opacity-50'
                  "
                ></div>

                <div
                  class="w-12 h-12 shrink-0 rounded-[14px] flex items-center justify-center text-white font-bold text-lg shadow-md transition-transform bg-[var(--c-indigo)]"
                  :class="[
                    activeSpaceId === space.id
                      ? 'rounded-[10px]'
                      : 'group-hover:rounded-[10px]',
                  ]"
                >
                  {{ space.name.charAt(0) }}
                </div>

                <div class="hidden sm:block flex-1 min-w-0">
                  <div
                    class="text-white/90 font-medium truncate text-sm"
                    :class="
                      activeSpaceId === space.id ? 'text-white font-bold' : ''
                    "
                  >
                    {{ space.name }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Add Space Button -->
          <div class="px-3 pb-6">
            <div
              class="group flex items-center gap-x-3 p-2 rounded-[16px] cursor-pointer transition-all hover:bg-white/5"
            >
              <div
                class="w-12 h-12 shrink-0 rounded-[14px] bg-white/5 border border-white/10 flex items-center justify-center text-green-500 font-bold text-xl group-hover:bg-green-500 group-hover:text-white transition-all"
              >
                +
              </div>
              <div
                class="hidden sm:block text-green-500 font-medium group-hover:text-white transition-colors"
              >
                探索新空间
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Middle Column: Sections (3 Cols ~ 25%) -->
      <div
        class="w-[280px] shrink-0 bg-white flex flex-col border-r border-[var(--c-navy)] border-opacity-10 z-0"
      >
        <div class="h-16 flex items-center px-6 border-b border-[var(--c-navy)] border-opacity-10 shrink-0">
          <h2 class="text-lg font-bold text-[var(--c-navy)]">{{ activeSpace?.name || '选择空间' }}</h2>
        </div>

        <!-- Sections List -->
        <div class="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-1">
          <div 
            v-for="section in sections" 
            :key="section.id"
            class="flex items-center justify-between px-3 py-2 rounded-[var(--radius-btn)] cursor-pointer text-sm font-medium transition-all"
            :class="activeSectionId === section.id ? 'bg-[var(--c-indigo)] text-white shadow-md shadow-[var(--c-indigo)]/20' : 'text-[var(--c-navy)] opacity-70 hover:opacity-100 hover:bg-[var(--c-fog)]'"
            @click="activeSectionId = section.id"
          >
            <div class="flex items-center gap-x-3">
              <el-icon :size="18" class="opacity-80"
                ><component :is="section.icon"
              /></el-icon>
              <span>{{ section.name }}</span>
            </div>
            <span v-if="section.unread > 0" class="text-xs font-bold px-2 py-0.5 rounded-full bg-white/20 text-white">{{ section.unread }}</span>
          </div>
        </div>
      </div>

      <!-- Right Column: Content Area (7 Cols ~ 58.3%) -->
      <div class="flex-1 h-full min-w-0 bg-white flex flex-col relative">
        <!-- Content Header -->
        <div class="h-16 flex items-center justify-between px-8 border-b border-[var(--c-navy)] border-opacity-10 shrink-0 bg-white z-10 sticky top-0">
          <div class="flex items-center gap-x-3">
            <h3 class="text-lg font-bold text-[var(--c-navy)]"># {{ activeSection?.name }}</h3>
            <span
              class="text-xs px-2 py-0.5 rounded-full bg-[var(--c-fog)] text-[var(--c-navy)]/60 font-medium line-clamp-1 border border-[var(--c-navy)]/5"
            >
              来自 {{ activeSpace?.name }}
            </span>
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
          <!-- Empty State Mockup -->
          <div
            v-if="activeSectionId !== 1"
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

          <!-- List State (for posts) -->
          <div v-else class="max-w-[800px] mx-auto space-y-4 pb-24">
            <template v-if="posts.length > 0">
              <div
                v-for="post in posts"
                :key="post.id"
                class="bg-white p-5 rounded-2xl shadow-sm border border-[var(--c-navy)]/5 hover:border-[var(--c-gold)]/30 transition-colors cursor-pointer group"
                @click="router.push(`/posts/${post.id}`)"
              >
                <div class="flex items-center gap-x-3 mb-3">
                  <div
                    class="w-10 h-10 rounded-full bg-[var(--c-fog)] overflow-hidden shrink-0 flex items-center justify-center font-bold text-[var(--c-navy)]"
                  >
                    {{ post.author_id }}
                  </div>
                  <div>
                    <div class="font-medium text-[var(--c-navy)] text-sm">
                      用户 {{ post.author_id }}
                    </div>
                    <div class="text-xs text-[var(--c-navy)]/50">
                      {{ new Date(post.created_at).toLocaleString() }}
                    </div>
                  </div>
                </div>
                <h3
                  class="font-medium text-[var(--c-navy)] text-lg mb-2 group-hover:text-[var(--c-indigo)]"
                >
                  {{ post.title }}
                </h3>
                <p
                  class="text-[var(--c-navy)]/70 text-sm line-clamp-2 leading-relaxed"
                >
                  {{ post.summary || post.content }}
                </p>
                <div class="mt-4 flex gap-x-4 text-xs text-[var(--c-navy)]/40 font-medium">
                  <span>{{ post.view_count || 0 }} 浏览</span>
                  <span>{{ post.like_count || 0 }} 赞</span>
                  <span>{{ post.comment_count || 0 }} 评论</span>
                </div>
              </div>
            </template>
            <template v-else>
              <div class="text-center text-[var(--c-navy)]/40 mt-10">
                暂无帖子
              </div>
            </template>
          </div>
        </div>

        <!-- Floating Action Button -->
        <button 
          v-if="activeSectionId === 1"
          class="absolute bottom-8 right-8 w-14 h-14 bg-[var(--c-indigo)] text-white rounded-full flex items-center justify-center shadow-user transition-all hover:-translate-y-1 hover:shadow-xl z-20 group"
          @click="router.push({ path: '/posts/new', query: { space_id: activeSpaceId } })"
        >
          <el-icon :size="24"><Plus /></el-icon>
        </button>
      </div>
    </div>
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
