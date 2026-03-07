<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
  <div class="hero-section flex flex-col justify-center max-w-[600px]">
    <div
      class="kicker text-[var(--c-gold)] text-sm font-semibold tracking-widest uppercase mb-4 opacity-90"
    >
      校园论坛 / Forum for Campus Resources
    </div>

    <h1
      class="font-serif text-[56px] leading-[1.15] text-[var(--c-fog)] mb-6 font-bold tracking-wide"
    >
      <span class="block">题目、政策、探索</span>
      <span class="block opacity-90">在一个地方看见</span>
    </h1>

    <p
      class="text-[var(--c-fog)] opacity-80 text-lg leading-relaxed mb-10 max-w-[480px]"
    >
      从真题到学校政策，从课程讨论到实用工具，让信息不再散落。
    </p>

    <div class="flex items-center gap-x-4 mb-14">
      <button
        class="bg-[var(--c-gold)] text-[var(--c-navy)] px-8 py-3.5 rounded-[var(--radius-btn)] font-medium hover:bg-white transition-colors shadow-lg shadow-[var(--c-gold)]/20 text-lg"
        @click="router.push('/home')"
      >
        进入论坛
      </button>
      <button
        class="bg-[rgba(255,255,255,0.1)] backdrop-blur-md border border-white/20 text-[var(--c-fog)] px-8 py-3.5 rounded-[var(--radius-btn)] font-medium hover:bg-white/20 transition-colors text-lg"
        @click="router.push('/materials')"
      >
        浏览资料
      </button>
    </div>

    <!-- Data Counters -->
    <div class="flex items-center gap-x-10 border-t border-white/10 pt-8">
      <div>
        <div class="font-sans text-2xl font-bold text-[var(--c-fog)] mb-1">
          12,000+
        </div>
        <div class="text-sm text-[var(--c-fog)] opacity-60">资料条目</div>
      </div>
      <div>
        <div class="font-sans text-2xl font-bold text-[var(--c-fog)] mb-1">
          220+
        </div>
        <div class="text-sm text-[var(--c-fog)] opacity-60">学校空间</div>
      </div>
      <div>
        <div class="font-sans text-2xl font-bold text-[var(--c-fog)] mb-1">
          Daily
        </div>
        <div class="text-sm text-[var(--c-fog)] opacity-60">
          每日更新政策与机会
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Text shadow for better readability over complex backgrounds */
.hero-section h1 {
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}
.hero-section p {
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
}
</style>
