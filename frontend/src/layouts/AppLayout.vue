<template>
  <div class="min-h-screen flex flex-col bg-slate-50">
    <Header />
    <div class="flex-grow container mx-auto flex pt-4">
      <aside class="w-64 hidden md:block shrink-0 px-4">
        <Sidebar />
      </aside>
      <main class="flex-grow px-4 md:px-8 bg-white border-x min-h-full pb-8">
        <router-view />
      </main>
      <!-- Optional Right Context Bar -->
      <aside class="w-72 hidden lg:block shrink-0 px-4">
        <!-- Contextual components can be injected via slots or specific route components later -->
        <router-view name="rightSidebar" />
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import Header from '@/components/common/Header.vue'
import Sidebar from '@/components/common/Sidebar.vue'
</script>
