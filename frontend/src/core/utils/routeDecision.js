/**
 * 路由决策工具
 * 
 * 这是前后端分离架构的核心路由管理文件?
 * 根据后端返回的业务数据（action_type, resource_type），前端自己决定跳转到哪里?
 * 
 * 主要功能?
 * 1. 根据操作类型决定路由（编辑、查看、添加、删除等?
 * 2. 根据资源类型决定路由（实训室、记录、用户、部门等?
 * 3. 前端路由?API 路径的映?
 * 
 * 对于新手?
 * - 后端只返回业务数据，不返回路由路?
 * - 前端根据 action_type（操作类型）�?resource_type（资源类型）决定跳转
 * - 这样前后端完全解耦，前端可以独立修改路由结构
 * 
 * 使用示例?
 * ```js
 * import { decideRouteByActionType } from '@/core/utils/routeDecision'
 * 
 * // 根据操作类型获取路由
 * const route = decideRouteByActionType('edit', 'sxs', { id: 1 })
 * // 返回: '/edit-sxs/1'
 * ```
 */

// ==================== 核心路由决策函数 ====================

/**
 * 根据操作获取路由路径
 * 
 * @param {Object} action - 操作对象
 * @param {Object} routeQuery - 路由查询参数（可选）
 * @returns {string|null} 路由路径
 */
export function getActionRoute(action, routeQuery = {}) {
  if (!action) return null
  if (action.action_type && action.resource_type) {
    const context = {
      ...action.context,
      resource_id: action.resource_id,
      id: action.resource_id
    }
    if (routeQuery.qtype !== undefined) {
      context.qtype = routeQuery.qtype
    }
    return decideRouteByActionType(action.action_type, action.resource_type, context, {})
  }
  return action.url || null
}

/**
 * 根据业务操作结果决定跳转路由
 * 
 * @param {Object} responseData - API 响应数据
 * @param {Object} currentContext - 当前上下文
 * @returns {string|null} 路由路径
 */
export function decideRouteFromBusinessData(responseData, currentContext = {}) {
  if (!responseData?.action) return null

  const { action, resource_type, context = {} } = responseData

  // 创建、更新、删除操作需要跳?
  if (['created', 'updated', 'deleted'].includes(action)) {
    return decideRouteByResourceType(resource_type, context, currentContext)
  }

  return null
}

/**
 * 根据操作类型和资源类型决定路由（核心方法?
 * 
 * @param {string} actionType - 操作类型?edit', 'view', 'add', 'delete', 'navigate'
 * @param {string} resourceType - 资源类型?sxs', 'record', 'user', 'dept' �?
 * @param {Object} context - 上下文信息（包含 id、sxsid 等）
 * @param {Object} currentContext - 当前路由上下?
 * @returns {string|null} 路由路径
 * 
 * 这是路由决策的核心入口，根据不同的操作类型调用对应的处理函数
 */
export function decideRouteByActionType(actionType, resourceType, context = {}, currentContext = {}) {
  // 从上下文中提取资?ID
  const resourceId = context.resource_id || context.id || context.sxsid || context.userid || context.class_name

  // 操作类型映射?
  const actionMap = {
    'edit': () => decideEditRoute(resourceType, resourceId, context),
    'update': () => decideEditRoute(resourceType, resourceId, context),
    'view': () => decideViewRoute(resourceType, resourceId, context),
    'detail': () => decideViewRoute(resourceType, resourceId, context),
    'add': () => decideAddRoute(resourceType, context),
    'create': () => decideAddRoute(resourceType, context),
    'navigate': () => decideNavigateRoute(resourceType, context),
    'delete': () => null  // 删除操作不需要跳?
  }

  return actionMap[actionType]?.() || decideRouteByResourceType(resourceType, context, currentContext)
}

// ==================== 编辑路由决策 ====================

/**
 * 决定编辑路由
 * 
 * @param {string} resourceType - 资源类型
 * @param {number|string} resourceId - 资源 ID
 * @param {Object} context - 上下文信息
 * @returns {string} 编辑页面路由
 */
