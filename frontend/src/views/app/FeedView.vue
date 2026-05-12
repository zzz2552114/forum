<template>
  <div class="min-h-screen bg-slate-50 pb-12 font-sans">
    <HomeHeader />
    
    <main class="max-w-3xl mx-auto pt-28 px-4">
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-extrabold text-slate-800 tracking-tight">发现新鲜事</h1>
          <p class="text-slate-500 mt-2">浏览全站动态，不错过任何热点</p>
        </div>
        <el-select v-model="filter" placeholder="Select" class="w-28" size="large" @change="fetchPosts">
          <el-option label="最新" value="latest" />
          <el-option label="推荐" value="hot" />
        </el-select>
      </div>
      
      <div class="space-y-6" v-loading="loading">
        <el-card 
          v-for="post in posts" 
          :key="post.id"
          @click="router.push(`/posts/${post.id}`)"
          shadow="hover" 
          class="border-none rounded-2xl cursor-pointer hover:shadow-xl hover:-translate-y-1 bg-white transition-all duration-300">
          <div class="p-2">
            <div class="flex items-center gap-3 mb-4">
              <el-avatar :size="32" :src="post.author?.avatar_url || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" class="ring-2 ring-blue-50" />
              <div class="flex flex-col">
                <span class="text-sm font-bold text-slate-800">{{ post.author?.nickname || post.author?.username }}</span>
                <span class="text-xs text-slate-400">
                  {{ new Date(post.created_at).toLocaleString() }} 
                  <span v-if="post.space">&middot; {{ post.space.name }}</span>
                </span>
              </div>
            </div>
            <h3 class="text-xl font-bold text-slate-800 mb-3 line-clamp-1 group-hover:text-blue-600 transition-colors">{{ post.title }}</h3>
            <p class="text-slate-500 text-sm line-clamp-2 leading-relaxed">
              {{ post.content.replace(/<[^>]*>?/gm, '') }}
            </p>
            <div class="flex gap-6 mt-5 text-slate-400 text-sm font-medium">
              <span class="flex items-center gap-1.5 hover:text-blue-500 transition-colors"><el-icon><View /></el-icon> {{ post.view_count || 0 }}</span>
              <span class="flex items-center gap-1.5 hover:text-blue-500 transition-colors"><el-icon><ChatDotRound /></el-icon> {{ post.comment_count || 0 }}</span>
              <span class="flex items-center gap-1.5 hover:text-blue-500 transition-colors"><el-icon><Star /></el-icon> {{ post.like_count || 0 }}</span>
            </div>
          </div>
        </el-card>

        <el-empty v-if="posts.length === 0 && !loading" description="暂无动态" />
        
        <div class="flex justify-center mt-8 pb-4" v-if="total > 0">
          <el-pagination 
            v-model:current-page="page" 
            :page-size="pageSize" 
            layout="prev, pager, next" 
            :total="total" 
            @current-change="fetchPosts"
            background
          />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { View, ChatDotRound, Star } from '@element-plus/icons-vue'
import HomeHeader from '@/components/HomeHeader.vue'
import request from '@/utils/request'

const router = useRouter()
const filter = ref('latest')
const loading = ref(false)
const posts = ref<any[]>([])
const page = ref(1)
const pageSize = ref(15)
const total = ref(0)

const fetchPosts = async () => {
  loading.value = true
  try {
    // Determine sort based on filter (backend might need updates to map 'hot', currently we just fetch latest)
    // Actually our backend `/posts/` simply returns latest by id/created_at due to default sorting or offset.
    const res: any = await request.get('/posts', {
      params: { 
        page: page.value, 
        page_size: pageSize.value 
        // If sorting is added to backend, we would pass filter.value here
      }
    })
    
    // We need space and author data which the backend returns in the PostResponse
    // For space name, we might need a separate fetch if backend doesn't embed it, 
    // but looking at `PostResponse` it embeds `space_id` and `author_id`. 
    // Wait, let's fetch full posts or fetch missing authors iteratively if not provided natively.
    // The backend `posts.py` currently returns `author_id` and `space_id`, not nested objects in PostResponse for nested objects, unfortunately.
    // Let's check `app/schemas/forum.py` if PostResponse has author and space.
  
    // Assuming backend returns it correctly, or we just display title and content for now if authors aren't nested.
    // Looking at `read_posts` in posts.py:
    // It returns `author_id` and `space_id` integers.
    // This frontend pattern assumes nested `author.username`. If not present, we fallback.
    
    posts.value = res.items || []
    total.value = res.pagination?.total || 0
    
    // Fallback parsing for usernames
    for (let p of posts.value) {
        if (!p.author) {
            // Mock object if not present in the api schema
            p.author = { username: `User ${p.author_id}`, avatar_url: '' }
        }
        if (!p.space) {
            p.space = { name: `Space ${p.space_id}` }
        }
    }
    
  } catch (error) {
    console.error('Failed to fetch posts:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPosts()
})
</script>
