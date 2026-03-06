import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import PublicLayout from '@/layouts/PublicLayout.vue'
import AppLayout from '@/layouts/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import NProgress from 'nprogress'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    component: PublicLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/public/HomeView.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/views/public/LoginView.vue'),
        meta: { title: '登录' }
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('@/views/public/RegisterView.vue'),
        meta: { title: '注册' }
      },
      {
        path: 'explore/spaces',
        name: 'ExploreSpaces',
        component: () => import('@/views/public/ExploreSpacesView.vue'),
        meta: { title: '探索空间' }
      },
      {
        path: 'spaces/:spaceId',
        name: 'SpaceDetail',
        component: () => import('@/views/public/SpaceView.vue'),
        meta: { title: '空间主页' }
      },
      {
        path: 'posts/:postId',
        name: 'PostDetail',
        component: () => import('@/views/public/PostDetailView.vue'),
        meta: { title: '帖子详情' }
      }
    ]
  },
  {
    path: '/app',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'feed',
        name: 'Feed',
        component: () => import('@/views/app/FeedView.vue'),
        meta: { title: '发现' }
      },
      {
        path: '/me/overview',
        name: 'MeOverview',
        component: () => import('@/views/app/MeOverviewView.vue'),
        meta: { title: '我的主页' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Route Guards
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  const authStore = useAuthStore()
  
  if (to.meta.title) {
    document.title = `${to.meta.title} - Forum`
  }

  // Ensure initial user state is loaded if token exists, useful for deep links on refresh
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchMe()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  } else {
    next()
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router
