<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Plus, Document, Download, CollectionTag, Search } from '@element-plus/icons-vue'
import HomeHeader from '@/components/HomeHeader.vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const searchQuery = ref('')
const activeSubject = ref('全部')

// Fetch categories from backend to act as "Subjects/Modules"
const categories = ref<any[]>([])
const spaces = ref<any[]>([]) 
const materials = ref<any[]>([])

const fetchCategories = async () => {
  try {
    const res: any = await request.get('/categories/')
    categories.value = res || []
  } catch (e) {
    console.error('Failed to fetch categories', e)
  }
}

const fetchSpaces = async () => {
  try {
    const res: any = await request.get('/spaces/')
    spaces.value = res || []
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || e.message || '获取空间列表失败')
  }
}

const handleUploadClick = () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录再分享资料')
    router.push('/?showLogin=true')
    return
  }
  showUploadModal.value = true
}

const fetchMaterials = async () => {
  try {
    const params: any = {
      page: 1,
      page_size: 50
    }
    
    // Attempt standard /resources/ or if searching use /search/resources
    let endpoint = '/resources/'
    if (searchQuery.value) {
      endpoint = '/search/resources'
      params.keyword = searchQuery.value
    }

    const res: any = await request.get(endpoint, { params })
    materials.value = res.items || []
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || e.message || '获取资料列表失败')
  }
}

onMounted(async () => {
  await fetchCategories()
  await fetchSpaces()
  fetchMaterials()
})

// Upload Modal State
const showUploadModal = ref(false)
const uploadForm = ref({
  title: '',
  description: '',
  space_id: null as number | null,
  resource_type: 'notes',
  version_note: 'Initial Upload'
})
const selectedFile = ref<File | null>(null)
const isUploading = ref(false)

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0] ?? null
  }
}

const submitUpload = async () => {
  if (!selectedFile.value) return ElMessage.warning('请选择要上传的文件')
  if (!uploadForm.value.title || !uploadForm.value.space_id) return ElMessage.warning('请完成必填项')

  isUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('biz_type', 'resource')

    const resFile: any = await request.post('/files/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    await request.post('/resources/', {
      title: uploadForm.value.title,
      description: uploadForm.value.description,
      space_id: uploadForm.value.space_id,
      resource_type: uploadForm.value.resource_type,
      file_id: resFile.id,
      version_note: uploadForm.value.version_note
    })
    
    ElMessage.success('上传成功')
    showUploadModal.value = false
    selectedFile.value = null
    uploadForm.value = { title: '', description: '', space_id: null, resource_type: 'notes', version_note: 'Initial Upload' }
    fetchMaterials()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || e.response?.data?.detail || e.message || '上传失败')
  } finally {
    isUploading.value = false
  }
}

const handleSearch = () => {
  fetchMaterials()
}

watch(activeSubject, () => {
  // If activeSubject is a category name and not '全部', we could filter spaces,
  // but for simplicity frontend computation works since /resources returns raw objects.
})

// Derive subjects list dynamically from course spaces
const courseCategory = computed(() => categories.value.find((c: any) => c.name === '课程' || c.slug === 'course'))
const courseSpaces = computed(() => {
  if (!courseCategory.value) return []
  return spaces.value.filter((s: any) => s.category_id === courseCategory.value.id)
})
  
const dynamicSubjects = computed(() => ['全部', ...courseSpaces.value.map(s => s.name)])

const filteredMaterials = computed(() => {
  // Final client side filtering by specific Space
  let result = materials.value

  if (activeSubject.value !== '全部') {
    const targetSpace = spaces.value.find((s: any) => s.name === activeSubject.value)
    if (targetSpace) {
      result = result.filter((m: any) => m.space_id === targetSpace.id)
    }
  }
  
  return result.sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
})

const clearFilters = () => {
  searchQuery.value = ''
  activeSubject.value = '全部'
  fetchMaterials()
}
</script>

