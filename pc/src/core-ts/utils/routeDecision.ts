/**
 * 路由决策工具
 */

import type { Action } from '../types'

export function getActionRoute(action: Action | null, routeQuery: Record<string, any> = {}): string | null {
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

interface BusinessData {
  action?: string
  resource_type?: string
  context?: Record<string, any>
}

export function decideRouteFromBusinessData(responseData: BusinessData | null, currentContext: Record<string, any> = {}): string | null {
  if (!responseData?.action) return null

  const { action, resource_type, context = {} } = responseData

  if (['created', 'updated', 'deleted'].includes(action)) {
    return decideRouteByResourceType(resource_type || '', context, currentContext)
  }

  return null
}

type ActionType = 'edit' | 'update' | 'view' | 'detail' | 'add' | 'create' | 'navigate' | 'delete'

export function decideRouteByActionType(actionType: ActionType | string, resourceType: string, context: Record<string, any> = {}, currentContext: Record<string, any> = {}): string | null {
  const resourceId = context.resource_id || context.id || context.sxsid || context.userid || context.class_name

  const actionMap: Record<string, (() => string | null)> = {
    'edit': () => decideEditRoute(resourceType, resourceId, context),
    'update': () => decideEditRoute(resourceType, resourceId, context),
    'view': () => decideViewRoute(resourceType, resourceId, context),
    'detail': () => decideViewRoute(resourceType, resourceId, context),
    'add': () => decideAddRoute(resourceType, context),
    'create': () => decideAddRoute(resourceType, context),
    'navigate': () => decideNavigateRoute(resourceType, context),
    'delete': () => null
  }

  return actionMap[actionType]?.() || decideRouteByResourceType(resourceType, context, currentContext)
}

function decideEditRoute(resourceType: string, resourceId: number | string | undefined, context: Record<string, any>): string {
  switch (resourceType) {
    case 'sxs':
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
      const tid = context.tid || context.typeid || '1'
      return `/update-user-role/${resourceId}?tid=${tid}`
    case 'permission':
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

function decideViewRoute(resourceType: string, resourceId: number | string | undefined, context: Record<string, any>): string {
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
    default:
      return decideRouteByResourceType(resourceType, context)
  }
}

function decideAddRoute(resourceType: string, context: Record<string, any>): string {
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

interface RouteConfig {
  pattern?: RegExp
  target: string | ((match: RegExpMatchArray | null, query: Record<string, any>) => string)
}

const BACK_ROUTE_CONFIG: Record<string, Record<string, string | RouteConfig>> = {
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
    '/listsxsinfo': { pattern: /^\/listsxsinfo(?:\/(\d+))?$/, target: (m, q) => `/listsxs/${m?.[1] || '4'}` },
    '/term': '/term',
    '/deptlist': '/deptlist',
    '/device-list': '/lab-resource-management',
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

function matchRouteConfig(currentPath: string, configSection: Record<string, string | RouteConfig>): { target: string; prefix: string; match?: RegExpMatchArray } | null {
  let bestMatch: RouteConfig | null = null
  let bestLength = -1
  let bestPrefix: string | null = null
  
  for (const [prefix, config] of Object.entries(configSection)) {
    if (currentPath.startsWith(prefix) || currentPath === prefix) {
      if (prefix.length > bestLength) {
        bestMatch = typeof config === 'string' ? { target: config } : config
        bestLength = prefix.length
        bestPrefix = prefix
      }
    }
  }
  
  if (bestMatch && bestPrefix) {
    if (bestMatch.pattern) {
      const match = currentPath.match(bestMatch.pattern)
      if (match) {
        return { ...bestMatch, match, prefix: bestPrefix }
      }
    }
    return { target: typeof bestMatch === 'string' ? bestMatch : bestMatch.target, prefix: bestPrefix }
  }
  return null
}

export function decideBackRoute(currentPath: string, routeQuery: Record<string, any> = {}): string {
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
        return result.target(result.match || null, routeQuery)
      }
      return result.target
    }
  }

  return '/'
}

function decideNavigateRoute(resourceType: string, context: Record<string, any>): string {
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

function decideRouteByResourceType(resourceType: string, context: Record<string, any> = {}, currentContext: Record<string, any> = {}): string {
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

export function getApiPath(routePath: string, routeQuery: Record<string, any> = {}, routeParams: Record<string, any> = {}): string | null {
  if (routePath.startsWith('/adduser')) {
    const match = routePath.match(/^\/adduser(?:\/(\d+))?$/)
    return `/users/`
  }
  if (routePath === '/addsxs') return '/laboratories/'
  if (routePath.startsWith('/addclass')) {
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

  return routePath.startsWith('/') ? routePath.substring(1) : routePath
}

export default {
  decideRouteFromBusinessData,
  getActionRoute,
  decideRouteByActionType,
  decideBackRoute,
  getApiPath
}
