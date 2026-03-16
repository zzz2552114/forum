<template>
  <div class="min-h-screen bg-slate-50 pb-12 font-sans">
    <HomeHeader />

    <main class="max-w-4xl mx-auto pt-8 px-4 space-y-8">
      <!-- Page Header -->
      <div class="flex items-center gap-4">
        <button @click="$router.back()" class="flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors">
          <el-icon :size="20"><ArrowLeft /></el-icon>
          <span class="font-medium">返回</span>
        </button>
        <h1 class="text-2xl font-bold text-slate-800">我的 AI</h1>
      </div>

      <!-- AI Settings Section -->
      <el-card shadow="never" class="border-none rounded-3xl shadow-sm">
        <template #header>
          <div class="px-2 flex items-center gap-2">
            <el-icon class="text-xl text-blue-600"><HelpFilled /></el-icon>
            <h3 class="text-xl font-bold text-slate-800">AI 调用设置</h3>
          </div>
        </template>
        <div class="p-2">
          <p class="text-sm text-slate-500 mb-6">配置阿里云百炼 API Key 以在评论区使用 @ai 提问功能。</p>
          <el-form :model="aiForm" label-position="top" @submit.prevent>
            <el-form-item label="阿里云百炼 Dashscope API Key">
              <el-input
                v-model="aiForm.ai_api_key"
                type="password"
                show-password
                placeholder="sk-xxxxxxxxxxxxxxxx"
                class="max-w-md"
              ></el-input>
            </el-form-item>
            <el-form-item label="AI 回复模型">
              <el-select v-model="aiForm.ai_model" placeholder="请选择模型" class="max-w-md">
                <el-option label="Qwen Plus (推荐)" value="qwen-plus"></el-option>
                <el-option label="Qwen Max" value="qwen-max"></el-option>
                <el-option label="Qwen Turbo" value="qwen-turbo"></el-option>
                <el-option label="DeepSeek V3" value="deepseek-v3"></el-option>
                <el-option label="DeepSeek R1" value="deepseek-r1"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="isSavingAi" @click="saveAiSettings" round>保存 AI 设置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-card>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ArrowLeft, HelpFilled } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import HomeHeader from '@/components/HomeHeader.vue'

const authStore = useAuthStore()

const isSavingAi = ref(false)
const aiForm = reactive({
  ai_api_key: '',
  ai_model: 'qwen-plus'
})

const saveAiSettings = async () => {
  isSavingAi.value = true
  try {
    await request.patch('/me/profile', {
      ai_api_key: aiForm.ai_api_key,
      ai_model: aiForm.ai_model
    })
    ElMessage.success('已保存 AI 设置')
    authStore.fetchMe()
  } catch (error) {
    ElMessage.error('保存失败，请检查网络')
  } finally {
    isSavingAi.value = false
  }
}

onMounted(() => {
  if (authStore.user) {
    aiForm.ai_api_key = authStore.user.ai_api_key || ''
    aiForm.ai_model = authStore.user.ai_model || 'qwen-plus'
  }
})
</script>
