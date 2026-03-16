<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { CollectionTag, Document, Download, Plus, Search, Star, StarFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'

import HomeHeader from '@/components/HomeHeader.vue'
import { SEARCH_RESOURCE_PAGE_SIZE } from '@/constants/search'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'
import { fuzzySort, highlightKeywordHtml } from '@/utils/search'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const searchQuery = ref('')
const activeSubject = ref('全部')
const selectedSchoolId = ref<number | null>(null)
const selectedCourseId = ref<number | null>(null)

const categories = ref<any[]>([])
const spaces = ref<any[]>([])
const materials = ref<any[]>([])

const showUploadModal = ref(false)
const selectedFile = ref<File | null>(null)
const isUploading = ref(false)
const uploadForm = ref({
  title: '',
  description: '',
  school_space_id: null as number | null,
  space_id: null as number | null,
  resource_type: 'notes',
  version_note: 'Initial Upload',
})

const normalizeName = (value: unknown) => String(value || '').toLowerCase()
const isCourseCategory = (category: any) =>
  ['课程', 'course'].includes(normalizeName(category?.name)) || normalizeName(category?.slug) === 'course'
const isSchoolCategory = (category: any) =>
  ['学校', 'school'].includes(normalizeName(category?.name)) || normalizeName(category?.slug) === 'school'

const fetchCategories = async () => {
  try {
    const res: any = await request.get('/categories/')
    categories.value = Array.isArray(res) ? res : []
  } catch (error) {
    console.error('Failed to fetch categories', error)
    categories.value = []
  }
}

const fetchSpaces = async () => {
  try {
    const res: any = await request.get('/spaces/')
    spaces.value = Array.isArray(res) ? res : []
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || error.message || '获取空间列表失败')
    spaces.value = []
  }
}

const courseCategory = computed(() => categories.value.find((item: any) => isCourseCategory(item)))
const schoolCategory = computed(() => categories.value.find((item: any) => isSchoolCategory(item)))
const courseSpaces = computed(() => {
  if (!courseCategory.value) return []
  return spaces.value.filter((item: any) => item.category_id === courseCategory.value.id)
})
const schoolSpaces = computed(() => {
  if (!schoolCategory.value) return []
  return spaces.value.filter((item: any) => item.category_id === schoolCategory.value.id)
})
const dynamicSubjects = computed(() => ['全部', ...courseSpaces.value.map((item: any) => item.name)])

const fetchMaterials = async () => {
  try {
    const params: Record<string, any> = {
      page: 1,
      page_size: SEARCH_RESOURCE_PAGE_SIZE,
      scope: 'materials',
    }
    if (searchQuery.value.trim()) params.keyword = searchQuery.value.trim()
    if (selectedSchoolId.value) params.school_space_id = selectedSchoolId.value
    if (selectedCourseId.value) params.course_space_id = selectedCourseId.value

    const res: any = await request.get('/search/resources', { params })
    materials.value = Array.isArray(res.items) ? res.items : []
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || error.message || '获取题库资料失败')
  }
}

const handleSearch = async () => {
  if (!selectedCourseId.value) {
    const query: Record<string, string> = {}
    if (searchQuery.value.trim()) query.keyword = searchQuery.value.trim()
    if (selectedSchoolId.value) query.schoolSpaceId = String(selectedSchoolId.value)
    router.push({ path: '/search/materials', query })
    return
  }
  await fetchMaterials()
}

const handleSubjectSelect = (subjectName: string) => {
  activeSubject.value = subjectName
  if (subjectName === '全部') {
    selectedCourseId.value = null
    return
  }
  const target = spaces.value.find((item: any) => item.name === subjectName)
  selectedCourseId.value = target?.id || null
}

const clearFilters = async () => {
  searchQuery.value = ''
  selectedSchoolId.value = null
  selectedCourseId.value = null
  activeSubject.value = '全部'
  await fetchMaterials()
}

const handleUploadClick = () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录再分享资料')
    router.push('/?showLogin=true')
    return
  }
  showUploadModal.value = true
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0] || null
  }
}

const submitUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请选择上传文件')
    return
  }
  if (!uploadForm.value.title || !uploadForm.value.space_id) {
    ElMessage.warning('请完成必填项')
    return
  }

  isUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('biz_type', 'resource')

    const fileRes: any = await request.post('/files/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    await request.post('/resources/', {
      title: uploadForm.value.title,
      description: uploadForm.value.description,
      school_space_id: uploadForm.value.school_space_id,
      space_id: uploadForm.value.space_id,
      resource_type: uploadForm.value.resource_type,
      file_id: fileRes.id,
      version_note: uploadForm.value.version_note,
    })

    ElMessage.success('上传成功')
    showUploadModal.value = false
    selectedFile.value = null
    uploadForm.value = {
      title: '',
      description: '',
      school_space_id: null,
      space_id: null,
      resource_type: 'notes',
      version_note: 'Initial Upload',
    }
    await fetchMaterials()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || error.response?.data?.detail || error.message || '上传失败')
  } finally {
    isUploading.value = false
  }
}

