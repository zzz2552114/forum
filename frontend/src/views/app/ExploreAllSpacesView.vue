<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Search } from '@element-plus/icons-vue'

import HomeHeader from '@/components/HomeHeader.vue'
import request from '@/utils/request'

const router = useRouter()
const route = useRoute()

const categories = ref<any[]>([])
const spaces = ref<any[]>([])
const searchQuery = ref('')
const selectedCategoryId = ref<number | null>(null)
const activeNames = ref<string[]>([])
const rankedSpaceIds = ref<number[]>([])

const allowedCategories = ['学校', '课程', '休闲娱乐', '专业', '探索']
const globalSearchMode = computed(() => route.query.global === '1')

const fetchCategories = async () => {
  try {
    const res: any = await request.get('/categories/')
    categories.value = (res || []).filter((item: any) => allowedCategories.includes(item.name))
  } catch (error) {
    console.error('Failed to fetch categories', error)
    categories.value = []
  }
}

const fetchSpaces = async () => {
  try {
    const res: any = await request.get('/spaces/')
    spaces.value = res || []
  } catch (error) {
    console.error('Failed to fetch spaces', error)
    spaces.value = []
  }
}

const applyRankingFromResult = (items: any[]) => {
  rankedSpaceIds.value = items.map((item) => Number(item.id)).filter((id) => Number.isFinite(id))
}

const performSpaceSearch = async () => {
  const keyword = searchQuery.value.trim()
  if (!globalSearchMode.value && !selectedCategoryId.value) {
    ElMessage.warning('请先选择模块，再进行空间搜索')
    return
  }

  const params: Record<string, any> = {}
  if (keyword) {
    params.keyword = keyword
  }
  if (!globalSearchMode.value && selectedCategoryId.value) {
    params.category_id = selectedCategoryId.value
  }

  try {
    const res: any = await request.get('/search/spaces', { params })
    applyRankingFromResult(res.items || [])
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || error.message || '搜索空间失败')
  }
}

const getSpacesByCategory = (categoryId: number) => {
  let base = spaces.value.filter((space) => space.category_id === categoryId)

  if (!globalSearchMode.value && selectedCategoryId.value && categoryId !== selectedCategoryId.value) {
    return []
  }

  if (rankedSpaceIds.value.length > 0) {
    const indexMap = new Map<number, number>()
    rankedSpaceIds.value.forEach((id, idx) => indexMap.set(id, idx))
    base = base
      .filter((space) => indexMap.has(space.id))
      .sort((a, b) => (indexMap.get(a.id) ?? 999999) - (indexMap.get(b.id) ?? 999999))
    return base
  }

  if (!searchQuery.value.trim()) {
    return base
  }

  const q = searchQuery.value.trim().toLowerCase()
  return base
    .filter((space) => String(space.name || '').toLowerCase().includes(q))
    .sort((a, b) => String(a.name || '').localeCompare(String(b.name || '')))
}

const goToSpace = (spaceId: number) => {
  router.push({ path: '/spaces', query: { spaceId: String(spaceId) } })
}

onMounted(async () => {
  await fetchCategories()
  await fetchSpaces()

  const queryKeyword = typeof route.query.keyword === 'string' ? route.query.keyword : ''
  const queryCategoryId = Number(route.query.categoryId)

  if (queryKeyword) {
    searchQuery.value = queryKeyword
  }

  if (queryCategoryId && !Number.isNaN(queryCategoryId)) {
    selectedCategoryId.value = queryCategoryId
    activeNames.value = [String(queryCategoryId)]
  } else {
    const schoolCategory = categories.value.find((item) => item.name === '学校')
    if (schoolCategory) {
      activeNames.value = [String(schoolCategory.id)]
    }
  }

  if (searchQuery.value) {
    await performSpaceSearch()
  }
})
</script>

<template>
  <div class="min-h-screen bg-[var(--c-fog)] flex flex-col">
    <HomeHeader />

    <main class="flex-1 w-full max-w-[920px] mx-auto px-6 py-10 pb-20 flex flex-col">
      <div class="flex items-center gap-x-4 mb-8">
        <button @click="router.back()" class="w-12 h-12 flex items-center justify-center rounded-full bg-white shadow-sm hover:bg-gray-50 transition-colors text-gray-500">
          <el-icon :size="20"><Back /></el-icon>
        </button>

        <el-select
          v-model="selectedCategoryId"
          class="w-[180px]"
          size="large"
          placeholder="选择模块"
          :disabled="globalSearchMode"
          clearable
        >
          <el-option
            v-for="cat in categories"
            :key="cat.id"
            :label="cat.name"
            :value="cat.id"
          />
        </el-select>

        <div class="relative flex-1">
          <el-icon class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 z-10" :size="20"><Search /></el-icon>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索空间名称..."
            class="w-full h-12 bg-white rounded-full pl-12 pr-4 text-[var(--c-navy)] focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)] shadow-sm transition-all"
            @keyup.enter="performSpaceSearch"
          />
        </div>

        <button class="h-12 px-5 rounded-full bg-[var(--c-indigo)] text-white font-medium hover:bg-opacity-90 transition-all" @click="performSpaceSearch">
          搜索
        </button>
      </div>

      <div class="bg-white rounded-2xl shadow-sm p-6">
        <h2 class="text-2xl font-bold text-[var(--c-navy)] mb-6 text-center">探索全站空间</h2>
        <p v-if="globalSearchMode" class="text-center text-[var(--c-navy)]/50 text-sm mb-4">
          当前为全局空间搜索结果（来自首页搜索）
        </p>

        <el-collapse v-model="activeNames" class="custom-collapse">
          <el-collapse-item v-for="cat in categories" :key="cat.id" :name="cat.id.toString()">
            <template #title>
              <div class="text-lg font-bold text-[var(--c-navy)] tracking-wide">{{ cat.name }} 模块</div>
            </template>

            <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-4">
              <template v-for="space in getSpacesByCategory(cat.id)" :key="space.id">
                <div
                  class="bg-[var(--c-fog)] rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer hover:bg-[var(--c-indigo)] hover:text-white transition-all group shadow-sm border border-transparent hover:border-black/5"
                  @click="goToSpace(space.id)"
                >
                  <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center text-xl font-bold text-[var(--c-indigo)] mb-3 group-hover:scale-110 transition-transform shadow-sm">
                    {{ String(space.name || '').charAt(0) }}
                  </div>
                  <span class="font-medium text-center line-clamp-1">{{ space.name }}</span>
                </div>
              </template>

              <div v-if="getSpacesByCategory(cat.id).length === 0" class="col-span-full text-center text-gray-400 py-4 text-sm">
                该模块下暂无匹配空间
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