function decideEditRoute(resourceType, resourceId, context) {
  switch (resourceType) {
    case 'sxs':
      // 编辑实训室，需要保?qtype 参数
      const q = context && context.qtype !== undefined ? `?qtype=${context.qtype}` : ''
      return `/edit-sxs/${resourceId}${q}`
    case 'record':
      return `/edit-record/${resourceId}`
    case 'maintain':
      return `/edit-maintain/${resourceId}`
    case 'class':
    case 'sxs_class':
      const sxsid = context?.sxsid || context?.qtype || '4'
      return `/edit-class/${resourceId}?sxsid=${sxsid}`
    case 'user':
      return `/edit-user/${resourceId}`
    case 'user_role':
      // 分配角色
      const tid = context.tid || context.typeid || '1'
      return `/update-user-role/${resourceId}?tid=${tid}`
    case 'permission':
      // 分配权限
      const tid2 = context.tid || context.typeid || '1'
      return `/assign-permission/${resourceId}?tid=${tid2}`
    case 'student':
      return `/edit-user/${resourceId}`
    case 'grade':
      return `/edit-record/${resourceId}`
    case 'dept':
      return `/edit-dept/${resourceId}`
    default:
      return resourceId ? `/update/${resourceId}` : '/update'
  }
}

// ==================== 查看路由决策 ====================

/**
 * 决定查看路由
 * 
 * @param {string} resourceType - 资源类型
 * @param {number|string} resourceId - 资源 ID
 * @param {Object} context - 上下文信?
 * @returns {string} 查看页面路由
 */
function decideViewRoute(resourceType, resourceId, context) {
  switch (resourceType) {
    case 'sxs':
      if (context.qtype !== undefined) {
        return `/listsxsinfo/${context.qtype}?type=detail&id=${resourceId}`
      }
      return `/listsxsinfo?id=${resourceId}`
    case 'sxs_class':
      if (resourceId) return `/listsxsclass/${resourceId}`
      return '/lab-resource-management'
    case 'record':
      if (context.sxsid) return '/personal-teaching'
      return '/personal-teaching'
    case 'sxs_record':
      if (context.qtype !== undefined && context.type !== undefined) {
        return `/listsxsinfo/${context.qtype}?type=${context.type}`
      }
      if (context.sxsid) return '/personal-teaching'
      return '/personal-teaching'
    case 'maintain':
      if (context.sxsid) return `/listsxsmaintain/${context.sxsid}?id=${resourceId}`
      return `/listsxsmaintain?id=${resourceId}`
    case 'class':
      if (context.sxsid) return `/listsxsclass/${context.sxsid}?id=${resourceId}`
      return '/lab-resource-management'
    case 'class_list':
      return '/lab-resource-management'
    case 'user_list':
      const typeid = context.typeid || 4
      return `/userlist/${typeid}`
    case 'equipment':
      return `/device-list?id=${resourceId}`
    default:
      return decideRouteByResourceType(resourceType, context)
  }
}

// ==================== 添加路由决策 ====================

/**
 * 决定添加路由
 * 
 * @param {string} resourceType - 资源类型
 * @param {Object} context - 上下文信?
 * @returns {string} 添加页面路由
 */
function decideAddRoute(resourceType, context) {
  switch (resourceType) {
    case 'sxs':
      return '/addsxs'
    case 'record':
      return '/add-record'
    case 'maintain':
      if (context.sxsid) return `/add?sxsid=${context.sxsid}`
      return '/add'
    case 'class':
      if (context.sxsid) return `/addclass/${context.sxsid}`
      return '/addclass'
    case 'user':
      if (context.typeid) return `/adduser/${context.typeid}`
      return '/adduser'
    case 'term':
      return '/addterm'
    case 'dept':
      return '/adddept'
    default:
      return '/add'
  }
}

// ==================== 返回路由决策 ====================

