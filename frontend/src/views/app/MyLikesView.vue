<template>
  <div class="min-h-screen bg-slate-50 pb-12 font-sans flex flex-col">
    <HomeHeader />

    <main class="flex-1 max-w-5xl mx-auto w-full pt-8 px-4 flex flex-col">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold flex items-center gap-2">
          <el-icon class="text-red-500"><Pointer /></el-icon> 我的点赞
        </h1>
        <el-button @click="$router.push('/me/overview')" plain>返回个人中心</el-button>
      </div>

      <el-card shadow="never" class="border-none rounded-2xl flex-1 flex flex-col min-h-[60vh] bg-transparent" v-loading="loading">
        <div v-if="likes.length > 0" class="space-y-4">
          <PostCard v-for="like in likes" :key="like.id" :post="like" />
        </div>
        <div v-else-if="!loading" class="my-auto flex justify-center w-full bg-white rounded-2xl p-12 shadow-sm">
          <el-empty description="你还没有点赞过任何内容" />
        </div>

        <div class="mt-8 flex justify-center" v-if="total > 0">
          <el-pagination 
            v-model:current-page="page" 
            :page-size="pageSize" 
            layout="prev, pager, next" 
            :total="total" 
            @current-change="fetchLikes" 
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
import { Pointer } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const loading = ref(true)
const likes = ref<any[]>([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const fetchLikes = async () => {
  if (!authStore.user) return
  loading.value = true
  try {
    const res: any = await request.get('/me/likes', {
      params: { page: page.value, page_size: pageSize.value }
    })
    likes.value = res.items || []
    total.value = res.pagination.total
  } catch (e) {
    console.error('Failed to fetch likes', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchMe()
  }
  fetchLikes()
})
</script>
