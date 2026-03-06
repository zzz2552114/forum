<template>
  <div class="h-full flex flex-col py-4 gap-6">
    <div class="px-2">
      <el-menu
        :default-active="activeMenu"
        class="border-none bg-transparent"
        router
      >
        <el-menu-item index="/feed" class="rounded-lg mb-1">
          <el-icon><Compass /></el-icon>
          <template #title>发现</template>
        </el-menu-item>
        <el-menu-item index="/me/overview" class="rounded-lg mb-1">
          <el-icon><User /></el-icon>
          <template #title>我的主页</template>
        </el-menu-item>
        <el-menu-item index="/notifications" class="rounded-lg mb-1">
          <el-icon><Bell /></el-icon>
          <template #title>通知</template>
        </el-menu-item>
      </el-menu>
    </div>

    <div class="px-4">
      <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">我关注的空间</h3>
      <ul class="space-y-2">
        <li v-for="space in subscribedSpaces" :key="space.id">
          <router-link 
            :to="`/spaces/${space.id}`" 
            class="flex items-center gap-2 px-2 py-1.5 text-slate-600 hover:bg-slate-100 hover:text-slate-900 rounded-md transition-colors"
          >
            <div class="w-6 h-6 rounded bg-indigo-100 text-indigo-600 flex items-center justify-center text-xs font-bold">
              {{ space.name.charAt(0) }}
            </div>
            <span class="text-sm truncate">{{ space.name }}</span>
          </router-link>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Compass, User, Bell } from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)

// Mock data for now, will connect to Pinia store later
const subscribedSpaces = ref([
  { id: 1, name: '高等数学讨论组' },
  { id: 2, name: '计算机组成原理' },
  { id: 3, name: '校园生活闲聊' }
])
</script>

<style scoped>
/* Override element plus menu item styles to look more like standard tailwind active states */
.el-menu-item.is-active {
  background-color: #eff6ff !important; /* blue-50 */
  color: #2563eb !important; /* blue-600 */
  font-weight: 500;
}
.el-menu-item:hover {
  background-color: #f1f5f9 !important; /* slate-100 */
}
</style>
