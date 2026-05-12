<script setup lang="ts">
import { ref } from 'vue'
import { ArrowLeft, Document, Loading } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  visible: boolean
  spaceId: number | null
  spaceName: string
}>()

const emit = defineEmits(['update:visible', 'success'])

const isSubmittingPost = ref(false)
const newPostForm = ref({ title: '', content: '' })
const isTradePost = ref(false)
const isUploadingAttachment = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const handleAttachmentUpload = async (e: Event) => {
  const target = e.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return
  const file = target.files[0]
  if (!file) return
  
  isUploadingAttachment.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('biz_type', 'attachment')

    const res: any = await request.post('/files/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    const isImage = file.type.startsWith('image/')
    const mdLink = isImage ? `\n![${file.name}](/uploads/${res.filename})\n` : `\n[${file.name}](/uploads/${res.filename})\n`
    newPostForm.value.content += mdLink
    ElMessage.success('附件插入成功')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || err.message || '附件上传失败')
  } finally {
    isUploadingAttachment.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

const submitPost = async () => {
  if (!newPostForm.value.title.trim() || !newPostForm.value.content.trim()) {
    return ElMessage.warning('标题和内容不能为空')
  }
  if (!props.spaceId) {
    return ElMessage.warning('空间 ID 为空，无法发帖')
  }
  isSubmittingPost.value = true
  try {
    await request.post('/posts/', {
      title: newPostForm.value.title,
      content: newPostForm.value.content,
      space_id: props.spaceId,
      tag_names: isTradePost.value ? ['交易'] : []
    })
    ElMessage.success('发布成功')
    newPostForm.value = { title: '', content: '' }
    isTradePost.value = false
    emit('success')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || '发布失败')
  } finally {
    isSubmittingPost.value = false
  }
}

const closeEditor = () => {
  emit('update:visible', false)
  newPostForm.value = { title: '', content: '' }
  isTradePost.value = false
}
</script>

<template>
  <div v-if="visible" class="absolute inset-0 z-[60] bg-black/40 backdrop-blur-sm flex justify-end overflow-hidden">
    <div class="w-full max-w-[800px] h-full bg-white shadow-2xl flex flex-col pt-16 animate-slide-in-right relative">
      <button @click="closeEditor" class="absolute top-6 left-6 w-10 h-10 rounded-full bg-[var(--c-fog)] text-[var(--c-navy)] flex items-center justify-center hover:bg-gray-200 transition-colors">
        <el-icon :size="20"><ArrowLeft /></el-icon>
      </button>
      <div class="px-10 pb-6 border-b border-[var(--c-navy)]/5 pt-1">
        <h2 class="text-2xl font-bold text-[var(--c-navy)]">发布新帖子</h2>
        <p class="text-[var(--c-navy)]/50 mt-1">发往 <span class="font-medium text-[var(--c-indigo)]">{{ spaceName || '未知空间' }}</span></p>
      </div>
      
      <div class="flex-1 overflow-y-auto px-10 py-8 custom-scrollbar space-y-6 bg-[var(--c-fog)]/30">
        <div>
          <label class="block text-sm font-medium text-[var(--c-navy)] mb-2">标题</label>
          <input v-model="newPostForm.title" type="text" placeholder="用一句话概括你的讨论点..." class="w-full text-lg px-4 py-3 bg-white border border-[var(--c-navy)]/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--c-indigo)] focus:border-transparent transition-all shadow-sm" />
        </div>
        <div class="flex items-center gap-x-3">
           <el-checkbox v-model="isTradePost" label="作为交易帖发布 (同时展示在交易专区)" size="large" />
        </div>
        <div class="flex flex-col h-[400px]">
          <div class="flex items-center justify-between mb-2">
            <label class="text-sm font-medium text-[var(--c-navy)]">正文 (支持 Markdown)</label>
            
            <input type="file" ref="fileInput" @change="handleAttachmentUpload" accept="image/*,.pdf" class="hidden" />
            <button @click="fileInput?.click()" :disabled="isUploadingAttachment" class="flex items-center gap-1 text-sm font-medium text-[var(--c-indigo)] hover:text-opacity-80 disabled:opacity-50">
              <el-icon v-if="isUploadingAttachment" class="is-loading"><Loading /></el-icon>
              <el-icon v-else><Document /></el-icon>
              插入图片 / PDF
            </button>
          </div>
          
          <textarea v-model="newPostForm.content" placeholder="详细描述你想分享或探讨的内容..." class="w-full flex-1 p-4 bg-white border border-[var(--c-navy)]/10 rounded-xl text-base text-[var(--c-navy)]/80 focus:outline-none focus:ring-2 focus:ring-[var(--c-indigo)] focus:border-transparent transition-all shadow-sm resize-none custom-scrollbar"></textarea>
        </div>
      </div>
      
      <div class="p-6 border-t border-[var(--c-navy)]/5 bg-white flex justify-end gap-x-4">
        <button @click="closeEditor" class="px-6 py-2.5 rounded-xl font-medium text-[var(--c-navy)]/70 hover:bg-[var(--c-fog)] transition-colors disabled:opacity-50" :disabled="isSubmittingPost">
          取消
        </button>
        <button @click="submitPost" :disabled="isSubmittingPost || !newPostForm.title.trim() || !newPostForm.content.trim()" class="px-8 py-2.5 rounded-xl font-medium text-white bg-[var(--c-indigo)] hover:bg-opacity-90 shadow-lg shadow-[var(--c-indigo)]/20 transition-all disabled:opacity-50 disabled:shadow-none min-w-[120px]">
          {{ isSubmittingPost ? '发布中...' : '发布帖子' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(15, 27, 45, 0.1);
  border-radius: 4px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: rgba(15, 27, 45, 0.2);
}
</style>
