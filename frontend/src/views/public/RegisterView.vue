<template>
  <div class="flex items-center justify-center min-h-[70vh]">
    <el-card class="w-full max-w-md shadow-lg rounded-xl border-none">
      <div class="text-center mb-8">
        <h2 class="text-2xl font-bold text-slate-800 tracking-tight">Register</h2>
        <p class="text-slate-500 text-sm mt-2">Join our academic community</p>
      </div>

      <el-form :model="form" @submit.prevent="handleRegister" label-position="top">
        <el-form-item label="Username">
          <el-input v-model="form.username" size="large" placeholder="Choose a username" />
        </el-form-item>
        
        <el-form-item label="Email">
          <el-input v-model="form.email" size="large" placeholder="Enter your email" />
        </el-form-item>

        <el-form-item label="Password">
          <el-input v-model="form.password" type="password" size="large" placeholder="Create a password" show-password />
        </el-form-item>

        <div class="mt-6">
          <el-button type="primary" size="large" class="w-full fw-bold bg-blue-600 hover:bg-blue-700 border-none" @click="handleRegister" :loading="loading">
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

const router = useRouter()
const loading = ref(false)

const form = ref({
  username: '',
  email: '',
  password: ''
})

const handleRegister = async () => {
  loading.value = true
  // Mock validation & transition
  setTimeout(() => {
    loading.value = false
    router.push('/login')
  }, 1000)
}
</script>
