<template>
  <div class="max-w-4xl mx-auto space-y-6 mt-4" v-loading="loading">
    
    <!-- Original Post -->
    <el-card v-if="post" shadow="never" class="border-none rounded-2xl p-2 md:p-6 mb-8">
      <!-- Author info & Meta -->
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <el-avatar :size="48" :src="post.author?.avatar_url || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" class="border border-slate-200" />
          <div>
            <div class="font-bold text-slate-800 text-lg flex items-center gap-2">
              {{ post.author?.nickname || post.author?.username }}
              <el-tag v-if="post.author?.trust_level" size="small" type="success" effect="light" class="rounded-full">Lv.{{ post.author?.trust_level }}</el-tag>
            </div>
            <div class="text-sm text-slate-400 mt-0.5 flex gap-2 items-center">
              <span>发布于 {{ new Date(post.created_at).toLocaleString() }}</span>
              <span>&middot;</span>
              <span class="flex items-center gap-1 hover:text-blue-500 cursor-pointer" @click="$router.push(`/spaces/${post.space_id}`)">
                在 <strong class="text-slate-500">{{ spaceName }}</strong>
              </span>
            </div>
          </div>
        </div>
        
        <!-- Action Menu -->
        <div>
          <el-dropdown trigger="click">
            <el-button type="info" plain circle class="border-none"><el-icon><MoreFilled /></el-icon></el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>分享链接</el-dropdown-item>
                <el-dropdown-item>举报内容</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- Title & Tags -->
      <h1 class="text-2xl md:text-3xl font-bold text-slate-800 mb-4 leading-snug">
        <el-icon v-if="post.is_pinned" class="text-orange-500 mr-2 text-2xl align-middle" title="置顶"><ArrowUpBold /></el-icon>
        <el-icon v-if="post.is_featured" class="text-red-500 mr-2 text-2xl align-middle" title="精华"><StarFilled /></el-icon>
        {{ post.title }}
      </h1>
      
      <div class="flex flex-wrap gap-2 mb-6" v-if="post.tags && post.tags.length > 0">
        <el-tag v-for="tag in post.tags" :key="tag.id" type="info" effect="plain" class="rounded-md border-none bg-slate-100 px-3">
          {{ tag.name }}
        </el-tag>
      </div>

      <!-- Content Markdown View (stubbed as simple text for now) -->
      <div class="prose max-w-none text-slate-700 leading-relaxed mb-8 markdown-body">
        <p class="whitespace-pre-wrap">{{ post.content }}</p>
      </div>
      
      <!-- Interaction Bar -->
      <div class="flex items-center gap-6 pt-4 border-t border-slate-100">
        <div class="flex items-center bg-slate-50 rounded-full border border-slate-200 overflow-hidden">
          <button class="px-4 py-2 hover:bg-blue-50 hover:text-blue-600 transition-colors flex items-center gap-2 font-medium" :class="{'text-blue-600': false}" @click="toggleLike">
            <el-icon class="text-lg"><CaretTop /></el-icon> {{ post.like_count || 0 }}
          </button>
          <div class="w-px h-6 bg-slate-200"></div>
          <button class="px-3 py-2 hover:bg-red-50 hover:text-red-600 transition-colors">
            <el-icon class="text-lg"><CaretBottom /></el-icon>
          </button>
        </div>
        
        <button class="flex items-center gap-2 text-slate-500 hover:text-blue-600 font-medium transition-colors" @click="scrollToComments">
          <el-icon class="text-xl"><ChatDotRound /></el-icon> {{ post.comment_count || 0 }} 评论
        </button>

        <button class="flex items-center gap-2 text-slate-500 hover:text-orange-500 font-medium transition-colors ml-auto" @click="toggleBookmark">
          <el-icon class="text-xl"><Star /></el-icon> 收藏
        </button>
      </div>
    </el-card>

    <!-- Comments Section -->
    <div id="comments" class="bg-white rounded-2xl shadow-sm border p-2 md:p-6" v-if="post">
      <h3 class="font-bold text-slate-800 text-lg mb-6 flex items-center gap-2">
        <el-icon class="text-blue-600"><ChatLineRound /></el-icon> 全部评论 ({{ totalComments }})
      </h3>
      
      <!-- Comment Input -->
      <div class="flex gap-4 mb-8">
        <el-avatar :size="40" :src="authStore.user?.avatar_url || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
        <div class="flex-1">
          <el-input v-model="newComment" type="textarea" :rows="3" placeholder="写下你的想法..." class="mb-3" />
          <div class="flex justify-end">
            <el-button type="primary" :disabled="!newComment.trim()" @click="submitComment">发布评论</el-button>
          </div>
        </div>
      </div>
      
      <!-- Comments List -->
      <div class="space-y-6" v-loading="loadingComments">
        <div v-for="comment in comments" :key="comment.id" class="flex gap-4 group">
          <el-avatar :size="36" :src="comment.author?.avatar_url || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" class="mt-1 shrink-0" />
          <div class="flex-1">
            <div class="bg-slate-50 rounded-2xl p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="font-bold text-slate-700 text-sm">{{ comment.author?.nickname || comment.author?.username }}</span>
                <span class="text-xs text-slate-400">{{ new Date(comment.created_at).toLocaleString() }}</span>
              </div>
              <p class="text-slate-700 text-sm whitespace-pre-wrap">{{ comment.content }}</p>
            </div>
            <div class="flex items-center gap-4 mt-2 px-2">
              <button class="text-xs text-slate-500 hover:text-blue-600 flex items-center gap-1 font-medium transition-colors">
                <el-icon><CaretTop /></el-icon> {{ comment.like_count || 0 }} 点赞
              </button>
              <button class="text-xs text-slate-500 hover:text-blue-600 font-medium transition-colors">回复</button>
            </div>
          </div>
        </div>
        
        <el-empty v-if="!loadingComments && comments.length === 0" description="还没有人评论，快来抢沙发！" />
        
        <!-- Pagination -->
        <div class="mt-6 flex justify-center" v-if="totalComments > 0">
          <el-pagination v-model:current-page="commentPage" :page-size="commentPageSize" layout="prev, pager, next" :total="totalComments" @current-change="fetchComments" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'