const BACK_ROUTE_CONFIG = {
  add: {
    '/adduser': { pattern: /^\/adduser(?:\/(\d+))?$/, target: (m, q) => `/userlist/${m?.[1] || q.typeid || '1'}` },
    '/addsxs': '/listsxs/4',
    '/addterm': '/term',
    '/adddept': '/deptlist',
    '/add-record': '/personal-teaching',
    '/report-maintenance': '/personal-teaching',
    '/add-device': '/device-list',
    '/addmaintain': { pattern: /^\/addmaintain(?:\/(\d+))?$/, target: (m, q) => m?.[1] && m[1] !== '0' ? `/listsxsmaintain/${m[1]}` : '/lab-resource-management' },
  },
  edit: {
    '/edit-sxs': { pattern: /^\/edit-sxs\/(\d+)$/, target: (m, q) => `/listsxs/${q.qtype || '4'}` },
    '/edit-user': { pattern: /^\/edit-user\/(\d+)$/, target: (m, q) => `/userlist/${q.typeid || q.tid || '4'}` },
    '/edit-dept': { pattern: /^\/edit-dept\/(\d+)$/, target: '/deptlist' },
    '/edit-record': { pattern: /^\/edit-record\/(\d+)$/, target: '/personal-teaching' },
    '/edit-maintain': { pattern: /^\/edit-maintain\/(\d+)$/, target: (m, q) => q.sxsid ? `/listsxsmaintain/${q.sxsid}` : '/listsxsmaintain' },
    '/edit-class': { pattern: /^\/edit-class\/(\d+)$/, target: (m, q) => q.sxsid ? `/listsxsclass` : '/lab-resource-management' },
    '/edit-device': { pattern: /^\/edit-device\/(\d+)$/, target: '/device-list' },
    '/update-user': '/',
    '/update-user-role': { pattern: /^\/update-user-role(?:\/(\d+))?$/, target: (m, q) => `/userlist/${q.tid || q.typeid || '1'}` },
    '/assign-permission': { pattern: /^\/assign-permission(?:\/(\d+))?$/, target: (m, q) => `/userlist/${q.tid || q.typeid || '1'}` },
    '/update': { pattern: /^\/update(?:\/(\d+))?$/, target: '/' },
  },
  list: {
    '/listsxs': { pattern: /^\/listsxs(?:\/(\d+))?$/, target: '/lab-resource-management' },
    '/userlist': { pattern: /^\/userlist(?:\/(\d+))?$/, target: '/user-management' },
    '/listsxsclass': { pattern: /^\/listsxsclass(?:\/(\d+))?\/?$/, target: (m, q) => `/listsxs/${q.qtype || m?.[1] || '2'}` },
    '/listsxsmaintain': { pattern: /^\/listsxsmaintain(?:\/(\d+))?$/, target: (m, q) => `/listsxs/${m?.[1] || '4'}` },
    '/listsxsfault': { pattern: /^\/listsxsfault(?:\/(\d+))?$/, target: (m, q) => `/listsxs/${m?.[1] || '4'}` },
    '/listsxsinfo': { pattern: /^\/listsxsinfo(?:\/(\d+))?$/, target: (m, q) => `/listsxs/${m?.[1] || '4'}` },
    '/term': '/term',
    '/deptlist': '/deptlist',
    '/device-list': '/listsxs/4',
  },
  dashboard: {
    '/personal-teaching': '/',
    '/user-management': '/',
    '/lab-resource-management': '/listsxs/4',
  },
  other: {
    '/change-password': '/change-password',
    '/global-search': '/global-search',
    '/workorder-center': '/workorder-center',
    '/comprehensive-stats': '/',
    '/import': '/listsxs/4',
    '/import-class': { pattern: /^\/import-class(?:\/(\d+))?$/, target: (m, q) => `/listsxs/${m?.[1] || '4'}` },
    '/import-sxs': '/listsxs/4',
    '/import-user': '/userlist/4',
    '/import-device': '/listsxs/4',
    '/cleanup-user-data': '/userlist/4',
    '/archive-term': '/',
    '/archived-terms': '/',
    '/view-archived-records': { pattern: /^\/view-archived-records\/(\d+)$/, target: '/' },
    '/error': '/',
    '/info': '/',
  }
}

function matchRouteConfig(currentPath, configSection) {
  let bestMatch = null
  let bestLength = -1
  let bestPrefix = null
  
  for (const [prefix, config] of Object.entries(configSection)) {
    if (currentPath.startsWith(prefix) || currentPath === prefix) {
      if (prefix.length > bestLength) {
        bestMatch = config
        bestLength = prefix.length
        bestPrefix = prefix
      }
    }
  }
  
  if (bestMatch) {
    if (typeof bestMatch === 'string') {
      return { target: bestMatch, prefix: bestPrefix }
    }
    if (bestMatch.pattern) {
      const match = currentPath.match(bestMatch.pattern)
      if (match) {
        return { ...bestMatch, match, prefix: bestPrefix }
      }
    }
  }
  return null
}

