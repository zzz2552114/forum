<script setup lang="ts">
import { ref, computed } from "vue";
import HomeHeader from "@/components/HomeHeader.vue";
import {
  Setting,
  Plus,
  ChatDotRound,
  Document,
  Message,
  Collection,
} from "@element-plus/icons-vue";

const username = ref("同学");

// Mock Spaces
const spaces = ref([
  { id: "1", name: "XX大学空间", type: "school", color: "bg-blue-500" },
  { id: "2", name: "高等数学空间", type: "course", color: "bg-green-500" },
  {
    id: "3",
    name: "考研交流空间",
    type: "activity",
    color: "bg-[var(--c-gold)]",
  },
]);

// Mock Sections
const sections = ref([
  { id: "post", name: "发帖区", icon: Message },
  { id: "chat", name: "聊天区", icon: ChatDotRound },
  { id: "exam", name: "学校真题区", icon: Document },
  { id: "policy", name: "学校政策区", icon: Collection },
]);

const selectedSpaceId = ref(spaces.value[0]?.id ?? null);
const selectedSection = ref("post");

const onSelectSpace = (spaceId: string) => {
  selectedSpaceId.value = spaceId;
  selectedSection.value = "post";
};

const currentSpace = computed(() =>
  spaces.value.find((s) => s.id === selectedSpaceId.value),
);
const currentSectionName = computed(
  () => sections.value.find((s) => s.id === selectedSection.value)?.name,
);

// Post Modal State
const showPostModal = ref(false);
const postTitle = ref("");
const postContent = ref("");

const handlePost = () => {
  showPostModal.value = false;
  postTitle.value = "";
  postContent.value = "";
};
</script>

