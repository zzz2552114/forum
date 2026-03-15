<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import HomeHeader from "@/components/HomeHeader.vue";
import FeatureCard from "@/components/FeatureCard.vue";
import request from "@/utils/request";
import { ElMessage } from "element-plus";

const router = useRouter();

// Real spaces
const joinedSpaces = ref<any[]>([]);

// Real materials (latest)
const newMaterials = ref<any[]>([]);

const fetchDashboardData = async () => {
  try {
    const spacesRes: any = await request.get('/spaces/me/subscriptions');
    joinedSpaces.value = (spacesRes.items || []).slice(0, 5); // Take up to 5 spaces

    const materialsRes: any = await request.get('/resources/', { params: { page: 1, page_size: 5 }});
    newMaterials.value = (materialsRes.items || []).slice(0, 5);
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || e.message || "获取大盘数据失败");
  }
};

onMounted(() => {
  fetchDashboardData();
});

// Mock exploration (keep for now as Explore is not fully backed by dynamic data in this card)
const explorations = ref([
  {
    id: 1,
    title: "XX年XX高校保研政策整理",
    summary: "涵盖30+双一流高校最新保研细则",
    type: "policy",
  },
  {
    id: 2,
    title: "XX公司最新大学生优惠",
    summary: "数码产品教育优惠最高直降1000元",
    type: "discount",
  },
  {
    id: 3,
    title: "大学生创业指南汇编",
    summary: "从0到1带你了解校园创业补贴与孵化器",
    type: "guide",
  },
  {
    id: 4,
    title: "一线城市租房补贴整理",
    summary: "北上广深应届生租房补贴申请全流程",
    type: "life",
  },
]);
</script>

