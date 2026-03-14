<template>
  <section class="max-w-3xl mx-auto bg-white rounded-2xl border border-slate-200 p-6 space-y-4">
    <header class="space-y-2">
      <h2 class="text-xl font-bold text-slate-800">Realtime Chat Demo</h2>
      <p class="text-sm text-slate-500">Standalone websocket demo, no business DB binding.</p>
    </header>

    <div class="grid gap-3 md:grid-cols-[1fr_1fr_auto]">
      <el-input v-model="usernameInput" placeholder="Username" :disabled="isConnected" />
      <el-input v-model="wsEndpoint" placeholder="WS endpoint" :disabled="isConnected" />
      <el-button v-if="!isConnected" type="primary" @click="handleConnect">Connect</el-button>
      <el-button v-else type="danger" plain @click="disconnect">Disconnect</el-button>
    </div>

    <div class="text-sm text-slate-600">
      <span class="font-medium">Online:</span> {{ onlineCount }}
      <span class="ml-4 font-medium">Status:</span>
      <span :class="isConnected ? 'text-emerald-600' : isConnecting ? 'text-amber-600' : 'text-slate-500'">
        {{ isConnected ? 'connected' : isConnecting ? 'connecting' : 'offline' }}
      </span>
      <span v-if="errorMessage" class="ml-4 text-red-600">{{ errorMessage }}</span>
    </div>

    <div class="h-72 overflow-y-auto rounded-xl border border-slate-200 bg-slate-50 p-3 space-y-2">
      <div
        v-for="(message, idx) in messages"
        :key="`${message.timestamp}-${idx}`"
        :class="message.type === 'system' ? 'text-slate-500 text-sm' : 'text-slate-800 text-sm'"
      >
        <template v-if="message.type === 'system'">
          [{{ message.display_time }}] System: {{ message.content }}
        </template>
        <template v-else>
          [{{ message.display_time }}] {{ message.username || 'anonymous' }}: {{ message.content }}
        </template>
      </div>
      <p v-if="messages.length === 0" class="text-sm text-slate-400">No messages yet.</p>
    </div>

    <div class="grid gap-3 md:grid-cols-[1fr_auto]">
      <el-input
        v-model="messageInput"
        placeholder="Say something..."
        :disabled="!isConnected"
        @keyup.enter="handleSend"
      />
      <el-button type="primary" :disabled="!isConnected" @click="handleSend">Send</el-button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import { useRealtimeChat } from './useRealtimeChat'

const usernameInput = ref('')
const wsEndpoint = ref('/ws/chat')
const messageInput = ref('')

const {
  connect,
  disconnect,
  errorMessage,
  isConnected,
  isConnecting,
  messages,
  onlineCount,
  sendMessage,
} = useRealtimeChat()

const handleConnect = (): void => {
  connect(usernameInput.value, wsEndpoint.value)
}

const handleSend = (): void => {
  const sent = sendMessage(messageInput.value)
  if (sent) {
    messageInput.value = ''
  }
}
</script>
