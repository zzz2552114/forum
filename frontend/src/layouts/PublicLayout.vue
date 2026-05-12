<template>
  <div class="min-h-screen flex flex-col bg-slate-50">
    <HomeHeader />
    <main class="flex-grow container mx-auto px-4 py-6">
      <router-view />
    </main>
    <footer class="bg-white border-t py-6 text-center text-slate-500 text-sm">
      &copy; {{ new Date().getFullYear() }} Forum Project. All rights reserved.
    </footer>
  </div>
</template>

<script setup lang="ts">
import HomeHeader from '@/components/HomeHeader.vue'
</script>
