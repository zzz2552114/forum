<template>
  <div class="flex items-center justify-center min-h-[70vh]">
    <el-card class="w-full max-w-md shadow-lg rounded-xl border-none">
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-slate-800 tracking-tight">Login</h2>
        <p class="text-slate-500 text-sm mt-2">Welcome back to the forum</p>
      </div>

      <el-form :model="form" @submit.prevent="handleLogin" label-position="top">
        <el-form-item label="Username">
          <el-input v-model="form.username" size="large" placeholder="Enter your username" />
        </el-form-item>
        
        <el-form-item label="Password">
          <el-input v-model="form.password" type="password" size="large" placeholder="Enter your password" show-password />
        </el-form-item>

        <div class="mt-6">
          <el-button type="primary" size="large" class="w-full fw-bold bg-blue-600 hover:bg-blue-700 border-none" @click="handleLogin" :loading="loading">
            Sign In
          </el-button>
        </div>
      </el-form>
      
      <div class="mt-6 text-center text-sm text-slate-500">
        Don't have an account? <router-link to="/register" class="text-blue-600 hover:underline">Sign up</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const form = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  loading.value = true
  try {
    await authStore.login(form.value)
    router.push('/app/feed')
  } catch (error) {
    // Handled by axios interceptor ideally
  } finally {
    loading.value = false
  }
}
</script>
