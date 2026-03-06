<template>
  <header class="bg-white border-b sticky top-0 z-50">
    <div class="container mx-auto px-4 h-16 flex items-center justify-between">
      <!-- Left: Logo & Nav -->
      <div class="flex items-center gap-6">
        <router-link to="/" class="flex items-center gap-2 group">
          <div class="w-8 h-8 bg-primary text-white rounded-lg flex items-center justify-center font-bold text-xl group-hover:scale-105 transition-transform bg-blue-600">
            F
          </div>
          <span class="font-bold text-lg text-slate-800 tracking-tight">Forum</span>
        </router-link>
        <nav class="hidden md:flex gap-4">
          <router-link to="/explore" class="text-slate-600 hover:text-blue-600 font-medium transition-colors">探索空间</router-link>
        </nav>
      </div>

      <!-- Middle: Search (Desktop) -->
      <div class="hidden md:flex flex-1 max-w-md mx-6">
        <el-input
          v-model="searchQuery"
          placeholder="搜索帖子、空间、资料..."
          class="w-full"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- Right: Actions & User -->
      <div class="flex items-center gap-4">
        <!-- Auth State: Logged In -->
        <template v-if="authStore.isAuthenticated">
          <el-button type="primary" :icon="Edit" round @click="$router.push('/posts/new')">
            发帖
          </el-button>
          
          <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="cursor-pointer" @click="$router.push('/notifications')">
            <el-icon class="text-xl text-slate-600 hover:text-blue-600 transition-colors"><Bell /></el-icon>
          </el-badge>

          <el-dropdown trigger="click" @command="handleCommand">
            <span class="el-dropdown-link flex items-center gap-2 cursor-pointer outline-none">
              <el-avatar :size="32" :src="authStore.user?.avatar_url || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
              <span class="hidden sm:inline font-medium text-slate-700">{{ authStore.user?.nickname || authStore.user?.username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">我的面板</el-dropdown-item>
                <el-dropdown-item command="settings">设置</el-dropdown-item>
                <el-dropdown-item divided command="logout" class="text-red-500">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        
        <!-- Auth State: Guest -->
        <template v-else>
          <el-button text @click="$router.push('/login')">登录</el-button>
          <el-button type="primary" @click="$router.push('/register')">注册</el-button>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Bell, Edit } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const searchQuery = ref('')
const unreadCount = ref(0) // Will hook to live data later

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/search', query: { keyword: searchQuery.value } })
  }
}

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/me/overview')
      break
    case 'settings':
      router.push('/me/settings/profile')
      break
    case 'logout':
      authStore.logout()
      router.push('/login')
      break
  }
}
</script>
