<template>
  <div class="min-h-screen bg-[var(--c-fog)] flex flex-col">
    <HomeHeader />

    <main class="flex-1 w-full max-w-[1280px] mx-auto px-[80px] py-10 pb-20">
      <div class="bg-white rounded-[var(--radius-card)] border border-[var(--c-navy)]/5 shadow-sm p-6 mb-6">
        <h2 class="text-2xl font-bold text-[var(--c-navy)] mb-2">帖子搜索结果</h2>
        <p class="text-[var(--c-navy)]/60 text-sm">
          关键词：<span class="font-semibold">{{ keyword || '（未输入）' }}</span>
          <span v-if="spaceId" class="ml-3">限定空间：#{{ spaceId }}</span>
        </p>
      </div>

      <div class="max-w-[900px] mx-auto">
        <PostList :posts="posts" @read="openPost" />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import HomeHeader from '@/components/HomeHeader.vue'
import PostList from '@/features/spaces/PostList.vue'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()

const posts = ref<any[]>([])
const keyword = ref('')
const spaceId = ref<number | null>(null)

const fetchPosts = async () => {
  try {
    const params: Record<string, any> = {
      page: 1,
      page_size: 100,
    }
    if (keyword.value.trim()) {
      params.keyword = keyword.value.trim()
    }
    if (spaceId.value) {
      params.space_id = spaceId.value
    }

    const res: any = await request.get('/search/posts', { params })
    posts.value = res.items || []
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || error.message || '加载帖子搜索结果失败')
    posts.value = []
  }
}

const syncFromRoute = () => {
  keyword.value = typeof route.query.keyword === 'string' ? route.query.keyword : ''
  const parsedSpaceId = Number(route.query.spaceId)
  spaceId.value = !Number.isNaN(parsedSpaceId) && parsedSpaceId > 0 ? parsedSpaceId : null
}

const openPost = (postId: number) => {
  const post = posts.value.find((item: any) => item.id === postId)
  const targetSpaceId = post?.space_id || spaceId.value
  router.push({
    path: '/spaces',
    query: {
      spaceId: String(targetSpaceId),
      sectionId: '1',
      postId: String(postId),
    },
  })
}

onMounted(async () => {
  syncFromRoute()
  await fetchPosts()
})

watch(
  () => route.query,
  async () => {
    syncFromRoute()
    await fetchPosts()
  },
  { deep: true },
)
</script>