<template>
  <div class="min-h-screen bg-[var(--c-fog)] flex flex-col">
    <HomeHeader />

    <main
      class="flex-1 w-full max-w-[1280px] mx-auto px-[80px] py-10 pb-20 flex flex-col h-[calc(100vh-88px)]"
    >
      <!-- Top Search Area -->
      <div
        class="w-full bg-white rounded-[var(--radius-card)] p-6 shadow-sm border border-[var(--c-navy)]/5 mb-6 shrink-0 relative overflow-hidden"
      >
        <div
          class="absolute right-0 top-0 bottom-0 w-64 bg-gradient-to-l from-[var(--c-fog)] to-transparent pointer-events-none z-0"
        ></div>
        <div class="relative z-10 flex gap-x-4">
          <div class="relative flex-1">
            <el-icon
              class="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--c-navy)] opacity-40 z-10"
              :size="20"
              ><Search
            /></el-icon>
            <input
              v-model="searchQuery"
              @keyup.enter="handleSearch"
              type="text"
              placeholder="搜索资料名称、摘要或文件名..."
              class="w-full h-14 bg-[var(--c-fog)] rounded-[16px] pl-12 pr-4 text-[var(--c-navy)] text-lg focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)] focus:bg-white transition-all border border-transparent shadow-inner"
            />
          </div>
          <button
            @click="handleSearch"
            class="h-14 px-8 bg-[var(--c-indigo)] text-white rounded-[16px] font-medium text-lg hover:bg-opacity-90 shadow-lg shadow-[var(--c-indigo)]/20 transition-all shrink-0"
          >
            搜索库
          </button>
          
          <!-- Upload Button -->
          <button
            @click="handleUploadClick"
            class="h-14 px-6 bg-[var(--c-gold)] text-white rounded-[16px] font-medium text-lg hover:bg-opacity-90 shadow-lg shadow-[var(--c-gold)]/20 transition-all shrink-0 flex items-center gap-x-2"
          >
            <el-icon><Plus /></el-icon> 上传资料
          </button>
        </div>
        <div class="mt-4 flex items-center justify-between">
          <div class="flex items-center gap-x-3 text-sm">
            <span class="text-[var(--c-navy)]/50">热门尝试:</span>
            <span
              class="px-3 py-1 rounded-full bg-[var(--c-navy)]/5 text-[var(--c-navy)]/70 hover:bg-[var(--c-gold)] hover:text-white cursor-pointer transition-colors"
              @click="searchQuery = '高等数学'"
              >高等数学</span
            >
            <span
              class="px-3 py-1 rounded-full bg-[var(--c-navy)]/5 text-[var(--c-navy)]/70 hover:bg-[var(--c-gold)] hover:text-white cursor-pointer transition-colors"
              @click="searchQuery = '期末真题'"
              >期末真题</span
            >
          </div>
          <div class="text-[var(--c-navy)]/50 text-sm font-medium">
            当前共 {{ filteredMaterials.length }} 份资料命中
          </div>
        </div>
      </div>

      <!-- Content Area -->
      <div class="flex-1 min-h-0 flex gap-x-6">
        <!-- Left: Categories -->
        <div
          class="w-64 shrink-0 bg-white rounded-[var(--radius-card)] shadow-sm border border-[var(--c-navy)]/5 overflow-y-auto custom-scrollbar flex flex-col p-3"
        >
          <div
            class="px-4 py-3 text-xs font-bold text-[var(--c-navy)]/40 tracking-widest uppercase mb-1"
          >
            所有科目
          </div>
          <div class="space-y-1">
            <div
              v-for="sub in dynamicSubjects"
              :key="sub"
              class="px-4 py-3 rounded-[12px] cursor-pointer font-medium transition-all group flex items-center justify-between"
              :class="
                activeSubject === sub
                  ? 'bg-[var(--c-indigo)] text-white shadow-md'
                  : 'text-[var(--c-navy)] hover:bg-[var(--c-fog)]'
              "
              @click="activeSubject = sub"
            >
              <span>{{ sub }}</span>
              <el-icon v-if="activeSubject === sub" class="text-[var(--c-gold)]"
                ><CollectionTag
              /></el-icon>
            </div>
          </div>
        </div>

        <!-- Right: Materials List -->
        <div
          class="flex-1 bg-white rounded-[var(--radius-card)] shadow-sm border border-[var(--c-navy)]/5 overflow-y-auto custom-scrollbar flex flex-col relative"
        >
          <div
            v-if="filteredMaterials.length === 0"
            class="flex-1 flex flex-col items-center justify-center text-[var(--c-navy)]/40"
          >
            <div
              class="w-24 h-24 mb-4 rounded-full bg-[var(--c-navy)]/5 flex items-center justify-center"
            >
              <el-icon :size="40" class="opacity-50"><Document /></el-icon>
            </div>
            <p class="text-xl font-medium mb-2">未找到匹配的资料</p>
            <p class="mb-6 opacity-80">尝试更换搜索词或选择其他科目</p>
            <button
              @click="clearFilters"
              class="px-6 py-2 border border-[var(--c-navy)]/20 rounded-[12px] hover:border-[var(--c-gold)] hover:text-[var(--c-gold)] transition-colors"
            >
              清空筛选
            </button>
          </div>

          <div v-else class="p-4 space-y-3">
            <div
              v-for="mat in filteredMaterials"
              :key="mat.id"
              class="group flex items-center justify-between p-4 rounded-2xl hover:bg-[var(--c-fog)] transition-colors border border-transparent hover:border-[var(--c-navy)]/5 cursor-pointer"
            >
              <div
                class="flex items-start gap-x-4 overflow-hidden pr-4 max-w-[80%]"
              >
                <div
                  class="w-12 h-12 bg-white rounded-[12px] flex items-center justify-center text-[#E85D04] shrink-0 border border-[var(--c-navy)]/5 shadow-sm"
                >
                  <el-icon :size="24"><Document /></el-icon>
                </div>
                <div class="min-w-0">
                  <h4
                    class="font-medium text-lg text-[var(--c-navy)] mb-1 truncate group-hover:text-[var(--c-indigo)] transition-colors"
                    :title="mat.title"
                  >
                    {{ mat.title }}
                  </h4>
                  <div
                    class="flex items-center gap-x-4 text-sm text-[var(--c-navy)]/50"
                  >
                    <span class="flex items-center gap-x-1 font-medium"
                      ><span
                        class="w-1.5 h-1.5 rounded-full bg-[var(--c-gold)] opacity-80 inline-block"
                      ></span>
                      {{ mat.space_name || spaces.find(s => s.id === mat.space_id)?.name || '未知空间' }}</span
                    >
                    <span>{{ mat.resource_type === 'past_exam' ? '往年试卷' : mat.resource_type === 'notes' ? '课堂笔记' : mat.resource_type === 'solution' ? '习题答案' : '其他资料' }}</span>
                    <span>最后更新：{{ new Date(mat.created_at).toLocaleDateString() }}</span>
                  </div>
                </div>
              </div>

              <div
                class="flex items-center gap-x-4 pl-4 border-l border-[var(--c-navy)]/5 shrink-0"
              >
                <div class="text-[var(--c-navy)]/40 text-sm hidden lg:block">
                  {{ mat.download_count }} 次下载
                </div>
                <!-- Assuming backend exposes file url through versions or direct url -->
                <a
                  :href="mat.versions?.[0]?.file_url || '#'"
                  target="_blank"
                  class="w-10 h-10 rounded-[12px] flex items-center justify-center bg-white text-[var(--c-indigo)] border border-[var(--c-navy)]/10 hover:border-[var(--c-indigo)] group-hover:bg-[var(--c-indigo)] group-hover:text-white transition-all shadow-sm"
                >
                  <el-icon :size="20"><Download /></el-icon>
                </a>
              </div>
            </div>

            <!-- Load More Mock -->
            <div
              class="pt-6 pb-2 flex justify-center border-t border-[var(--c-navy)]/5 mt-4"
            >
              <button
                class="px-8 py-2.5 rounded-full border border-[var(--c-navy)]/10 text-[var(--c-navy)] font-medium hover:bg-[var(--c-fog)] hover:border-[var(--c-navy)]/20 transition-all"
              >
                加载更多
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Upload Modal -->
    <el-dialog v-model="showUploadModal" title="上传资料分享给同学们" width="500px" style="border-radius: var(--radius-card)">
      <div class="space-y-4 pt-2 pb-2">
        <div>
          <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">标题 <span class="text-red-500">*</span></label>
          <input v-model="uploadForm.title" placeholder="资料主要内容说明" class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-1 focus:ring-[var(--c-gold)] outline-none" />
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">所属空间 <span class="text-red-500">*</span></label>
            <el-select v-model="uploadForm.space_id" placeholder="选择空间" class="w-full">
              <el-option v-for="s in spaces" :key="s.id" :label="s.name" :value="s.id" />
            </el-select>
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
        </div>
        
        <!-- File Input -->
        <div>
           <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">选择文件 <span class="text-red-500">*</span></label>
           <input type="file" @change="handleFileChange" class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-[var(--c-indigo)] file:text-white hover:file:opacity-90"/>
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
</style>
