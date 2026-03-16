<template>
  <div class="min-h-screen bg-[var(--c-fog)] flex flex-col">
    <HomeHeader />

    <main class="flex-1 w-full max-w-[1280px] mx-auto px-[80px] py-10 pb-20">
      <div class="bg-white rounded-[var(--radius-card)] border border-[var(--c-navy)]/5 shadow-sm p-6 mb-6">
        <h2 class="text-2xl font-bold text-[var(--c-navy)] mb-2">帖子搜索结果</h2>
        <p class="text-[var(--c-navy)]/60 text-sm">
          <span>关键词：</span>
          <span class="font-semibold">{{ keyword || '请输入关键词' }}</span>
          <span v-if="spaceId" class="ml-3">限定空间：#{{ spaceId }}</span>
        </p>
      </div>

      <div class="max-w-[900px] mx-auto space-y-4">
        <div
          v-for="post in posts"
          :key="post.id"
          class="bg-white p-5 rounded-2xl shadow-sm border border-[var(--c-navy)]/5 hover:border-[var(--c-gold)]/30 transition-colors cursor-pointer group"
          @click="openPost(post.id)"
        >
          <div class="flex items-center gap-x-3 mb-3">
            <div class="w-10 h-10 rounded-full bg-[var(--c-fog)] overflow-hidden shrink-0 flex items-center justify-center font-bold text-[var(--c-navy)]">
              {{ post.author?.nickname?.[0] || post.author?.username?.[0] || 'U' }}
            </div>
            <div>
              <div class="font-medium text-[var(--c-navy)] text-sm">
                {{ post.author?.nickname || post.author?.username || `用户 ${post.author_id}` }}
              </div>
              <div class="text-xs text-[var(--c-navy)]/50 mt-0.5">
                {{ new Date(post.created_at).toLocaleString() }}
              </div>
            </div>
          </div>
          <h3 class="font-medium text-[var(--c-navy)] text-lg mb-2 group-hover:text-[var(--c-indigo)]" v-html="renderHighlight(post.title || '')"></h3>
          <p class="text-[var(--c-navy)]/70 text-sm line-clamp-2 leading-relaxed" v-html="renderHighlight(post.summary || post.content || '')"></p>
        </div>

        <div v-if="posts.length === 0" class="text-center text-[var(--c-navy)]/40 py-16">
          暂无匹配的帖子
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import HomeHeader from '@/components/HomeHeader.vue'
import request from '@/utils/request'
import { highlightKeywordHtml } from '@/utils/search'

const route = useRoute()
const router = useRouter()

const posts = ref<any[]>([])
const keyword = ref('')
const spaceId = ref<number | null>(null)

const renderHighlight = (value: string) => highlightKeywordHtml(value, keyword.value)

const fetchPosts = async () => {
  try {
    const params: Record<string, any> = {
      page: 1,
      page_size: 100,
    }
    if (keyword.value.trim()) params.keyword = keyword.value.trim()
    if (spaceId.value) params.space_id = spaceId.value

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
  if (!targetSpaceId) {
    ElMessage.warning('未找到帖子所在空间')
    return
  }
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

<style scoped>
:deep(.search-highlight) {
  background: rgba(245, 191, 66, 0.35);
  color: inherit;
  border-radius: 4px;
  padding: 0 2px;
}
</style>