const downloadFile = (resource: any) => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录再下载')
    return
  }
  window.open(`/api/v1/resources/${resource.id}/download?token=${encodeURIComponent(token)}`, '_blank')
  resource.download_count = (resource.download_count || 0) + 1
}

const toggleBookmark = async (resource: any) => {
  try {
    const res: any = await request.post(`/resources/${resource.id}/bookmark`)
    resource.is_bookmarked = res.bookmarked
    if (resource.is_bookmarked) {
      resource.bookmark_count = (resource.bookmark_count || 0) + 1
      ElMessage.success('已加入收藏')
    } else {
      resource.bookmark_count = Math.max(0, (resource.bookmark_count || 0) - 1)
      ElMessage.success('已取消收藏')
    }
  } catch {
    ElMessage.error('操作失败')
  }
}

const filteredMaterials = computed(() => {
  const sortedByTime = [...materials.value].sort(
    (a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  )
  if (!searchQuery.value.trim()) return sortedByTime

  return fuzzySort(sortedByTime, searchQuery.value, (item: any) => [
    { text: item.title, weight: 10 },
    { text: item.description, weight: 4 },
    { text: item.space_name || item.course_space_name, weight: 3 },
    { text: item.school_space_name, weight: 3 },
  ])
})

const renderHighlight = (value: string) => highlightKeywordHtml(value, searchQuery.value)

watch(selectedCourseId, (courseId) => {
  if (!courseId) {
    activeSubject.value = '全部'
    return
  }
  const target = spaces.value.find((item: any) => item.id === courseId)
  activeSubject.value = target?.name || '全部'
})

onMounted(async () => {
  await fetchCategories()
  await fetchSpaces()

  if (typeof route.query.keyword === 'string') searchQuery.value = route.query.keyword
  const querySchoolId = Number(route.query.schoolSpaceId)
  const queryCourseId = Number(route.query.courseSpaceId)
  const querySpaceId = Number(route.query.spaceId)
  if (!Number.isNaN(querySchoolId) && querySchoolId > 0) selectedSchoolId.value = querySchoolId
  if (!Number.isNaN(queryCourseId) && queryCourseId > 0) {
    selectedCourseId.value = queryCourseId
  } else if (!Number.isNaN(querySpaceId) && querySpaceId > 0) {
    selectedCourseId.value = querySpaceId
  }

  await fetchMaterials()
})
</script>

<template>
  <div class="min-h-screen bg-[var(--c-fog)] flex flex-col">
    <HomeHeader />

    <main class="flex-1 w-full max-w-[1280px] mx-auto px-[80px] py-10 pb-20 flex flex-col h-[calc(100vh-88px)]">
      <div class="w-full bg-white rounded-[var(--radius-card)] p-6 shadow-sm border border-[var(--c-navy)]/5 mb-6 shrink-0 relative overflow-hidden">
        <div class="absolute right-0 top-0 bottom-0 w-64 bg-gradient-to-l from-[var(--c-fog)] to-transparent pointer-events-none z-0"></div>
        <div class="relative z-10 flex gap-x-3">
          <div class="relative flex-1">
            <el-icon class="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--c-navy)] opacity-40 z-10" :size="20"><Search /></el-icon>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索题库资料名称、摘要或文件名..."
              class="w-full h-14 bg-[var(--c-fog)] rounded-[16px] pl-12 pr-4 text-[var(--c-navy)] text-lg focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)] focus:bg-white transition-all border border-transparent shadow-inner"
              @keyup.enter="handleSearch"
            />
          </div>

          <el-select v-model="selectedSchoolId" clearable placeholder="学校筛选" class="w-[170px]" size="large">
            <el-option v-for="space in schoolSpaces" :key="space.id" :label="space.name" :value="space.id" />
          </el-select>

          <el-select v-model="selectedCourseId" clearable placeholder="课程筛选" class="w-[190px]" size="large">
            <el-option v-for="space in courseSpaces" :key="space.id" :label="space.name" :value="space.id" />
          </el-select>

          <button class="h-14 px-6 bg-[var(--c-indigo)] text-white rounded-[16px] font-medium text-lg hover:bg-opacity-90 shadow-lg shadow-[var(--c-indigo)]/20 transition-all shrink-0" @click="handleSearch">
            搜索库
          </button>
          <button class="h-14 px-6 bg-[var(--c-gold)] text-white rounded-[16px] font-medium text-lg hover:bg-opacity-90 shadow-lg shadow-[var(--c-gold)]/20 transition-all shrink-0 flex items-center gap-x-2" @click="handleUploadClick">
            <el-icon><Plus /></el-icon> 上传资料
          </button>
        </div>

        <div class="mt-4 flex items-center justify-between">
          <div class="flex items-center gap-x-3 text-sm">
            <span class="text-[var(--c-navy)]/50">热门尝试:</span>
            <span class="px-3 py-1 rounded-full bg-[var(--c-navy)]/5 text-[var(--c-navy)]/70 hover:bg-[var(--c-gold)] hover:text-white cursor-pointer transition-colors" @click="searchQuery = '经济学'">经济学</span>
            <span class="px-3 py-1 rounded-full bg-[var(--c-navy)]/5 text-[var(--c-navy)]/70 hover:bg-[var(--c-gold)] hover:text-white cursor-pointer transition-colors" @click="searchQuery = '期末真题'">期末真题</span>
          </div>
          <div class="text-[var(--c-navy)]/50 text-sm font-medium">
            当前共 {{ filteredMaterials.length }} 份资料命中
          </div>
        </div>
      </div>

      <div class="flex-1 min-h-0 flex gap-x-6">
        <div class="w-64 shrink-0 bg-white rounded-[var(--radius-card)] shadow-sm border border-[var(--c-navy)]/5 overflow-y-auto custom-scrollbar flex flex-col p-3">
          <div class="px-4 py-3 text-xs font-bold text-[var(--c-navy)]/40 tracking-widest uppercase mb-1">所有科目</div>
          <div class="space-y-1">
            <div
              v-for="subject in dynamicSubjects"
              :key="subject"
              class="px-4 py-3 rounded-[12px] cursor-pointer font-medium transition-all group flex items-center justify-between"
              :class="activeSubject === subject ? 'bg-[var(--c-indigo)] text-white shadow-md' : 'text-[var(--c-navy)] hover:bg-[var(--c-fog)]'"
              @click="handleSubjectSelect(subject)"
            >
              <span>{{ subject }}</span>
              <el-icon v-if="activeSubject === subject" class="text-[var(--c-gold)]"><CollectionTag /></el-icon>
            </div>
          </div>
        </div>

        <div class="flex-1 bg-white rounded-[var(--radius-card)] shadow-sm border border-[var(--c-navy)]/5 overflow-y-auto custom-scrollbar flex flex-col relative">
          <div v-if="filteredMaterials.length === 0" class="flex-1 flex flex-col items-center justify-center text-[var(--c-navy)]/40">
            <div class="w-24 h-24 mb-4 rounded-full bg-[var(--c-navy)]/5 flex items-center justify-center">
              <el-icon :size="40" class="opacity-50"><Document /></el-icon>
            </div>
            <p class="text-xl font-medium mb-2">未找到匹配资料</p>
            <p class="mb-6 opacity-80">你可以尝试更换关键词，或切换课程/学校筛选</p>
            <button class="px-6 py-2 border border-[var(--c-navy)]/20 rounded-[12px] hover:border-[var(--c-gold)] hover:text-[var(--c-gold)] transition-colors" @click="clearFilters">
              清空筛选
            </button>
          </div>

          <div v-else class="p-4 space-y-3">
            <div
              v-for="mat in filteredMaterials"
              :id="`material-${mat.id}`"
              :key="mat.id"
              class="group flex items-center justify-between p-4 rounded-2xl hover:bg-[var(--c-fog)] transition-colors border border-transparent hover:border-[var(--c-navy)]/5 cursor-pointer"
            >
              <div class="flex items-start gap-x-4 overflow-hidden pr-4 max-w-[80%]">
                <div class="w-12 h-12 bg-white rounded-[12px] flex items-center justify-center text-[#E85D04] shrink-0 border border-[var(--c-navy)]/5 shadow-sm">
                  <el-icon :size="24"><Document /></el-icon>
                </div>
                <div class="min-w-0">
                  <h4 class="font-medium text-lg text-[var(--c-navy)] mb-1 truncate group-hover:text-[var(--c-indigo)] transition-colors" :title="mat.title" v-html="renderHighlight(mat.title || '')"></h4>
                  <div class="flex items-center gap-x-4 text-sm text-[var(--c-navy)]/50">
                    <span class="flex items-center gap-x-1 font-medium">
                      <span class="w-1.5 h-1.5 rounded-full bg-[var(--c-gold)] opacity-80 inline-block"></span>
                      {{ mat.space_name || spaces.find((s: any) => s.id === mat.space_id)?.name || '未知空间' }}
                    </span>
                    <span>
                      {{ mat.resource_type === 'past_exam' ? '往年试卷' : mat.resource_type === 'notes' ? '课堂笔记' : mat.resource_type === 'solution' ? '习题答案' : '其他资料' }}
                    </span>
                    <span>最后更新：{{ new Date(mat.created_at).toLocaleDateString() }}</span>
                  </div>
                </div>
              </div>

              <div class="flex items-center gap-x-4 pl-4 border-l border-[var(--c-navy)]/5 shrink-0">
                <div class="text-[var(--c-navy)]/40 text-sm hidden lg:block text-right">
                  <div class="flex items-center gap-1"><el-icon><Star /></el-icon> {{ mat.bookmark_count || 0 }} 次收藏</div>
                  <div class="flex items-center gap-1"><el-icon><Download /></el-icon> {{ mat.download_count || 0 }} 次下载</div>
                </div>
                <button
                  class="w-10 h-10 rounded-[12px] flex items-center justify-center bg-white border transition-all shadow-sm"
                  :class="mat.is_bookmarked ? 'text-orange-500 border-orange-200 hover:bg-orange-50' : 'text-[var(--c-indigo)] border-[var(--c-navy)]/10 hover:border-orange-300 hover:text-orange-500'"
                  @click.stop="toggleBookmark(mat)"
                >
                  <el-icon :size="20"><StarFilled v-if="mat.is_bookmarked" /><Star v-else /></el-icon>
                </button>
                <button
                  class="w-10 h-10 rounded-[12px] flex items-center justify-center bg-white text-[var(--c-indigo)] border border-[var(--c-navy)]/10 hover:border-[var(--c-indigo)] group-hover:bg-[var(--c-indigo)] group-hover:text-white transition-all shadow-sm"
                  @click.stop="downloadFile(mat)"
                >
                  <el-icon :size="20"><Download /></el-icon>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <el-dialog v-model="showUploadModal" title="上传资料分享给同学们" width="500px" style="border-radius: var(--radius-card)">
      <div class="space-y-4 pt-2 pb-2">
        <div>
          <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">标题 <span class="text-red-500">*</span></label>
          <input v-model="uploadForm.title" placeholder="资料主要内容说明" class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-1 focus:ring-[var(--c-gold)] outline-none" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">所属学校 <span class="text-[var(--c-navy)]/40 text-xs font-normal ml-1">可选</span></label>
            <el-select v-model="uploadForm.school_space_id" placeholder="选择学校" class="w-full" clearable>
              <el-option v-for="space in schoolSpaces" :key="space.id" :label="space.name" :value="space.id" />
            </el-select>
          </div>
          <div>
            <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">所属课程 <span class="text-red-500">*</span></label>
            <el-select v-model="uploadForm.space_id" placeholder="选择课程" class="w-full">
              <el-option v-for="space in courseSpaces" :key="space.id" :label="space.name" :value="space.id" />
            </el-select>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">资料类别</label>
          <el-select v-model="uploadForm.resource_type" placeholder="类别" class="w-full">
            <el-option label="往年试卷" value="past_exam" />
            <el-option label="课堂笔记" value="notes" />
            <el-option label="习题与答案" value="solution" />
            <el-option label="其他" value="other" />
          </el-select>
        </div>

        <div>
          <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">选择文件 <span class="text-red-500">*</span></label>
          <input type="file" class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-[var(--c-indigo)] file:text-white hover:file:opacity-90" @change="handleFileChange" />
        </div>

        <div>
          <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">补充描述</label>
          <textarea v-model="uploadForm.description" placeholder="关于该资料的说明..." rows="2" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-1 focus:ring-[var(--c-gold)] outline-none resize-none"></textarea>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-x-3">
          <button class="px-5 py-1.5 rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-50" :disabled="isUploading" @click="showUploadModal = false">取消</button>
          <button class="px-5 py-1.5 rounded-lg bg-[var(--c-indigo)] text-white hover:bg-opacity-90 flex items-center justify-center disabled:opacity-50" :disabled="isUploading" @click="submitUpload">
            <span v-if="isUploading" class="mr-2 inline-block w-4 h-4 border-2 border-[var(--c-fog)] border-t-transparent rounded-full animate-spin"></span>
            {{ isUploading ? '上传中...' : '开始上传' }}
          </button>
        </div>
      </template>
    </el-dialog>
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
  background-color: rgba(15, 27, 45, 0.1);
  border-radius: 4px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: rgba(15, 27, 45, 0.2);
}

:deep(.search-highlight) {
  background: rgba(245, 191, 66, 0.35);
  color: inherit;
  border-radius: 4px;
  padding: 0 2px;
}
</style>
