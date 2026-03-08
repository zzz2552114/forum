<script setup lang="ts">
import { ref, computed, onMounted, watch, markRaw } from 'vue'
import { Plus, ChatDotSquare, Document, ChatLineRound, Location, ShoppingCart, Headset, Star, Setting } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeHeader from '@/components/HomeHeader.vue'
import { ArrowLeft, CaretTop, CaretBottom, ChatDotRound, StarFilled, MoreFilled, ArrowUpBold, View, Loading } from '@element-plus/icons-vue'

const router = useRouter()

// State
const categories = ref<any[]>([])
const spaces = ref<any[]>([])
const activeSpaceId = ref<number | null>(null)
const activeSectionId = ref(1)
const expandedCategories = ref<number[]>([])

const isJoinLoading = ref(false)
const posts = ref<any[]>([])

// Inline Post Detail State
const selectedPostId = ref<number | null>(null)
const selectedPost = ref<any>(null)
const loadingPost = ref(false)
const comments = ref<any[]>([])
const loadingComments = ref(false)
const newComment = ref('')

const fetchPostDetail = async (id: number) => {
  selectedPostId.value = id
  loadingPost.value = true
  try {
    selectedPost.value = await request.get(`/posts/${id}`)
    await fetchComments(id)
  } catch (e) {
    ElMessage.error('无法加载帖子详情')
    selectedPostId.value = null
  } finally {
    loadingPost.value = false
  }
}

const fetchComments = async (id: number) => {
  loadingComments.value = true
  try {
    const res: any = await request.get(`/comments/post/${id}`, {
      params: { page: 1, page_size: 100 }
    })
    comments.value = res.items || []
  } catch (e) {
    console.error(e)
  } finally {
    loadingComments.value = false
  }
}

const submitComment = async () => {
  if (!newComment.value.trim() || !selectedPostId.value) return
  try {
    await request.post('/comments/', {
      content: newComment.value,
      post_id: selectedPostId.value
    })
    ElMessage.success('评论成功')
    newComment.value = ''
    await fetchComments(selectedPostId.value)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || '评论失败')
  }
}

const isLiked = ref(false)
const isBookmarked = ref(false)
const authStore = useAuthStore()

const toggleLike = async () => {
  if (!authStore.isAuthenticated) return ElMessage.warning('请先登录再操作')
  if (!selectedPostId.value || !selectedPost.value) return
  try {
    if (isLiked.value) {
      await request.delete(`/posts/${selectedPostId.value}/likes/me`)
      selectedPost.value.like_count--
    } else {
      await request.put(`/posts/${selectedPostId.value}/likes/me`)
      selectedPost.value.like_count++
    }
    isLiked.value = !isLiked.value
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || '操作失败')
  }
}

const toggleBookmark = async () => {
  if (!authStore.isAuthenticated) return ElMessage.warning('请先登录再操作')
  if (!selectedPostId.value || !selectedPost.value) return
  try {
    if (isBookmarked.value) {
      await request.delete(`/posts/${selectedPostId.value}/bookmarks/me`)
    } else {
      await request.put(`/posts/${selectedPostId.value}/bookmarks/me`)
    }
    isBookmarked.value = !isBookmarked.value
    ElMessage.success(isBookmarked.value ? '已收藏' : '已取消收藏')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || '操作失败')
  }
}

const goBackToPosts = () => {
  selectedPostId.value = null
  selectedPost.value = null
  isLiked.value = false
  isBookmarked.value = false
}

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
  goBackToPosts()
  if (activeSectionId.value === 1) fetchPostsForSpace()
})

