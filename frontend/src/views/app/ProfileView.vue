<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import HomeHeader from '@/components/HomeHeader.vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'

const router = useRouter()
const authStore = useAuthStore()

const userForm = reactive({
  username: '',
  bio: '',
})

const avatarUrl = ref('')
const fileInput = ref<HTMLInputElement | null>(null)
const isSaving = ref(false)

onMounted(() => {
  if (authStore.user) {
    userForm.username = authStore.user.username || ''
    userForm.bio = authStore.user.bio || ''
    avatarUrl.value = authStore.user.avatar_url || ''
  }
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleAvatarChange = async (e: Event) => {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    const res: any = await request.post('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    avatarUrl.value = res.url || res.data?.url || ''
    ElMessage.success('头像上传成功')
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.message || '上传失败')
  }
}

const handleUpdate = async () => {
  isSaving.value = true
  try {
    const payload: Record<string, string> = {}
    if (userForm.username && userForm.username !== authStore.user?.username) {
      payload.username = userForm.username
    }
    if (userForm.bio !== (authStore.user?.bio || '')) {
      payload.bio = userForm.bio
    }
    if (avatarUrl.value && avatarUrl.value !== (authStore.user?.avatar_url || '')) {
      payload.avatar_url = avatarUrl.value
    }

    if (Object.keys(payload).length === 0) {
      ElMessage.info('没有需要修改的内容')
      return
    }

    await request.patch('/me/profile', payload)
    ElMessage.success('个人资料已更新')
    await authStore.fetchMe()  // refresh store so header updates
    router.push('/me/overview')
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.message || '保存失败')
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-[var(--c-fog)] flex flex-col h-screen overflow-hidden">
    <!-- Header -->
    <div class="shrink-0">
      <HomeHeader />
    </div>

    <div class="flex-1 overflow-y-auto flex justify-center py-10 px-4 custom-scrollbar">
      <div class="w-full max-w-2xl bg-white rounded-2xl shadow-sm border border-[var(--c-navy)]/5 p-8 flex flex-col items-center h-fit">
        <!-- Back Button -->
        <div class="w-full flex justify-start mb-6">
           <button @click="router.back()" class="flex items-center gap-2 text-[var(--c-navy)]/60 hover:text-[var(--c-navy)] transition-colors">
              <el-icon :size="20"><ArrowLeft /></el-icon>
              <span class="font-medium">返回</span>
            </button>
        </div>

        <h1 class="text-2xl font-bold text-[var(--c-navy)] mb-8">个人空间</h1>

        <!-- Avatar Upload -->
        <div class="mb-8 flex flex-col items-center">
          <div
            class="w-24 h-24 rounded-full bg-[var(--c-fog)] border-2 border-[var(--c-gold)] border-dashed flex items-center justify-center text-[var(--c-navy)]/40 mb-4 cursor-pointer hover:bg-[var(--c-navy)]/5 transition-colors overflow-hidden"
            @click="triggerFileInput"
          >
            <img v-if="avatarUrl" :src="avatarUrl" class="w-full h-full object-cover" />
            <span v-else>点击上传头像</span>
          </div>
          <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="handleAvatarChange" />
        </div>

        <div class="w-full max-w-sm space-y-6">
          <div>
            <label class="block text-sm font-medium text-[var(--c-navy)] mb-2">修改用户名</label>
            <input v-model="userForm.username" type="text" placeholder="输入新的用户名" class="w-full bg-[var(--c-fog)] border border-transparent rounded-lg px-4 py-2 text-[var(--c-navy)] focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)] focus:bg-white transition-all">
          </div>
          <div>
            <label class="block text-sm font-medium text-[var(--c-navy)] mb-2">添加个人简介</label>
            <textarea v-model="userForm.bio" placeholder="介绍一下你自己..." rows="3" class="w-full bg-[var(--c-fog)] border border-transparent rounded-lg px-4 py-2 text-[var(--c-navy)] focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)] focus:bg-white transition-all resize-none"></textarea>
          </div>

          <div class="pt-4 flex justify-between gap-4">
             <button @click="handleUpdate" :disabled="isSaving" class="flex-1 py-2 rounded-lg bg-[var(--c-indigo)] text-white hover:bg-opacity-90 font-medium transition-colors disabled:opacity-50">
               {{ isSaving ? '保存中...' : '保存修改' }}
             </button>
             <button @click="router.push('/me/overview')" class="py-2 px-6 rounded-lg bg-[var(--c-fog)] text-[var(--c-navy)] hover:bg-gray-200 font-medium transition-colors">取消</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
