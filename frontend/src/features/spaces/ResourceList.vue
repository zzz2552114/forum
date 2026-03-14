<script setup lang="ts">
import { Document } from '@element-plus/icons-vue'

defineProps<{
  resources: any[]
  activeSpaceName: string
}>()

defineEmits(['download'])
</script>

<template>
  <template v-if="resources.length > 0">
    <div class="flex items-center justify-between mb-4 px-1">
      <span class="text-sm text-[var(--c-navy)]/50 font-medium">共 {{ resources.length }} 份资料</span>
    </div>
    <div class="space-y-3">
      <div
        v-for="mat in resources"
        :key="mat.id"
        class="group flex items-center justify-between p-4 bg-white rounded-2xl hover:bg-[var(--c-fog)] shadow-sm transition-colors border border-transparent hover:border-[var(--c-navy)]/5 cursor-pointer text-left"
      >
        <div class="flex items-start gap-x-4 overflow-hidden pr-4 max-w-[80%]">
          <div class="w-12 h-12 bg-white rounded-[12px] flex items-center justify-center text-[#E85D04] shrink-0 border border-[var(--c-navy)]/5 shadow-sm">
            <el-icon :size="24"><Document /></el-icon>
          </div>
          <div class="min-w-0">
            <h4 class="font-medium text-lg text-[var(--c-navy)] mb-1 truncate group-hover:text-[var(--c-indigo)] transition-colors" :title="mat.title">
              {{ mat.title }}
            </h4>
            <div class="flex items-center gap-x-4 text-sm text-[var(--c-navy)]/50">
              <span class="flex items-center gap-x-1 font-medium">
                <span class="w-1.5 h-1.5 rounded-full bg-[var(--c-gold)] opacity-80 inline-block"></span>
                {{ activeSpaceName || '未知空间' }}
              </span>
              <span>{{ mat.resource_type === 'past_exam' ? '往年试卷' : mat.resource_type === 'notes' ? '课堂笔记' : mat.resource_type === 'solution' ? '习题答案' : mat.resource_type === 'policy' ? '政策文件' : '其他资料' }}</span>
              <span>最后更新：{{ new Date(mat.created_at).toLocaleDateString() }}</span>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-x-4 pl-4 border-l border-[var(--c-navy)]/5 shrink-0">
          <div class="text-[var(--c-navy)]/40 text-sm hidden lg:block">
            {{ mat.download_count }} 次下载
          </div>
          <button
            @click.stop="$emit('download', mat)"
            class="w-10 h-10 rounded-[12px] flex items-center justify-center bg-white text-[var(--c-indigo)] border border-[var(--c-navy)]/10 hover:border-[var(--c-indigo)] group-hover:bg-[var(--c-indigo)] group-hover:text-white transition-all shadow-sm"
          >
            <el-icon :size="20"><Document /></el-icon>
          </button>
        </div>
      </div>
    </div>
  </template>
  <template v-else>
    <div class="text-center text-[var(--c-navy)]/40 mt-10">
      暂无资料
    </div>
  </template>
</template>
