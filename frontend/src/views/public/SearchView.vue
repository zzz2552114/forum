<template>
  <div class="max-w-5xl mx-auto py-6">
    <div class="mb-8 text-center max-w-2xl mx-auto">
      <h1 class="text-3xl font-bold text-slate-800 mb-6">全站搜索</h1>
      <el-input
        v-model="keyword"
        size="large"
        placeholder="搜索帖子、空间或标签..."
        clearable
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button :icon="Search" @click="handleSearch" class="bg-blue-600 text-white hover:bg-blue-700">搜索</el-button>
        </template>
      </el-input>
      
      <!-- Search Suggestions Box (dummy for layout) -->
      <div v-if="suggestions.length > 0" class="mt-2 p-2 bg-white rounded-lg shadow border text-left flex gap-2 overflow-x-auto">
        <el-tag v-for="word in suggestions" :key="word" @click="keyword = word; handleSearch()" class="cursor-pointer" effect="light">
          {{ word }}
        </el-tag>
      </div>
    </div>

    <!-- Results -->
    <div v-loading="loading">
      <el-tabs v-model="activeTab" @tab-change="handleSearch">
        <el-tab-pane label="帖子" name="posts">
          <div class="space-y-4 pt-4">
            <PostCard v-for="post in results" :key="post.id" :post="post" />
            <el-empty v-if="!loading && results.length === 0" description="未找到相关帖子" />
          </div>
        </el-tab-pane>
        <el-tab-pane label="空间" name="spaces">
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 pt-4">
             <el-card v-for="space in results" :key="space.id" shadow="hover" class="rounded-xl cursor-pointer" @click="$router.push(`/spaces/${space.id}`)">
              <h3 class="font-bold text-slate-800">{{ space.name }}</h3>
              <p class="text-slate-500 text-sm mt-2 line-clamp-2">{{ space.description }}</p>
             </el-card>
             <el-empty v-if="!loading && results.length === 0" description="未找到相关空间" class="col-span-full" />
          </div>
        </el-tab-pane>
      </el-tabs>
      
      <div class="mt-6 flex justify-center" v-if="total > 0">
        <el-pagination v-model:current-page="page" :page-size="pageSize" layout="prev, pager, next" :total="total" @current-change="fetchResults" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import request from '@/utils/request'
import PostCard from '@/components/post/PostCard.vue'

const route = useRoute()
const router = useRouter()

const keyword = ref(route.query.keyword as string || '')
const activeTab = ref((route.query.type as string) || 'posts')
const loading = ref(false)
const results = ref<any[]>([])
const suggestions = ref<string[]>([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const fetchSuggestions = async () => {
  if (!keyword.value) {
    suggestions.value = []
    return
  }
  try {
    const res: any = await request.get('/search/suggestions', { params: { query: keyword.value } })
    suggestions.value = res
  } catch (e) {
    // Ignore suggestion errors
  }
}

const fetchResults = async () => {
  if (!keyword.value) return
  loading.value = true
  try {
    const res: any = await request.get(`/search/${activeTab.value}`, {
      params: { q: keyword.value, page: page.value, page_size: pageSize.value }
    })
    results.value = res.items
    total.value = res.pagination.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  router.replace({ path: '/search', query: { keyword: keyword.value, type: activeTab.value } })
  page.value = 1
  fetchResults()
  fetchSuggestions()
}

watch(() => route.query.keyword, (newVal) => {
  if (newVal !== keyword.value) {
    keyword.value = newVal as string
    handleSearch()
  }
})

onMounted(() => {
  if (keyword.value) {
    handleSearch()
  }
})
</script>
