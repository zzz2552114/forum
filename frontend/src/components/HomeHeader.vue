<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { Search, Bell, Setting, UserFilled } from "@element-plus/icons-vue";

const router = useRouter();
const searchQuery = ref("");

const props = defineProps({
  username: {
    type: String,
    default: "User",
  },
});
</script>

<template>
  <header
    class="h-[88px] bg-white border-b border-[var(--c-navy)] border-opacity-5 flex items-center justify-between px-[80px] sticky top-0 z-40"
  >
    <!-- Left: Logo & Welcome -->
    <div class="flex items-center gap-x-6">
      <div
        class="w-16 h-16 bg-[var(--c-navy)] rounded-xl flex items-center justify-center cursor-pointer overflow-hidden shadow-sm"
        @click="router.push('/home')"
      >
        <span
          class="font-serif text-[var(--c-fog)] text-xl font-bold tracking-widest pl-1"
          >FRM</span
        >
      </div>
      <div class="flex flex-col">
        <span class="text-[var(--c-navy)] opacity-60 text-sm mb-0.5"
          >Forum Dashboard</span
        >
        <span class="text-[var(--c-navy)] font-medium text-lg"
          >欢迎你，{{ username }}</span
        >
      </div>
    </div>

    <!-- Middle: Search -->
    <div class="w-[320px]">
      <div class="relative flex items-center">
        <el-icon class="absolute left-4 text-[var(--c-navy)] opacity-40 z-10"
          ><Search
        /></el-icon>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索空间、资料、帖子..."
          class="w-full bg-[var(--c-fog)] rounded-[var(--radius-btn)] pl-11 pr-4 py-2.5 text-[var(--c-navy)] focus:outline-none focus:ring-2 focus:ring-[var(--c-gold)] focus:bg-white transition-all border border-transparent"
        />
      </div>
    </div>

    <!-- Right: Actions -->
    <div class="flex items-center gap-x-5">
      <button
        class="w-10 h-10 rounded-full flex items-center justify-center hover:bg-[var(--c-fog)] text-[var(--c-navy)] opacity-70 hover:opacity-100 transition-all relative"
      >
        <el-icon :size="20"><Bell /></el-icon>
        <!-- Unread badge -->
        <span
          class="absolute top-2 right-2.5 w-2 h-2 bg-[var(--c-danger)] rounded-full border-2 border-white"
        ></span>
      </button>

      <button
        class="w-10 h-10 rounded-full flex items-center justify-center hover:bg-[var(--c-fog)] text-[var(--c-navy)] opacity-70 hover:opacity-100 transition-all"
      >
        <el-icon :size="20"><Setting /></el-icon>
      </button>

      <!-- Avatar -->
      <div
        class="ml-2 w-10 h-10 rounded-full bg-[var(--c-fog)] border border-[var(--c-navy)] border-opacity-10 overflow-hidden cursor-pointer flex items-center justify-center text-[var(--c-navy)] opacity-50 hover:opacity-80 transition-opacity"
      >
        <el-icon :size="20"><UserFilled /></el-icon>
      </div>
    </div>
  </header>
</template>

<style scoped>
/* Scoped styles */
</style>
