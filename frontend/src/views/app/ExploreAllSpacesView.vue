<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Search } from '@element-plus/icons-vue'

import HomeHeader from '@/components/HomeHeader.vue'
import request from '@/utils/request'
import { highlightKeywordHtml } from '@/utils/search'

type Category = {
  id: number
  name: string
}

type SpaceItem = {
  id: number
  name: string
  description?: string | null
  category_id: number
}

const router = useRouter()
const route = useRoute()

const categories = ref<Category[]>([])
const allSpaces = ref<SpaceItem[]>([])
const searchResultIds = ref<number[]>([])
const selectedCategoryId = ref<number | null>(null)
const searchQuery = ref('')
const activeNames = ref<string[]>([])
const lastAppliedQueryKey = ref('')
const lastSearchedQueryKey = ref('')

const allowedCategories = ['学校', '课程', '休闲娱乐', '专业', '探索']

const hasKeyword = computed(() => searchQuery.value.trim().length > 0)

const parseRouteKeyword = (): string => {
  const raw = route.query.keyword
  if (Array.isArray(raw)) return String(raw[0] || '').trim()
  if (typeof raw === 'string') return raw.trim()
  return ''
}

const parseRouteCategoryId = (): number | null => {
  const raw = Array.isArray(route.query.categoryId) ? route.query.categoryId[0] : route.query.categoryId
  const categoryId = Number(raw)
  if (Number.isNaN(categoryId) || categoryId <= 0) return null
  return categoryId
}

const fetchCategories = async () => {
  try {
    const res: any = await request.get('/categories/')
    categories.value = (Array.isArray(res) ? res : []).filter((item: any) =>
      allowedCategories.includes(String(item.name || '')),
    )
  } catch (error) {
    console.error('Failed to fetch categories', error)
    categories.value = []
  }
}

const fetchSpaces = async () => {
  try {
    const res: any = await request.get('/spaces/')
    allSpaces.value = Array.isArray(res) ? res : []
  } catch (error) {
    console.error('Failed to fetch spaces', error)
    allSpaces.value = []
  }
}

const performSpaceSearch = async (options: { silent?: boolean; force?: boolean } = {}) => {
  const keyword = searchQuery.value.trim()
  const categoryId = selectedCategoryId.value

  if (!categoryId) {
    searchResultIds.value = []
    if (!options.silent) ElMessage.warning('请先选择模块后再搜索')
    return
  }
  if (!keyword) {
    searchResultIds.value = []
    if (!options.silent) ElMessage.warning('请输入关键词后再搜索')
    return
  }

  const queryKey = `${categoryId}|${keyword}`
  if (!options.force && lastSearchedQueryKey.value === queryKey) return
  lastSearchedQueryKey.value = queryKey

  try {
    const res: any = await request.get('/search/spaces', {
      params: {
        category_id: categoryId,
        keyword,
        page: 1,
        page_size: 100,
      },
    })
    const items = Array.isArray(res.items) ? res.items : []
    searchResultIds.value = items.map((item: any) => Number(item.id)).filter((id) => Number.isFinite(id))
    activeNames.value = [String(categoryId)]
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || error.message || '空间搜索失败')
  }
}

const syncFromRouteAndSearch = async () => {
  const queryKeyword = parseRouteKeyword()
  const queryCategoryId = parseRouteCategoryId()
  const queryKey = `${queryCategoryId ?? ''}|${queryKeyword}`
  if (lastAppliedQueryKey.value === queryKey) return
  lastAppliedQueryKey.value = queryKey

  selectedCategoryId.value = queryCategoryId
  searchQuery.value = queryKeyword
  activeNames.value = queryCategoryId ? [String(queryCategoryId)] : []

  await performSpaceSearch({ silent: true })
}

const handleSearchSubmit = async () => {
  const keyword = searchQuery.value.trim()
  if (!selectedCategoryId.value) {
    ElMessage.warning('请先选择模块后再搜索')
    return
  }
  if (!keyword) {
    ElMessage.warning('请输入关键词后再搜索')
    return
  }

  const routeKeyword = parseRouteKeyword()
  const routeCategoryId = parseRouteCategoryId()
  if (routeKeyword === keyword && routeCategoryId === selectedCategoryId.value) {
    await performSpaceSearch({ silent: true, force: true })
    return
  }

  await router.replace({
    path: '/explore-spaces',
    query: {
      keyword,
      categoryId: String(selectedCategoryId.value),
    },
  })
}

