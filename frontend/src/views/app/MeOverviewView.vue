<template>
  <div class="min-h-screen bg-slate-50 pb-12 font-sans">
    <HomeHeader />

    <main class="max-w-4xl mx-auto pt-8 px-4 space-y-8">
      <!-- Premium Header Card -->
      <div class="bg-gradient-to-r from-slate-900 to-slate-800 rounded-3xl shadow-xl overflow-hidden relative">
        <div class="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
          <el-icon class="text-9xl text-white"><User /></el-icon>
        </div>
        <div class="flex flex-col md:flex-row items-center md:items-start gap-8 p-8 relative z-10">
          <el-avatar :size="100" :src="authStore.user?.avatar_url || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" class="border-4 border-white shadow-lg" />
          <div class="flex-1 text-center md:text-left">
            <h1 class="text-3xl font-extrabold text-white flex flex-col md:flex-row items-center gap-4 mb-2">
              {{ authStore.user?.nickname || authStore.user?.username }}
              <el-tag size="small" type="warning" effect="dark" class="rounded-full px-4 border-none bg-yellow-500 text-yellow-50">
                Lv.{{ authStore.user?.trust_level || 1 }} User
              </el-tag>
            </h1>
            <p class="text-slate-300 text-sm md:text-base max-w-xl">{{ authStore.user?.bio || 'This user hasn\'t written a bio yet.' }}</p>
            <div class="flex flex-wrap justify-center md:justify-start gap-4 mt-6 text-sm text-slate-300" v-if="authStore.user?.school_name">
              <span class="flex items-center gap-1.5 bg-slate-800/50 px-3 py-1.5 rounded-full"><el-icon><School /></el-icon> {{ authStore.user.school_name }}</span>
            </div>
          </div>
          <div class="mt-4 md:mt-0">
            <el-button @click="$router.push('/me/settings/profile')" round :icon="Setting" color="rgba(255,255,255,0.1)" class="text-white border-white/20 hover:bg-white/20 border">
              编辑个人资料
            </el-button>
          </div>
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-2 lg:grid-cols-5 md:grid-cols-3 gap-4 md:gap-6">
        <el-card shadow="hover" class="border-none rounded-2xl text-center p-4 hover:-translate-y-1 transition-transform duration-300" v-for="stat in stats" :key="stat.label">
          <div class="text-slate-500 text-sm font-medium mb-2">{{ stat.label }}</div>
          <div class="text-3xl font-extrabold text-slate-800">{{ stat.value }}</div>
        </el-card>
      </div>

      <!-- Quick Links -->
      <el-card shadow="never" class="border-none rounded-3xl mt-8 shadow-sm">
        <template #header>
          <div class="px-2">
            <h3 class="text-xl font-bold text-slate-800">快捷访问</h3>
          </div>
        </template>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 p-2">
          <!-- 现有卡片 -->
          <div @click="$router.push('/me/posts')" class="flex items-center justify-between p-5 rounded-2xl bg-slate-50 hover:bg-white hover:shadow-md border border-transparent hover:border-slate-100 cursor-pointer transition-all duration-300">
            <div class="flex items-center gap-4"><div class="p-2 bg-blue-100 rounded-xl text-blue-600 flex items-center justify-center"><el-icon class="text-xl"><Document /></el-icon></div> <span class="font-bold text-slate-700">我的帖子</span></div>
            <el-icon class="text-slate-400"><ArrowRight /></el-icon>
          </div>
          <div @click="$router.push('/me/favorites')" class="flex items-center justify-between p-5 rounded-2xl bg-slate-50 hover:bg-white hover:shadow-md border border-transparent hover:border-slate-100 cursor-pointer transition-all duration-300">
            <div class="flex items-center gap-4"><div class="p-2 bg-orange-100 rounded-xl text-orange-600 flex items-center justify-center"><el-icon class="text-xl"><Star /></el-icon></div> <span class="font-bold text-slate-700">我的收藏</span></div>
            <el-icon class="text-slate-400"><ArrowRight /></el-icon>
          </div>
          <div @click="$router.push('/me/materials')" class="flex items-center justify-between p-5 rounded-2xl bg-slate-50 hover:bg-white hover:shadow-md border border-transparent hover:border-slate-100 cursor-pointer transition-all duration-300">
            <div class="flex items-center gap-4"><div class="p-2 bg-green-100 rounded-xl text-green-600 flex items-center justify-center"><el-icon class="text-xl"><FolderOpened /></el-icon></div> <span class="font-bold text-slate-700">我的资料库</span></div>
            <el-icon class="text-slate-400"><ArrowRight /></el-icon>
          </div>
          <div @click="$router.push('/me/comments')" class="flex items-center justify-between p-5 rounded-2xl bg-slate-50 hover:bg-white hover:shadow-md border border-transparent hover:border-slate-100 cursor-pointer transition-all duration-300">
            <div class="flex items-center gap-4"><div class="p-2 bg-purple-100 rounded-xl text-purple-600 flex items-center justify-center"><el-icon class="text-xl"><Comment /></el-icon></div> <span class="font-bold text-slate-700">我的评论</span></div>
            <el-icon class="text-slate-400"><ArrowRight /></el-icon>
          </div>

          <!-- 新增卡片 -->
          <div @click="$router.push('/me/likes')" class="flex items-center justify-between p-5 rounded-2xl bg-slate-50 hover:bg-white hover:shadow-md border border-transparent hover:border-slate-100 cursor-pointer transition-all duration-300">
            <div class="flex items-center gap-4"><div class="p-2 bg-red-100 rounded-xl text-red-600 flex items-center justify-center"><el-icon class="text-xl"><Pointer /></el-icon></div> <span class="font-bold text-slate-700">我的点赞</span></div>
            <el-icon class="text-slate-400"><ArrowRight /></el-icon>
          </div>
          <div class="flex items-center justify-between p-5 rounded-2xl bg-slate-50 hover:bg-white hover:shadow-md border border-transparent hover:border-slate-100 cursor-pointer transition-all duration-300">
            <div class="flex items-center gap-4"><div class="p-2 bg-teal-100 rounded-xl text-teal-600 flex items-center justify-center"><el-icon class="text-xl"><View /></el-icon></div> <span class="font-bold text-slate-700">我的关注</span></div>
            <el-icon class="text-slate-400"><ArrowRight /></el-icon>
          </div>
          <div class="flex items-center justify-between p-5 rounded-2xl bg-slate-50 hover:bg-white hover:shadow-md border border-transparent hover:border-slate-100 cursor-pointer transition-all duration-300">
            <div class="flex items-center gap-4"><div class="p-2 bg-pink-100 rounded-xl text-pink-600 flex items-center justify-center"><el-icon class="text-xl"><Avatar /></el-icon></div> <span class="font-bold text-slate-700">我的粉丝</span></div>
            <el-icon class="text-slate-400"><ArrowRight /></el-icon>
          </div>
          <div class="flex items-center justify-between p-5 rounded-2xl bg-slate-50 hover:bg-white hover:shadow-md border border-transparent hover:border-slate-100 cursor-pointer transition-all duration-300">
            <div class="flex items-center gap-4"><div class="p-2 bg-indigo-100 rounded-xl text-indigo-600 flex items-center justify-center"><el-icon class="text-xl"><Connection /></el-icon></div> <span class="font-bold text-slate-700">我的好友</span></div>
            <el-icon class="text-slate-400"><ArrowRight /></el-icon>
          </div>
          <div class="flex items-center justify-between p-5 rounded-2xl bg-slate-50 hover:bg-white hover:shadow-md border border-transparent hover:border-slate-100 cursor-pointer transition-all duration-300">
            <div class="flex items-center gap-4"><div class="p-2 bg-cyan-100 rounded-xl text-cyan-600 flex items-center justify-center"><el-icon class="text-xl"><ChatSquare /></el-icon></div> <span class="font-bold text-slate-700">我的临时群组</span></div>
            <el-icon class="text-slate-400"><ArrowRight /></el-icon>
          </div>
        </div>
      </el-card>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Setting, School, ArrowRight, Document, Star, FolderOpened, Comment, User, Pointer, View, Avatar, Connection, ChatSquare } from '@element-plus/icons-vue'
import request from '@/utils/request'
import HomeHeader from '@/components/HomeHeader.vue'

const authStore = useAuthStore()

const stats = ref([
  { label: '加入空间', value: 0 },
  { label: '帖子发布', value: 0 },
  { label: '粉丝数量', value: 0 },
  { label: '资料贡献', value: 0 },
  { label: '荣誉声望', value: authStore.user?.reputation_score || 0 }
])

onMounted(async () => {
  try {
    const data: any = await request.get('/me/stats')
    if (stats.value[0]) stats.value[0].value = data.joined_spaces_count || 0
    if (stats.value[1]) stats.value[1].value = data.post_count || 0
    if (stats.value[2]) stats.value[2].value = data.follower_count || 0
    if (stats.value[3]) stats.value[3].value = data.resource_count || 0
  } catch (e) {
    console.error('Failed to fetch stats', e)
  }
})
</script>
