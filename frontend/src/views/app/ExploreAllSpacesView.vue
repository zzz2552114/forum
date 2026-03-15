<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import request from '@/utils/request'
import { useRouter } from 'vue-router'
import { Search, Back } from '@element-plus/icons-vue'
import HomeHeader from '@/components/HomeHeader.vue'

const router = useRouter()

const categories = ref<any[]>([])
const spaces = ref<any[]>([])
const searchQuery = ref('')
const activeNames = ref<string[]>([])

const allowedCategories = ['学校', '课程', '休闲娱乐', '专业', '探索']

const fetchCategories = async () => {
  try {
    const res: any = await request.get('/categories/')
    categories.value = (res || []).filter((c: any) => allowedCategories.includes(c.name))
  } catch (e) {
    console.error('Failed to fetch categories', e)
  }
}

const fetchSpaces = async () => {
  try {
    const res: any = await request.get('/spaces/')
    spaces.value = res || []
  } catch (e: any) {
    console.error('Failed to fetch spaces', e)
  }
}

onMounted(async () => {
  await fetchCategories()
  await fetchSpaces()
  // Default expand '学校'
  const schoolCat = categories.value.find(c => c.name === '学校')
  if (schoolCat) {
    activeNames.value = [schoolCat.id.toString()]
  }
})

// Filter spaces based on search query
const filteredSpaces = computed(() => {
  if (!searchQuery.value) return spaces.value
  const q = searchQuery.value.toLowerCase()
  return spaces.value.filter(s => s.name.toLowerCase().includes(q))
})

const getSpacesByCategory = (categoryId: number) => {
  return filteredSpaces.value.filter(s => s.category_id === categoryId)
}

const goToSpace = (spaceId: number) => {
  router.push({ path: '/spaces', query: { spaceId } })
}
</script>

<template>
  <div class="min-h-screen bg-[var(--c-fog)] flex flex-col">
    <HomeHeader />

    <main class="flex-1 w-full max-w-[800px] mx-auto px-6 py-10 pb-20 flex flex-col">
      <!-- Top Search Area -->
      <div class="flex items-center gap-x-4 mb-8">
        <button @click="router.back()" class="w-12 h-12 flex items-center justify-center rounded-full bg-white shadow-sm hover:bg-gray-50 transition-colors text-gray-500">
          <el-icon :size="20"><Back /></el-icon>
        </button>
        <div class="relative flex-1">
          <el-icon class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 z-10" :size="20"><Search /></el-icon>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索空间名称..."
            class="w-full h-12 bg-white rounded-full pl-12 pr-4 text-[var(--c-navy)] focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)] shadow-sm transition-all"
          />
        </div>
      </div>

      <div class="bg-white rounded-2xl shadow-sm p-6">
        <h2 class="text-2xl font-bold text-[var(--c-navy)] mb-6 text-center">探索全站空间</h2>

        <el-collapse v-model="activeNames" class="custom-collapse">
          <el-collapse-item v-for="cat in categories" :key="cat.id" :name="cat.id.toString()">
            <template #title>
              <div class="text-lg font-bold text-[var(--c-navy)] tracking-wide">{{ cat.name }} 模块</div>
            </template>
            
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-4">
              <template v-for="space in getSpacesByCategory(cat.id)" :key="space.id">
                <div 
                  @click="goToSpace(space.id)"
                  class="bg-[var(--c-fog)] rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer hover:bg-[var(--c-indigo)] hover:text-white transition-all group shadow-sm border border-transparent hover:border-black/5"
                >
                  <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center text-xl font-bold text-[var(--c-indigo)] mb-3 group-hover:scale-110 transition-transform shadow-sm">
                    {{ space.name.charAt(0) }}
                  </div>
                  <span class="font-medium text-center line-clamp-1">{{ space.name }}</span>
                </div>
              </template>
              
              <div v-if="getSpacesByCategory(cat.id).length === 0" class="col-span-full text-center text-gray-400 py-4 text-sm">
                该模块下暂无空间
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </main>
  </div>
</template>

<style scoped>
.custom-collapse {
  border-top: none;
  border-bottom: none;
}
:deep(.el-collapse-item__header) {
  background-color: transparent;
  border-bottom: 1px solid rgba(15, 27, 45, 0.05);
  font-size: 1.125rem;
}
:deep(.el-collapse-item__wrap) {
  border-bottom: none;
  background-color: transparent;
}
:deep(.el-collapse-item__content) {
  padding-bottom: 24px;
}
</style>
