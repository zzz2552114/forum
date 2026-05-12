<script setup lang="ts">
import { ref } from "vue";
import TopNav from "@/components/TopNav.vue";
import HeroSection from "@/components/HeroSection.vue";
import AuthCard from "@/components/AuthCard.vue";

const currentAuthView = ref<"login" | "register">("login");

const handleOpenAuth = (type: "login" | "register") => {
  currentAuthView.value = type;
  // Optionally scroll or highlight the AuthCard if on mobile
};
</script>

<template>
  <div class="min-h-screen relative overflow-hidden bg-[var(--c-navy)]">
    <!-- Background Poster Layer -->
    <div
      class="absolute inset-0 z-0 bg-[url('https://images.unsplash.com/photo-1541339907198-e08756dedf3f?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center"
    >
      <!-- Dark Overlay -->
      <div class="absolute inset-0 bg-[rgba(10,18,30,0.48)]"></div>
      <!-- Blue-Black Gradient -->
      <div
        class="absolute inset-0 bg-gradient-to-br from-[var(--c-navy)]/80 via-transparent to-[var(--c-indigo)]/90"
      ></div>
    </div>

    <!-- Top Navigation Layer -->
    <TopNav @open-auth="handleOpenAuth" />

    <!-- Hero Content Layer -->
    <main class="relative z-10 w-full h-full min-h-screen pt-[88px]">
      <div
        class="max-w-[1280px] mx-auto px-[80px] h-[calc(100vh-88px)] min-h-[600px] flex items-center justify-between"
      >
        <!-- Left: Hero Text -->
        <div class="ml-4 -mt-16">
          <HeroSection />
        </div>

        <!-- Right: Auth Card -->
        <div class="mr-4 -mt-16">
          <AuthCard />
        </div>
      </div>
    </main>
  </div>
</template>