export function decideBackRoute(currentPath, routeQuery = {}) {
  if (routeQuery.back_url) {
    return routeQuery.back_url
  }
  
  if (currentPath.startsWith('/view-archived-records') && routeQuery.type) {
    const match = currentPath.match(/^\/view-archived-records\/(\d+)$/)
    if (match) {
      const newQuery = { ...routeQuery }
      delete newQuery.type
      const queryString = Object.keys(newQuery).length > 0 
        ? '?' + Object.entries(newQuery).map(([k, v]) => `${k}=${v}`).join('&') 
        : ''
      return `/view-archived-records/${match[1]}${queryString}`
    }
  }
  
  if (currentPath.startsWith('/addclass')) {
    const match = currentPath.match(/^\/addclass(?:\/(\d+))?$/)
    if (match && match[1]) {
      const sxsid = match[1]
      if (routeQuery.filter_sxs) {
        return `/listsxsclass/${sxsid}?filter_sxs=${routeQuery.filter_sxs}`
      }
      return `/listsxsclass/${sxsid}?filter_sxs=${sxsid}`
    }
    return '/lab-resource-management'
  }
  
  if (currentPath === '/add' || currentPath.startsWith('/addmaintain')) {
    const sxsid = routeQuery.sxsid || routeQuery.id
    if (sxsid && sxsid !== '0' && sxsid !== 0) return `/listsxsmaintain/${sxsid}`
    return '/lab-resource-management'
  }

  for (const section of Object.values(BACK_ROUTE_CONFIG)) {
    const result = matchRouteConfig(currentPath, section)
    if (result) {
      if (typeof result.target === 'function') {
        return result.target(result.match, routeQuery)
      }
      return result.target
    }
  }

  return '/'
}

// ==================== 导航路由决策 ====================

/**
 * 决定导航路由
 * 
 * @param {string} resourceType - 资源类型（导航目标）
 * @param {Object} context - 上下文信?
 * @returns {string} 导航路由
 */
function decideNavigateRoute(resourceType, context) {
  switch (resourceType) {
    case 'user_management_dashboard':
      return '/user-management'
    case 'lab_resource_management_dashboard':
      return '/lab-resource-management'
    case 'scheduling_management_dashboard':
      return '/lab-resource-management'
    case 'personal_teaching_dashboard':
      return '/personal-teaching'
    case 'home':
      return '/'
    case 'global_search':
      return '/global-search'
    case 'message_center':
      return '/workorder-center'
    case 'workorder_center':
    case 'workorder-center':
      return '/workorder-center'
    case 'change_password':
      return '/change-password'
    case 'update_user':
      return '/update-user'
    case 'import-class':
      return '/import-class'
    case 'report-maintenance':
      return '/report-maintenance'
    case 'comprehensive_stats':
      return '/comprehensive-stats'
    case 'backup_manage':
      return '/backup-manage'
    default:
      return decideRouteByResourceType(resourceType, context)
  }
}

// ==================== 资源类型路由决策 ====================

/**
 * 根据资源类型决定路由
 * 
 * @param {string} resourceType - 资源类型
 * @param {Object} context - 上下文信?
 * @param {Object} currentContext - 当前路由上下?
 * @returns {string} 路由路径
 */
function decideRouteByResourceType(resourceType, context, currentContext) {
  switch (resourceType) {
    case 'sxs':
    case 'sxs_list':
      if (context.qtype !== undefined) return `/listsxs/${context.qtype}`
      return '/listsxs/2'
    case 'record':
      if (context.sxsid) return '/personal-teaching'
      return '/personal-teaching'
    case 'maintain':
      if (context.sxsid) return `/listsxsmaintain/${context.sxsid}`
      return '/listsxsmaintain'
    case 'class':
      if (context.sxsid) return `/listsxsclass/${context.sxsid}`
      return '/lab-resource-management'
    case 'student':
      return '/personal-teaching'
    case 'user':
      if (context.typeid) return `/userlist/${context.typeid}`
      return '/user-management'
    case 'message':
    case 'workorder':
    case 'workorder-center':
      return '/workorder-center'
    default:
      return currentContext.defaultRoute || '/'
  }
}

