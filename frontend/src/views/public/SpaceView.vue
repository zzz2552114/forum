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
      
        <div v-else-if="activeTab === 'resources'" class="space-y-4 relative" v-loading="loadingMaterials">
          <div v-if="!loadingMaterials && materials.length === 0" class="flex flex-col items-center justify-center text-[var(--c-navy)]/40 min-h-[300px]">
            <el-empty description="该空间暂无资料" />
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="mat in materials"
              :key="mat.id"
              class="group flex items-center justify-between p-4 rounded-2xl bg-white hover:bg-[var(--c-fog)] transition-colors border border-transparent hover:border-[var(--c-navy)]/5 cursor-pointer shadow-sm"
            >
              <div class="flex items-start gap-x-4 overflow-hidden pr-4 max-w-[70%]">
                <div class="w-12 h-12 bg-[var(--c-fog)] rounded-[12px] flex items-center justify-center text-[#E85D04] shrink-0 border border-[var(--c-navy)]/5">
                  <el-icon :size="24"><Document /></el-icon>
                </div>
                <div class="min-w-0">
                  <h4 class="font-medium text-lg text-[var(--c-navy)] mb-1 truncate group-hover:text-[var(--c-indigo)] transition-colors" :title="mat.title">
                    {{ mat.title }}
                  </h4>
                  <div class="flex items-center gap-x-4 text-sm text-[var(--c-navy)]/50">
                    <span class="flex items-center gap-x-1 font-medium"><span class="w-1.5 h-1.5 rounded-full bg-[var(--c-gold)] opacity-80 inline-block"></span>
                      {{ space?.name || '未知空间' }}</span
                    >
                    <span>更新于：{{ new Date(mat.created_at).toLocaleDateString() }}</span>
                  </div>
                </div>
              </div>

              <div class="flex items-center gap-x-3 pl-4 border-l border-[var(--c-navy)]/5 shrink-0">
                <div class="text-[var(--c-navy)]/40 text-sm hidden lg:block text-right">
                  <div class="flex items-center gap-1"><el-icon><Star /></el-icon> {{ mat.bookmark_count || 0 }} 次收藏</div>
                  <div class="flex items-center gap-1"><el-icon><Download /></el-icon> {{ mat.download_count || 0 }} 次下载</div>
                </div>
                <!-- Bookmark Button -->
                <button
                  @click.stop="toggleBookmark(mat)"
                  class="w-10 h-10 rounded-[12px] flex items-center justify-center bg-white border transition-all shadow-sm"
                  :class="mat.is_bookmarked ? 'text-orange-500 border-orange-200 hover:bg-orange-50' : 'text-[var(--c-indigo)] border-[var(--c-navy)]/10 hover:border-orange-300 hover:text-orange-500'"
                >
                  <el-icon :size="20"><StarFilled v-if="mat.is_bookmarked" /><Star v-else /></el-icon>
                </button>
                <!-- Download Button -->
                <button
                  @click.stop="downloadFile(mat)"
                  class="w-10 h-10 rounded-[12px] flex items-center justify-center bg-white text-[var(--c-indigo)] border border-[var(--c-navy)]/10 hover:border-[var(--c-indigo)] group-hover:bg-[var(--c-indigo)] group-hover:text-white transition-all shadow-sm"
                >
                  <el-icon :size="20"><Download /></el-icon>
                </button>
              </div>
            </div>

            <div class="mt-6 flex justify-center" v-if="totalMaterials > materials.length || matPage > 1">
              <el-pagination v-model:current-page="matPage" :page-size="matPageSize" layout="prev, pager, next" :total="totalMaterials" @current-change="fetchMaterials" />
            </div>
          </div>
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
import { Document, FolderOpened, Warning, UserFilled, Edit, Download, Star, StarFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

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

const materials = ref<any[]>([])
const loadingMaterials = ref(false)
const matPage = ref(1)
const matPageSize = ref(10)
const totalMaterials = ref(0)

const fetchMaterials = async () => {
  loadingMaterials.value = true
  try {
    const res: any = await request.get(`/resources/`, {
      params: { space_id: spaceId.value, page: matPage.value, page_size: matPageSize.value }
    })
    materials.value = res.items || []
    totalMaterials.value = res.pagination.total
  } catch (e) {
    console.error(e)
  } finally {
    loadingMaterials.value = false
  }
}

onMounted(() => {
  fetchSpace()
  fetchPosts()
  fetchMaterials()
})

const handleSelect = (key: string) => {
  activeTab.value = key
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
    }
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const downloadFile = async (mat: any) => {
  if (!mat) return;
  try {
    const response = await request.post(`/resources/${mat.id}/download`, {}, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response as any]));
    const link = document.createElement('a');
    link.href = url;
    link.download = mat.filename || `${mat.title}.pdf`; // generic fallback
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    mat.download_count = (mat.download_count || 0) + 1;
  } catch (e) {
    ElMessage.error('下载遇到错误');
  }
}

const toggleSubscribe = () => {
  isSubscribed.value = !isSubscribed.value
}

</script>
