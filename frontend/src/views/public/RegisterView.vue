<template>
  <div class="flex items-center justify-center min-h-[70vh]">
    <el-card class="w-full max-w-md shadow-lg rounded-xl border-none">
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-slate-800 tracking-tight">Register</h2>
        <p class="text-slate-500 text-sm mt-2">Join our academic community</p>
      </div>

      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" @keyup.enter="handleRegister">
        <el-form-item label="Username" prop="username">
          <el-input v-model="form.username" size="large" placeholder="Choose a username" />
        </el-form-item>
        
        <el-form-item label="Email" prop="email">
          <el-input v-model="form.email" size="large" placeholder="Enter your email" />
        </el-form-item>

        <el-form-item label="Password" prop="password">
          <el-input v-model="form.password" type="password" size="large" placeholder="Create a password" show-password />
        </el-form-item>

        <div class="mt-6">
          <el-button type="primary" native-type="button" size="large" class="w-full fw-bold bg-blue-600 hover:bg-blue-700 border-none" @click="handleRegister" :loading="loading">
            Create Account
          </el-button>
        </div>
      </el-form>
      
      <div class="mt-6 text-center text-sm text-slate-500">
        Already have an account? <router-link to="/login" class="text-blue-600 hover:underline">Sign in</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const formRef = ref()

const form = ref({
  username: '',
  email: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: 'Please enter username', trigger: 'blur' }],
  email: [
    { required: true, message: 'Please enter email', trigger: 'blur' },
    { type: 'email', message: 'Please enter valid email', trigger: 'blur' }
  ],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }]
}

const handleRegister = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return // 校验不通过
  }
  loading.value = true
  try {
    await authStore.register(form.value)
    ElMessage.success('注册成功，请登录')
    await router.push('/login')
  } catch {
    // error 已由 axios interceptor 显示
  } finally {
    loading.value = false
  }
}
</script>

