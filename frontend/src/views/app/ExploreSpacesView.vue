<script setup lang="ts">
import { ref, computed, onMounted, markRaw } from 'vue'
import { Search, Plus, Location, Present, Star, Monitor, Trophy, Document, Upload } from '@element-plus/icons-vue'
import HomeHeader from '@/components/HomeHeader.vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

// State
const activeSectionId = ref(1)

const sections = ref([
  { id: 1, name: '学校政策', icon: markRaw(Location), unread: 0 },
  { id: 2, name: '大学生优惠合集', icon: markRaw(Present), unread: 0 },
  { id: 3, name: '保研经验分享', icon: markRaw(Star), unread: 0 },
  { id: 4, name: '论坛精华帖', icon: markRaw(Trophy), unread: 0 },
  { id: 5, name: '每日热度榜', icon: markRaw(Monitor), unread: 0 },
])

const activeSection = computed(() => {
  return sections.value.find((s: any) => s.id === activeSectionId.value)
})

const searchQuery = ref('')
const materials = ref<any[]>([])
const spaces = ref<any[]>([])
const categories = ref<any[]>([])

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

const schoolCategory = computed(() => categories.value.find((c: any) => c.name === '学校' || c.slug === 'school'))
const schoolSpaces = computed(() => {
  if (!schoolCategory.value) return []
  return spaces.value.filter((s: any) => s.category_id === schoolCategory.value.id)
})

const fetchMaterials = async () => {
  try {
    const params: any = {
      page: 1,
      page_size: 50,
      resource_type: 'policy' // assuming policy maps to this section for mockup
    }
    
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
  if (activeSectionId.value === 1) {
    fetchMaterials()
  }
})

const handleSearch = () => {
  if (activeSectionId.value === 1) {
    fetchMaterials()
  }
}

// Upload Modal State
const showUploadModal = ref(false)
const uploadForm = ref({
  title: '',
  description: '',
  school_space_id: null as number | null,
  resource_type: 'policy',
  version_note: 'Initial Upload'
})
const selectedFile = ref<File | null>(null)
const isUploading = ref(false)

const handleUploadClick = () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录再分享资料')
    router.push('/?showLogin=true')
    return
  }
  showUploadModal.value = true
}

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0] ?? null
  }
}

const submitUpload = async () => {
  if (!selectedFile.value) return ElMessage.warning('请选择要上传的文件')
  if (!uploadForm.value.title || !uploadForm.value.school_space_id) return ElMessage.warning('请完成必填项')

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
    
    // Create using the school space as the primary space id to satisfy backend constraints if needed, or pass specifically.
    // In resources.py, space_id is required. We will pass school_space_id as space_id if there is no other space.
    await request.post('/resources/', {
      title: uploadForm.value.title,
      description: uploadForm.value.description,
      school_space_id: uploadForm.value.school_space_id,
      space_id: uploadForm.value.school_space_id, // Defaulting space_id to school_space_id for policies
      resource_type: uploadForm.value.resource_type,
      file_id: resFile.id,
      version_note: uploadForm.value.version_note
    })
    
    ElMessage.success('上传成功')
    showUploadModal.value = false
    selectedFile.value = null
    uploadForm.value = { title: '', description: '', school_space_id: null, resource_type: 'policy', version_note: 'Initial Upload' }
    fetchMaterials()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || e.response?.data?.detail || e.message || '上传失败')
  } finally {
    isUploading.value = false
  }
}

