<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import MegaDrawer from "./MegaDrawer.vue";

const router = useRouter();

defineEmits(["open-auth"]);

const navItems = [
  "进入论坛",
  "资料汇编",
  "学校空间",
  "课程讨论",
  "娱乐组团",
  "AI 产品",
];
const openMenu = ref<string | null>(null);

const onNavClick = (item: string) => {
  if (item === "进入论坛") {
    openMenu.value = null;
    router.push("/home");
    return;
  }
  openMenu.value = openMenu.value === item ? null : item;
};

const closeMenu = () => {
  openMenu.value = null;
};

const onEsc = (e: KeyboardEvent) => {
  if (e.key === "Escape") closeMenu();
};

onMounted(() => {
  window.addEventListener("keydown", onEsc);
});

onUnmounted(() => {
  window.removeEventListener("keydown", onEsc);
});
</script>

<template>
  <header
    class="top-nav h-[88px] w-full fixed top-0 z-50 flex items-center justify-between px-[80px]"
    :class="{ 'nav-drawer-open': openMenu !== null }"
  >
    <!-- Logo -->
    <div
      class="text-[var(--c-fog)] font-serif text-2xl tracking-widest cursor-pointer font-bold"
      @click="router.push('/')"
    >
      FORUM
    </div>

    <!-- Nav Items -->
    <nav class="flex h-full items-center gap-x-2">
      <div
        v-for="item in navItems"
        :key="item"
        class="nav-item h-full flex items-center px-4 cursor-pointer relative text-[var(--c-fog)] transition-all"
        :class="{
          active: openMenu === item,
          'font-medium': openMenu === item,
          'opacity-70 hover:opacity-100': openMenu !== item,
        }"
        @click.stop="onNavClick(item)"
      >
        {{ item }}
        <div
          v-if="openMenu === item"
          class="absolute bottom-0 left-0 right-0 h-[2px] bg-[var(--c-gold)]"
        ></div>
        <div
          class="nav-hover-bg absolute inset-4 rounded-lg bg-[var(--c-fog)] opacity-0 transition-opacity"
        ></div>
      </div>
    </nav>

    <!-- Actions -->
    <div class="flex items-center gap-x-4">
      <button
        class="text-[var(--c-fog)] opacity-80 hover:opacity-100 transition-opacity"
        @click="$emit('open-auth', 'register')"
      >
        注册
      </button>
      <button
        class="bg-[var(--c-indigo)] text-[var(--c-fog)] px-6 py-2.5 rounded-[var(--radius-btn)] hover:bg-opacity-80 transition-all font-medium border border-white/10"
        @click="$emit('open-auth', 'login')"
      >
        登录
      </button>
    </div>
  </header>

  <MegaDrawer
    :is-open="openMenu !== null"
    :active-menu="openMenu"
    @close="closeMenu"
  />
</template>

<style scoped>
.top-nav {
  transition:
    background-color 0.3s ease,
    backdrop-filter 0.3s ease;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.nav-drawer-open {
  background-color: rgba(8, 14, 24, 0.72);
  backdrop-filter: blur(10px);
}

.nav-item:hover .nav-hover-bg {
  opacity: 0.1;
}
</style>