import { CaretTop, CaretBottom, ChatDotRound, Star, MoreFilled, ArrowUpBold, StarFilled, ChatLineRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const authStore = useAuthStore()
const postId = ref(route.params.postId)

const post = ref<any>(null)
const spaceName = ref('未知空间')
const loading = ref(true)

const comments = ref<any[]>([])
const loadingComments = ref(true)
const totalComments = ref(0)
const commentPage = ref(1)
const commentPageSize = ref(10)
const newComment = ref('')

const fetchPost = async () => {
  loading.value = true
  try {
    post.value = await request.get(`/posts/${postId.value}`)
    if (post.value?.space_id) {
      const spaceData: any = await request.get(`/spaces/${post.value.space_id}`)
      spaceName.value = spaceData.name
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const fetchComments = async () => {
  loadingComments.value = true
  try {
    const res: any = await request.get(`/comments/post/${postId.value}`, {
      params: { page: commentPage.value, page_size: commentPageSize.value }
    })
    comments.value = res.items
    totalComments.value = res.pagination.total
  } catch (e) {
    console.error(e)
  } finally {
    loadingComments.value = false
  }
}

const submitComment = async () => {
  try {
    await request.post('/comments/', {
      content: newComment.value,
      post_id: parseInt(postId.value as string)
    })
    ElMessage.success('评论发布成功')
    newComment.value = ''
    commentPage.value = 1
    await fetchComments()
  } catch (e) {
    console.error(e)
  }
}

const toggleLike = () => {
  ElMessage.info('点赞功能开发中')
}

const toggleBookmark = () => {
  ElMessage.info('收藏功能开发中')
}

const scrollToComments = () => {
  document.getElementById('comments')?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(() => {
  fetchPost()
  fetchComments()
})
</script>

<style scoped>
/* Optional custom scrollbar for better aesthetics if needed */
.markdown-body {
  font-size: 1.05rem;
}
</style>
