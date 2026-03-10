<template>
  <div class="min-h-screen bg-[var(--c-fog)] flex flex-col">
    <HomeHeader />

    <main class="flex-1 w-full max-w-[1280px] mx-auto px-4 sm:px-[80px] py-10 pb-20 flex flex-col h-[calc(100vh-88px)]">
      
      <!-- Top header area -->
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold flex items-center gap-2 text-slate-800">
          <el-icon class="text-green-500"><FolderOpened /></el-icon> 我的资料库
        </h1>
        <el-button @click="$router.push('/me/overview')" plain>返回个人中心</el-button>
      </div>

      <!-- Content Area -->
      <div class="flex-1 min-h-0 flex flex-col md:flex-row gap-6">
        <!-- Left: Categories -->
        <div class="w-full md:w-64 shrink-0 bg-white rounded-[var(--radius-card)] shadow-sm border border-[var(--c-navy)]/5 flex flex-col p-3 overflow-y-auto custom-scrollbar">
          <div class="px-4 py-3 text-xs font-bold text-[var(--c-navy)]/40 tracking-widest uppercase mb-1">
            资料分区
          </div>
          <div class="space-y-1">
            <div
              v-for="sub in tabs"
              :key="sub.id"
              class="px-4 py-3 rounded-[12px] cursor-pointer font-medium transition-all group flex items-center justify-between"
              :class="activeTab === sub.id ? 'bg-[var(--c-indigo)] text-white shadow-md' : 'text-[var(--c-navy)] hover:bg-[var(--c-fog)]'"
              @click="activeTab = sub.id; fetchMaterials()"
            >
              <div class="flex items-center gap-2">
                <el-icon><component :is="sub.icon" /></el-icon>
                <span>{{ sub.name }}</span>
              </div>
              <el-icon v-if="activeTab === sub.id" class="text-[var(--c-gold)]"><ArrowRightBold /></el-icon>
            </div>
          </div>
        </div>

        <!-- Right: Materials List -->
        <div class="flex-1 bg-white rounded-[var(--radius-card)] shadow-sm border border-[var(--c-navy)]/5 overflow-y-auto custom-scrollbar flex flex-col relative" v-loading="loading">
          <div v-if="!loading && materials.length === 0" class="flex-1 flex flex-col items-center justify-center text-[var(--c-navy)]/40 min-h-[400px]">
            <div class="w-24 h-24 mb-4 rounded-full bg-[var(--c-navy)]/5 flex items-center justify-center">
              <el-icon :size="40" class="opacity-50"><Document /></el-icon>
            </div>
            <p class="text-xl font-medium mb-2">该分区暂无资料</p>
          </div>

          <div v-else class="p-4 space-y-3">
            <div v-for="mat in materials" :key="mat.id" class="group flex items-center justify-between p-4 rounded-2xl hover:bg-[var(--c-fog)] transition-colors border border-transparent hover:border-[var(--c-navy)]/5 cursor-pointer">
              <div class="flex items-start gap-x-4 overflow-hidden pr-4 max-w-[70%]" @click="viewMaterial(mat)">
                <div class="w-12 h-12 bg-white rounded-[12px] flex items-center justify-center text-[#E85D04] shrink-0 border border-[var(--c-navy)]/5 shadow-sm">
                  <el-icon :size="24"><Document /></el-icon>
                </div>
                <div class="min-w-0">
                  <h4 class="font-medium text-lg text-[var(--c-navy)] mb-1 truncate group-hover:text-[var(--c-indigo)] transition-colors" :title="mat.title">
                    {{ mat.title }}
                  </h4>
                  <div class="flex items-center gap-x-4 text-sm text-[var(--c-navy)]/50">
                    <span class="flex items-center gap-x-1 font-medium"><span class="w-1.5 h-1.5 rounded-full bg-[var(--c-gold)] opacity-80 inline-block"></span>
                      {{ mat.space_name || (spaces.find(s => s.id === mat.space_id)?.name) || '未知空间' }}
                    </span>
                    <span>{{ mat.resource_type === 'past_exam' ? '往年试卷' : mat.resource_type === 'notes' ? '课堂笔记' : mat.resource_type === 'solution' ? '习题答案' : '其他资料' }}</span>
                    <span>更新于：{{ new Date(mat.created_at).toLocaleDateString() }}</span>
                  </div>
                </div>
              </div>

              <div class="flex items-center gap-x-3 pl-4 border-l border-[var(--c-navy)]/5 shrink-0">
                <div class="text-[var(--c-navy)]/40 text-sm hidden lg:block text-right">
                  <div class="flex items-center gap-1 justify-end"><el-icon><Star /></el-icon> {{ mat.bookmark_count || 0 }}</div>
                  <div class="flex items-center gap-1 justify-end"><el-icon><Download /></el-icon> {{ mat.download_count || 0 }}</div>
                </div>
                <!-- Bookmark button -->
                <button @click.stop="toggleBookmark(mat)" class="w-10 h-10 rounded-[12px] flex items-center justify-center bg-white border transition-all shadow-sm"
                  :class="mat.is_bookmarked ? 'text-orange-500 border-orange-200 hover:bg-orange-50' : 'text-slate-400 border-[var(--c-navy)]/10 hover:border-orange-300 hover:text-orange-500'">
                  <el-icon :size="20"><StarFilled v-if="mat.is_bookmarked" /><Star v-else /></el-icon>
                </button>
                <!-- Download button -->
                <button @click.stop="downloadResource(mat)" class="w-10 h-10 rounded-[12px] flex items-center justify-center bg-white text-[var(--c-indigo)] border border-[var(--c-navy)]/10 hover:border-[var(--c-indigo)] hover:bg-[var(--c-indigo)] hover:text-white transition-all shadow-sm" title="下载资料">
                  <el-icon :size="20"><Download /></el-icon>
                </button>
              </div>
            </div>

            <div class="pt-6 pb-2 flex justify-center border-t border-[var(--c-navy)]/5 mt-4" v-if="total > materials.length">
              <el-pagination v-model:current-page="page" :page-size="pageSize" layout="prev, pager, next" :total="total" @current-change="fetchMaterials" />
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { FolderOpened, ArrowRightBold, Document, Download, Star, StarFilled, Upload } from '@element-plus/icons-vue'
import HomeHeader from '@/components/HomeHeader.vue'
import request from '@/utils/request'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()