// ==================== API 路径映射 ====================

/**
 * 根据前端路由路径获取对应?API 路径
 * 
 * @param {string} routePath - 前端路由路径
 * @param {Object} routeQuery - 路由查询参数
 * @param {Object} routeParams - 路由参数
 * @returns {string|null} API 路径
 * 
 * 这是前后端路由映射的核心，将前端路由转换为后?API 路径
 */
export function getApiPath(routePath, routeQuery = {}, routeParams = {}) {
  // ========== 添加页面 API 路径 ==========
  
  if (routePath.startsWith('/adduser')) {
    const match = routePath.match(/^\/adduser(?:\/(\d+))?$/)
    const typeid = match?.[1] || routeQuery.typeid || 1
    return `/users/`
  }
  if (routePath === '/addsxs') return '/laboratories/'
  if (routePath.startsWith('/addclass')) {
    const match = routePath.match(/^\/addclass(?:\/(\d+))?$/)
    const labId = match?.[1] || routeQuery?.laboratory_id || routeParams?.laboratory_id || 0
    return `/schedules/`
  }
  if (routePath === '/addterm') return '/semesters/'
  if (routePath === '/adddept') return '/departments/'
  if (routePath === '/add' || routePath.startsWith('/addmaintain')) {
    return '/work-orders/'
  }
  if (routePath === '/add-record') return '/records/'
  if (routePath === '/report-maintenance') {
    return '/work-orders/'
  }

  // ========== 编辑页面 API 路径 ==========
  
  if (routePath === '/update-user') return '/users/me/'
  if (routePath.startsWith('/update-user-role')) {
    const match = routePath.match(/^\/update-user-role(?:\/(\d+))?$/)
    const userId = match?.[1] || routeParams.id
    if (userId) return `/users/${userId}/update_role/`
    return null
  }
  if (routePath.startsWith('/edit-class/')) {
    const match = routePath.match(/^\/edit-class\/(\d+)$/)
    if (match) return `/schedules/${match[1]}/`
  }
  if (routePath.startsWith('/edit-sxs/')) {
    const match = routePath.match(/^\/edit-sxs\/(\d+)$/)
    if (match) return `/laboratories/${match[1]}/`
  }
  if (routePath.startsWith('/edit-record/')) {
    const match = routePath.match(/^\/edit-record\/(\d+)$/)
    if (match) return `/records/${match[1]}/`
  }
  if (routePath.startsWith('/edit-maintain/')) {
    const match = routePath.match(/^\/edit-maintain\/(\d+)$/)
    if (match) return `/work-orders/${match[1]}/`
  }
  if (routePath.startsWith('/edit-dept/')) {
    const match = routePath.match(/^\/edit-dept\/(\d+)$/)
    if (match) return `/departments/${match[1]}/`
  }
  if (routePath.startsWith('/edit-user/')) {
    const match = routePath.match(/^\/edit-user\/(\d+)$/)
    if (match) return `/users/${match[1]}/`
  }

  // ========== 列表页面 API 路径 ==========
  
  if (routePath === '/term') return '/semesters/'
  if (routePath === '/deptlist') return '/departments/'
  if (routePath.startsWith('/userlist')) {
    return '/users/'
  }
  if (routePath.startsWith('/listsxsmaintain')) {
    return '/work-orders/'
  }
  if (routePath.startsWith('/listsxsclass')) {
    return '/schedules/'
  }
  if (routePath.startsWith('/listsxsinfo')) {
    return '/laboratories/'
  }
  if (routePath.startsWith('/listsxs')) {
    return '/laboratories/'
  }
  if (routePath.startsWith('/view-archived-records')) {
    const match = routePath.match(/^\/view-archived-records(?:\/(\d+))?$/)
    return match?.[1] ? `/records/archived/${match[1]}/` : '/records/archived/'
  }

  // 其他路由直接使用
  return routePath.startsWith('/') ? routePath.substring(1) : routePath
}