<template>
  <div class="h-screen bg-[var(--c-fog)] flex flex-col overflow-hidden">
    <HomeHeader :username="username" />

    <div class="flex-1 flex overflow-hidden">
      <!-- Left Column: Spaces List (2 Cols ~ 16.6%) -->
      <div
        class="w-[84px] sm:w-[240px] shrink-0 bg-[#0F1522] flex flex-col items-center sm:items-stretch py-6 border-r border-black/10 z-10 transition-all"
      >
        <div
          class="px-6 mb-4 hidden sm:block text-white/50 text-xs font-bold tracking-wider"
        >
          已加入空间
        </div>

        <div class="flex-1 overflow-y-auto custom-scrollbar px-3 space-y-2">
          <div
            v-for="space in spaces"
            :key="space.id"
            class="group flex items-center gap-x-3 p-2 rounded-[16px] cursor-pointer transition-all relative"
            :class="
              selectedSpaceId === space.id ? 'bg-white/10' : 'hover:bg-white/5'
            "
            @click="onSelectSpace(space.id)"
          >
            <!-- Active Indicator Line -->
            <div
              class="absolute left-[-12px] w-1 bg-white rounded-r-md transition-all duration-300"
              :class="
                selectedSpaceId === space.id
                  ? 'h-8 opacity-100'
                  : 'h-0 opacity-0 group-hover:h-4 group-hover:opacity-50'
              "
            ></div>

            <div
              class="w-12 h-12 shrink-0 rounded-[14px] flex items-center justify-center text-white font-bold text-lg shadow-md transition-transform"
              :class="[
                space.color,
                selectedSpaceId === space.id
                  ? 'rounded-[10px]'
                  : 'group-hover:rounded-[10px]',
              ]"
            >
              {{ space.name.charAt(0) }}
            </div>

            <div class="hidden sm:block flex-1 min-w-0">
              <div
                class="text-white/90 font-medium truncate text-sm"
                :class="
                  selectedSpaceId === space.id ? 'text-white font-bold' : ''
                "
              >
                {{ space.name }}
              </div>
            </div>
          </div>

          <!-- Add Space Button -->
          <div
            class="group flex items-center gap-x-3 p-2 rounded-[16px] cursor-pointer transition-all mt-4 hover:bg-white/5"
          >
            <div
              class="w-12 h-12 shrink-0 rounded-[14px] bg-white/5 border border-white/10 flex items-center justify-center text-green-500 font-bold text-xl group-hover:bg-green-500 group-hover:text-white transition-all"
            >
              +
            </div>
            <div
              class="hidden sm:block text-green-500 font-medium group-hover:text-white transition-colors"
            >
              探索新空间
            </div>
          </div>
        </div>
      </div>

      <!-- Middle Column: Sections (3 Cols ~ 25%) -->
      <div
        class="w-[280px] shrink-0 bg-[#172033] flex flex-col border-r border-black/10 z-0"
      >
        <div
          class="h-[60px] flex items-center px-4 border-b border-white/5 shadow-sm"
        >
          <h2 class="text-white font-bold text-lg truncate">
            {{ currentSpace?.name || "选择空间" }}
          </h2>
        </div>

        <div class="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-0.5">
          <div
            v-for="sec in sections"
            :key="sec.id"
            class="flex items-center gap-x-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors"
            :class="
              selectedSection === sec.id
                ? 'bg-white/10 text-white font-medium'
                : 'text-white/60 hover:bg-white/5 hover:text-white/90'
            "
            @click="selectedSection = sec.id"
          >
            <el-icon :size="18" class="opacity-80"
              ><component :is="sec.icon"
            /></el-icon>
            <span class="text-[15px]">{{ sec.name }}</span>
          </div>
        </div>
      </div>

      <!-- Right Column: Content Area (7 Cols ~ 58.3%) -->
      <div class="flex-1 bg-white relative flex flex-col min-w-0">
        <!-- Top Toolbar -->
        <div
          class="h-[60px] shrink-0 flex items-center justify-between px-6 border-b border-[var(--c-navy)]/5 sticky top-0 bg-white/90 backdrop-blur-sm z-10 shadow-sm"
        >
          <div class="flex items-center gap-x-3 text-[var(--c-navy)]">
            <span class="font-bold text-lg"># {{ currentSectionName }}</span>
            <span
              class="text-xs px-2 py-0.5 rounded-full bg-[var(--c-fog)] text-[var(--c-navy)]/60 font-medium line-clamp-1 border border-[var(--c-navy)]/5"
            >
              来自 {{ currentSpace?.name }}
            </span>
          </div>
          <button
            class="w-8 h-8 rounded hover:bg-[var(--c-fog)] flex items-center justify-center text-[var(--c-navy)]/60 hover:text-[var(--c-navy)] transition-colors"
          >
            <el-icon :size="20"><Setting /></el-icon>
          </button>
        </div>

        <!-- Scrollable Content -->
        <div
          class="flex-1 overflow-y-auto px-6 py-6 custom-scrollbar bg-[var(--c-fog)]/30"
        >
          <!-- Empty State Mockup -->
          <div
            v-if="selectedSection !== 'post'"
            class="h-full flex flex-col items-center justify-center text-[var(--c-navy)]/40 mt-20"
          >
            <div
              class="w-20 h-20 mb-4 rounded-full bg-[var(--c-navy)]/5 flex items-center justify-center"
            >
              <el-icon :size="32"
                ><component
                  :is="sections.find((s) => s.id === selectedSection)?.icon"
              /></el-icon>
            </div>
            <p class="text-lg font-medium">还没有内容</p>
            <p class="text-sm mt-1">成为第一个在这里发布的人吧！</p>
          </div>

          <!-- List State Mockup (for posts) -->
          <div v-else class="max-w-[800px] mx-auto space-y-4 pb-24">
            <div
              v-for="i in 5"
              :key="i"
              class="bg-white p-5 rounded-2xl shadow-sm border border-[var(--c-navy)]/5 hover:border-[var(--c-gold)]/30 transition-colors cursor-pointer group"
            >
              <div class="flex items-center gap-x-3 mb-3">
                <div
                  class="w-10 h-10 rounded-full bg-[var(--c-fog)] overflow-hidden shrink-0"
                ></div>
                <div>
                  <div class="font-medium text-[var(--c-navy)] text-sm">
                    用户 {{ i * 11 }}
                  </div>
                  <div class="text-xs text-[var(--c-navy)]/50">
                    {{ i }} 小时前
                  </div>
                </div>
              </div>
              <h3
                class="font-medium text-[var(--c-navy)] text-lg mb-2 group-hover:text-[var(--c-indigo)]"
              >
                这是一条测试帖子的标题 - 关于期末考试的复习建议
              </h3>
              <p
                class="text-[var(--c-navy)]/70 text-sm line-clamp-2 leading-relaxed"
              >
                这里是正文这里是正文这里是正文这里是正文这里是正文。由于是模拟的数据所以随便写一点文字占个位。希望大家都能考个好成绩！
              </p>
            </div>
          </div>
        </div>

        <!-- Floating Action Button -->
        <button
          class="absolute right-8 bottom-8 w-14 h-14 bg-[var(--c-indigo)] text-white rounded-2xl flex items-center justify-center shadow-xl shadow-[var(--c-indigo)]/30 hover:bg-[var(--c-navy)] hover:-translate-y-1 transition-all z-20"
          @click="showPostModal = true"
        >
          <el-icon :size="24"><Plus /></el-icon>
        </button>

        <!-- Post Modal Overlay -->
        <div
          v-if="showPostModal"
          class="absolute inset-0 z-30 flex items-center justify-center bg-[var(--c-navy)]/40 backdrop-blur-sm p-4"
        >
          <div
            class="w-full max-w-[600px] bg-white rounded-[24px] shadow-2xl flex flex-col overflow-hidden"
            @click.stop
          >
            <div
              class="px-6 py-4 border-b border-[var(--c-fog)] flex items-center justify-between bg-white"
            >
              <h2 class="text-lg font-bold text-[var(--c-navy)]">
                在 #{{ currentSectionName }} 发帖
              </h2>
              <button
                @click="showPostModal = false"
                class="text-[var(--c-navy)]/40 hover:text-[var(--c-navy)]"
              >
                Esc
              </button>
            </div>
            <div class="p-6 flex flex-col gap-y-4">
              <input
                v-model="postTitle"
                type="text"
                placeholder="标题（必填）"
                class="w-full shrink-0 text-lg font-medium bg-[var(--c-fog)] rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)] transition-all border border-transparent placeholder:text-[var(--c-navy)]/30"
              />
              <textarea
                v-model="postContent"
                placeholder="在此输入你的内容..."
                class="w-full flex-1 min-h-[200px] bg-[var(--c-fog)] rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)] transition-all border border-transparent resize-none placeholder:text-[var(--c-navy)]/30"
              ></textarea>
            </div>
            <div
              class="px-6 py-4 border-t border-[var(--c-fog)] bg-white/50 flex justify-end gap-x-3"
            >
              <button
                @click="showPostModal = false"
                class="px-6 py-2.5 rounded-[12px] text-[var(--c-navy)]/60 font-medium hover:bg-[var(--c-fog)] transition-colors"
              >
                取消
              </button>
              <button
                @click="handlePost"
                class="px-8 py-2.5 rounded-[12px] bg-[var(--c-indigo)] text-white font-medium shadow-md shadow-[var(--c-indigo)]/20 hover:bg-opacity-90 transition-all"
              >
                发布
              </button>
            </div>
          </div>
        </div>
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
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
}

.bg-white .custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(15, 27, 45, 0.1);
}
.bg-white .custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: rgba(15, 27, 45, 0.2);
}
</style>
