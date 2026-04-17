/**
 * 用户状态管理
 * 
 * 这是整个应用最核心的状态管理，负责：
 * 1. 用户信息的存储和更新
 * 2. 登录/登出功能
 * 3. 权限判断（超级管理员、分院管理员、实训室管理员、教师等）
 * 
 * 对于新手：
 * - sessionStorage 是浏览器会话存储，关闭标签页就清除
 * - localStorage 是本地持久存储，除非手动清除否则一直存在
 * - computed 是计算属性，会根据依赖自动更新
 * - 权限系统采用角色判断，不同角色有不同的操作权限
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  /**
   * 用户信息对象
   * 
   * 从 sessionStorage 初始化，包含：
   * - id: 用户ID
   * - username: 用户名
   * - is_superuser: 是否超级管理员
   * - is_departadmin: 是否分院管理员
   * - is_sxsadmin: 是否实训室管理员
   * - is_teacher: 是否教师
   * - 其他用户属性...
   */
  const user = ref(JSON.parse(sessionStorage.getItem('user') || '{}'))

  /**
   * 更新用户信息
   * 
   * @param {Object} userData - 新的用户数据
   * 
   * 同时更新内存中的 user 和 sessionStorage
   * 这样刷新页面后用户信息不会丢失
   */
  const updateUser = (userData) => {
    user.value = userData
    sessionStorage.setItem('user', JSON.stringify(userData))
  }

  /**
   * 是否已认证（已登录）
   * 
   * 通过检查 user.id 是否存在来判断
   */
  const isAuthenticated = computed(() => !!(user.value && user.value.id))
  
  // ==================== 角色判断 ====================
  
  /** 是否超级管理员（最高权限） */
  const isSuperuser = computed(() => user.value?.is_superuser === true)
  
  /** 是否分院管理员 */
  const isDepartAdmin = computed(() => user.value?.is_departadmin === true)
  
  /** 是否实训室管理员 */
  const isSxsAdmin = computed(() => user.value?.is_sxsadmin === true)
  
  /** 是否教师 */
  const isTeacher = computed(() => user.value?.is_teacher === true)

  /**
   * 用户角色名称（中文）
   * 
   * 按权限从高到低判断，返回对应的角色名称
   */
  const userRole = computed(() => {
    if (isSuperuser.value) return '超级管理员'
    if (isDepartAdmin.value) return '分院管理员'
    if (isSxsAdmin.value) return '实训室管理员'
    if (isTeacher.value) return '教师'
    return '普通用户'
  })

  /**
   * 登录方法
   * 
   * @param {Object} credentials - 登录凭证 { username, password }
   * @returns {Object} 登录响应
   * @throws {Error} 登录失败时抛出错误
   * 
   * 对于新手：
   * - async/await 是处理异步操作的方式
   * - try/catch 捕获错误
   * - throw new Error 会中断执行并抛出错误给调用者处理
   */
  const login = async (credentials) => {
    try {
      const response = await api.post('/login/', credentials)
      if (response && response.success && response.user) {
        updateUser(response.user)
        return response
      }
      throw new Error(response?.message || '登录失败')
    } catch (error) {
      throw error
    }
  }

  /**
   * 登出方法
   * 
   * @param {Object} options - 配置选项
   * @param {boolean} options.redirectToLogin - 是否重定向到登录页（默认 true）
   * 
   * 清除所有登录状态：
   * 1. 调用后端登出接口
   * 2. 清除 sessionStorage 中的用户信息
   * 3. 清除 localStorage 中的 token
   * 4. 重置内存中的 user 对象
   * 5. 跳转到登录页
   */
  const logout = async (options = {}) => {
    const { redirectToLogin = true } = options
    try {
      await api.post('/logout/')
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      // 清理本地存储
      sessionStorage.removeItem('user')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      user.value = {}
      
      // 跳转到登录页
      if (redirectToLogin) {
        router.push('/login')
      }
    }
  }

  /**
   * 检查用户是否拥有指定角色之一
   * 
   * @param {string|string[]} requiredRoles - 需要的角色（单个或数组）
   * @returns {boolean} 是否拥有权限
   * 
   * 使用示例：
   * checkPermission('superuser')  // 检查是否超级管理员
   * checkPermission(['superuser', 'departadmin'])  // 检查是否超级管理员或分院管理员
   */
  const checkPermission = (requiredRoles) => {
    if (!isAuthenticated.value) return false
    const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles]
    return roles.some(role => {
      switch (role) {
        case 'superuser': return isSuperuser.value
        case 'departadmin': return isDepartAdmin.value
        case 'sxsadmin': return isSxsAdmin.value
        case 'teacher': return isTeacher.value
        default: return false
      }
    })
  }

  /**
   * 检查用户是否拥有指定角色之一（checkPermission 的别名）
   */
  const hasAnyRole = checkPermission

  /**
   * 检查用户是否同时拥有所有指定角色
   * 
   * @param {string[]} roles - 需要的角色数组
   * @returns {boolean} 是否同时拥有所有角色
   * 
   * 使用示例：
   * hasAllRoles(['superuser', 'teacher'])  // 必须同时是超级管理员和教师
   */
  const hasAllRoles = (roles) => {
    if (!isAuthenticated.value) return false
    return roles.every(role => {
      switch (role) {
        case 'superuser': return isSuperuser.value
        case 'departadmin': return isDepartAdmin.value
        case 'sxsadmin': return isSxsAdmin.value
        case 'teacher': return isTeacher.value
        default: return false
      }
    })
  }

  // 导出所有状态和方法供外部使用
  return {
    // 状态
    user,
    isAuthenticated,
    isSuperuser,
    isDepartAdmin,
    isSxsAdmin,
    isTeacher,
    userRole,
    
    // 方法
    updateUser,
    login,
    logout,
    checkPermission,
    hasAnyRole,
    hasAllRoles
  }
})
