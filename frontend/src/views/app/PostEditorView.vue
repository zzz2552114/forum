<template>
  <div class="max-w-4xl mx-auto py-6">
    <el-card shadow="never" class="border-none rounded-2xl">
      <h1 class="text-2xl font-bold text-slate-800 mb-6 flex items-center gap-2">
        <el-icon class="text-blue-600"><EditPen /></el-icon> 发布新帖子
      </h1>
      
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <el-form-item label="所属空间" prop="space_id">
            <el-select v-model="form.space_id" placeholder="选择一个相关的空间" filterable class="w-full">
              <el-option v-for="space in spaces" :key="space.id" :label="space.name" :value="space.id" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="标签" prop="tags">
            <el-select
              v-model="form.tag_ids"
              multiple
              filterable
              remote
              reserve-keyword
              placeholder="添加标签 (最多5个)"
              :remote-method="searchTags"
              :loading="loadingTags"
              class="w-full"
            >
              <el-option v-for="tag in availableTags" :key="tag.id" :label="tag.name" :value="tag.id" />
            </el-select>
          </el-form-item>
        </div>

        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" size="large" placeholder="一句话概括你想分享的内容或提出的问题" maxlength="100" show-word-limit />
        </el-form-item>

        <el-form-item label="类型">
          <el-radio-group v-model="form.type">
            <el-radio value="discussion" border>讨论</el-radio>
            <el-radio value="question" border>提问</el-radio>
            <el-radio value="article" border>文章</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="正文" prop="content">
          <!-- A placeholder textarea for markdown editing for MVP. A real MR plugin can be added later -->
          <el-input v-model="form.content" type="textarea" :rows="15" placeholder="支持 Markdown 语法。请详细描述你的问题或分享内容..." class="font-mono text-sm" />
          <div class="mt-2 text-xs text-slate-400 flex items-center justify-between w-full">
            <span>支持 Markdown 格式。拖拽或粘贴文件上传功能开发中。</span>
          </div>
        </el-form-item>

        <div class="flex justify-between items-center mt-8 pt-4 border-t border-slate-100">
          <el-button @click="$router.back()">取消</el-button>
          <div class="flex gap-4">
            <el-button @click="saveDraft" plain>保存草稿</el-button>
            <el-button type="primary" @click="submitPost" :loading="submitting" size="large" class="px-8 fw-bold">发布帖子</el-button>
          </div>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { EditPen } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const route = useRoute()
const formRef = ref()

const form = ref({
  space_id: route.query.space_id ? Number(route.query.space_id) : undefined,
  title: '',
  content: '',
  type: 'discussion',
  tag_ids: []
})

const spaces = ref<any[]>([])
const availableTags = ref<any[]>([])
const loadingTags = ref(false)
const submitting = ref(false)

const rules = {
  space_id: [{ required: true, message: '请选择一个空间', trigger: 'change' }],
  title: [
    { required: true, message: '标题不能为空', trigger: 'blur' },
    { min: 5, max: 100, message: '长度在 5 到 100 个字符', trigger: 'blur' }
  ],
  content: [{ required: true, message: '正文不能为空', trigger: 'blur' }]
}

const fetchSpaces = async () => {
  try {
    const res: any = await request.get('/spaces/')
    spaces.value = res.items || res
  } catch (e) {
    console.error(e)
  }
}

const searchTags = async (query: string) => {
  if (query) {
    loadingTags.value = true
    try {
      const res: any = await request.get('/tags/', { params: { keyword: query } })
      availableTags.value = res.items || res
    } catch (e) {
      console.error(e)
    } finally {
      loadingTags.value = false
    }
  } else {
    availableTags.value = []
  }
}

const saveDraft = () => {
  localStorage.setItem('postDraft', JSON.stringify(form.value))
  ElMessage.success('草稿已保存到本地')
}

const submitPost = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitting.value = true
      try {
        const res: any = await request.post('/posts/', form.value)
        ElMessage.success('发布成功！')
        localStorage.removeItem('postDraft')
        router.push(`/posts/${res.id}`)
      } catch (e) {
        console.error(e)
      } finally {
        submitting.value = false
      }
    } else {
      ElMessage.warning('请检查输入内容是否完整')
    }
  })
}

onMounted(() => {
  fetchSpaces()
  const savedDraft = localStorage.getItem('postDraft')
  if (savedDraft) {
    try {
      const parsed = JSON.parse(savedDraft)
      form.value = { ...form.value, ...parsed }
      ElMessage.info('已恢复之前保存的草稿')
    } catch (e) {
      localStorage.removeItem('postDraft')
    }
  }
})
</script>
