/**
 * 认证相关组合式函?
 * 
 * 这是用户认证的统一入口，封装了 Pinia UserStore 的功能?
 * 
 * 主要功能?
 * 1. 获取当前用户信息和登录状?
 * 2. 判断用户角色（超级管理员、分院管理员、实训室管理员、教师）
 * 3. 登录、登出操?
 * 4. 权限检?
 * 
 * 对于新手?
 * - 这个 composable 是对 stores/user.js 的封?
 * - storeToRefs 用于保持响应式，直接解构会丢失响应?
 * - 在任何组件中都可以使?useAuth() 获取用户信息
 * 
 * 使用示例?
 * ```js
 * import { useAuth } from '@/core/hooks'
 * 
 * const { user, isSuperuser, login, logout } = useAuth()
 * 
 * // 检查是否登?
 * if (isAuthenticated.value) {
 *    * }
 * 
 * // 检查权?
 * if (isSuperuser.value) {
 *   // 显示管理员功?
 * }
 * 
 * // 登录
 * await login({ username: 'admin', password: '123456' })
 * 
 * // 登出
 * await logout()
 * ```
 */

import { useUserStore } from '@/core/store/user'
import { storeToRefs } from 'pinia'

/**
 * 认证组合式函?
 * 
 * @returns {Object} 认证相关的状态和方法
 * @property {Ref<Object>} user - 当前用户信息对象
 * @property {Ref<boolean>} isAuthenticated - 是否已登?
 * @property {Ref<boolean>} isSuperuser - 是否超级管理?
 * @property {Ref<boolean>} isDepartAdmin - 是否分院管理?
 * @property {Ref<boolean>} isSxsAdmin - 是否实训室管理员
 * @property {Ref<boolean>} isTeacher - 是否教师
 * @property {Ref<string>} userRole - 用户角色名称（中文）
 * @property {Function} updateUser - 更新用户信息
 * @property {Function} login - 登录方法
 * @property {Function} logout - 登出方法
 * @property {Function} checkPermission - 检查权?
 */
export function useAuth() {
  // 获取 Pinia store 实例
  const store = useUserStore()
  
  // 使用 storeToRefs 保持响应?
  // 对于新手：直接解?store 会丢失响应性，必须?storeToRefs
  const { 
    user, 
    isAuthenticated, 
    isSuperuser, 
    isDepartAdmin, 
    isSxsAdmin, 
    isTeacher, 
    userRole 
  } = storeToRefs(store)

  return {
    // 响应式状态（通过 storeToRefs 解构?
    user,
    isAuthenticated,
    isSuperuser,
    isDepartAdmin,
    isSxsAdmin,
    isTeacher,
    userRole,
    
    // 方法可以直接解构（不需?storeToRefs�?
    updateUser: store.updateUser,
    login: store.login,
    logout: store.logout,
    checkPermission: store.checkPermission,
    hasAnyRole: store.hasAnyRole,
    hasAllRoles: store.hasAllRoles
  }
}
