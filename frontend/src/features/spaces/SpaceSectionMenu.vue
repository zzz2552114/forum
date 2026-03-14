<script setup lang="ts">
const props = defineProps<{
  activeSectionId: number
  activeSpaceName: string
  sections: Array<{ id: number, name: string, icon: any, unread: number }>
}>()

const emit = defineEmits(['update:activeSectionId'])
</script>

<template>
  <div class="w-[280px] shrink-0 bg-white flex flex-col border-r border-[var(--c-navy)] border-opacity-10 z-0">
    <div class="h-16 flex items-center px-6 border-b border-[var(--c-navy)] border-opacity-10 shrink-0">
      <h2 class="text-lg font-bold text-[var(--c-navy)]">{{ activeSpaceName || '选择空间' }}</h2>
    </div>

    <!-- Sections List -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-1">
      <div 
        v-for="section in sections" 
        :key="section.id"
        class="flex items-center justify-between px-3 py-2 rounded-[var(--radius-btn)] cursor-pointer text-sm font-medium transition-all"
        :class="activeSectionId === section.id ? 'bg-[var(--c-indigo)] text-white shadow-md shadow-[var(--c-indigo)]/20' : 'text-[var(--c-navy)] opacity-70 hover:opacity-100 hover:bg-[var(--c-fog)]'"
        @click="emit('update:activeSectionId', section.id)"
      >
        <div class="flex items-center gap-x-3">
          <el-icon :size="18" class="opacity-80"><component :is="section.icon" /></el-icon>
          <span>{{ section.name }}</span>
        </div>
        <span v-if="section.unread > 0" class="text-xs font-bold px-2 py-0.5 rounded-full bg-white/20 text-white">{{ section.unread }}</span>
      </div>
    </div>
  </div>
</template>