<template>
  <div class="min-h-screen bg-[var(--c-fog)] flex flex-col">
    <!-- Header -->
    <HomeHeader />

    <!-- Main Content -->
    <main class="flex-1 w-full max-w-[1280px] mx-auto px-[80px] py-10 pb-20">
      <!-- Welcome Banner -->
      <div
        class="w-full h-[180px] bg-[var(--c-navy)] rounded-[var(--radius-card)] relative overflow-hidden mb-10 flex items-center px-16 shadow-xl shadow-[var(--c-navy)]/10"
      >
        <!-- Decoration -->
        <div
          class="absolute -right-20 -top-40 w-80 h-80 bg-[var(--c-indigo)] rounded-full blur-3xl opacity-50"
        ></div>
        <div
          class="absolute right-40 bottom-[-50px] w-60 h-60 bg-[var(--c-gold)] rounded-full blur-3xl opacity-20"
        ></div>

        <div class="relative z-10 flex-1">
          <h2
            class="text-3xl font-serif text-[var(--c-fog)] font-bold mb-3 tracking-wide"
          >
            今天先看什么？
          </h2>
          <p class="text-[var(--c-fog)] opacity-80 text-lg">
            你的学校空间、最新题库和随心探索
          </p>
        </div>

        <div class="relative z-10 flex items-center gap-x-4">
          <button
            class="bg-[rgba(255,255,255,0.1)] backdrop-blur-md border border-white/20 text-[var(--c-fog)] px-6 py-2.5 rounded-[var(--radius-btn)] font-medium hover:bg-white/20 transition-colors"
            @click="router.push('/spaces')"
          >
            查看我的学校
          </button>
          <button
            class="bg-[var(--c-gold)] text-[var(--c-navy)] px-6 py-2.5 rounded-[var(--radius-btn)] font-medium hover:bg-white transition-colors"
            @click="router.push('/materials')"
          >
            进入资料汇编
          </button>
        </div>
      </div>

      <!-- Three Feature Cards -->
      <div class="grid grid-cols-3 gap-x-6">
        <!-- Card 1: 讨论空间 -->
        <FeatureCard
          title="讨论空间"
          subtitle="进入你的学校与讨论社区"
          targetRoute="/spaces"
        >
          <div class="space-y-1">
            <div
              v-for="space in joinedSpaces"
              :key="space.id"
              class="h-[72px] flex items-center px-4 rounded-xl hover:bg-[var(--c-fog)] cursor-pointer group transition-colors"
              @click="router.push('/spaces')"
            >
              <div
                class="w-12 h-12 rounded-[12px] bg-white border border-[var(--c-navy)]/5 flex items-center justify-center text-[var(--c-navy)] font-bold text-lg shadow-sm group-hover:shadow group-hover:-translate-y-0.5 transition-all"
              >
                {{ space.name.charAt(0) }}
              </div>
              <div class="ml-4 flex-1">
                <div
                  class="text-[var(--c-navy)] font-medium group-hover:text-[var(--c-indigo)] transition-colors"
                >
                  {{ space.name }}
                </div>
              </div>
            </div>

            <div
              class="h-[72px] flex items-center justify-center px-4 rounded-xl hover:bg-white cursor-pointer group transition-all mt-2 border border-dashed border-[var(--c-navy)]/20 hover:border-[var(--c-gold)]"
            >
              <div
                class="text-[var(--c-navy)]/50 group-hover:text-[var(--c-gold)] font-medium flex items-center gap-x-2"
              >
                <span class="text-xl">+</span> 加入更多空间
              </div>
            </div>
          </div>
        </FeatureCard>

        <!-- Card 2: 题库上新 -->
        <FeatureCard
          title="题库上新"
          subtitle="最近更新的真题与课件"
          targetRoute="/materials"
        >
          <div class="space-y-3 px-2 pt-2">
            <div
              v-for="mat in newMaterials"
              :key="mat.id"
              class="group cursor-pointer bg-white border border-[var(--c-navy)]/5 rounded-xl p-4 hover:shadow-md hover:border-[var(--c-gold)]/30 hover:-translate-y-1 transition-all"
            >
              <div
                class="text-[var(--c-navy)] font-medium mb-2 group-hover:text-[var(--c-indigo)] line-clamp-2 leading-snug"
              >
                {{ mat.title }}
              </div>
              <div class="flex items-center justify-between text-xs mt-3">
                <div class="flex gap-x-2">
                  <span
                    class="bg-[var(--c-fog)] text-[var(--c-navy)]/70 px-2 py-0.5 rounded"
                  >
                    {{ mat.resource_type === 'past_exam' ? '往年试卷' : mat.resource_type === 'notes' ? '课堂笔记' : mat.resource_type === 'solution' ? '习题答案' : '其他资料' }}
                  </span>
                </div>
                <div class="text-[var(--c-navy)]/50 flex items-center gap-x-3">
                  <span>{{ mat.download_count || 0 }} 次下载</span>
                  <span>{{ new Date(mat.created_at).toLocaleDateString() }}</span>
                </div>
              </div>
            </div>
          </div>
        </FeatureCard>

        <!-- Card 3: 无限探索 -->
        <FeatureCard title="无限探索" subtitle="发现学校政策、优惠与校园指南" targetRoute="/explore">
          <div class="space-y-1 mt-1">
            <div
              v-for="item in explorations"
              :key="item.id"
              class="p-4 rounded-xl hover:bg-[var(--c-fog)] cursor-pointer group transition-colors relative overflow-hidden"
            >
              <!-- Hover colored background block -->
              <div
                class="absolute left-0 top-0 bottom-0 w-1 bg-[var(--c-gold)] opacity-0 group-hover:opacity-100 transition-opacity"
              ></div>

              <div class="flex items-start justify-between">
                <div class="flex-1 pr-4">
                  <div
                    class="text-[var(--c-navy)] font-medium mb-1.5 group-hover:text-[var(--c-indigo)] transition-colors"
                  >
                    {{ item.title }}
                  </div>
                  <div class="text-sm text-[var(--c-navy)]/60 line-clamp-1">
                    {{ item.summary }}
                  </div>
                </div>
                <div
                  class="text-[var(--c-gold)] opacity-0 group-hover:opacity-100 transform translate-x-2 group-hover:translate-x-0 transition-all mt-1"
                >
                  &rarr;
                </div>
              </div>
            </div>
          </div>
        </FeatureCard>
      </div>
    </main>
  </div>
</template>