const tabs = [
  { id: 'uploads', name: '我的上传', icon: Upload },
  { id: 'downloads', name: '我的下载', icon: Download },
  { id: 'favorites', name: '我的收藏', icon: StarFilled }
]
const activeTab = ref('uploads')

const loading = ref(false)
const materials = ref<any[]>([])
const spaces = ref<any[]>([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const fetchSpaces = async () => {
  try {
    const res: any = await request.get('/spaces/')
    spaces.value = res || []
  } catch (e) {
    console.error(e)
  }
}

const fetchMaterials = async () => {
  if (!authStore.user) return
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (activeTab.value === 'uploads') {
      params.uploader_id = authStore.user.id
    } else if (activeTab.value === 'downloads') {
      params.downloaded_by_id = authStore.user.id
    } else if (activeTab.value === 'favorites') {
      params.bookmarked_by_id = authStore.user.id
    }

    const res: any = await request.get('/resources/', { params })
    materials.value = res.items || []
    
    // Setup initial bookmarked state for UI (mock if not returned by backend)
    materials.value.forEach(m => {
      // In favorite tab they are obviously bookmarked, else we might not know without an extra field
      if (activeTab.value === 'favorites') m.is_bookmarked = true
    })
    
    total.value = res.pagination.total
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || '获取列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchMe()
  }
  await fetchSpaces()
  fetchMaterials()
})

const viewMaterial = (mat: any) => {
  console.log('View material', mat)
  // Can be expanded to view material details or trigger download
}

const toggleBookmark = async (mat: any) => {
  try {
    const res: any = await request.post(`/resources/${mat.id}/bookmark`)
    mat.is_bookmarked = res.bookmarked
    if (mat.is_bookmarked) {
      mat.bookmark_count = (mat.bookmark_count || 0) + 1
      ElMessage.success('已加入收藏')
    } else {
      mat.bookmark_count = Math.max(0, (mat.bookmark_count || 0) - 1)
      ElMessage.success('已取消收藏')
      if (activeTab.value === 'favorites') fetchMaterials() // refresh if in favorites
    }
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const downloadResource = async (mat: any) => {
  try {
    const response = await request.post(`/resources/${mat.id}/download`, {}, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response as any]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', mat.filename || `${mat.title}.pdf`) // generic fallback
    document.body.appendChild(link)
    link.click()
    link.remove()
    mat.download_count = (mat.download_count || 0) + 1
  } catch (e) {
    ElMessage.error('下载遇到错误')
  }
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(15, 27, 45, 0.1);
  border-radius: 4px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: rgba(15, 27, 45, 0.2);
}
</style>
