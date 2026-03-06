<template>
  <div class="max-w-6xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-slate-800 tracking-tight">探索空间</h1>
        <p class="text-slate-500 mt-1">发现属于你的学术社区与兴趣天地</p>
      </div>
      <div class="flex items-center gap-3">
        <el-input v-model="searchQuery" placeholder="搜索空间" prefix-icon="Search" clearable class="w-64" />
        <el-select v-model="categoryFilter" placeholder="全部分类" clearable class="w-32">
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
      </div>
    </div>

    <!-- Space Grid -->
    <div v-loading="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <el-card v-for="space in filteredSpaces" :key="space.id" shadow="hover" class="rounded-2xl border-none h-full flex flex-col cursor-pointer transition-shadow hover:shadow-lg" @click="$router.push(`/spaces/${space.id}`)">
        <div class="flex gap-4 items-start">
          <div class="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xl shrink-0">
            {{ space.name.charAt(0) }}
          </div>
          <div class="flex-1">
            <div class="flex justify-between items-start">
              <h3 class="font-bold text-slate-800 truncate" :title="space.name">{{ space.name }}</h3>
              <el-tag size="small" type="info" class="rounded-full">{{ space.type || '通用' }}</el-tag>
            </div>
            <p class="text-sm text-slate-500 mt-1 line-clamp-2">{{ space.description || '暂无简介' }}</p>
          </div>
        </div>
        
        <div class="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 mt-auto">
          <div class="flex gap-4">
            <span class="flex items-center gap-1"><el-icon><ChatDotSquare /></el-icon> {{ space.post_count || 0 }}</span>
            <span class="flex items-center gap-1"><el-icon><User /></el-icon> {{ space.subscriber_count || 0 }}</span>
          </div>
          <el-button type="primary" plain round size="small" @click.stop="toggleSubscribe(space)">
            {{ isSubscribed(space) ? '已关注' : '+ 关注' }}
          </el-button>
        </div>
      </el-card>
      
      <!-- Empty State -->
      <div v-if="!loading && filteredSpaces.length === 0" class="col-span-full py-20 text-center">
        <el-empty description="没有找到匹配的空间" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'
import { ChatDotSquare, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const loading = ref(true)
const spaces = ref<any[]>([])
const categories = ref<any[]>([])
const searchQuery = ref('')
const categoryFilter = ref<number | ''>('')
const mySubscriptions = ref<number[]>([]) // Currently authenticated user's subscriptions

const fetchData = async () => {
  loading.value = true
  try {
    const [spacesRes, catsRes] = await Promise.all([
      request.get('/spaces/'),
      request.get('/categories/')
    ])
    spaces.value = (spacesRes as any).items || spacesRes
    categories.value = (catsRes as any).items || catsRes
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})

const filteredSpaces = computed(() => {
  return spaces.value.filter(s => {
    const matchCat = categoryFilter.value ? s.category_id === categoryFilter.value : true
    const matchSearch = searchQuery.value ? s.name.toLowerCase().includes(searchQuery.value.toLowerCase()) : true
    return matchCat && matchSearch
  })
})

const isSubscribed = (space: any) => mySubscriptions.value.includes(space.id)

const toggleSubscribe = async (space: any) => {
  try {
    if (isSubscribed(space)) {
      await request.delete(`/spaces/${space.id}/subscriptions/me`)
      mySubscriptions.value = mySubscriptions.value.filter(id => id !== space.id)
      space.subscriber_count--
    } else {
      await request.put(`/spaces/${space.id}/subscriptions/me`)
      mySubscriptions.value.push(space.id)
      space.subscriber_count++
    }
    ElMessage.success(isSubscribed(space) ? '已成功关注' : '已取消关注')
  } catch (e) {
    console.error(e)
  }
}
</script>
