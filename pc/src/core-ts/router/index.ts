/**
 * 路由配置文件
 */

import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import { useUserStore } from '../store/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/pc/auth/Login.vue')
  },
  
  {
    path: '/',
    name: 'Index',
    component: () => import('@/views/pc/dashboard/Index.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/term',
    name: 'Term',
    component: () => import('@/views/pc/crud/list/TermList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/addterm',
    name: 'AddTerm',
    component: () => import('@/views/pc/crud/add/AddTerm.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/deptlist',
    name: 'DeptList',
    component: () => import('@/views/pc/crud/list/DeptList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/adddept',
    name: 'AddDept',
    component: () => import('@/views/pc/crud/add/AddDept.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/userlist/:id?',
    name: 'UserList',
    component: () => import('@/views/pc/crud/list/UserList.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/listsxs/:id?',
    name: 'ListSxs',
    component: () => import('@/views/pc/crud/list/SxsList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/listsxsinfo/:id?',
    name: 'ListSxsInfo',
    component: () => import('@/views/pc/crud/list/RecordList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/addsxs',
    name: 'AddSxs',
    component: () => import('@/views/pc/crud/add/AddSxs.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/listsxsclass/:id?',
    name: 'ListSxsClass',
    component: () => import('@/views/pc/crud/list/ClassList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/addclass/:sxsid?',
    name: 'AddClass',
    component: () => import('@/views/pc/crud/add/AddClass.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/add-record',
    name: 'AddRecord',
    component: () => import('@/views/pc/crud/add/AddRecord.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/listsxsmaintain/:id?',
    name: 'ListSxsMaintain',
    component: () => import('@/views/pc/crud/list/MaintainList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/listsxsfault/:id?',
    name: 'ListSxsFault',
    component: () => import('@/views/pc/crud/list/RecordList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/record-detail/:type/:id',
    name: 'RecordDetail',
    component: () => import('@/views/pc/crud/detail/RecordDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/add',
    name: 'Add',
    component: () => import('@/views/pc/crud/add/AddMaintain.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/addmaintain/:sxsid?',
    name: 'AddMaintain',
    component: () => import('@/views/pc/crud/add/AddMaintain.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/report-maintenance',
    name: 'ReportMaintenance',
    component: () => import('@/views/pc/crud/add/ReportMaintenance.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/adduser/:id?',
    name: 'AddUser',
    component: () => import('@/views/pc/crud/add/AddUser.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/edit-class/:id',
    name: 'EditClass',
    component: () => import('@/views/pc/crud/edit/EditClass.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-sxs/:id',
    name: 'EditSxs',
    component: () => import('@/views/pc/crud/edit/EditSxs.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-record/:id',
    name: 'EditRecord',
    component: () => import('@/views/pc/crud/edit/EditRecord.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-maintain/:id',
    name: 'EditMaintain',
    component: () => import('@/views/pc/crud/edit/EditCommon.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-dept/:id',
    name: 'EditDept',
    component: () => import('@/views/pc/crud/edit/EditDept.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-user/:id',
    name: 'EditUserAdmin',
    component: () => import('@/views/pc/crud/edit/EditUser.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/update-user',
    name: 'UpdateUser',
    component: () => import('@/views/pc/crud/edit/EditUser.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/update-user-role/:id?',
    name: 'UpdateUserRole',
    component: () => import('@/views/pc/crud/edit/EditUserRole.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/update/:id?',
    name: 'Update',
    component: () => import('@/views/pc/crud/edit/EditCommon.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/error',
    name: 'Error',
    component: () => import('@/views/pc/crud/Info.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/info',
    name: 'Info',
    component: () => import('@/views/pc/crud/Info.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/workorder-center',
    name: 'WorkOrderCenter',
    component: () => import('@/views/pc/common/WorkOrderCenter.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/workorder/:id',
    name: 'WorkOrderDetail',
    component: () => import('@/views/pc/common/WorkOrderDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/global-search',
    name: 'GlobalSearch',
    component: () => import('@/views/pc/common/GlobalSearch.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ai-assistant',
    name: 'AIAssistant',
    component: () => import('@/views/pc/common/AIAssistant.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/archive-term',
    name: 'ArchiveTerm',
    component: () => import('@/views/pc/lab/ArchiveTerm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/archived-terms',
    name: 'ArchivedTermList',
    component: () => import('@/views/pc/lab/ArchivedTermList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/view-archived-records/:id',
    name: 'ViewArchivedRecords',
    component: () => import('@/views/pc/lab/ArchivedRecordDashboard.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/comprehensive-stats',
    name: 'ComprehensiveStats',
    component: () => import('@/views/pc/stats/ComprehensiveStats.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/assign-permission/:id?',
    name: 'AssignPermission',
    component: () => import('@/views/pc/user/AssignPermission.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/assign-role/:id',
    name: 'AssignRole',
    component: () => import('@/views/pc/crud/edit/AssignRole.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/import',
    name: 'Import',
    component: () => import('@/views/pc/lab/Import.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/import-class/:sxsid?',
    name: 'ImportClass',
    component: () => import('@/views/pc/lab/Import.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/import-sxs',
    name: 'ImportSXS',
    component: () => import('@/views/pc/lab/Import.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/import-user',
    name: 'ImportUser',
    component: () => import('@/views/pc/lab/Import.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/personal-teaching',
    name: 'PersonalTeachingDashboard',
    component: () => import('@/views/pc/dashboard/PersonalTeachingDashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user-management',
    name: 'UserManagementDashboard',
    component: () => import('@/views/pc/dashboard/UserManagementDashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/lab-resource-management',
    name: 'LabResourceDashboard',
    component: () => import('@/views/pc/dashboard/LabResourceDashboard.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/device-list',
    name: 'DeviceList',
    component: () => import('@/views/pc/lab/LabComputers.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/import-device',
    name: 'ImportDevice',
    component: () => import('@/views/pc/lab/Import.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/add-device',
    name: 'AddDevice',
    component: () => import('@/views/pc/crud/add/AddDevice.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-device/:id',
    name: 'EditDevice',
    component: () => import('@/views/pc/crud/add/EditDevice.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/cleanup-user-data',
    name: 'CleanupUserData',
    component: () => import('@/views/pc/user/CleanupUserData.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/change-password',
    name: 'ChangePassword',
    component: () => import('@/views/pc/auth/ChangePassword.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/backup-manage',
    name: 'BackupManage',
    component: () => import('@/views/pc/system/BackupManage.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/system-admin',
    name: 'SystemAdmin',
    component: () => import('@/views/pc/system/SystemAdmin.vue'),
    meta: { requiresAuth: true, requiredRole: 'systemadmin' }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

const _originalPush = router.push
router.push = function(to: any) {
  return (_originalPush as any).call(router, to).catch((err: any) => {
    try {
      const targetPath = typeof to === 'string' ? to : (to && to.path) ? to.path : router.resolve(to).path
      if (targetPath === '/') {
        return router.replace('/').catch(() => { window.location.href = '/' })
      }
    } catch (error) { }
    throw err
  })
}

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const userStr = sessionStorage.getItem('user')
  const firstLoginFlag = sessionStorage.getItem('first_login')
  
  let isAuthenticated = false
  let userData: any = null
  
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
      sessionStorage.removeItem('first_login')
    }
    isAuthenticated = false
  }

  if (to.path === '/login' && isAuthenticated) {
    return next('/')
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login')
  }

  if (isAuthenticated && firstLoginFlag === 'true' && to.path !== '/change-password') {
    return next('/change-password')
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
