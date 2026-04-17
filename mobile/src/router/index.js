/**
 * 路由配置文件
 * 
 * 本文件定义了整个应用的路由规则。
 * 
 * 对于新手：
 * - 路由就是 URL 路径与 Vue 组件的映射关系
 * - createWebHashHistory 使用 URL 中的 # 后面的内容作为路由（如 #/userlist）
 * - meta: { requiresAuth: true } 表示该页面需要登录才能访问
 * - 直接 import 组件，应用启动时一次性加载，避免路由切换时白屏
 */

import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

import Login from '@/views/mobile/auth/Login.vue'
import Index from '@/views/mobile/dashboard/Index.vue'
import TermList from '@/views/mobile/crud/list/TermList.vue'
import AddTerm from '@/views/mobile/crud/add/AddTerm.vue'
import DeptList from '@/views/mobile/crud/list/DeptList.vue'
import AddDept from '@/views/mobile/crud/add/AddDept.vue'
import UserList from '@/views/mobile/crud/list/UserList.vue'
import LabAdminList from '@/views/mobile/crud/list/LabAdminList.vue'
import SxsList from '@/views/mobile/crud/list/SxsList.vue'
import RecordList from '@/views/mobile/crud/list/RecordList.vue'
import AddSxs from '@/views/mobile/crud/add/AddSxs.vue'
import AddUser from '@/views/mobile/crud/add/AddUser.vue'
import AddRecord from '@/views/mobile/crud/add/AddRecord.vue'
import AddMaintain from '@/views/mobile/crud/add/AddMaintain.vue'
import ReportMaintenance from '@/views/mobile/crud/add/ReportMaintenance.vue'
import EditRecord from '@/views/mobile/crud/edit/EditRecord.vue'
import EditSxs from '@/views/mobile/crud/edit/EditSxs.vue'
import EditDept from '@/views/mobile/crud/edit/EditDept.vue'
import EditUser from '@/views/mobile/crud/edit/EditUser.vue'
import EditUserRole from '@/views/mobile/crud/edit/EditUserRole.vue'
import EditCommon from '@/views/mobile/crud/edit/EditCommon.vue'
import Info from '@/views/mobile/crud/Info.vue'
import LabResourceDashboard from '@/views/mobile/dashboard/LabResourceDashboard.vue'
import Profile from '@/views/mobile/user/Profile.vue'
import EditProfile from '@/views/mobile/user/EditProfile.vue'
import ChangePassword from '@/views/mobile/auth/ChangePassword.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  
  {
    path: '/',
    name: 'Index',
    component: Index,
    meta: { requiresAuth: true }
  },

  {
    path: '/term',
    name: 'Term',
    component: TermList,
    meta: { requiresAuth: true }
  },
  {
    path: '/addterm',
    name: 'AddTerm',
    component: AddTerm,
    meta: { requiresAuth: true }
  },

  {
    path: '/deptlist',
    name: 'DeptList',
    component: DeptList,
    meta: { requiresAuth: true }
  },
  {
    path: '/adddept',
    name: 'AddDept',
    component: AddDept,
    meta: { requiresAuth: true }
  },

  {
    path: '/userlist/:id?',
    name: 'UserList',
    component: UserList,
    meta: { requiresAuth: true }
  },
  {
    path: '/lab-admin-list',
    name: 'LabAdminList',
    component: LabAdminList,
    meta: { requiresAuth: true }
  },

  {
    path: '/listsxs/:id?',
    name: 'ListSxs',
    component: SxsList,
    meta: { requiresAuth: true }
  },
  {
    path: '/listsxsinfo/:id?',
    name: 'ListSxsInfo',
    component: RecordList,
    meta: { requiresAuth: true }
  },
  {
    path: '/addsxs',
    name: 'AddSxs',
    component: AddSxs,
    meta: { requiresAuth: true }
  },

  {
    path: '/adduser/:id?',
    name: 'AddUser',
    component: AddUser,
    meta: { requiresAuth: true }
  },

  {
    path: '/add-record',
    name: 'AddRecord',
    component: AddRecord,
    meta: { requiresAuth: true }
  },

  {
    path: '/addmaintain/:sxsid?',
    name: 'AddMaintain',
    component: AddMaintain,
    meta: { requiresAuth: true }
  },

  {
    path: '/report-maintenance',
    name: 'ReportMaintenance',
    component: ReportMaintenance,
    meta: { requiresAuth: true }
  },

  {
    path: '/edit-record/:id',
    name: 'EditRecord',
    component: EditRecord,
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-sxs/:id',
    name: 'EditSxs',
    component: EditSxs,
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-dept/:id',
    name: 'EditDept',
    component: EditDept,
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-user/:id',
    name: 'EditUserAdmin',
    component: EditUser,
    meta: { requiresAuth: true }
  },
  {
    path: '/update-user',
    name: 'UpdateUser',
    component: EditUser,
    meta: { requiresAuth: true }
  },
  {
    path: '/update-user-role/:id?',
    name: 'UpdateUserRole',
    component: EditUserRole,
    meta: { requiresAuth: true }
  },
  {
    path: '/update/:id?',
    name: 'Update',
    component: EditCommon,
    meta: { requiresAuth: true }
  },

  {
    path: '/error',
    name: 'Error',
    component: Info,
    meta: { requiresAuth: true }
  },
  {
    path: '/info',
    name: 'Info',
    component: Info,
    meta: { requiresAuth: true }
  },

  {
    path: '/lab-resource-management',
    name: 'LabResourceDashboard',
    component: LabResourceDashboard,
    meta: { requiresAuth: true }
  },

  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },

  {
    path: '/edit-profile',
    name: 'EditProfile',
    component: EditProfile,
    meta: { requiresAuth: true }
  },

  {
    path: '/change-password',
    name: 'ChangePassword',
    component: ChangePassword,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

const _originalPush = router.push
router.push = (to) => {
  return _originalPush.call(router, to).catch((err) => {
    try {
      const targetPath = typeof to === 'string' ? to : (to && to.path) ? to.path : router.resolve(to).path
      if (targetPath === '/') {
        return router.replace('/').catch(() => { window.location.href = '/' })
      }
    } catch (_) { }
    throw err
  })
}

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
