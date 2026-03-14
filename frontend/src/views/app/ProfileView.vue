<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import HomeHeader from '@/components/HomeHeader.vue'
import { ElMessage } from 'element-plus'

const router = useRouter()

const userForm = ref({
  username: '',
  nickname: '',
})

const handleUpdate = () => {
  ElMessage.info('研发中...')
}

const handleUploadAvatar = () => {
  ElMessage.info('研发中...')
}
</script>

<template>
  <div class="min-h-screen bg-[var(--c-fog)] flex flex-col h-screen overflow-hidden">
    <!-- Header -->
    <div class="shrink-0">
      <HomeHeader />
    </div>

    <div class="flex-1 flex overflow-hidden justify-center py-10">
      <div class="w-full max-w-2xl bg-white rounded-2xl shadow-sm border border-[var(--c-navy)]/5 p-8 flex flex-col items-center">
        <!-- Back Button -->
        <div class="w-full flex justify-start mb-6">
           <button @click="router.back()" class="flex items-center gap-2 text-[var(--c-navy)]/60 hover:text-[var(--c-navy)] transition-colors">
              <el-icon :size="20"><ArrowLeft /></el-icon>
              <span class="font-medium">返回</span>
            </button>
        </div>

        <h1 class="text-2xl font-bold text-[var(--c-navy)] mb-8">个人空间</h1>

        <!-- Mock Avatar Upload -->
        <div class="mb-8 flex flex-col items-center">
          <div class="w-24 h-24 rounded-full bg-[var(--c-fog)] border-2 border-[var(--c-gold)] border-dashed flex items-center justify-center text-[var(--c-navy)]/40 mb-4 cursor-pointer hover:bg-[var(--c-navy)]/5 transition-colors" @click="handleUploadAvatar">
            <span>点击上传头像</span>
          </div>
        </div>

        <div class="w-full max-w-sm space-y-6">
          <div>
            <label class="block text-sm font-medium text-[var(--c-navy)] mb-2">修改用户名</label>
            <input v-model="userForm.username" type="text" placeholder="输入新的用户名" class="w-full bg-[var(--c-fog)] border border-transparent rounded-lg px-4 py-2 text-[var(--c-navy)] focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)] focus:bg-white transition-all">
          </div>
          <div>
            <label class="block text-sm font-medium text-[var(--c-navy)] mb-2">修改昵称</label>
            <input v-model="userForm.nickname" type="text" placeholder="输入新的昵称" class="w-full bg-[var(--c-fog)] border border-transparent rounded-lg px-4 py-2 text-[var(--c-navy)] focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)] focus:bg-white transition-all">
          </div>

          <div class="pt-4 flex justify-between gap-4">
             <button @click="handleUpdate" class="flex-1 py-2 rounded-lg bg-[var(--c-indigo)] text-white hover:bg-opacity-90 font-medium transition-colors">保存修改</button>
             <button @click="router.push('/home')" class="py-2 px-6 rounded-lg bg-[var(--c-fog)] text-[var(--c-navy)] hover:bg-gray-200 font-medium transition-colors">取消</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