watch(activeSectionId, () => {
  goBackToPosts()
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

// Create Post State
const showCreatePostEditor = ref(false)
const isSubmittingPost = ref(false)
const newPostForm = ref({ title: '', content: '' })
const isUploadingAttachment = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const handleAttachmentUpload = async (e: Event) => {
  const target = e.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return
  const file = target.files[0]
  
  isUploadingAttachment.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('biz_type', 'attachment')

    const res: any = await request.post('/files/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    // Insert into content
    const isImage = file.type.startsWith('image/')
    const mdLink = isImage ? `\n![${file.name}](/uploads/${res.filename})\n` : `\n[${file.name}](/uploads/${res.filename})\n`
    newPostForm.value.content += mdLink
    ElMessage.success('附件插入成功')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || err.message || '附件上传失败')
  } finally {
    isUploadingAttachment.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

const submitPost = async () => {
  if (!newPostForm.value.title.trim() || !newPostForm.value.content.trim()) {
    return ElMessage.warning('标题和内容不能为空')
  }
  isSubmittingPost.value = true
  try {
    await request.post('/posts/', {
      title: newPostForm.value.title,
      content: newPostForm.value.content,
      space_id: activeSpaceId.value,
      tags: []
    })
    ElMessage.success('发布成功')
    showCreatePostEditor.value = false
    newPostForm.value = { title: '', content: '' }
    fetchPostsForSpace()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || '发布失败')
  } finally {
    isSubmittingPost.value = false
  }
}

const closeEditor = () => {
  showCreatePostEditor.value = false
  newPostForm.value = { title: '', content: '' }
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

          <!-- Inline Post Detail State -->
          <div v-else-if="selectedPostId" class="max-w-[800px] mx-auto pb-24" v-loading="loadingPost">
            <template v-if="selectedPost">
              <div class="bg-white p-6 rounded-2xl shadow-sm border border-[var(--c-navy)]/5 mb-6">
                <div class="flex items-center justify-between mb-6">
                  <div class="flex items-center gap-4">
                    <div class="w-12 h-12 rounded-full bg-[var(--c-fog)] overflow-hidden shrink-0 flex items-center justify-center font-bold text-[var(--c-navy)] text-lg">
                      {{ selectedPost.author?.nickname?.[0] || selectedPost.author?.username?.[0] || 'U' }}
                    </div>
                    <div>
                      <div class="font-bold text-[var(--c-navy)] text-lg flex items-center gap-2">
                        {{ selectedPost.author?.nickname || selectedPost.author?.username || `用户 ${selectedPost.author_id}` }}
                        <span v-if="selectedPost.author?.trust_level" class="text-xs px-2 py-0.5 rounded-full bg-[var(--c-gold)] text-white">Lv.{{ selectedPost.author?.trust_level }}</span>
                      </div>
                      <div class="text-sm text-[var(--c-navy)]/50 mt-0.5">
                        发布于 {{ new Date(selectedPost.created_at).toLocaleString() }}
                      </div>
                    </div>
                  </div>
                  <el-dropdown trigger="click">
                    <button class="w-8 h-8 rounded-full hover:bg-[var(--c-fog)] flex items-center justify-center text-[var(--c-navy)]/60 transition-colors">
                      <el-icon><MoreFilled /></el-icon>
                    </button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item>分享链接</el-dropdown-item>
                        <el-dropdown-item>举报内容</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>

                <h1 class="text-2xl font-bold text-[var(--c-navy)] mb-4 leading-snug">
                  <el-icon v-if="selectedPost.is_pinned" class="text-orange-500 mr-2 align-middle text-xl"><ArrowUpBold /></el-icon>
                  <el-icon v-if="selectedPost.is_featured" class="text-red-500 mr-2 align-middle text-xl"><StarFilled /></el-icon>
                  {{ selectedPost.title }}
                </h1>

                <div class="prose max-w-none text-[var(--c-navy)]/80 leading-relaxed mb-8 whitespace-pre-wrap text-[1.05rem]">
                  {{ selectedPost.content }}
                </div>

                <!-- Interaction Bar -->
                <div class="flex items-center gap-6 pt-4 border-t border-[var(--c-navy)]/5">
                  <div class="flex items-center bg-[var(--c-fog)] rounded-full border border-[var(--c-navy)]/5 overflow-hidden">
                    <button class="px-4 py-2 hover:bg-[var(--c-indigo)]/10 hover:text-[var(--c-indigo)] transition-colors flex items-center gap-2 font-medium" :class="{'text-[var(--c-indigo)]': isLiked}" @click="toggleLike">
                      <el-icon class="text-lg"><CaretTop /></el-icon> {{ selectedPost.like_count || 0 }}
                    </button>
                    <div class="w-px h-6 bg-[var(--c-navy)]/10"></div>
                    <button class="px-3 py-2 hover:bg-red-50 hover:text-red-600 transition-colors">
                      <el-icon class="text-lg"><CaretBottom /></el-icon>
                    </button>
                  </div>
                  
                  <button class="flex items-center gap-2 text-[var(--c-navy)]/50 hover:text-[var(--c-indigo)] font-medium transition-colors" @click="document.getElementById('comments-section')?.scrollIntoView({ behavior: 'smooth' })">
                    <el-icon class="text-xl"><ChatDotRound /></el-icon> {{ selectedPost.comment_count || 0 }} 评论
                  </button>

                  <button class="flex items-center gap-2 hover:text-orange-500 font-medium transition-colors ml-auto" :class="isBookmarked ? 'text-orange-500' : 'text-[var(--c-navy)]/50'" @click="toggleBookmark">
                    <el-icon class="text-xl"><Star v-if="!isBookmarked" /><StarFilled v-else /></el-icon> {{ isBookmarked ? '已收藏' : '收藏' }}
                  </button>
                </div>
              </div>

              <!-- Comments Section -->
              <div id="comments-section" class="bg-white rounded-2xl shadow-sm border border-[var(--c-navy)]/5 p-6">
                <h3 class="font-bold text-[var(--c-navy)] text-lg mb-6 flex items-center gap-2">
                  <el-icon class="text-[var(--c-indigo)]"><ChatLineRound /></el-icon> 全部评论 ({{ comments.length }})
                </h3>
                
                <div class="flex gap-4 mb-8">
                  <div class="w-10 h-10 rounded-full bg-[var(--c-fog)] flex items-center justify-center font-bold text-[var(--c-navy)] shrink-0">
                    {{ authStore.user?.username?.[0] || 'U' }}
                  </div>
                  <div class="flex-1">
                    <el-input v-model="newComment" type="textarea" :rows="3" placeholder="写下你的想法..." class="mb-3 w-full" />
                    <div class="flex justify-end">
                      <button class="px-5 py-2 rounded-lg bg-[var(--c-indigo)] text-white font-medium hover:opacity-90 transition-opacity disabled:opacity-50" :disabled="!newComment.trim()" @click="submitComment">发布评论</button>
                    </div>
                  </div>
                </div>

                <div class="space-y-6" v-loading="loadingComments">
                  <div v-for="comment in comments" :key="comment.id" class="flex gap-4 group">
                    <div class="w-10 h-10 rounded-full bg-[var(--c-fog)] flex items-center justify-center font-bold text-[var(--c-navy)] shrink-0 mt-1">
                      {{ comment.author?.nickname?.[0] || comment.author?.username?.[0] || 'U' }}
                    </div>
                    <div class="flex-1">
                      <div class="bg-[var(--c-fog)] rounded-2xl p-4">
                        <div class="flex items-center justify-between mb-2">
                          <span class="font-bold text-[var(--c-navy)] text-sm">{{ comment.author?.nickname || comment.author?.username }}</span>
                          <span class="text-xs text-[var(--c-navy)]/40">{{ new Date(comment.created_at).toLocaleString() }}</span>
                        </div>
                        <p class="text-[var(--c-navy)]/80 text-sm whitespace-pre-wrap">{{ comment.content }}</p>
                      </div>
                    </div>
                  </div>
                  <div v-if="!loadingComments && comments.length === 0" class="text-center text-[var(--c-navy)]/40 py-8">
                    还没有人评论，快来抢沙发！
                  </div>
                </div>
              </div>
            </template>
          </div>

          <!-- List State (for posts) -->
          <div v-else class="max-w-[800px] mx-auto space-y-4 pb-24">
            <template v-if="posts.length > 0">
              <div
                v-for="post in posts"
                :key="post.id"
                class="bg-white p-5 rounded-2xl shadow-sm border border-[var(--c-navy)]/5 hover:border-[var(--c-gold)]/30 transition-colors cursor-pointer group"
                @click="fetchPostDetail(post.id)"
              >
                <div class="flex items-center gap-x-3 mb-3">
                  <div
                    class="w-10 h-10 rounded-full bg-[var(--c-fog)] overflow-hidden shrink-0 flex items-center justify-center font-bold text-[var(--c-navy)]"
                  >
                    {{ post.author?.nickname?.[0] || post.author?.username?.[0] || 'U' }}
                  </div>
                  <div>
                    <div class="font-medium text-[var(--c-navy)] text-sm flex gap-x-2 items-center">
                      {{ post.author?.nickname || post.author?.username || `用户 ${post.author_id}` }}
                      <span v-if="post.author?.trust_level" class="text-[10px] px-1.5 py-0.5 rounded-full bg-[var(--c-gold)]/20 text-[var(--c-gold)] font-bold">Lv.{{ post.author?.trust_level }}</span>
                    </div>
                    <div class="text-xs text-[var(--c-navy)]/50 mt-0.5">
                      {{ new Date(post.created_at).toLocaleString() }}
                    </div>
                  </div>
                </div>
                <h3
                  class="font-medium text-[var(--c-navy)] text-lg mb-2 group-hover:text-[var(--c-indigo)]"
                >
                  <el-icon v-if="post.is_pinned" class="text-orange-500 mr-1 align-middle"><ArrowUpBold /></el-icon>
                  <el-icon v-if="post.is_featured" class="text-red-500 mr-1 align-middle"><StarFilled /></el-icon>
                  {{ post.title }}
                </h3>
                <p
                  class="text-[var(--c-navy)]/70 text-sm line-clamp-2 leading-relaxed"
                >
                  {{ post.summary || post.content }}
                </p>
                <div class="mt-4 flex gap-x-4 text-xs text-[var(--c-navy)]/40 font-medium">
                  <span class="flex items-center gap-1"><el-icon><View /></el-icon>{{ post.view_count || 0 }}</span>
                  <span class="flex items-center gap-1"><el-icon><CaretTop /></el-icon>{{ post.like_count || 0 }}</span>
                  <span class="flex items-center gap-1"><el-icon><ChatDotRound /></el-icon>{{ post.comment_count || 0 }}</span>
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
          v-if="activeSectionId === 1 && !selectedPostId"
          class="absolute bottom-8 right-8 w-14 h-14 bg-[var(--c-indigo)] text-white rounded-full flex items-center justify-center shadow-user transition-all hover:-translate-y-1 hover:shadow-xl z-20 group"
          @click="showCreatePostEditor = true"
        >
          <el-icon :size="24"><Plus /></el-icon>
        </button>
      </div>
    </div>

    <!-- Inline Post Editor Overlay -->
    <div v-if="showCreatePostEditor" class="absolute inset-0 z-50 bg-black/40 backdrop-blur-sm flex justify-end">
      <div class="w-full max-w-[800px] h-full bg-white shadow-2xl flex flex-col pt-16 animate-slide-in-right relative">
        <button @click="closeEditor" class="absolute top-6 left-6 w-10 h-10 rounded-full bg-[var(--c-fog)] text-[var(--c-navy)] flex items-center justify-center hover:bg-gray-200 transition-colors">
          <el-icon :size="20"><ArrowLeft /></el-icon>
        </button>
        <div class="px-10 pb-6 border-b border-[var(--c-navy)]/5 pt-1">
          <h2 class="text-2xl font-bold text-[var(--c-navy)]">发布新帖子</h2>
          <p class="text-[var(--c-navy)]/50 mt-1">发往 <span class="font-medium text-[var(--c-indigo)]">{{ activeSpace?.name }}</span></p>
        </div>
        
        <div class="flex-1 overflow-y-auto px-10 py-8 custom-scrollbar space-y-6 bg-[var(--c-fog)]/30">
          <div>
            <label class="block text-sm font-medium text-[var(--c-navy)] mb-2">标题</label>
            <input v-model="newPostForm.title" type="text" placeholder="用一句话概括你的讨论点..." class="w-full text-lg px-4 py-3 bg-white border border-[var(--c-navy)]/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--c-indigo)] focus:border-transparent transition-all shadow-sm" />
          </div>
          <div class="flex flex-col h-[400px]">
            <div class="flex items-center justify-between mb-2">
              <label class="text-sm font-medium text-[var(--c-navy)]">正文 (支持 Markdown)</label>
              
              <!-- Attachment Button -->
              <input type="file" ref="fileInput" @change="handleAttachmentUpload" accept="image/*,.pdf" class="hidden" />
              <button @click="fileInput?.click()" :disabled="isUploadingAttachment" class="flex items-center gap-1 text-sm font-medium text-[var(--c-indigo)] hover:text-opacity-80 disabled:opacity-50">
                <el-icon v-if="isUploadingAttachment" class="is-loading"><Loading /></el-icon>
                <el-icon v-else><Document /></el-icon>
                插入图片 / PDF
              </button>
            </div>
            
            <textarea v-model="newPostForm.content" placeholder="详细描述你想分享或探讨的内容..." class="w-full flex-1 p-4 bg-white border border-[var(--c-navy)]/10 rounded-xl text-base text-[var(--c-navy)]/80 focus:outline-none focus:ring-2 focus:ring-[var(--c-indigo)] focus:border-transparent transition-all shadow-sm resize-none custom-scrollbar"></textarea>
          </div>
        </div>
        
        <div class="p-6 border-t border-[var(--c-navy)]/5 bg-white flex justify-end gap-x-4">
          <button @click="closeEditor" class="px-6 py-2.5 rounded-xl font-medium text-[var(--c-navy)]/70 hover:bg-[var(--c-fog)] transition-colors disabled:opacity-50" :disabled="isSubmittingPost">
            取消
          </button>
          <button @click="submitPost" :disabled="isSubmittingPost || !newPostForm.title.trim() || !newPostForm.content.trim()" class="px-8 py-2.5 rounded-xl font-medium text-white bg-[var(--c-indigo)] hover:bg-opacity-90 shadow-lg shadow-[var(--c-indigo)]/20 transition-all disabled:opacity-50 disabled:shadow-none min-w-[120px]">
            {{ isSubmittingPost ? '发布中...' : '发布帖子' }}
          </button>
        </div>
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
