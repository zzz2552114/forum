<script setup lang="ts">
const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    required: true,
  },
  targetRoute: {
    type: String,
    default: "",
  },
});

import { useRouter } from "vue-router";
const router = useRouter();

const onHeaderClick = () => {
  if (props.targetRoute) {
    router.push(props.targetRoute);
  }
};
</script>

<template>
  <div
    class="feature-card bg-white rounded-[var(--radius-card)] overflow-hidden flex flex-col group transition-all duration-300"
  >
    <!-- Header Area -->
    <div
      class="h-[80px] px-6 py-4 flex flex-col justify-center border-b border-[var(--c-fog)] cursor-pointer hover:bg-[var(--c-fog)] transition-colors"
      @click="onHeaderClick"
    >
      <div class="flex items-center justify-between">
        <h3
          class="font-serif text-xl font-bold text-[var(--c-navy)] group-hover:text-[var(--c-indigo)] transition-colors"
        >
          {{ title }}
        </h3>
        <!-- Chevron right icon hidden by default, visible on hover -->
        <span
          class="opacity-0 group-hover:opacity-100 transform translate-x-[-10px] group-hover:translate-x-0 transition-all text-[var(--c-gold)]"
        >
          &rarr;
        </span>
      </div>
      <p class="text-[var(--c-navy)] opacity-50 text-sm mt-1">{{ subtitle }}</p>
    </div>

    <!-- Content Slot -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-2">
      <slot></slot>
    </div>

    <!-- Footer Slot -->
    <div
      v-if="$slots.footer"
      class="p-4 border-t border-[var(--c-fog)] bg-white mt-auto"
    >
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<style scoped>
.feature-card {
  height: 620px;
  box-shadow: var(--shadow-card-light);
  border: 1px solid rgba(15, 23, 34, 0.04);
}
.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 50px rgba(15, 23, 34, 0.12);
}

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
