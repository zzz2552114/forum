<template>
  <div class="min-h-screen bg-[var(--c-fog)] flex flex-col">
    <HomeHeader />

    <main class="flex-1 w-full max-w-[1280px] mx-auto px-[80px] py-10 pb-20">
      <div class="bg-white rounded-[var(--radius-card)] border border-[var(--c-navy)]/5 shadow-sm p-6 mb-6">
        <h2 class="text-2xl font-bold text-[var(--c-navy)] mb-2">其他资料搜索结果</h2>
        <p class="text-[var(--c-navy)]/60 text-sm">
          关键词：<span class="font-semibold">{{ keyword || '（未输入）' }}</span>
          <span v-if="spaceId" class="ml-3">限定空间：#{{ spaceId }}</span>
        </p>
      </div>

      <div class="bg-white rounded-[var(--radius-card)] border border-[var(--c-navy)]/5 shadow-sm p-4 space-y-3">
        <div
          v-for="item in resources"
          :key="item.id"
          class="group flex items-center justify-between p-4 rounded-2xl hover:bg-[var(--c-fog)] transition-colors border border-transparent hover:border-[var(--c-navy)]/5"
        >
          <div class="flex items-start gap-x-4 overflow-hidden pr-4 max-w-[78%]">
            <div class="w-12 h-12 bg-white rounded-[12px] flex items-center justify-center text-[var(--c-navy)] shrink-0 border border-[var(--c-navy)]/5 shadow-sm">
              <el-icon :size="24"><Document /></el-icon>
            </div>
            <div class="min-w-0">
              <button class="font-medium text-lg text-[var(--c-navy)] mb-1 truncate group-hover:text-[var(--c-indigo)] transition-colors text-left" @click="goToExplore(item)">
                {{ item.title }}
              </button>
              <div class="flex items-center gap-x-4 text-sm text-[var(--c-navy)]/50">
                <span>{{ item.school_space_name || '未知学校' }}</span>
                <span>{{ item.resource_type || 'other' }}</span>
                <span>最后更新：{{ new Date(item.created_at).toLocaleDateString() }}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-x-3 pl-3 border-l border-[var(--c-navy)]/5 shrink-0">
            <button
              class="w-10 h-10 rounded-[12px] flex items-center justify-center bg-white border transition-all shadow-sm"
              :class="item.is_bookmarked ? 'text-orange-500 border-orange-200 hover:bg-orange-50' : 'text-[var(--c-indigo)] border-[var(--c-navy)]/10 hover:border-orange-300 hover:text-orange-500'"
              @click.stop="toggleBookmark(item)"
            >
              <el-icon :size="20"><StarFilled v-if="item.is_bookmarked" /><Star v-else /></el-icon>
            </button>
            <button
              class="w-10 h-10 rounded-[12px] flex items-center justify-center bg-white text-[var(--c-indigo)] border border-[var(--c-navy)]/10 hover:border-[var(--c-indigo)] group-hover:bg-[var(--c-indigo)] group-hover:text-white transition-all shadow-sm"
              @click.stop="downloadFile(item)"
            >
              <el-icon :size="20" style="transform: rotate(180deg)"><Upload /></el-icon>
            </button>
          </div>
        </div>

        <div v-if="resources.length === 0" class="text-center text-[var(--c-navy)]/40 py-16">
          暂无匹配的其他资料
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, Star, StarFilled, Upload } from '@element-plus/icons-vue'

import HomeHeader from '@/components/HomeHeader.vue'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()

const keyword = ref('')
const spaceId = ref<number | null>(null)
const resources = ref<any[]>([])

const syncFromRoute = () => {
  keyword.value = typeof route.query.keyword === 'string' ? route.query.keyword : ''
  const parsedSpaceId = Number(route.query.spaceId)
  spaceId.value = !Number.isNaN(parsedSpaceId) && parsedSpaceId > 0 ? parsedSpaceId : null
}

const fetchResources = async () => {
  try {
    const params: Record<string, any> = {
      page: 1,
      page_size: 100,
      scope: 'explore',
    }
    if (keyword.value.trim()) {
      params.keyword = keyword.value.trim()
    }
    if (spaceId.value) {
      params.space_id = spaceId.value
    }
    const res: any = await request.get('/search/resources', { params })
    resources.value = res.items || []
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || error.message || '加载其他资料搜索结果失败')
    resources.value = []
  }
}

const goToExplore = (item: any) => {
  router.push({
    path: '/explore',
    query: {
      keyword: item.title || '',
      schoolSpaceId: item.school_space_id ? String(item.school_space_id) : item.space_id ? String(item.space_id) : undefined,
      resourceId: String(item.id),
    },
  })
}

const downloadFile = (item: any) => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录再下载')
    return
  }
  window.open(`/api/v1/resources/${item.id}/download?token=${encodeURIComponent(token)}`, '_blank')
  item.download_count = (item.download_count || 0) + 1
}

const toggleBookmark = async (item: any) => {
  try {
    const res: any = await request.post(`/resources/${item.id}/bookmark`)
    item.is_bookmarked = res.bookmarked
    if (item.is_bookmarked) {
      item.bookmark_count = (item.bookmark_count || 0) + 1
      ElMessage.success('已加入收藏')
    } else {
      item.bookmark_count = Math.max(0, (item.bookmark_count || 0) - 1)
      ElMessage.success('已取消收藏')
    }
  } catch {
    ElMessage.error('收藏操作失败')
  }
}

onMounted(async () => {
  syncFromRoute()
  await fetchResources()
})

watch(
  () => route.query,
  async () => {
    syncFromRoute()
    await fetchResources()
  },
  { deep: true },
)
</script>
