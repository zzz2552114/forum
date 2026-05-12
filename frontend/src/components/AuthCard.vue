<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLogin = ref(true)
const form = ref({
  account: '', // This will be used as username
  password: '',
  remember: false
})
const loading = ref(false)
const errorMsg = ref('')

const handleSubmit = async () => {
  if (!form.value.account || !form.value.password) {
    errorMsg.value = '请输入账号和密码'
    return
  }
  
  loading.value = true
  errorMsg.value = ''
  
  try {
    if (isLogin.value) {
      await authStore.login({
        username: form.value.account,
        password: form.value.password
      })
    } else {
      await authStore.register({
        username: form.value.account,
        email: form.value.account + '@test.com', // fake email for quick register
        password: form.value.password
      })
      // auto login after register
      await authStore.login({
        username: form.value.account,
        password: form.value.password
      })
    }
    
    // Jump to dashboard
    router.push('/home')
  } catch (err: any) {
    console.error(err)
    errorMsg.value = err.response?.data?.detail || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}

const switchMode = (mode: boolean) => {
  isLogin.value = mode
  errorMsg.value = ''
  form.value.password = ''
}

const handleGuestBrowse = async () => {
  await authStore.enterGuestSession()
  router.push('/home')
}
</script>

<template>
  <div class="auth-card w-[360px] p-8 flex flex-col relative overflow-hidden">
    <!-- Glow effect behind the card -->
    <div class="absolute -top-20 -right-20 w-40 h-40 bg-[var(--c-gold)] opacity-20 blur-3xl rounded-full"></div>

    <h2 class="text-2xl font-serif font-bold text-[var(--c-navy)] mb-6 tracking-wide">欢迎回来</h2>
    
    <div class="flex gap-x-6 mb-6 border-b border-[var(--c-navy)] border-opacity-10 pb-2">
      <button 
        class="text-base font-medium transition-all relative"
        :class="isLogin ? 'text-[var(--c-navy)]' : 'text-[var(--c-navy)] opacity-50 hover:opacity-80'"
        @click="switchMode(true)"
      >
        登录
        <div v-if="isLogin" class="absolute -bottom-[9px] left-0 right-0 h-[2px] bg-[var(--c-gold)] rounded-t-sm"></div>
      </button>
      <button 
        class="text-base font-medium transition-all relative"
        :class="!isLogin ? 'text-[var(--c-navy)]' : 'text-[var(--c-navy)] opacity-50 hover:opacity-80'"
        @click="switchMode(false)"
      >
        注册
        <div v-if="!isLogin" class="absolute -bottom-[9px] left-0 right-0 h-[2px] bg-[var(--c-gold)] rounded-t-sm"></div>
      </button>
    </div>

    <!-- Error message display -->
    <div v-if="errorMsg" class="mb-4 text-sm text-[var(--c-danger)] font-medium bg-[var(--c-danger)]/10 px-3 py-2 rounded-lg">
      {{ errorMsg }}
    </div>

    <form class="flex flex-col gap-y-4" @submit.prevent="handleSubmit">
      <div class="space-y-1">
        <label class="text-sm text-[var(--c-navy)] opacity-80 font-medium">学号或用户名</label>
        <input 
          v-model="form.account" 
          type="text" 
          required
          class="w-full bg-white bg-opacity-60 border border-[var(--c-navy)] border-opacity-10 rounded-[var(--radius-btn)] px-4 py-2.5 text-[var(--c-navy)] focus:outline-none focus:border-[var(--c-gold)] focus:bg-white transition-all"
        />
      </div>
      <div class="space-y-1">
        <label class="text-sm text-[var(--c-navy)] opacity-80 font-medium">密码</label>
        <input 
          v-model="form.password" 
          type="password" 
          required
          class="w-full bg-white bg-opacity-60 border border-[var(--c-navy)] border-opacity-10 rounded-[var(--radius-btn)] px-4 py-2.5 text-[var(--c-navy)] focus:outline-none focus:border-[var(--c-gold)] focus:bg-white transition-all"
        />
      </div>

      <div class="flex items-center justify-between mt-2 mb-2">
        <label class="flex items-center gap-x-2 text-sm text-[var(--c-navy)] opacity-70 cursor-pointer">
          <input v-model="form.remember" type="checkbox" class="rounded border-[var(--c-navy)] text-[var(--c-indigo)] focus:ring-[var(--c-gold)]" />
          记住我
        </label>
        <a href="#" class="text-sm text-[var(--c-gold)] hover:opacity-80 transition-opacity">忘记密码？</a>
      </div>

      <button 
        type="submit" 
        :disabled="loading"
        class="w-full bg-[var(--c-indigo)] text-[var(--c-fog)] rounded-[var(--radius-btn)] py-3 font-medium hover:bg-opacity-90 shadow-lg shadow-[var(--c-indigo)]/20 transition-all disabled:opacity-50 flex justify-center items-center"
      >
        <span v-if="loading" class="mr-2 inline-block w-4 h-4 border-2 border-[var(--c-fog)] border-t-transparent rounded-full animate-spin"></span>
        {{ isLogin ? '进入论坛' : '注册并进入' }}
      </button>
      <button 
        type="button" 
        @click="handleGuestBrowse"
        class="w-full bg-transparent text-[var(--c-navy)] opacity-70 border border-[var(--c-navy)] border-opacity-20 rounded-[var(--radius-btn)] py-3 font-medium hover:bg-white hover:opacity-100 transition-all mt-2"
      >
        游客浏览
      </button>
    </form>
  </div>
</template>

<style scoped>
.auth-card {
  min-height: 440px;
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(24px);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-overlay-dark);
  border: 1px solid rgba(255, 255, 255, 0.4);
}
</style>