/**
 * 新架?(V2) API 路径映射
 * 将老架构的路径映射到新架构?RESTful 路径
 */
export function getApiPathV2(routePath, routeQuery = {}, routeParams = {}) {
  // 清理路径，去除开头和结尾的斜?
  const cleanPath = routePath.replace(/^\/|\/$/g, '')
  
  // 1. 静态映射表 (简单路?
  const staticMap = {
    'userinfo/deptlist': 'departments/',
    'userinfo/adddept': 'departments/',
    'userinfo/batch_deldept': 'departments/batch_delete/',
    'userinfo/term': 'semesters/',
    'userinfo/addterm': 'semesters/',
    'userinfo/batch_delterm': 'semesters/batch_delete/',
    'userinfo/archive_current_term_records': 'semesters/archive_records/',
    'userinfo/logout': 'auth/logout/',
    'userinfo/change_password': 'auth/change-password/',
    'userinfo/update_userinfo': 'users/profile/',
    'userinfo/importuser': 'users/import_users/',
    'userinfo/batch_deluser': 'users/batch_delete/',
    
    'login': 'auth/login/',
    'logout': 'auth/logout/',
    'captcha': 'auth/captcha/',
    'verify_captcha': 'auth/captcha/verify/',
    'change_password': 'auth/password/change/',
    'password_reset_contact': 'auth/password-reset-contact/',
    'security_question': 'auth/security-question/',
    'get_security_question': 'auth/security-question/user/',
    'verify_security_answer': 'auth/security-question/verify/',
    'reset_password_by_security': 'auth/password/reset-by-security/',
    
    'sxs/addsxs': 'laboratories/',
    'sxs/batch_delsxs': 'laboratories/batch_delete/',
    'sxs/import_sxs': 'laboratories/import_laboratories/',
    'sxs/addrecord': 'records/',
    'sxs/batch_delrecord': 'records/batch_delete/',
    'sxs/addclass': 'schedules/',
    'sxs/batch_delclass': 'schedules/batch_delete/',
    'sxs/check_schedule_conflict': 'schedules/check_conflict/',
    'sxs/listequipment': 'equipments/',
    'sxs/addequipment': 'equipments/',
    'sxs/batch_delequipment': 'equipments/batch_delete/',
    'sxs/import_equipment': 'equipments/import_equipments/',
    'sxs/workorder': 'work-orders/',
    'sxs/global_search': 'common/search/',
    'sxs/progress': 'common/progress/',
    'sxs/comprehensive_stats': 'statistics/comprehensive/',
    'sxs/user_management': 'statistics/dashboard/user/',
    'sxs/lab_resource_management': 'statistics/dashboard/lab/',
    'sxs/scheduling_management': 'statistics/dashboard/schedule/',
    'sxs/personal_teaching': 'statistics/dashboard/personal/'
  }

  if (staticMap[cleanPath]) return staticMap[cleanPath]

  // 2. 正则映射?(带参数路?
  
  // 用户列表: userinfo/userlist/1 -> users/?role=1
  const userListMatch = cleanPath.match(/^userinfo\/userlist\/(\d+)$/)
  if (userListMatch) {
    const typeid = userListMatch[1]
    const roleMap = { '1': 1, '2': 2, '3': 4, '4': 16 }
    return `users/?role=${roleMap[typeid] || typeid}`
  }

  // 用户操作: userinfo/deluser/123 -> users/123/
  const userItemMatch = cleanPath.match(/^userinfo\/(deluser|updateuserrole|assign_permission|resetpassword|cleanup_user_data|activate)\/(\d+)/)
  if (userItemMatch) {
    const action = userItemMatch[1]
    const id = userItemMatch[2]
    const actionMap = {
      'deluser': '',
      'updateuserrole': 'update_role/',
      'assign_permission': 'assign_permission/',
      'resetpassword': 'reset_password/',
      'cleanup_user_data': 'cleanup_data/',
      'activate': 'activate/'
    }
    return `users/${id}/${actionMap[action]}`
  }

  // 部门编辑: userinfo/updatedept/1 -> departments/1/
  const deptItemMatch = cleanPath.match(/^userinfo\/(updatedept|deldept)\/(\d+)/)
  if (deptItemMatch) return `departments/${deptItemMatch[2]}/`

  // 学期操作: userinfo/(currentterm|delterm)/1 -> semesters/1/
  const termItemMatch = cleanPath.match(/^userinfo\/(currentterm|delterm|view_archived_records)\/(\d+)/)
  if (termItemMatch) {
    const action = termItemMatch[1]
    const id = termItemMatch[2]
    if (action === 'currentterm') return `semesters/${id}/set_current/`
    return `semesters/${id}/`
  }

  // 实验室列? sxs/listsxs/4 -> laboratories/
  if (cleanPath.match(/^sxs\/listsxs\/\d+$/)) return 'laboratories/'

  // 实验室操? sxs/(delsxs|editsxs)/123 -> laboratories/123/
  const labItemMatch = cleanPath.match(/^sxs\/(delsxs|editsxs|listsxsinfo)\/(\d+)/)
  if (labItemMatch) return `laboratories/${labItemMatch[2]}/`

  // 课表/维护记录列表: sxs/listsxsclass/123 -> schedules/?laboratory_id=123
  const labRelationMatch = cleanPath.match(/^sxs\/(listsxsclass|listsxsmaintain)\/(\d+)/)
  if (labRelationMatch) {
    const type = labRelationMatch[1]
    const id = labRelationMatch[2]
    const endpoint = type === 'listsxsclass' ? 'schedules/' : 'work-orders/'
    return id !== '0' ? `${endpoint}?laboratory_id=${id}` : endpoint
  }

  // 记录/课表/设备单项操作: sxs/(delrecord|editrecord|delclass|editclass|delequipment|editequipment)/123
  const itemMatch = cleanPath.match(/^sxs\/(delrecord|editrecord|delclass|editclass|delequipment|editequipment)\/(\d+)/)
  if (itemMatch) {
    const type = itemMatch[1]
    const id = itemMatch[2]
    if (type.includes('record')) return `records/${id}/`
    if (type.includes('class')) return `schedules/${id}/`
    if (type.includes('equipment')) return `equipments/${id}/`
  }

  // 默认尝试原始路径
  return cleanPath + (cleanPath.endsWith('/') ? '' : '/')
}

