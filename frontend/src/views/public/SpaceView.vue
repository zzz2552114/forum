<template>
  <div class="max-w-6xl mx-auto flex flex-col md:flex-row gap-6 mt-4">
    
    <!-- Left Context / Nav -->
    <aside class="w-full md:w-64 shrink-0 space-y-4">
      <el-card shadow="never" class="border-none bg-slate-50 rounded-xl" v-loading="loadingSpace">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-lg">
            {{ space?.name?.charAt(0) || 'S' }}
          </div>
          <div>
            <h2 class="font-bold text-slate-800">{{ space?.name || 'Loading...' }}</h2>
            <div class="text-xs text-slate-500">{{ space?.type || '通用空间' }}</div>
          </div>
        </div>
        
        <el-button type="primary" class="w-full font-bold shadow-sm" @click="toggleSubscribe">
          {{ isSubscribed ? '已关注' : '关注该空间' }}
        </el-button>
        
        <el-menu :default-active="activeTab" class="mt-4 border-none bg-transparent" @select="handleSelect">
          <el-menu-item index="posts" class="h-10 leading-10 rounded-lg mb-1">
            <el-icon><Document /></el-icon> 帖子
          </el-menu-item>
          <el-menu-item index="resources" class="h-10 leading-10 rounded-lg mb-1">
            <el-icon><FolderOpened /></el-icon> 资料
          </el-menu-item>
          <el-menu-item index="rules" class="h-10 leading-10 rounded-lg mb-1">
            <el-icon><Warning /></el-icon> 规则
          </el-menu-item>
          <el-menu-item index="moderators" class="h-10 leading-10 rounded-lg mb-1">
            <el-icon><UserFilled /></el-icon> 版主
          </el-menu-item>
        </el-menu>
      </el-card>

      <!-- Space Stats -->
      <el-card shadow="never" class="border-none rounded-xl" v-if="space">
        <h3 class="font-bold text-slate-800 mb-2">简介</h3>
        <p class="text-sm text-slate-600 mb-4">{{ space.description || '这个空间很神秘，什么也没写。' }}</p>
        
        <div class="flex justify-between text-xs text-slate-500">
          <span>创建于</span>
          <span>{{ new Date(space.created_at).toLocaleDateString() }}</span>
        </div>
      </el-card>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1">
      <div v-if="activeTab === 'posts'">
        <div class="flex justify-between items-center mb-4">
          <el-radio-group v-model="postSort" size="small">
            <el-radio-button label="最新" value="latest" />
            <el-radio-button label="最热" value="hot" />
          </el-radio-group>
          <el-button type="primary" :icon="Edit" @click="$router.push(`/posts/new?space_id=${spaceId}`)">发布帖子</el-button>
        </div>
        
        <div class="space-y-4" v-loading="loadingPosts">
          <PostCard v-for="post in posts" :key="post.id" :post="post" />
          <el-empty v-if="!loadingPosts && posts.length === 0" description="暂无帖子" />
        </div>
        
        <div class="mt-6 flex justify-center" v-if="totalPosts > 0">
          <el-pagination v-model:current-page="page" :page-size="pageSize" layout="prev, pager, next" :total="totalPosts" @current-change="fetchPosts" />
        </div>
      </div>
      
      <div v-else-if="activeTab === 'resources'">
        <el-empty description="资料功能开发中" />
      </div>
      <div v-else-if="activeTab === 'rules'">
        <el-card shadow="never" class="border-none rounded-xl">
          <h2 class="text-xl font-bold mb-4">空间规则</h2>
          <el-empty description="暂无自定义规则" />
        </el-card>
      </div>
      <div v-else-if="activeTab === 'moderators'">
         <el-card shadow="never" class="border-none rounded-xl">
          <h2 class="text-xl font-bold mb-4">版主列表</h2>
          <el-empty description="暂无管理团队成员" />
        </el-card>
      </div>
    </main>
    
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/utils/request'
import PostCard from '@/components/post/PostCard.vue'
import { Document, FolderOpened, Warning, UserFilled, Edit } from '@element-plus/icons-vue'

const route = useRoute()
const spaceId = computed(() => Number(route.params.spaceId))

const activeTab = ref('posts')
const postSort = ref('latest')

const space = ref<any>(null)
const loadingSpace = ref(true)
const isSubscribed = ref(false)

const posts = ref<any[]>([])
const loadingPosts = ref(true)
const page = ref(1)
const pageSize = ref(10)
const totalPosts = ref(0)

const fetchSpace = async () => {
  loadingSpace.value = true
  try {
    space.value = await request.get(`/spaces/${spaceId.value}`)
  } catch (e) {
    console.error(e)
  } finally {
    loadingSpace.value = false
  }
}

const fetchPosts = async () => {
  loadingPosts.value = true
  try {
    const res: any = await request.get(`/posts/`, {
      params: { space_id: spaceId.value, page: page.value, page_size: pageSize.value }
    })
    posts.value = res.items
    totalPosts.value = res.pagination.total
  } catch (e) {
    console.error(e)
  } finally {
    loadingPosts.value = false
  }
}

onMounted(() => {
  fetchSpace()
  fetchPosts()
})

const handleSelect = (key: string) => {
  activeTab.value = key
}

const toggleSubscribe = () => {
  isSubscribed.value = !isSubscribed.value
}

</script>