const downloadFile = (url: string) => {
  if (!url || url === '#') return;
  const a = document.createElement('a');
  a.href = url;
  a.download = '';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
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
              placeholder="搜索发现新鲜事、政策、经验..."
              class="w-full h-14 bg-[var(--c-fog)] rounded-[16px] pl-12 pr-4 text-[var(--c-navy)] text-lg focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)] focus:bg-white transition-all border border-transparent shadow-inner"
            />
          </div>
          <button
            @click="handleSearch"
            class="h-14 px-8 bg-[var(--c-indigo)] text-white rounded-[16px] font-medium text-lg hover:bg-opacity-90 shadow-lg shadow-[var(--c-indigo)]/20 transition-all shrink-0"
          >
            探索
          </button>
        </div>
      </div>

      <!-- Content Area (12 columns equivalent: 3 for sidebar, 9 for content) -->
      <div class="flex-1 min-h-0 flex gap-x-6">
        <!-- Left: Categories Sidebar -->
        <div
          class="w-[280px] shrink-0 bg-white rounded-[var(--radius-card)] shadow-sm border border-[var(--c-navy)]/5 overflow-y-auto custom-scrollbar flex flex-col p-3"
        >
          <div
            class="px-4 py-3 text-xs font-bold text-[var(--c-navy)]/40 tracking-widest uppercase mb-1"
          >
            探索发现
          </div>
          <div class="space-y-1">
            <div
              v-for="section in sections"
              :key="section.id"
              class="px-4 py-3 rounded-[12px] cursor-pointer font-medium transition-all group flex items-center gap-x-3"
              :class="
                activeSectionId === section.id
                  ? 'bg-[var(--c-indigo)] text-white shadow-md'
                  : 'text-[var(--c-navy)] hover:bg-[var(--c-fog)]'
              "
              @click="activeSectionId = section.id"
            >
              <el-icon :size="18" :class="activeSectionId === section.id ? 'text-[var(--c-gold)]' : 'opacity-70'">
                  <component :is="section.icon" />
              </el-icon>
              <span>{{ section.name }}</span>
            </div>
          </div>
        </div>

        <!-- Right: Materials List -->
        <div
          class="flex-1 bg-white rounded-[var(--radius-card)] shadow-sm border border-[var(--c-navy)]/5 overflow-y-auto custom-scrollbar flex flex-col relative"
        >
          <div class="h-16 flex items-center justify-between px-6 border-b border-[var(--c-navy)]/5 shrink-0 sticky top-0 bg-white z-10">
              <h3 class="text-lg font-bold text-[var(--c-navy)]">{{ activeSection?.name }}</h3>
              <button
                v-if="activeSectionId === 1"
                @click="handleUploadClick"
                class="px-5 py-1.5 bg-[var(--c-gold)] text-white rounded-full font-medium text-sm hover:bg-opacity-90 shadow-sm shadow-[var(--c-gold)]/20 transition-all flex items-center gap-x-1"
              >
                <el-icon><Plus /></el-icon> 上传政策
              </button>
          </div>

          <div
            v-if="activeSectionId !== 1 || materials.length === 0"
            class="flex-1 flex flex-col items-center justify-center text-[var(--c-navy)]/40"
          >
            <div
              class="w-24 h-24 mb-4 rounded-full bg-[var(--c-navy)]/5 flex items-center justify-center"
            >
              <el-icon :size="40" class="opacity-50"><component :is="activeSection?.icon" /></el-icon>
            </div>
            <p v-if="activeSectionId !== 1" class="text-xl font-medium mb-2">内容区开发中</p>
            <p v-else class="text-xl font-medium mb-2">暂无政策文件</p>
            <p class="mb-6 opacity-80">在这里发现无限可能</p>
          </div>

          <div v-else class="p-4 space-y-3">
            <div
              v-for="mat in materials"
              :key="mat.id"
              class="group flex items-center justify-between p-4 rounded-2xl hover:bg-[var(--c-fog)] transition-colors border border-transparent hover:border-[var(--c-navy)]/5 cursor-pointer"
            >
              <div
                class="flex items-start gap-x-4 overflow-hidden pr-4 max-w-[80%]"
              >
                <div
                  class="w-12 h-12 bg-white rounded-[12px] flex items-center justify-center text-[var(--c-navy)] shrink-0 border border-[var(--c-navy)]/5 shadow-sm"
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
                      {{ mat.space_name || spaces.find(s => s.id === mat.space_id)?.name || '未知学校' }}</span
                    >
                    <span>最后更新：{{ new Date(mat.created_at).toLocaleDateString() }}</span>
                  </div>
                </div>
              </div>

              <div
                class="flex items-center gap-x-4 pl-4 border-l border-[var(--c-navy)]/5 shrink-0"
              >
                <!-- Download Button -->
                <button
                  @click.stop="downloadFile(mat.versions?.[0]?.file_url)"
                  class="w-10 h-10 rounded-[12px] flex items-center justify-center bg-white text-[var(--c-indigo)] border border-[var(--c-navy)]/10 hover:border-[var(--c-indigo)] group-hover:bg-[var(--c-indigo)] group-hover:text-white transition-all shadow-sm"
                >
                  <el-icon :size="20" style="transform: rotate(180deg)"><Upload /></el-icon>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Upload Modal -->
    <el-dialog v-model="showUploadModal" title="上传政策文件" width="500px" style="border-radius: var(--radius-card)">
      <div class="space-y-4 pt-2 pb-2">
        <div>
          <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">政策标题 <span class="text-red-500">*</span></label>
          <input v-model="uploadForm.title" placeholder="如：XX大学2026年保研细则" class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:ring-1 focus:ring-[var(--c-gold)] outline-none" />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">所属学校 <span class="text-red-500">*</span></label>
          <el-select v-model="uploadForm.school_space_id" placeholder="必须选择学校" class="w-full">
            <el-option v-for="s in schoolSpaces" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </div>

        <div>
           <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">选择文件 <span class="text-red-500">*</span></label>
           <input type="file" @change="handleFileChange" class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-[var(--c-indigo)] file:text-white hover:file:opacity-90"/>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-[var(--c-navy)] mb-1">补充描述</label>
          <textarea v-model="uploadForm.description" placeholder="关于该政策的说明..." rows="2" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-1 focus:ring-[var(--c-gold)] outline-none resize-none"></textarea>
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
