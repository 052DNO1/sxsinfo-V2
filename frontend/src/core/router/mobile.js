/**
 * 移动端路由配置文件
 */

import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/core/store/user'

// 核心页面同步加载（首屏需要）
import Login from '@/views/mobile/auth/Login.vue'
import Index from '@/views/mobile/dashboard/Index.vue'

// 其他页面使用懒加载，按需导入
const TermList = () => import('@/views/mobile/crud/list/TermList.vue')
const AddTerm = () => import('@/views/mobile/crud/add/AddTerm.vue')
const DeptList = () => import('@/views/mobile/crud/list/DeptList.vue')
const AddDept = () => import('@/views/mobile/crud/add/AddDept.vue')
const UserList = () => import('@/views/mobile/crud/list/UserList.vue')
const SxsList = () => import('@/views/mobile/crud/list/SxsList.vue')
const RecordList = () => import('@/views/mobile/crud/list/RecordList.vue')
const RecordDetail = () => import('@/views/mobile/crud/detail/RecordDetail.vue')
const AddSxs = () => import('@/views/mobile/crud/add/AddSxs.vue')
const ClassList = () => import('@/views/mobile/crud/list/ClassList.vue')
const AddClass = () => import('@/views/mobile/crud/add/AddClass.vue')
const AddRecord = () => import('@/views/mobile/crud/add/AddRecord.vue')
const MaintainList = () => import('@/views/mobile/crud/list/MaintainList.vue')
const AddMaintain = () => import('@/views/mobile/crud/add/AddMaintain.vue')
const ReportMaintenance = () => import('@/views/mobile/crud/add/ReportMaintenance.vue')
const AddUser = () => import('@/views/mobile/crud/add/AddUser.vue')
const AddDevice = () => import('@/views/mobile/crud/add/AddDevice.vue')
const DeviceList = () => import('@/views/mobile/crud/list/DeviceList.vue')
const EditClass = () => import('@/views/mobile/crud/edit/EditClass.vue')
const EditSxs = () => import('@/views/mobile/crud/edit/EditSxs.vue')
const EditDevice = () => import('@/views/mobile/crud/edit/EditDevice.vue')
const EditRecord = () => import('@/views/mobile/crud/edit/EditRecord.vue')
const EditCommon = () => import('@/views/mobile/crud/edit/EditCommon.vue')
const EditDept = () => import('@/views/mobile/crud/edit/EditDept.vue')
const EditUser = () => import('@/views/mobile/crud/edit/EditUser.vue')
const EditUserRole = () => import('@/views/mobile/crud/edit/EditUserRole.vue')
const Info = () => import('@/views/mobile/crud/Info.vue')
const MessageList = () => import('@/views/mobile/common/MessageList.vue')
const ArchiveTerm = () => import('@/views/mobile/lab/ArchiveTerm.vue')
const ArchivedTermList = () => import('@/views/mobile/lab/ArchivedTermList.vue')
const ArchivedRecordList = () => import('@/views/mobile/lab/ArchivedRecordList.vue')
const LabResourceDashboard = () => import('@/views/mobile/dashboard/LabResourceDashboard.vue')
const Toolbox = () => import('@/views/mobile/dashboard/Toolbox.vue')
const Profile = () => import('@/views/mobile/user/Profile.vue')
const EditProfile = () => import('@/views/mobile/user/EditProfile.vue')
const ChangePassword = () => import('@/views/mobile/auth/ChangePassword.vue')
const OperationLog = () => import('@/views/mobile/system/OperationLog.vue')

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
    path: '/record-list',
    name: 'RecordList',
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
    path: '/classlist',
    name: 'ClassList',
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
    path: '/maintain-list',
    name: 'MaintainList',
    component: MaintainList,
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
    path: '/add-device',
    name: 'AddDevice',
    component: AddDevice,
    meta: { requiresAuth: true }
  },

  {
    path: '/device-list',
    name: 'DeviceList',
    component: DeviceList,
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
    path: '/edit-device/:id',
    name: 'EditDevice',
    component: EditDevice,
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
    path: '/message-list',
    name: 'MessageList',
    component: MessageList,
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
    path: '/archived-records/:id',
    name: 'ArchivedRecordList',
    component: ArchivedRecordList,
    meta: { requiresAuth: true }
  },

  {
    path: '/lab-resource-management',
    name: 'LabResourceDashboard',
    component: LabResourceDashboard,
    meta: { requiresAuth: true }
  },

  {
    path: '/toolbox',
    name: 'Toolbox',
    component: Toolbox,
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
  },

  {
    path: '/operation-log',
    name: 'OperationLog',
    component: OperationLog,
    meta: { requiresAuth: true }
  },

  {
    path: '/record-detail/:id',
    name: 'RecordDetail',
    component: RecordDetail,
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
    } catch (error) { }
    throw err
  })
}

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
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

  if (isAuthenticated && firstLoginFlag === 'true' && to.path === '/' && from.path !== '/change-password') {
    return next('/change-password')
  }

  next()
})

export default router
