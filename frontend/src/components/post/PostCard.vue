<template>
  <el-card shadow="hover" class="border-none rounded-xl cursor-pointer hover:shadow-md transition-shadow group" @click="$router.push(`/posts/${post.id}`)">
    <div class="flex gap-4">
      <div class="hidden sm:flex flex-col items-center gap-1 shrink-0 pt-1">
        <el-button type="info" plain circle size="small" class="border-none bg-slate-50 hover:bg-slate-100 hover:text-blue-500">
          <el-icon><CaretTop /></el-icon>
        </el-button>
        <span class="font-bold text-slate-600 text-sm">{{ post.like_count || 0 }}</span>
        <el-button type="info" plain circle size="small" class="border-none bg-slate-50 hover:bg-slate-100 hover:text-red-500">
          <el-icon><CaretBottom /></el-icon>
        </el-button>
      </div>
      
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 mb-2 text-xs text-slate-500">
          <el-avatar :size="20" :src="post.author?.avatar_url || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
          <span class="font-medium text-slate-700 hover:text-blue-600 truncate">{{ post.author?.nickname || post.author?.username || '佚名' }}</span>
          <span>&middot;</span>
          <span>{{ new Date(post.created_at).toLocaleDateString() }}</span>
          
          <template v-if="post.tags && post.tags.length > 0">
            <span>&middot;</span>
            <el-tag v-for="tag in post.tags.slice(0, 2)" :key="tag.id" size="small" type="info" effect="plain" class="rounded-md border-none bg-slate-100">{{ tag.name }}</el-tag>
          </template>
        </div>
        
        <h3 class="text-lg font-bold text-slate-800 mb-1 group-hover:text-blue-600 transition-colors truncate">
          <el-icon v-if="post.is_pinned" class="text-orange-500 mr-1" title="置顶"><ArrowUpBold /></el-icon>
          <el-icon v-if="post.is_featured" class="text-red-500 mr-1" title="精华"><StarFilled /></el-icon>
          {{ post.title }}
        </h3>
        
        <p class="text-slate-500 text-sm line-clamp-2 leading-relaxed">
          {{ post.content }}
        </p>
        
        <div class="flex gap-4 mt-3 text-slate-400 text-sm sm:hidden">
          <span class="flex items-center gap-1"><el-icon><CaretTop /></el-icon> {{ post.like_count || 0 }}</span>
          <span class="flex items-center gap-1"><el-icon><ChatDotRound /></el-icon> {{ post.comment_count || 0 }}</span>
          <span class="flex items-center gap-1"><el-icon><View /></el-icon> {{ post.view_count || 0 }}</span>
        </div>
      </div>
      
      <div class="hidden sm:flex flex-col items-end shrink-0 gap-2">
        <el-tag v-if="post.status === 'resolved'" type="success" effect="light" class="rounded-full"><el-icon><Select /></el-icon> 已解决</el-tag>
        <div class="mt-auto flex gap-4 text-slate-400 text-xs">
          <span class="flex items-center gap-1" title="评论"><el-icon class="text-base"><ChatDotRound /></el-icon> {{ post.comment_count || 0 }}</span>
          <span class="flex items-center gap-1" title="浏览"><el-icon class="text-base"><View /></el-icon> {{ post.view_count || 0 }}</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { CaretTop, CaretBottom, ChatDotRound, View, ArrowUpBold, StarFilled, Select } from '@element-plus/icons-vue'

defineProps<{
  post: any
}>()
</script>
