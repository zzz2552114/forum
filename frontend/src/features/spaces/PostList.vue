<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowUpBold, StarFilled, View, CaretTop, ChatDotRound } from '@element-plus/icons-vue'

const props = defineProps<{
  posts: any[]
}>()

defineEmits(['read'])

const postSortMethod = ref('created_at')
const sortedPosts = computed(() => {
  const sorted = [...props.posts]
  if (postSortMethod.value === 'created_at') {
    sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  } else if (postSortMethod.value === 'updated_at') {
    sorted.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
  } else if (postSortMethod.value === 'like_count') {
    sorted.sort((a, b) => (b.like_count || 0) - (a.like_count || 0))
  }
  return sorted
})
</script>

<template>
  <template v-if="sortedPosts.length > 0">
    <div class="flex items-center justify-between mb-4 px-1">
      <span class="text-sm text-[var(--c-navy)]/50 font-medium">共 {{ sortedPosts.length }} 篇帖子</span>
      <el-select v-model="postSortMethod" size="small" class="w-28 shadow-sm">
        <el-option label="最新发布" value="created_at" />
        <el-option label="最新回复" value="updated_at" />
        <el-option label="最多点赞" value="like_count" />
      </el-select>
    </div>
    <div class="space-y-4">
      <div
        v-for="post in sortedPosts"
        :key="post.id"
        class="bg-white p-5 rounded-2xl shadow-sm border border-[var(--c-navy)]/5 hover:border-[var(--c-gold)]/30 transition-colors cursor-pointer group"
        @click="$emit('read', post.id)"
      >
        <div class="flex items-center gap-x-3 mb-3">
          <div class="w-10 h-10 rounded-full bg-[var(--c-fog)] overflow-hidden shrink-0 flex items-center justify-center font-bold text-[var(--c-navy)]">
            {{ post.author?.nickname?.[0] || post.author?.username?.[0] || 'U' }}
          </div>
          <div>
            <div class="font-medium text-[var(--c-navy)] text-sm flex gap-x-2 items-center">
              {{ post.author?.nickname || post.author?.username || `用户 ${post.author_id}` }}
              <span v-if="post.author?.trust_level" class="text-[10px] px-1.5 py-0.5 rounded-full bg-[var(--c-gold)]/20 text-[var(--c-gold)] font-bold">Lv.{{ post.author?.trust_level }}</span>
            </div>
            <div class="text-xs text-[var(--c-navy)]/50 mt-0.5">
              {{ new Date(post.created_at).toLocaleString() }}
            </div>
          </div>
        </div>
        <h3 class="font-medium text-[var(--c-navy)] text-lg mb-2 group-hover:text-[var(--c-indigo)]">
          <el-icon v-if="post.is_pinned" class="text-orange-500 mr-1 align-middle"><ArrowUpBold /></el-icon>
          <el-icon v-if="post.is_featured" class="text-red-500 mr-1 align-middle"><StarFilled /></el-icon>
          {{ post.title }}
        </h3>
        <p class="text-[var(--c-navy)]/70 text-sm line-clamp-2 leading-relaxed">
          {{ post.summary || post.content }}
        </p>
        <div class="mt-4 flex gap-x-4 text-xs text-[var(--c-navy)]/40 font-medium">
          <span class="flex items-center gap-1"><el-icon><View /></el-icon>{{ post.view_count || 0 }}</span>
          <span class="flex items-center gap-1"><el-icon><CaretTop /></el-icon>{{ post.like_count || 0 }}</span>
          <span class="flex items-center gap-1"><el-icon><ChatDotRound /></el-icon>{{ post.comment_count || 0 }}</span>
        </div>
      </div>
    </div>
  </template>
  <template v-else>
    <div class="text-center text-[var(--c-navy)]/40 mt-10">
      暂无帖子
    </div>
  </template>
</template>