// ==================== 默认导出 ====================

export function handleBusinessResponse(response, router, options = {}) {
  if (!response || !router) return false

  const { currentContext = {} } = options
  const route = decideRouteFromBusinessData(response, currentContext)

  if (route) {
    router.push(route)
    return true
  }

  return false
}

// ==================== 导航 Composable ====================

import { useRouter, useRoute } from 'vue-router'

export function useNavigation() {
  const router = useRouter()
  const route = useRoute()

  const goBack = (options = {}) => {
    const { fallback } = options
    if (fallback) {
      router.push(fallback).catch(() => router.go(-1))
    } else {
      router.go(-1)
    }
  }

  const smartBack = (shouldRefresh = true) => {
    const backPath = decideBackRoute(route.path, route.query)
    const query = shouldRefresh ? { ...route.query, _t: Date.now() } : route.query
    router.push({ path: backPath, query }).catch(() => router.go(-1))
  }

  const smartGoBack = (currentPath, query = {}) => {
    const backPath = decideBackRoute(currentPath, query)
    router.push(backPath).catch(() => router.go(-1))
  }

  const navigateTo = (path, options = {}) => {
    const { query, params } = options
    router.push({ path, query, params }).catch(() => {})
  }

  const goHome = () => {
    const current = router.currentRoute?.value
    let navigating = goHome._nav || false
    if (navigating) return
    goHome._nav = true
    
    if (current && current.path === '/') {
      router.replace('/').catch(() => {}).finally(() => { goHome._nav = false })
      return
    }
    router.push('/').catch(() => {
      router.replace('/').catch(() => { window.location.href = '/' })
    }).finally(() => {
      goHome._nav = false
    })
  }

  return {
    goBack,
    smartBack,
    smartGoBack,
    navigateTo,
    goHome
  }
}

export default {
  decideRouteFromBusinessData,
  handleBusinessResponse,
  decideRouteByActionType,
  decideBackRoute,
  getApiPath,
  getApiPathV2,
  useNavigation
}
