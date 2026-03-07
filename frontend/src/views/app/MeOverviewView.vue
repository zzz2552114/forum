<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Header Card -->
    <el-card shadow="never" class="border-none bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl">
      <div class="flex items-center gap-6 p-4">
        <el-avatar :size="80" :src="authStore.user?.avatar_url || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" class="border-4 border-white shadow-sm" />
        <div class="flex-1">
          <h1 class="text-2xl font-bold text-slate-800 flex items-center gap-3">
            {{ authStore.user?.nickname || authStore.user?.username }}
            <el-tag size="small" type="success" effect="light" class="rounded-full px-3">
              Lv.{{ authStore.user?.trust_level || 1 }} User
            </el-tag>
          </h1>
          <p class="text-slate-500 mt-2">{{ authStore.user?.bio || 'This user hasn\'t written a bio yet.' }}</p>
          <div class="flex gap-4 mt-3 text-sm text-slate-500" v-if="authStore.user?.school_name">
            <span class="flex items-center gap-1"><el-icon><School /></el-icon> {{ authStore.user.school_name }}</span>
          </div>
        </div>
        <div>
          <el-button @click="$router.push('/me/settings/profile')" round :icon="Setting">Edit Profile</el-button>
        </div>
      </div>
    </el-card>

    <!-- Stats Grid -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <el-card shadow="hover" class="border-none rounded-xl text-center p-2" v-for="stat in stats" :key="stat.label">
        <div class="text-slate-500 text-sm font-medium mb-1">{{ stat.label }}</div>
        <div class="text-2xl font-bold text-slate-800">{{ stat.value }}</div>
      </el-card>
    </div>

    <!-- Quick Links -->
    <el-card shadow="never" class="border-none rounded-xl mt-6">
      <template #header>
        <h3 class="font-bold text-slate-800">Quick Activities</h3>
      </template>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="flex items-center justify-between p-4 rounded-lg bg-slate-50 hover:bg-slate-100 cursor-pointer transition-colors">
          <div class="flex items-center gap-3"><el-icon class="text-blue-500 text-xl"><Document /></el-icon> <span class="font-medium">My Posts</span></div>
          <el-icon class="text-slate-400"><ArrowRight /></el-icon>
        </div>
        <div class="flex items-center justify-between p-4 rounded-lg bg-slate-50 hover:bg-slate-100 cursor-pointer transition-colors">
          <div class="flex items-center gap-3"><el-icon class="text-orange-500 text-xl"><Star /></el-icon> <span class="font-medium">My Bookmarks</span></div>
          <el-icon class="text-slate-400"><ArrowRight /></el-icon>
        </div>
        <div class="flex items-center justify-between p-4 rounded-lg bg-slate-50 hover:bg-slate-100 cursor-pointer transition-colors">
          <div class="flex items-center gap-3"><el-icon class="text-green-500 text-xl"><FolderOpened /></el-icon> <span class="font-medium">My Resources</span></div>
          <el-icon class="text-slate-400"><ArrowRight /></el-icon>
        </div>
        <div class="flex items-center justify-between p-4 rounded-lg bg-slate-50 hover:bg-slate-100 cursor-pointer transition-colors">
          <div class="flex items-center gap-3"><el-icon class="text-purple-500 text-xl"><Comment /></el-icon> <span class="font-medium">My Comments</span></div>
          <el-icon class="text-slate-400"><ArrowRight /></el-icon>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Setting, School, ArrowRight, Document, Star, FolderOpened, Comment } from '@element-plus/icons-vue'
import request from '@/utils/request'

const authStore = useAuthStore()

const stats = ref([
  { label: 'Posts', value: 0 },
  { label: 'Comments', value: 0 },
  { label: 'Resources', value: 0 },
  { label: 'Reputation', value: authStore.user?.reputation_score || 0 }
])

onMounted(async () => {
  try {
    const data: any = await request.get('/me/stats')
    if (stats.value[0]) stats.value[0].value = data.post_count || 0
    if (stats.value[1]) stats.value[1].value = data.comment_count || 0
    if (stats.value[2]) stats.value[2].value = data.resource_count || 0
  } catch (e) {
    console.error('Failed to fetch stats', e)
  }
})
</script>
