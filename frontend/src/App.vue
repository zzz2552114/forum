<template>
  <el-config-provider>
    <router-view />
  </el-config-provider>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(async () => {
  // Try to load user profile on startup if we have a token
  if (authStore.isAuthenticated) {
    await authStore.fetchMe()
  }
})
</script>
