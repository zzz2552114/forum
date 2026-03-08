import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";
import AppLayout from "@/layouts/AppLayout.vue";
import { useAuthStore } from "@/stores/auth";
import NProgress from "nprogress";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "Landing",
    component: () => import("@/views/public/HomeView.vue"),
    meta: { title: "首页" },
  },
  {
    path: "/home",
    name: "HomeDashboard",
    component: () => import("@/views/app/HomeDashboardView.vue"),
    meta: { title: "主页", requiresAuth: false }, // Allowing mock view without real auth for now
  },
  {
    path: "/spaces",
    name: "Spaces",
    component: () => import("@/views/app/SpacesView.vue"),
    meta: { title: "讨论空间", requiresAuth: false },
  },
  {
    path: "/materials",
    name: "Materials",
    component: () => import("@/views/app/MaterialsView.vue"),
    meta: { title: "资料汇编", requiresAuth: false },
  },

  {
    path: "/app",
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: "feed",
        name: "Feed",
        component: () => import("@/views/app/FeedView.vue"),
        meta: { title: "发现" },
      },

      {
        path: "/explore",
        name: "Explore",
        component: () => import("@/views/app/ExploreSpacesView.vue"),
        meta: { title: "无限探索" },
      },
      {
        path: "/me/overview",
        name: "MeOverview",
        component: () => import("@/views/app/MeOverviewView.vue"),
        meta: { title: "我的主页" },
      },
      {
        path: "/notifications",
        name: "Notifications",
        component: () => import("@/views/app/NotificationsView.vue"),
        meta: { title: "消息中心" },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Route Guards — use return-only style (Vue Router 4)
router.beforeEach(async (to) => {
  NProgress.start();

  const authStore = useAuthStore();

  if (to.meta.title) {
    document.title = `${to.meta.title} - Forum`;
  }

  // Ensure initial user state is loaded if token exists
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchMe();
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { path: "/", query: { redirect: to.fullPath, showLogin: "true" } };
  }
  // return undefined = allow navigation
});

router.afterEach(() => {
  NProgress.done();
});

export default router;
