<template>
  <article class="rounded-[var(--radius-card)] border border-[var(--c-navy)]/10 bg-white p-4 shadow-sm space-y-2">
    <header class="flex items-center justify-between gap-3">
      <h4 class="font-serif text-base font-bold text-[var(--c-navy)]">AI 任务状态</h4>
      <span class="text-xs px-2 py-1 rounded-full" :class="statusClass">{{ statusText }}</span>
    </header>

    <p class="text-sm text-[var(--c-navy)]/70 line-clamp-2">{{ prompt }}</p>

    <p v-if="task.result" class="text-sm text-[var(--c-success)] whitespace-pre-wrap">{{ task.result }}</p>
    <p v-else-if="task.error" class="text-sm text-[var(--c-danger)]">{{ task.error }}</p>

    <footer class="text-xs text-[var(--c-navy)]/45">
      任务 ID: {{ task.id }}
    </footer>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { AiMentionTask } from './types'

const props = defineProps<{
  task: AiMentionTask
}>()

const prompt = computed(() => props.task.prompt || '未提供任务描述')

const statusText = computed(() => {
  if (props.task.status === 'queued') return '排队中'
  if (props.task.status === 'running') return '执行中'
  if (props.task.status === 'succeeded') return '已完成'
  if (props.task.status === 'timeout') return '超时'
  return '失败'
})

const statusClass = computed(() => {
  if (props.task.status === 'queued') return 'bg-[var(--c-fog)] text-[var(--c-navy)]/70'
  if (props.task.status === 'running') return 'bg-[var(--c-gold)]/15 text-[var(--c-gold)]'
  if (props.task.status === 'succeeded') return 'bg-[var(--c-success)]/15 text-[var(--c-success)]'
  if (props.task.status === 'timeout') return 'bg-[var(--c-danger)]/10 text-[var(--c-danger)]'
  return 'bg-[var(--c-danger)]/15 text-[var(--c-danger)]'
})
</script>
