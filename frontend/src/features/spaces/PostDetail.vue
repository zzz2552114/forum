<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ArrowLeft, MoreFilled, ArrowUpBold, StarFilled, CaretTop, CaretBottom, ChatDotRound, Star, ChatLineRound } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  postId: number
}>()

const emit = defineEmits(['back'])

const authStore = useAuthStore()

// State
const selectedPost = ref<any>(null)
const loadingPost = ref(false)
const comments = ref<any[]>([])
const loadingComments = ref(false)
const isLiked = ref(false)
const isBookmarked = ref(false)
const newComment = ref('')
const replyToId = ref<number | null>(null)
const isSubmittingComment = ref(false)

const fetchPostDetail = async (id: number) => {
  loadingPost.value = true
  try {
    selectedPost.value = await request.get(`/posts/${id}`)
    await fetchComments(id)
  } catch (e) {
    ElMessage.error('无法加载帖子详情')
    emit('back')
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
    const rawComments = res.items || []
    
    // 构建一层嵌套的“楼中楼”树形结构
    const topLevel: any[] = []
    const map = new Map()

    rawComments.forEach((c: any) => {
      c.replies = []
      map.set(c.id, c)
    })

    rawComments.forEach((c: any) => {
      if (c.parent_id) {
        let parent = map.get(c.parent_id)
        let rootParent = parent
        // 追溯找到顶级评论（帖子下的一级评论）
        while (rootParent && rootParent.parent_id) {
           rootParent = map.get(rootParent.parent_id)
        }
        if (rootParent) {
          rootParent.replies.push(c)
        } else if (parent) {
          parent.replies.push(c)
        } else {
          topLevel.push(c)
        }
      } else {
        topLevel.push(c)
      }
    })
    
    comments.value = topLevel
  } catch (e) {
    console.error(e)
  } finally {
    loadingComments.value = false
  }
}

const submitComment = async () => {
  if (!newComment.value.trim() || !props.postId) return
  isSubmittingComment.value = true
  try {
    const payload: any = { content: newComment.value, post_id: props.postId }
    if (replyToId.value) {
      payload.parent_id = replyToId.value
    }
    await request.post(`/comments/`, payload)
    newComment.value = ''
    replyToId.value = null
    ElMessage.success('评论发布成功')
    fetchComments(props.postId)
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || err.response?.data?.detail || err.message || '发布评论失败')
  } finally {
    isSubmittingComment.value = false
  }
}

const handleReply = (commentId: number, username: string) => {
  replyToId.value = commentId
  newComment.value = `回复 @${username} : `
  document.getElementById('comment-input')?.focus()
}

const toggleLike = async () => {
  if (!authStore.isAuthenticated) return ElMessage.warning('请先登录再操作')
  if (!props.postId || !selectedPost.value) return
  try {
    if (isLiked.value) {
      await request.delete(`/posts/${props.postId}/likes/me`)
      selectedPost.value.like_count--
    } else {
      await request.put(`/posts/${props.postId}/likes/me`)
      selectedPost.value.like_count++
    }
    isLiked.value = !isLiked.value
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || '操作失败')
  }
}

const toggleBookmark = async () => {
  if (!authStore.isAuthenticated) return ElMessage.warning('请先登录再操作')
  if (!props.postId || !selectedPost.value) return
  try {
    if (isBookmarked.value) {
      await request.delete(`/posts/${props.postId}/bookmarks/me`)
    } else {
      await request.put(`/posts/${props.postId}/bookmarks/me`)
    }
    isBookmarked.value = !isBookmarked.value
    ElMessage.success(isBookmarked.value ? '已收藏' : '已取消收藏')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || '操作失败')
  }
}

const scrollToComments = () => {
  document.getElementById('comments-section')?.scrollIntoView({ behavior: 'smooth' })
}

watch(() => props.postId, (newId) => {
  if (newId) {
    fetchPostDetail(newId)
    // reset state
    isLiked.value = false
    isBookmarked.value = false
    replyToId.value = null
    newComment.value = ''
  }
})

onMounted(() => {
  if (props.postId) {
    fetchPostDetail(props.postId)
  }
})
</script>

