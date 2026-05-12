<script setup lang="ts">
import { onMounted, onUnmounted } from "vue";

const props = defineProps<{
  isOpen: boolean;
  activeMenu: string | null;
}>();

const emit = defineEmits<{
  (e: "close"): void;
}>();

// Mock data content for the drawer based on active menu
const drawerData: Record<string, { title: string; items: string[] }[]> = {
  资料汇编: [
    {
      title: "备考资料",
      items: ["真题汇集", "PPT 模板", "保研经验帖", "考研时间线"],
    },
    { title: "政策指南", items: ["各校政策", "大学生优惠合集"] },
  ],
  学校空间: [
    { title: "我的圈子", items: ["我的学校", "同城高校"] },
    { title: "发现空间", items: ["热门学校", "专业交流群", "校园活动墙"] },
  ],
  课程讨论: [
    { title: "理学基础", items: ["高等数学", "线性代数", "概率论"] },
    { title: "通识必修", items: ["计算机基础", "英语四六级"] },
  ],
  娱乐组团: [
    { title: "线上活动", items: ["游戏开黑", "电影拼单"] },
    { title: "线下组局", items: ["饭搭子", "健身搭子", "周末出行"] },
  ],
  "AI 产品": [
    { title: "求职赋能", items: ["简历优化"] },
    {
      title: "学习提效",
      items: ["PPT 大纲生成", "论文阅读助手", "政策总结器", "学习计划助手"],
    },
  ],
};

const handleOutsideClick = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  // Check if click is inside drawer or nav, handled in parent or assume it's root
  if (props.isOpen && target.classList.contains("drawer-overlay")) {
    emit("close");
  }
};

onMounted(() => {
  document.addEventListener("click", handleOutsideClick);
});

onUnmounted(() => {
  document.removeEventListener("click", handleOutsideClick);
});
</script>

<template>
  <Transition name="fade-drawer">
    <div
      v-if="isOpen && activeMenu && drawerData[activeMenu]"
      class="fixed inset-0 top-[88px] z-40 drawer-overlay"
    >
      <div class="mega-drawer w-full backdrop-blur-xl border-t border-white/5">
        <div
          class="max-w-[1280px] mx-auto px-[80px] h-full flex items-start pt-10 gap-x-6"
        >
          <div
            v-for="(column, idx) in drawerData[activeMenu]"
            :key="idx"
            class="flex-1"
          >
            <h4
              class="text-[var(--c-fog)] opacity-50 mb-4 text-sm font-medium tracking-wider"
            >
              {{ column.title }}
            </h4>
            <ul class="space-y-3">
              <li v-for="(item, i) in column.items" :key="i">
                <a
                  href="#"
                  class="text-[var(--c-fog)] hover:text-[var(--c-gold)] transition-colors text-base"
                  >{{ item }}</a
                >
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.mega-drawer {
  height: 260px;
  background-color: rgba(9, 16, 28, 0.82);
  backdrop-filter: blur(20px);
  border-bottom-left-radius: var(--radius-drawer);
  border-bottom-right-radius: var(--radius-drawer);
}

.fade-drawer-enter-active,
.fade-drawer-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}

.fade-drawer-enter-from,
.fade-drawer-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
