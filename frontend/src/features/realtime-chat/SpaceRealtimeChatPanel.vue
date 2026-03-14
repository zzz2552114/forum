<template>
  <section class="flex flex-col h-full bg-white rounded-[var(--radius-card)] border border-[var(--c-navy)]/10 shadow-[var(--shadow-card-light)] p-5">
    <header class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h3 class="text-lg font-serif font-bold text-[var(--c-navy)]">即时聊天区</h3>
        <p class="text-sm text-[var(--c-navy)]/55">空间 {{ spaceId }} · 分区 {{ sectionId }}</p>
      </div>
      <div class="text-sm text-[var(--c-navy)]/70 flex items-center gap-4">
        <span>在线 {{ onlineCount }}</span>
        <span :class="statusClass">{{ statusText }}</span>
      </div>
    </header>

    <div class="flex-1 overflow-y-auto rounded-xl border border-[var(--c-navy)]/10 bg-[var(--c-fog)] p-3 space-y-2 mt-4 mb-4 custom-scrollbar">
      <div
        v-for="(event, idx) in messages"
        :key="`${event.event_id}-${idx}`"
        class="text-sm"
        :class="event.type === 'chat' ? 'text-[var(--c-navy)]' : 'text-[var(--c-navy)]/65'"
      >
        <template v-if="event.type === 'chat'">
          [{{ event.display_time }}] <strong>{{ event.username || '匿名用户' }}</strong>: {{ event.content }}
        </template>
        <template v-else>
          [{{ event.display_time }}] {{ event.message }}
        </template>
      </div>
      <p v-if="messages.length === 0" class="text-sm text-[var(--c-navy)]/45">暂无消息。</p>
    </div>

    <div class="shrink-0 space-y-2">
      <div class="flex gap-3">
        <input
          v-model="draft"
          class="flex-1 h-11 rounded-[var(--radius-btn)] border border-[var(--c-navy)]/15 px-4 bg-white text-[var(--c-navy)] focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)]"
          placeholder="输入消息，支持 @用户名"
          :disabled="!isConnected"
          @input="handleDraftInput"
          @keyup.enter="handleSend"
        />
        <button
          class="h-11 px-5 rounded-[var(--radius-btn)] bg-[var(--c-indigo)] text-white font-medium hover:bg-[var(--c-navy)] transition-colors disabled:opacity-50"
          :disabled="!isConnected"
          @click="handleSend"
        >
          发送
        </button>
      </div>

      <div
        v-if="mentionCandidates.length > 0"
        class="rounded-xl border border-[var(--c-navy)]/10 bg-white p-2 flex flex-wrap gap-2"
      >
        <button
          v-for="candidate in mentionCandidates"
          :key="candidate"
          class="px-3 py-1.5 text-xs rounded-full bg-[var(--c-fog)] text-[var(--c-navy)]/80 hover:bg-[var(--c-indigo)] hover:text-white transition-colors"
          @click="applyMention(candidate)"
        >
          @{{ candidate }}
        </button>
      </div>
    </div>

    <p v-if="errorMessage" class="text-sm text-[var(--c-danger)]">{{ errorMessage }}</p>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { useSpaceRealtimeChat } from './useSpaceRealtimeChat'

const props = withDefaults(defineProps<{
  spaceId: number
  sectionId: number
  username: string
  token?: string
  endpoint?: string
}>(), {
  token: '',
  endpoint: '/ws/chat',
})

const draft = ref('')
const mentionQuery = ref('')

const {
  connect,
  connectionState,
  errorMessage,
  isConnected,
  messages,
  onlineCount,
  sendMessage,
} = useSpaceRealtimeChat({
  spaceId: props.spaceId,
  sectionId: props.sectionId,
  username: props.username,
  token: props.token,
  endpoint: props.endpoint,
})

const participantUsernames = computed(() => {
  const seen = new Set<string>()
  const list: string[] = []

  if (props.username.trim()) {
    seen.add(props.username)
    list.push(props.username)
  }

  for (const event of messages.value) {
    const username = (event.username || '').trim()
    if (!username || seen.has(username)) {
      continue
    }
    seen.add(username)
    list.push(username)
  }

  return list
})

const mentionCandidates = computed(() => {
  const query = mentionQuery.value.trim().toLowerCase()
  if (!query && draft.value.lastIndexOf('@') < 0) {
    return []
  }

  return participantUsernames.value
    .filter((name) => name.toLowerCase().includes(query))
    .slice(0, 8)
})

const statusText = computed(() => {
  if (connectionState.value === 'connected') {
    return '已连接'
  }
  if (connectionState.value === 'connecting') {
    return '连接中'
  }
  if (connectionState.value === 'reconnecting') {
    return '重连中'
  }
  return '离线'
})

const statusClass = computed(() => {
  if (connectionState.value === 'connected') {
    return 'text-[var(--c-success)]'
  }
  if (connectionState.value === 'reconnecting' || connectionState.value === 'connecting') {
    return 'text-[var(--c-gold)]'
  }
  return 'text-[var(--c-danger)]'
})

const handleDraftInput = (): void => {
  const cursorText = draft.value
  const atIndex = cursorText.lastIndexOf('@')
  if (atIndex < 0) {
    mentionQuery.value = ''
    return
  }

  const mentionText = cursorText.slice(atIndex + 1)
  if (/\s/.test(mentionText)) {
    mentionQuery.value = ''
    return
  }
  mentionQuery.value = mentionText
}

const applyMention = (username: string): void => {
  const atIndex = draft.value.lastIndexOf('@')
  if (atIndex < 0) {
    draft.value = `${draft.value.trim()} @${username} `
  } else {
    draft.value = `${draft.value.slice(0, atIndex)}@${username} `
  }
  mentionQuery.value = ''
}

const handleSend = (): void => {
  const ok = sendMessage(draft.value)
  if (ok) {
    draft.value = ''
    mentionQuery.value = ''
  }
}

onMounted(() => {
  void connect()
})
</script>