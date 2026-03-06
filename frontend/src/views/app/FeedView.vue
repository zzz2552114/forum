<template>
  <div class="feed-container">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-slate-800 tracking-tight">发现</h1>
      <el-select v-model="filter" placeholder="Select" class="w-32">
        <el-option label="最新" value="latest" />
        <el-option label="推荐" value="hot" />
      </el-select>
    </div>
    
    <div class="space-y-4">
      <el-card shadow="hover" class="border-none rounded-xl cursor-pointer hover:shadow-md transition-shadow">
        <div class="flex items-center gap-3 mb-3">
          <el-avatar :size="28" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
          <span class="text-sm font-medium text-slate-700">UserOne</span>
          <span class="text-xs text-slate-400">&middot; 2 hours ago</span>
          <span class="text-xs text-slate-400">&middot; 高等数学</span>
        </div>
        <h3 class="text-lg font-bold text-slate-800 mb-2">如何在考试中拿到满分？</h3>
        <p class="text-slate-600 text-sm line-clamp-2">这是一段帖子摘要，主要讲的是平时如何复习等等... 这里应该使用类似ChatGPT那样的优雅排版。</p>
        <div class="flex gap-4 mt-4 text-slate-400 text-sm">
          <span class="flex items-center gap-1 hover:text-blue-500"><el-icon><View /></el-icon> 120</span>
          <span class="flex items-center gap-1 hover:text-blue-500"><el-icon><ChatDotRound /></el-icon> 15</span>
          <span class="flex items-center gap-1 hover:text-blue-500"><el-icon><Star /></el-icon> 20</span>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { View, ChatDotRound, Star } from '@element-plus/icons-vue'

const filter = ref('latest')
</script>
