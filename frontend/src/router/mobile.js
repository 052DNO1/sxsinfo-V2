import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/core/store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/mobile/auth/Login.vue')
  },
  {
    path: '/',
    name: 'Index',
    component: () => import('@/views/mobile/dashboard/Index.vue'),
    meta: { requiresAuth: true }
  },
  
  // ========== 通用列表页面 - 使用统一的 List.vue ==========
  {
    path: '/term',
    name: 'Term',
    component: () => import('@/views/mobile/crud/List.vue'),
    meta: { requiresAuth: true, listType: 'term' }
  },
  {
    path: '/deptlist',
    name: 'DeptList',
    component: () => import('@/views/mobile/crud/List.vue'),
    meta: { requiresAuth: true, listType: 'dept' }
  },
  {
    path: '/userlist/:id?',
    name: 'UserList',
    component: () => import('@/views/mobile/crud/List.vue'),
    meta: { requiresAuth: true, listType: 'user' }
  },
  {
    path: '/lab-admin-list',
    name: 'LabAdminList',
    component: () => import('@/views/mobile/crud/List.vue'),
    meta: { requiresAuth: true, listType: 'labadmin' }
  },
  {
    path: '/listsxs/:id?',
    name: 'ListSxs',
    component: () => import('@/views/mobile/crud/List.vue'),
    meta: { requiresAuth: true, listType: 'sxs' }
  },
  {
    path: '/listsxsinfo/:id?',
    name: 'ListSxsInfo',
    component: () => import('@/views/mobile/crud/List.vue'),
    meta: { requiresAuth: true, listType: 'record' }
  },

  // ========== 通用添加页面 - 使用统一的 Add.vue ==========
  {
    path: '/addterm',
    name: 'AddTerm',
    component: () => import('@/views/mobile/crud/Add.vue'),
    meta: { requiresAuth: true, formType: 'term' }
  },
  {
    path: '/adddept',
    name: 'AddDept',
    component: () => import('@/views/mobile/crud/Add.vue'),
    meta: { requiresAuth: true, formType: 'dept' }
  },
  {
    path: '/addsxs',
    name: 'AddSxs',
    component: () => import('@/views/mobile/crud/Add.vue'),
    meta: { requiresAuth: true, formType: 'sxs' }
  },
  {
    path: '/adduser/:id?',
    name: 'AddUser',
    component: () => import('@/views/mobile/crud/Add.vue'),
    meta: { requiresAuth: true, formType: 'user' }
  },
  {
    path: '/add-record',
    name: 'AddRecord',
    component: () => import('@/views/mobile/crud/Add.vue'),
    meta: { requiresAuth: true, formType: 'record' }
  },
  {
    path: '/addmaintain/:sxsid?',
    name: 'AddMaintain',
    component: () => import('@/views/mobile/crud/Add.vue'),
    meta: { requiresAuth: true, formType: 'maintain' }
  },
  {
    path: '/report-maintenance',
    name: 'ReportMaintenance',
    component: () => import('@/views/mobile/crud/Add.vue'),
    meta: { requiresAuth: true, formType: 'report' }
  },

  // ========== 通用编辑/更新页面 - 使用统一的 Update.vue ==========
  {
    path: '/edit-record/:id',
    name: 'EditRecord',
    component: () => import('@/views/mobile/crud/Update.vue'),
    meta: { requiresAuth: true, formType: 'record', mode: 'edit' }
  },
  {
    path: '/edit-sxs/:id',
    name: 'EditSxs',
    component: () => import('@/views/mobile/crud/Update.vue'),
    meta: { requiresAuth: true, formType: 'sxs', mode: 'edit' }
  },
  {
    path: '/edit-dept/:id',
    name: 'EditDept',
    component: () => import('@/views/mobile/crud/Update.vue'),
    meta: { requiresAuth: true, formType: 'dept', mode: 'edit' }
  },
  {
    path: '/edit-user/:id',
    name: 'EditUserAdmin',
    component: () => import('@/views/mobile/crud/Update.vue'),
    meta: { requiresAuth: true, formType: 'user', mode: 'edit' }
  },
  {
    path: '/update-user',
    name: 'UpdateUser',
    component: () => import('@/views/mobile/crud/Update.vue'),
    meta: { requiresAuth: true, formType: 'user', mode: 'update' }
  },
  {
    path: '/update-user-role/:id?',
    name: 'UpdateUserRole',
    component: () => import('@/views/mobile/crud/Update.vue'),
    meta: { requiresAuth: true, formType: 'userrole', mode: 'edit' }
  },
  {
    path: '/update/:id?',
    name: 'Update',
    component: () => import('@/views/mobile/crud/Update.vue'),
    meta: { requiresAuth: true, formType: 'common', mode: 'edit' }
  },

  // ========== 信息和错误页面 ==========
  {
    path: '/error',
    name: 'Error',
    component: () => import('@/views/mobile/crud/Info.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/info',
    name: 'Info',
    component: () => import('@/views/mobile/crud/Info.vue'),
    meta: { requiresAuth: true }
  },

  // ========== Dashboard 页面 ==========
  {
    path: '/lab-resource-management',
    name: 'LabResourceDashboard',
    component: () => import('@/views/mobile/dashboard/LabResourceDashboard.vue'),
    meta: { requiresAuth: true }
  },

  // ========== 用户相关页面 ==========
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/mobile/user/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-profile',
    name: 'EditProfile',
    component: () => import('@/views/mobile/user/EditProfile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: () => import('@/views/mobile/auth/ChangePassword.vue'),
    meta: { requiresAuth: true }
  },
  
  // ========== 其他功能页面 ==========
  {
    path: '/global-search',
    name: 'GlobalSearch',
    component: () => import('@/views/mobile/common/GlobalSearch.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/messages',
    name: 'MessageList',
    component: () => import('@/views/mobile/common/MessageList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ai-assistant',
    name: 'AiAssistant',
    component: () => import('@/views/mobile/common/AiAssistant.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/archive-term',
    name: 'ArchiveTerm',
    component: () => import('@/views/mobile/lab/ArchiveTerm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/import-data',
    name: 'ImportData',
    component: () => import('@/views/mobile/lab/Import.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/assign-permission',
    name: 'AssignPermission',
    component: () => import('@/views/mobile/user/AssignPermission.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/cleanup-user-data',
    name: 'CleanupUserData',
    component: () => import('@/views/mobile/user/CleanupUserData.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/stats/comprehensive',
    name: 'ComprehensiveStats',
    component: () => import('@/views/mobile/stats/ComprehensiveStats.vue'),
    meta: { requiresAuth: true }
  },
  
  // ========== 兜底路由 - 404 ==========
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const userStr = sessionStorage.getItem('user')
  
  let isAuthenticated = false
  let userData = null
  
  if (userStr) {
    try {
      userData = JSON.parse(userStr)
    } catch {
      userData = null
    }
  }
  
  if (token && userData && userData.id) {
    isAuthenticated = true
  } else {
    if (token || userStr) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      sessionStorage.removeItem('user')
    }
    isAuthenticated = false
  }

  if (to.path === '/login' && isAuthenticated) {
    return next('/')
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login')
  }

  if (to.path.startsWith('/listsxs/')) {
    const match = to.path.match(/^\/listsxs\/(\d+)/)
    const qtype = match ? match[1] : null
    if (qtype && !['2', '4'].includes(String(qtype))) {
      return next('/lab-resource-management')
    }
  }

  next()
})

export default router