<template>
  <div class="max-w-[800px] mx-auto pb-24" v-loading="loadingPost">
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
          
          <button class="flex items-center gap-2 text-[var(--c-navy)]/50 hover:text-[var(--c-indigo)] font-medium transition-colors" @click="scrollToComments">
            <el-icon class="text-xl"><ChatDotRound /></el-icon> {{ comments.length }} 评论
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
          <div class="flex-1 relative">
            <div v-if="replyToId" class="absolute -top-6 left-0 text-xs text-indigo-500 font-medium flex items-center gap-2">
               正在回复...
               <button @click="replyToId = null; newComment = ''" class="text-[var(--c-navy)]/40 hover:text-red-500">取消</button>
            </div>
            <el-input id="comment-input" v-model="newComment" type="textarea" :rows="3" placeholder="写下你的想法..." class="mb-3 w-full" />
            <div class="flex justify-end">
              <button class="px-5 py-2 rounded-lg bg-[var(--c-indigo)] text-white font-medium hover:opacity-90 transition-opacity disabled:opacity-50" :disabled="!newComment.trim()" @click="submitComment">发布评论</button>
            </div>
          </div>
        </div>

        <div class="space-y-6" v-loading="loadingComments">
          <!-- Parent Comments -->
          <div v-for="comment in comments" :key="comment.id" class="flex gap-4 group">
            <div class="w-10 h-10 rounded-full bg-[var(--c-fog)] flex items-center justify-center font-bold text-[var(--c-navy)] shrink-0 mt-1">
              {{ comment.author?.nickname?.[0] || comment.author?.username?.[0] || 'U' }}
            </div>
            <div class="flex-1">
              <div class="bg-[var(--c-fog)] rounded-2xl p-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="font-bold text-[var(--c-navy)] text-sm flex items-center gap-2">
                    {{ comment.author?.nickname || comment.author?.username }}
                    <span v-if="comment.author?.trust_level" class="text-[10px] px-1.5 rounded-full bg-[var(--c-gold)] text-white">Lv.{{ comment.author?.trust_level }}</span>
                  </span>
                  <span class="text-xs text-[var(--c-navy)]/40">{{ new Date(comment.created_at).toLocaleString() }}</span>
                </div>
                <p class="text-[var(--c-navy)]/80 text-sm whitespace-pre-wrap">{{ comment.content }}</p>
                <div class="mt-2 flex justify-end">
                   <button class="text-xs font-medium text-[var(--c-navy)]/40 hover:text-[var(--c-indigo)] opacity-0 group-hover:opacity-100 transition-opacity" @click="handleReply(comment.id, comment.author?.nickname || comment.author?.username)">回复</button>
                </div>
              </div>
              
              <!-- Nested Replies (Max 1 level deep roughly) -->
              <div v-if="comment.replies && comment.replies.length > 0" class="mt-3 space-y-3">
                <div v-for="reply in comment.replies" :key="reply.id" class="flex gap-3 group/reply">
                  <div class="w-8 h-8 rounded-full bg-white flex items-center justify-center font-bold text-[var(--c-navy)]/70 shrink-0 border border-[var(--c-navy)]/5 text-xs">
                    {{ reply.author?.nickname?.[0] || reply.author?.username?.[0] || 'U' }}
                  </div>
                  <div class="flex-1">
                    <div class="bg-white border border-[var(--c-navy)]/5 rounded-2xl p-3">
                      <div class="flex items-center justify-between mb-1">
                        <span class="font-bold text-[var(--c-navy)]/80 text-xs">{{ reply.author?.nickname || reply.author?.username }}</span>
                        <span class="text-[10px] text-[var(--c-navy)]/40">{{ new Date(reply.created_at).toLocaleString() }}</span>
                      </div>
                      <p class="text-[var(--c-navy)]/70 text-sm whitespace-pre-wrap">{{ reply.content }}</p>
                      <div class="mt-1 flex justify-end">
                         <button class="text-[10px] font-medium text-[var(--c-navy)]/40 hover:text-[var(--c-indigo)] opacity-0 group-hover/reply:opacity-100 transition-opacity" @click="handleReply(comment.id, reply.author?.nickname || reply.author?.username)">回复</button>
                      </div>
                    </div>
                  </div>
                </div>
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
</template>
