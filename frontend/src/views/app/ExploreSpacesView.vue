<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search, Plus, Location, Present, Star, Monitor, Position } from '@element-plus/icons-vue'
import HomeHeader from '@/components/HomeHeader.vue'

// State
const activeSectionId = ref(1)

const sections = ref([
  { id: 1, name: '学校政策区', icon: Location, unread: 0 },
  { id: 2, name: '大学生优惠区', icon: Present, unread: 0 },
  { id: 3, name: '论坛活动区', icon: Star, unread: 0 },
  { id: 4, name: 'AI探索区', icon: Monitor, unread: 0 },
  { id: 5, name: '广告位招租', icon: Position, unread: 0 },
])

const activeSection = computed(() => {
  return sections.value.find((s: any) => s.id === activeSectionId.value)
})

const searchQuery = ref('')

const handleSearch = () => {
  console.log('Search for explore:', searchQuery.value)
  // To be implemented or mocked
}

const handleUploadClick = () => {
  console.log('Upload click in explore')
  // To be implemented or mocked
}
</script>

<template>
  <div class="h-screen flex flex-col bg-[var(--c-bg)] overflow-hidden font-sans">
    <HomeHeader />

    <div class="flex-1 flex overflow-hidden">
      <!-- Left Sidebar -->
      <aside class="w-[280px] bg-[var(--c-navy)] flex flex-col shadow-2xl z-10 shrink-0">
        <!-- Logo Area -->
        <div class="h-20 flex items-center px-6">
          <div class="w-10 h-10 bg-white/10 rounded-[12px] flex items-center justify-center mr-3 backdrop-blur-sm shadow-inner">
            <span class="font-serif text-[var(--c-fog)] text-xl font-bold">EX</span>
          </div>
          <span class="text-white font-medium text-lg tracking-wide opacity-90">无限探索</span>
        </div>

        <!-- Sections List -->
        <div class="flex-1 overflow-y-auto custom-scrollbar px-3 py-4 space-y-2">
          <div
            v-for="section in sections"
            :key="section.id"
            class="group flex items-center gap-x-3 p-3 rounded-[16px] cursor-pointer transition-all relative"
            :class="activeSectionId === section.id ? 'bg-white/10' : 'hover:bg-white/5'"
            @click="activeSectionId = section.id"
          >
            <!-- Active Indicator -->
            <div
              class="absolute left-[-12px] w-1 bg-[var(--c-gold)] rounded-r-md transition-all duration-300"
              :class="activeSectionId === section.id ? 'h-8 opacity-100' : 'h-0 opacity-0'"
            ></div>

            <el-icon
              :size="20"
              class="transition-colors"
              :class="activeSectionId === section.id ? 'text-[var(--c-gold)]' : 'text-white/40 group-hover:text-white/70'"
            >
              <component :is="section.icon" />
            </el-icon>

            <span
              class="text-sm font-medium transition-colors flex-1"
              :class="activeSectionId === section.id ? 'text-white' : 'text-white/60 group-hover:text-white/90'"
            >
              {{ section.name }}
            </span>
          </div>
        </div>
      </aside>

      <!-- Main Content Area -->
      <main class="flex-1 bg-[var(--c-bg)] relative overflow-hidden flex flex-col">
        <!-- Header Image & Search Area -->
        <div class="h-[280px] shrink-0 relative flex flex-col justify-end px-12 py-10">
          <div class="absolute inset-0 bg-gradient-to-br from-[var(--c-indigo)] to-[var(--c-navy)] opacity-95"></div>
          <!-- Decorative Pattern -->
          <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(circle at 2px 2px, white 1px, transparent 0); background-size: 32px 32px;"></div>

          <div class="relative z-10 w-full max-w-4xl mx-auto flex items-end justify-between gap-6">
            <div class="flex-1">
              <h1 class="text-4xl font-bold text-white mb-6 drop-shadow-md">
                探索 {{ activeSection?.name }}
              </h1>
              <div class="relative flex items-center w-full max-w-2xl">
                <el-icon class="absolute left-4 text-[var(--c-navy)] opacity-40 z-10" :size="20"><Search /></el-icon>
                <input
                  v-model="searchQuery"
                  @keyup.enter="handleSearch"
                  type="text"
                  placeholder="搜索发现新鲜事、优惠、活动..."
                  class="w-full h-14 bg-white/95 backdrop-blur-md rounded-[16px] pl-12 pr-4 text-[var(--c-navy)] text-lg focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)] transition-all shadow-lg"
                />
              </div>
            </div>
            
            <button
              @click="handleUploadClick"
              class="h-14 px-8 bg-[var(--c-gold)] text-white rounded-[16px] font-medium text-lg hover:bg-opacity-90 shadow-lg shadow-[var(--c-gold)]/30 transition-all shrink-0 flex items-center gap-x-2"
            >
              <el-icon><Plus /></el-icon> 发布内容
            </button>
          </div>
        </div>

        <!-- Content Area -->
        <div class="flex-1 overflow-y-auto px-12 py-8 custom-scrollbar bg-gray-50/50">
          <div class="max-w-4xl mx-auto flex flex-col items-center justify-center h-64 opacity-60">
             <div class="text-6xl mb-4">✨</div>
             <p class="text-xl font-medium text-[var(--c-navy)]">在这里发现无限可能</p>
             <p class="text-[var(--c-navy)]/60 mt-2">（内容区开发中）</p>
          </div>
        </div>
      </main>
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
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
}
</style>
