import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import DashboardView from '../views/DashboardView.vue'
import DeviceView from '../views/DeviceView.vue'
import HistoryView from '../views/HistoryView.vue'
import LoginView from '../views/LoginView.vue'
import MachineSelectView from '../views/MachineSelectView.vue'
import UserManagementView from '../views/UserManagementView.vue'
import OperationLogView from '../views/OperationLogView.vue'


const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { public: true },
    },

    {
      path: '/machines',
      name: 'machines',
      component: MachineSelectView,
      meta: { requiresAuth: true, requiresMachine: false },
    },
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true, requiresMachine: true },
    },
    {
      path: '/device',
      name: 'device',
      component: DeviceView,
      meta: { requiresAuth: true, requiresMachine: true },
    },
    {
      path: '/history',
      name: 'history',
      component: HistoryView,
      meta: { requiresAuth: true, requiresMachine: true },
    },
    {
      path: '/users',
      name: 'users',
      component: UserManagementView,
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/logs',
      name: 'logs',
      component: OperationLogView,
      meta: { requiresAuth: true, requiresAdmin: true },
    },
  ],
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  
  // 恢复登录状态
  if (!authStore.isLoggedIn) {
    authStore.restoreSession()
  }
  
  const isLoggedIn = authStore.isLoggedIn
  const isMachineLogin = authStore.isMachineLogin
  const hasSelectedMachine = !!authStore.currentMachine
  
  // 公开页面（登录页）
  if (to.meta.public) {
    if (isLoggedIn && !to.meta.skipAuthRedirect) {
      // 已登录，跳转到对应页面
      if (isMachineLogin || hasSelectedMachine) {
        next('/')
      } else {
        next('/machines')
      }
    } else {
      next()
    }
    return
  }
  
  // 需要登录的页面
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
    return
  }
  
  // 需要选择机器的页面
  if (to.meta.requiresMachine) {
    // 机器登录模式直接进入
    if (isMachineLogin) {
      next()
      return
    }
    
    // 用户登录模式需要选择机器
    if (!hasSelectedMachine) {
      next('/machines')
      return
    }
  }
  
  // 需要管理员权限的页面
  if (to.meta.requiresAdmin && authStore.userRole !== 'admin') {
    next('/')
    return
  }
  
  next()
})

export default router
