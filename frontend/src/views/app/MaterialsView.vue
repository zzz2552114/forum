<script setup lang="ts">
import { ref, computed } from "vue";
import HomeHeader from "@/components/HomeHeader.vue";
import {
  Search,
  Document,
  Download,
  CollectionTag,
} from "@element-plus/icons-vue";

const searchQuery = ref("");
const activeSubject = ref("全部");

const subjects = [
  "全部",
  "高等数学",
  "线性代数",
  "数学分析",
  "概率论与数理统计",
  "离散数学",
  "大学物理",
];

// Mock Materials
const materials = ref([
  {
    id: 1,
    title: "2023-2024学年第二学期高等数学A期末试卷及答案.pdf",
    school: "清华大学",
    subject: "高等数学",
    updatedAt: "2024-06-20",
    url: "#",
    downloads: 1420,
  },
  {
    id: 2,
    title: "线性代数核心公式速记指南",
    school: "同济大学",
    subject: "线性代数",
    updatedAt: "2024-05-15",
    url: "#",
    downloads: 856,
  },
  {
    id: 3,
    title: "概率论与数理统计重点题型解析",
    school: "浙江大学",
    subject: "概率论与数理统计",
    updatedAt: "2024-04-10",
    url: "#",
    downloads: 921,
  },
  {
    id: 4,
    title: "大学物理精讲笔记整理",
    school: "北京大学",
    subject: "大学物理",
    updatedAt: "2024-03-22",
    url: "#",
    downloads: 443,
  },
  {
    id: 5,
    title: "高等数学B真题演练 (含解析)",
    school: "复旦大学",
    subject: "高等数学",
    updatedAt: "2024-02-18",
    url: "#",
    downloads: 310,
  },
  {
    id: 6,
    title: "离散数学习题集精选",
    school: "上海交通大学",
    subject: "离散数学",
    updatedAt: "2023-12-05",
    url: "#",
    downloads: 615,
  },
  {
    id: 7,
    title: "数学分析考研真题汇编",
    school: "中国科学技术大学",
    subject: "数学分析",
    updatedAt: "2023-10-12",
    url: "#",
    downloads: 1024,
  },
]);

const filteredMaterials = computed(() => {
  return materials.value
    .filter((m) => {
      const matchSubject =
        activeSubject.value === "全部" || m.subject === activeSubject.value;
      const matchSearch =
        !searchQuery.value ||
        m.title.includes(searchQuery.value) ||
        m.school.includes(searchQuery.value) ||
        m.subject.includes(searchQuery.value);
      return matchSubject && matchSearch;
    })
    .sort(
      (a, b) =>
        new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
    );
});

const clearFilters = () => {
  searchQuery.value = "";
  activeSubject.value = "全部";
};
</script>

