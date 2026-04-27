/**
 * 路由配置文件
 * 
 * 本文件定义了整个应用的路由规则
 * 
 * 对于新手来说，路由就是 URL 路径到 Vue 组件的映射关系。
 * - 路由就是 URL 路径和 Vue 组件的映射关系
 * - createWebHashHistory 使用 URL 中的 # 后面的内容作为路由（例如：#/userlist）
 * - meta: { requiresAuth: true } 表示该页面需要登录才能访问
 * - 使用 () => import() 实现路由懒加载，按需加载页面组件
 */

import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/core/store/user'

// 核心页面同步加载（首屏需要）
import Login from '@/views/pc/auth/Login.vue'
import Index from '@/views/pc/dashboard/Index.vue'

// 其他页面使用懒加载，按需导入
const TermList = () => import('@/views/pc/crud/list/TermList.vue')
const AddTerm = () => import('@/views/pc/crud/add/AddTerm.vue')
const DeptList = () => import('@/views/pc/crud/list/DeptList.vue')
const AddDept = () => import('@/views/pc/crud/add/AddDept.vue')
const UserList = () => import('@/views/pc/crud/list/UserList.vue')
const SxsList = () => import('@/views/pc/crud/list/SxsList.vue')
const RecordList = () => import('@/views/pc/crud/list/RecordList.vue')
const RecordDetail = () => import('@/views/pc/crud/detail/RecordDetail.vue')
const AddSxs = () => import('@/views/pc/crud/add/AddSxs.vue')
const ClassList = () => import('@/views/pc/crud/list/ClassList.vue')
const AddClass = () => import('@/views/pc/crud/add/AddClass.vue')
const AddRecord = () => import('@/views/pc/crud/add/AddRecord.vue')
const MaintainList = () => import('@/views/pc/crud/list/MaintainList.vue')
const AddMaintain = () => import('@/views/pc/crud/add/AddMaintain.vue')
const ReportMaintenance = () => import('@/views/pc/crud/add/ReportMaintenance.vue')
const AddUser = () => import('@/views/pc/crud/add/AddUser.vue')
const EditClass = () => import('@/views/pc/crud/edit/EditClass.vue')
const EditSxs = () => import('@/views/pc/crud/edit/EditSxs.vue')
const EditRecord = () => import('@/views/pc/crud/edit/EditRecord.vue')
const EditCommon = () => import('@/views/pc/crud/edit/EditCommon.vue')
const EditDept = () => import('@/views/pc/crud/edit/EditDept.vue')
const EditUser = () => import('@/views/pc/crud/edit/EditUser.vue')
const EditUserRole = () => import('@/views/pc/crud/edit/EditUserRole.vue')
const Info = () => import('@/views/pc/crud/Info.vue')
const WorkOrderCenter = () => import('@/views/pc/common/WorkOrderCenter.vue')
const WorkOrderDetail = () => import('@/views/pc/common/WorkOrderDetail.vue')
const GlobalSearch = () => import('@/views/pc/common/GlobalSearch.vue')
const AIAssistant = () => import('@/views/pc/common/AIAssistant.vue')
const ArchiveTerm = () => import('@/views/pc/lab/ArchiveTerm.vue')
const ArchivedTermList = () => import('@/views/pc/lab/ArchivedTermList.vue')
const ArchivedRecordDashboard = () => import('@/views/pc/lab/ArchivedRecordDashboard.vue')
const ComprehensiveStats = () => import('@/views/pc/stats/ComprehensiveStats.vue')
const AssignPermission = () => import('@/views/pc/user/AssignPermission.vue')
const AssignRole = () => import('@/views/pc/crud/edit/AssignRole.vue')
const Import = () => import('@/views/pc/lab/Import.vue')
const PersonalTeachingDashboard = () => import('@/views/pc/dashboard/PersonalTeachingDashboard.vue')
const UserManagementDashboard = () => import('@/views/pc/dashboard/UserManagementDashboard.vue')
const LabResourceDashboard = () => import('@/views/pc/dashboard/LabResourceDashboard.vue')
const LabComputers = () => import('@/views/pc/lab/LabComputers.vue')
const AddDevice = () => import('@/views/pc/crud/add/AddDevice.vue')
const EditDevice = () => import('@/views/pc/crud/add/EditDevice.vue')
const CleanupUserData = () => import('@/views/pc/user/CleanupUserData.vue')
const ChangePassword = () => import('@/views/pc/auth/ChangePassword.vue')
const BackupManage = () => import('@/views/pc/system/BackupManage.vue')
const CacheConfig = () => import('@/views/pc/system/CacheConfig.vue')
const OperationLog = () => import('@/views/pc/system/OperationLog.vue')

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
    path: '/listsxsclass/:id?',
    name: 'ListSxsClass',
    component: ClassList,
    meta: { requiresAuth: true }
  },
  {
    path: '/addclass/:sxsid?',
    name: 'AddClass',
    component: AddClass,
    meta: { requiresAuth: true }
  },

  {
    path: '/add-record',
    name: 'AddRecord',
    component: AddRecord,
    meta: { requiresAuth: true }
  },

  {
    path: '/listsxsmaintain/:id?',
    name: 'ListSxsMaintain',
    component: MaintainList,
    meta: { requiresAuth: true }
  },
  {
    path: '/listsxsfault/:id?',
    name: 'ListSxsFault',
    component: RecordList,
    meta: { requiresAuth: true }
  },
  {
    path: '/record-detail/:type/:id',
    name: 'RecordDetail',
    component: RecordDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/add',
    name: 'Add',
    component: AddMaintain,
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
    path: '/adduser/:id?',
    name: 'AddUser',
    component: AddUser,
    meta: { requiresAuth: true }
  },

  {
    path: '/edit-class/:id',
    name: 'EditClass',
    component: EditClass,
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-sxs/:id',
    name: 'EditSxs',
    component: EditSxs,
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-record/:id',
    name: 'EditRecord',
    component: EditRecord,
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-maintain/:id',
    name: 'EditMaintain',
    component: EditCommon,
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
    path: '/workorder-center',
    name: 'WorkOrderCenter',
    component: WorkOrderCenter,
    meta: { requiresAuth: true }
  },
  {
    path: '/workorder/:id',
    name: 'WorkOrderDetail',
    component: WorkOrderDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/global-search',
    name: 'GlobalSearch',
    component: GlobalSearch,
    meta: { requiresAuth: true }
  },
  {
    path: '/ai-assistant',
    name: 'AIAssistant',
    component: AIAssistant,
    meta: { requiresAuth: true }
  },

  {
    path: '/archive-term',
    name: 'ArchiveTerm',
    component: ArchiveTerm,
    meta: { requiresAuth: true }
  },
  {
    path: '/archived-terms',
    name: 'ArchivedTermList',
    component: ArchivedTermList,
    meta: { requiresAuth: true }
  },
  {
    path: '/view-archived-records/:id',
    name: 'ViewArchivedRecords',
    component: ArchivedRecordDashboard,
    meta: { requiresAuth: true }
  },

  {
    path: '/comprehensive-stats',
    name: 'ComprehensiveStats',
    component: ComprehensiveStats,
    meta: { requiresAuth: true }
  },

  {
    path: '/assign-permission/:id?',
    name: 'AssignPermission',
    component: AssignPermission,
    meta: { requiresAuth: true }
  },
  {
    path: '/assign-role/:id',
    name: 'AssignRole',
    component: AssignRole,
    meta: { requiresAuth: true }
  },

  {
    path: '/import',
    name: 'Import',
    component: Import,
    meta: { requiresAuth: true }
  },
  {
    path: '/import-class/:sxsid?',
    name: 'ImportClass',
    component: Import,
    meta: { requiresAuth: true }
  },
  {
    path: '/import-sxs',
    name: 'ImportSXS',
    component: Import,
    meta: { requiresAuth: true }
  },
  {
    path: '/import-user',
    name: 'ImportUser',
    component: Import,
    meta: { requiresAuth: true }
  },

  {
    path: '/personal-teaching',
    name: 'PersonalTeachingDashboard',
    component: PersonalTeachingDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/user-management',
    name: 'UserManagementDashboard',
    component: UserManagementDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/lab-resource-management',
    name: 'LabResourceDashboard',
    component: LabResourceDashboard,
    meta: { requiresAuth: true }
  },

  {
    path: '/device-list',
    name: 'DeviceList',
    component: LabComputers,
    meta: { requiresAuth: true }
  },
  {
    path: '/import-device',
    name: 'ImportDevice',
    component: Import,
    meta: { requiresAuth: true }
  },
  {
    path: '/add-device',
    name: 'AddDevice',
    component: AddDevice,
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-device/:id',
    name: 'EditDevice',
    component: EditDevice,
    meta: { requiresAuth: true }
  },

  {
    path: '/cleanup-user-data',
    name: 'CleanupUserData',
    component: CleanupUserData,
    meta: { requiresAuth: true }
  },

  {
    path: '/change-password',
    name: 'ChangePassword',
    component: ChangePassword,
    meta: { requiresAuth: true }
  },

  {
    path: '/backup-manage',
    name: 'BackupManage',
    component: BackupManage,
    meta: { requiresAuth: true }
  },
  {
    path: '/cache-config',
    name: 'CacheConfig',
    component: CacheConfig,
    meta: { requiresAuth: true, requiredRole: 'systemadmin' }
  },
  {
    path: '/operation-log',
    name: 'OperationLog',
    component: OperationLog,
    meta: { requiresAuth: true, requiredRole: 'systemadmin' }
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
    } catch (error) { }throw err
  })
}

router.beforeEach((to, from, next) => {
  const token = sessionStorage.getItem('access_token')
  const userStr = sessionStorage.getItem('user')
  const firstLoginFlag = sessionStorage.getItem('first_login')
  
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
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('refresh_token')
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

  if (isAuthenticated && firstLoginFlag === 'true' && to.path === '/' && from.path !== '/change-password') {
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
