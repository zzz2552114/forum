<template>
  <div class="min-h-screen bg-slate-50 pb-12 font-sans flex flex-col">
    <HomeHeader />

    <main class="flex-1 max-w-5xl mx-auto w-full pt-8 px-4 flex flex-col">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold flex items-center gap-2">
          <el-icon class="text-orange-500"><StarFilled /></el-icon> 我的收藏 (帖子)
        </h1>
        <el-button @click="$router.push('/me/overview')" plain>返回个人中心</el-button>
      </div>

      <el-card shadow="never" class="border-none rounded-2xl flex-1 flex flex-col min-h-[60vh]" v-loading="loading">
        <div v-if="posts.length > 0" class="space-y-4">
          <PostCard v-for="post in posts" :key="post.id" :post="post" />
        </div>
        <el-empty v-else-if="!loading" description="你还没有收藏过任何帖子" class="my-auto" />

        <div class="mt-8 flex justify-center" v-if="total > 0">
          <el-pagination 
            v-model:current-page="page" 
            :page-size="pageSize" 
            layout="prev, pager, next" 
            :total="total" 
            @current-change="fetchPosts" 
          />
        </div>
      </el-card>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import HomeHeader from '@/components/HomeHeader.vue'
import PostCard from '@/components/post/PostCard.vue'
import { StarFilled } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const loading = ref(true)
const posts = ref<any[]>([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const fetchPosts = async () => {
  if (!authStore.user) return
  loading.value = true
  try {
    const res: any = await request.get('/posts/', {
      params: { bookmarked_by_id: authStore.user.id, page: page.value, page_size: pageSize.value }
    })
    posts.value = res.items || []
    total.value = res.pagination.total
  } catch (e) {
    console.error('Failed to fetch bookmarked posts', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchMe()
  }
  fetchPosts()
})
</script>