const getSpacesByCategory = (categoryId: number): SpaceItem[] => {
  const base = allSpaces.value.filter((space) => space.category_id === categoryId)

  if (selectedCategoryId.value && categoryId !== selectedCategoryId.value && hasKeyword.value) {
    return []
  }

  if (categoryId !== selectedCategoryId.value) {
    return base.sort((a, b) => String(a.name || '').localeCompare(String(b.name || '')))
  }

  if (!hasKeyword.value) {
    return base.sort((a, b) => String(a.name || '').localeCompare(String(b.name || '')))
  }

  if (!searchResultIds.value.length) return []

  const rank = new Map<number, number>()
  searchResultIds.value.forEach((id, index) => rank.set(id, index))

  return base
    .filter((space) => rank.has(space.id))
    .sort(
      (a, b) =>
        (rank.get(a.id) ?? Number.MAX_SAFE_INTEGER) - (rank.get(b.id) ?? Number.MAX_SAFE_INTEGER),
    )
}

const renderHighlight = (value: string) => highlightKeywordHtml(value, searchQuery.value)

onMounted(async () => {
  await fetchCategories()
  await fetchSpaces()
})

watch(
  () => route.query,
  () => {
    void syncFromRouteAndSearch()
  },
  { immediate: true, deep: true },
)
</script>

<template>
  <div class="min-h-screen bg-[var(--c-fog)] flex flex-col">
    <HomeHeader />

    <main class="flex-1 w-full max-w-[920px] mx-auto px-6 py-10 pb-20 flex flex-col">
      <div class="flex items-center gap-x-4 mb-8 min-w-0">
        <button
          @click="router.back()"
          class="w-12 h-12 flex items-center justify-center rounded-full bg-white shadow-sm hover:bg-gray-50 transition-colors text-gray-500 shrink-0"
        >
          <el-icon :size="20"><Back /></el-icon>
        </button>

        <el-select
          v-model="selectedCategoryId"
          class="explore-space-category-select shrink-0"
          style="width: 180px; min-width: 180px; max-width: 180px; flex: 0 0 180px"
          size="large"
          placeholder="选择模块"
          clearable
        >
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>

        <div
          class="flex flex-1 min-w-[220px] h-12 items-center gap-2 rounded-full bg-white px-4 text-[var(--c-navy)] shadow-sm border border-transparent focus-within:border-[var(--c-gold)] transition-all"
        >
          <el-icon class="text-gray-400 shrink-0" :size="20"><Search /></el-icon>
          <input
            v-model="searchQuery"
            data-testid="explore-spaces-keyword-input"
            type="text"
            placeholder="请输入空间关键词..."
            class="w-full bg-transparent text-[var(--c-navy)] focus:outline-none"
            @keyup.enter="handleSearchSubmit"
          />
        </div>

        <button
          class="h-12 w-24 rounded-full bg-[var(--c-indigo)] text-white font-medium hover:bg-opacity-90 transition-all shrink-0"
          @click="handleSearchSubmit"
        >
          搜索
        </button>
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
                  class="bg-[var(--c-fog)] rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer hover:bg-[var(--c-indigo)] hover:text-white transition-all group shadow-sm border border-transparent hover:border-black/5"
                  @click="router.push({ path: '/spaces', query: { spaceId: String(space.id) } })"
                >
                  <div
                    class="w-12 h-12 bg-white rounded-full flex items-center justify-center text-xl font-bold text-[var(--c-indigo)] mb-3 group-hover:scale-110 transition-transform shadow-sm"
                  >
                    {{ String(space.name || '').charAt(0) }}
                  </div>
                  <span class="font-medium text-center line-clamp-1" v-html="renderHighlight(space.name || '')"></span>
                  <p
                    v-if="space.description"
                    class="text-xs opacity-70 text-center line-clamp-1 mt-1"
                    v-html="renderHighlight(space.description || '')"
                  ></p>
                </div>
              </template>

              <div
                v-if="getSpacesByCategory(cat.id).length === 0"
                class="col-span-full text-center text-gray-400 py-4 text-sm"
              >
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

:deep(.search-highlight) {
  background: rgba(245, 191, 66, 0.35);
  color: inherit;
  border-radius: 4px;
  padding: 0 2px;
}

:deep(.explore-space-category-select.el-select) {
  width: 180px !important;
  min-width: 180px;
  max-width: 180px;
  flex: 0 0 180px;
}
</style>