<template>
  <div class="min-h-screen bg-[var(--c-fog)] flex flex-col">
    <HomeHeader username="同学" />

    <main
      class="flex-1 w-full max-w-[1280px] mx-auto px-[80px] py-10 pb-20 flex flex-col h-[calc(100vh-88px)]"
    >
      <!-- Top Search Area -->
      <div
        class="w-full bg-white rounded-[var(--radius-card)] p-6 shadow-sm border border-[var(--c-navy)]/5 mb-6 shrink-0 relative overflow-hidden"
      >
        <div
          class="absolute right-0 top-0 bottom-0 w-64 bg-gradient-to-l from-[var(--c-fog)] to-transparent pointer-events-none z-0"
        ></div>
        <div class="relative z-10 flex gap-x-4">
          <div class="relative flex-1">
            <el-icon
              class="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--c-navy)] opacity-40 z-10"
              :size="20"
              ><Search
            /></el-icon>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索高校、科目、真题..."
              class="w-full h-14 bg-[var(--c-fog)] rounded-[16px] pl-12 pr-4 text-[var(--c-navy)] text-lg focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)] focus:bg-white transition-all border border-transparent shadow-inner"
            />
          </div>
          <button
            class="h-14 px-8 bg-[var(--c-indigo)] text-white rounded-[16px] font-medium text-lg hover:bg-opacity-90 shadow-lg shadow-[var(--c-indigo)]/20 transition-all shrink-0"
          >
            搜索库
          </button>
        </div>
        <div class="mt-4 flex items-center justify-between">
          <div class="flex items-center gap-x-3 text-sm">
            <span class="text-[var(--c-navy)]/50">热门尝试:</span>
            <span
              class="px-3 py-1 rounded-full bg-[var(--c-navy)]/5 text-[var(--c-navy)]/70 hover:bg-[var(--c-gold)] hover:text-white cursor-pointer transition-colors"
              @click="searchQuery = '高等数学'"
              >高等数学</span
            >
            <span
              class="px-3 py-1 rounded-full bg-[var(--c-navy)]/5 text-[var(--c-navy)]/70 hover:bg-[var(--c-gold)] hover:text-white cursor-pointer transition-colors"
              @click="searchQuery = '期末真题'"
              >期末真题</span
            >
          </div>
          <div class="text-[var(--c-navy)]/50 text-sm font-medium">
            当前共 {{ filteredMaterials.length }} 份资料命中
          </div>
        </div>
      </div>

      <!-- Content Area -->
      <div class="flex-1 min-h-0 flex gap-x-6">
        <!-- Left: Categories -->
        <div
          class="w-64 shrink-0 bg-white rounded-[var(--radius-card)] shadow-sm border border-[var(--c-navy)]/5 overflow-y-auto custom-scrollbar flex flex-col p-3"
        >
          <div
            class="px-4 py-3 text-xs font-bold text-[var(--c-navy)]/40 tracking-widest uppercase mb-1"
          >
            所有科目
          </div>
          <div class="space-y-1">
            <div
              v-for="sub in subjects"
              :key="sub"
              class="px-4 py-3 rounded-[12px] cursor-pointer font-medium transition-all group flex items-center justify-between"
              :class="
                activeSubject === sub
                  ? 'bg-[var(--c-indigo)] text-white shadow-md'
                  : 'text-[var(--c-navy)] hover:bg-[var(--c-fog)]'
              "
              @click="activeSubject = sub"
            >
              <span>{{ sub }}</span>
              <el-icon v-if="activeSubject === sub" class="text-[var(--c-gold)]"
                ><CollectionTag
              /></el-icon>
            </div>
          </div>
        </div>

        <!-- Right: Materials List -->
        <div
          class="flex-1 bg-white rounded-[var(--radius-card)] shadow-sm border border-[var(--c-navy)]/5 overflow-y-auto custom-scrollbar flex flex-col relative"
        >
          <div
            v-if="filteredMaterials.length === 0"
            class="flex-1 flex flex-col items-center justify-center text-[var(--c-navy)]/40"
          >
            <div
              class="w-24 h-24 mb-4 rounded-full bg-[var(--c-navy)]/5 flex items-center justify-center"
            >
              <el-icon :size="40" class="opacity-50"><Document /></el-icon>
            </div>
            <p class="text-xl font-medium mb-2">未找到匹配的资料</p>
            <p class="mb-6 opacity-80">尝试更换搜索词或选择其他科目</p>
            <button
              @click="clearFilters"
              class="px-6 py-2 border border-[var(--c-navy)]/20 rounded-[12px] hover:border-[var(--c-gold)] hover:text-[var(--c-gold)] transition-colors"
            >
              清空筛选
            </button>
          </div>

          <div v-else class="p-4 space-y-3">
            <div
              v-for="mat in filteredMaterials"
              :key="mat.id"
              class="group flex items-center justify-between p-4 rounded-2xl hover:bg-[var(--c-fog)] transition-colors border border-transparent hover:border-[var(--c-navy)]/5 cursor-pointer"
            >
              <div
                class="flex items-start gap-x-4 overflow-hidden pr-4 max-w-[80%]"
              >
                <div
                  class="w-12 h-12 bg-white rounded-[12px] flex items-center justify-center text-[#E85D04] shrink-0 border border-[var(--c-navy)]/5 shadow-sm"
                >
                  <el-icon :size="24"><Document /></el-icon>
                </div>
                <div class="min-w-0">
                  <h4
                    class="font-medium text-lg text-[var(--c-navy)] mb-1 truncate group-hover:text-[var(--c-indigo)] transition-colors"
                    :title="mat.title"
                  >
                    {{ mat.title }}
                  </h4>
                  <div
                    class="flex items-center gap-x-4 text-sm text-[var(--c-navy)]/50"
                  >
                    <span class="flex items-center gap-x-1 font-medium"
                      ><span
                        class="w-1.5 h-1.5 rounded-full bg-[var(--c-gold)] opacity-80 inline-block"
                      ></span>
                      {{ mat.school }}</span
                    >
                    <span>{{ mat.subject }}</span>
                    <span>最后更新：{{ mat.updatedAt }}</span>
                  </div>
                </div>
              </div>

              <div
                class="flex items-center gap-x-4 pl-4 border-l border-[var(--c-navy)]/5 shrink-0"
              >
                <div class="text-[var(--c-navy)]/40 text-sm hidden lg:block">
                  {{ mat.downloads }} 次下载
                </div>
                <a
                  :href="mat.url"
                  target="_blank"
                  class="w-10 h-10 rounded-[12px] flex items-center justify-center bg-white text-[var(--c-indigo)] border border-[var(--c-navy)]/10 hover:border-[var(--c-indigo)] group-hover:bg-[var(--c-indigo)] group-hover:text-white transition-all shadow-sm"
                >
                  <el-icon :size="20"><Download /></el-icon>
                </a>
              </div>
            </div>

            <!-- Load More Mock -->
            <div
              class="pt-6 pb-2 flex justify-center border-t border-[var(--c-navy)]/5 mt-4"
            >
              <button
                class="px-8 py-2.5 rounded-full border border-[var(--c-navy)]/10 text-[var(--c-navy)] font-medium hover:bg-[var(--c-fog)] hover:border-[var(--c-navy)]/20 transition-all"
              >
                加载更多
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
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
