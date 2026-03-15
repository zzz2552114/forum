<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = defineProps<{
  categories: any[]
  spaces: any[]
  recentSpaces?: any[]
  activeSpaceId: number | null
}>()

const emit = defineEmits(['update:activeSpaceId'])

const expandedCategories = ref<number[]>([])
const recentExpanded = ref(true)

const toggleRecent = () => {
  recentExpanded.value = !recentExpanded.value
}

onMounted(() => {
  // Wait to expand categories when they arrive
  if (props.categories.length > 0) {
    expandedCategories.value = props.categories.map(c => c.id)
  }
})

// Since categories can arrive after mount, watch for changes
import { watch } from 'vue'
watch(() => props.categories, (newCats) => {
  if (newCats.length > 0 && expandedCategories.value.length === 0) {
    expandedCategories.value = newCats.map(c => c.id)
  }
})

const toggleCategory = (id: number) => {
  if (expandedCategories.value.includes(id)) {
    expandedCategories.value = expandedCategories.value.filter(cid => cid !== id)
  } else {
    expandedCategories.value.push(id)
  }
}
</script>

<template>
  <div class="w-[84px] sm:w-[240px] shrink-0 bg-[#0F1522] flex flex-col items-center sm:items-stretch py-6 border-r border-black/10 z-10 transition-all">
    <div class="px-6 mb-4 hidden sm:block text-white/50 text-xs font-bold tracking-wider">
      已加入空间
    </div>

    <div class="flex-1 overflow-y-auto custom-scrollbar pt-2 space-y-4">
      <div v-for="category in categories" :key="category.id" class="mb-2">
        <!-- Category Title (Drawer Header) -->
        <div 
          class="px-5 py-2 flex items-center justify-between text-white/50 text-xs font-bold tracking-wider cursor-pointer hover:text-white/80 transition-colors"
          @click="toggleCategory(category.id)"
        >
          <span>{{ category.name }}</span>
          <span>{{ expandedCategories.includes(category.id) ? '▼' : '▶' }}</span>
        </div>
        
        <!-- Category Spaces List -->
        <div v-show="expandedCategories.includes(category.id)" class="px-3 space-y-2 mt-1">
          <div
            v-for="space in spaces.filter(s => s.category_id === category.id)"
            :key="space.id"
            class="group flex items-center gap-x-3 p-2 rounded-[16px] cursor-pointer transition-all relative"
            :class="activeSpaceId === space.id ? 'bg-white/10' : 'hover:bg-white/5'"
            @click="emit('update:activeSpaceId', space.id)"
          >
            <!-- Active Indicator Line -->
            <div
              v-if="activeSpaceId === space.id"
              class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-[var(--c-gold)] rounded-r-md"
            ></div>

            <!-- Space Icon -->
            <div
              class="w-10 h-10 rounded-[12px] bg-white/5 flex items-center justify-center shrink-0 border border-white/5 group-hover:bg-white/10 transition-colors"
            >
              <img
                v-if="space.icon_url"
                :src="space.icon_url"
                alt=""
                class="w-6 h-6 object-contain"
              />
              <span v-else class="text-white/80 font-bold text-lg">{{ space.name?.[0] }}</span>
            </div>

            <!-- Space Info (Hidden on mobile) -->
            <div class="min-w-0 hidden sm:block">
              <div
                class="text-white font-medium text-sm truncate opacity-90 group-hover:opacity-100"
              >
                {{ space.name }}
              </div>
              <div class="text-white/40 text-xs truncate">
                {{ space.member_count || 0 }} 人加入
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- Recent Spaces Section -->
      <div v-if="recentSpaces && recentSpaces.length > 0" class="mb-4 mt-6 border-t border-white/10 pt-4">
        <div 
          class="px-5 py-2 flex items-center justify-between text-white/50 text-xs font-bold tracking-wider cursor-pointer hover:text-white/80 transition-colors"
          @click="toggleRecent()"
        >
          <span>最近浏览</span>
          <span>{{ recentExpanded ? '▼' : '▶' }}</span>
        </div>
        
        <div v-show="recentExpanded" class="px-3 space-y-2 mt-1">
          <div
            v-for="space in recentSpaces"
            :key="space.id"
            class="group flex items-center gap-x-3 p-2 rounded-[16px] cursor-pointer transition-all relative"
            :class="activeSpaceId === space.id ? 'bg-white/10' : 'hover:bg-white/5'"
            @click="emit('update:activeSpaceId', space.id)"
          >
            <!-- Active Indicator Line -->
            <div
              v-if="activeSpaceId === space.id"
              class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-[var(--c-gold)] rounded-r-md"
            ></div>

            <!-- Space Icon -->
            <div
              class="w-10 h-10 rounded-[12px] bg-white/5 flex items-center justify-center shrink-0 border border-white/5 group-hover:bg-white/10 transition-colors opacity-60 grayscale group-hover:grayscale-0 group-hover:opacity-100"
            >
              <img
                v-if="space.icon_url"
                :src="space.icon_url"
                alt=""
                class="w-6 h-6 object-contain"
              />
              <span v-else class="text-white/80 font-bold text-lg">{{ space.name?.[0] }}</span>
            </div>

            <!-- Space Info -->
            <div class="min-w-0 hidden sm:block">
              <div
                class="text-white/80 font-medium text-sm truncate group-hover:text-white"
              >
                {{ space.name }}
              </div>
              <div class="text-[var(--c-gold)] text-[10px] mt-0.5 opacity-80">
                未加入
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
