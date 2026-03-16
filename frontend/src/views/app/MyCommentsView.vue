<template>
  <div class="min-h-screen bg-slate-50 pb-12 font-sans flex flex-col">
    <HomeHeader />

    <main class="flex-1 max-w-5xl mx-auto w-full pt-8 px-4 flex flex-col">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold flex items-center gap-2">
          <el-icon class="text-purple-500"><Comment /></el-icon> 我的评论
        </h1>
        <el-button @click="$router.push('/me/overview')" plain>返回个人中心</el-button>
      </div>

      <el-card shadow="never" class="border-none rounded-2xl flex-1 flex flex-col min-h-[60vh] bg-transparent pb-10" v-loading="loading">
        <div v-if="comments.length > 0" class="space-y-6">
          <div 
            v-for="comment in comments" 
            :key="comment.id"
            class="bg-white rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow cursor-pointer border border-slate-100 relative group"
            @click="goToPost(comment)"
          >
            <!-- Comment Header / Context -->
            <div class="flex items-center gap-2 text-xs text-slate-500 mb-3 bg-slate-50 p-3 rounded-xl">
              <span class="font-medium text-slate-700">在帖子：</span>
              <span class="font-bold text-slate-800 line-clamp-1 flex-1">
                {{ comment.post?.title || '未知帖子' }}
              </span>
              <span class="shrink-0 text-slate-400">&middot;</span>
              <el-tag v-if="comment.space" size="small" type="info" effect="plain" class="rounded-md border-none bg-white shrink-0">
                来自 {{ comment.space.name }}
              </el-tag>
            </div>
            
            <!-- Comment Content / Bubble -->
            <div class="pl-2 border-l-4 border-purple-200 group-hover:border-purple-400 transition-colors">
              <p class="text-slate-700 text-sm whitespace-pre-wrap leading-relaxed">
                {{ comment.content }}
              </p>
              <div class="mt-3 text-xs text-slate-400">
                {{ new Date(comment.created_at).toLocaleString() }}
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="!loading" class="my-auto flex justify-center w-full bg-white rounded-2xl p-12 shadow-sm">
          <el-empty description="你还没有发表过评论" />
        </div>

        <div class="mt-8 flex justify-center" v-if="total > 0">
          <el-pagination 
            v-model:current-page="page" 
            :page-size="pageSize" 
            layout="prev, pager, next" 
            :total="total" 
            @current-change="fetchComments" 
          />
        </div>
      </el-card>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import HomeHeader from '@/components/HomeHeader.vue'
import { Comment } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const comments = ref<any[]>([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const fetchComments = async () => {
  if (!authStore.user) return
  loading.value = true
  try {
    const res: any = await request.get('/me/comments', {
      params: { page: page.value, page_size: pageSize.value }
    })
    comments.value = res.items || []
    total.value = res.pagination.total
  } catch (e) {
    console.error('Failed to fetch comments', e)
  } finally {
    loading.value = false
  }
}

const goToPost = (comment: any) => {
  if (comment.post && comment.space) {
    router.push({
      path: '/spaces',
      query: { spaceId: comment.space.id, postId: comment.post.id }
    })
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchMe()
  }
  fetchComments()
})
</script>
