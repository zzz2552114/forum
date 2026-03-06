<template>
  <div class="flex items-center justify-center min-h-[70vh]">
    <el-card class="w-full max-w-md shadow-lg rounded-xl border-none">
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-slate-800 tracking-tight">Login</h2>
        <p class="text-slate-500 text-sm mt-2">Welcome back to the forum</p>
      </div>

      <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleLogin" label-position="top">
        <el-form-item label="Username" prop="username">
          <el-input v-model="form.username" size="large" placeholder="Enter your username" />
        </el-form-item>
        
        <el-form-item label="Password" prop="password">
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
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const loading = ref(false)
const formRef = ref()

const form = ref({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: 'Please enter username', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.login(form.value)
        ElMessage.success('Login successful')
        const redirect = route.query.redirect as string || '/app/feed'
        router.push(redirect)
      } catch (error) {
        // Handled by axios interceptor
      } finally {
        loading.value = false
      }
    }
  })
}
</script>
