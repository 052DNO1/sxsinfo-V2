import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/client'
import type { User } from '../types'

interface LoginCredentials {
  username: string
  password: string
}

interface LoginResponse {
  success: boolean
  data?: {
    user: User
    access: string
    refresh: string
  }
  message?: string
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User>(JSON.parse(sessionStorage.getItem('user') || '{}'))

  const updateUser = (userData: User): void => {
    user.value = userData
    sessionStorage.setItem('user', JSON.stringify(userData))
  }

  const isAuthenticated = computed(() => !!(user.value && user.value.id))

  const isSuperuser = computed(() => user.value?.is_superuser === true)
  const isSystemAdmin = computed(() => user.value?.is_systemadmin === true)
  const isSuperAdmin = computed(() => user.value?.is_super_admin === true && user.value?.is_superuser !== true)
  const isDepartAdmin = computed(() => user.value?.is_departadmin === true)
  const isSxsAdmin = computed(() => user.value?.is_sxsadmin === true)
  const isTeacher = computed(() => user.value?.is_teacher === true)

  const userRole = computed(() => {
    if (isSuperuser.value) return '系统管理员'
    if (isSuperAdmin.value) return '管理员-校长'
    if (isDepartAdmin.value) return '分院管理员'
    if (isSxsAdmin.value) return '实训室管理员'
    if (isTeacher.value) return '教师'
    return '普通用户'
  })

  const login = async (credentials: LoginCredentials): Promise<LoginResponse> => {
    try {
      const response = await api.post<LoginResponse>('auth/login/', credentials)
      if (response && response.success && response.data?.user) {
        updateUser(response.data.user)
        if (response.data.access) localStorage.setItem('access_token', response.data.access)
        if (response.data.refresh) localStorage.setItem('refresh_token', response.data.refresh)
        return response
      }
      throw new Error(response?.message || '登录失败')
    } catch (error) {
      throw error
    }
  }

  interface LogoutOptions {
    redirectToLogin?: boolean
  }

  const logout = async (options: LogoutOptions = {}): Promise<void> => {
    const { redirectToLogin = true } = options
    try {
      await api.post('auth/logout/')
    } catch (error) {
    } finally {
      sessionStorage.removeItem('user')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      user.value = {} as User
      
      if (redirectToLogin) {
        window.location.href = '/login'
      }
    }
  }

  type UserRole = 'superuser' | 'systemadmin' | 'departadmin' | 'sxsadmin' | 'teacher'

  const checkPermission = (requiredRoles: UserRole | UserRole[]): boolean => {
    if (!isAuthenticated.value) return false
    const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles]
    return roles.some(role => {
      switch (role) {
        case 'superuser': return isSuperuser.value
        case 'systemadmin': return isSystemAdmin.value
        case 'departadmin': return isDepartAdmin.value
        case 'sxsadmin': return isSxsAdmin.value
        case 'teacher': return isTeacher.value
        default: return false
      }
    })
  }

  const hasAnyRole = checkPermission

  const hasAllRoles = (roles: UserRole[]): boolean => {
    if (!isAuthenticated.value) return false
    return roles.every(role => {
      switch (role) {
        case 'superuser': return isSuperuser.value
        case 'systemadmin': return isSystemAdmin.value
        case 'departadmin': return isDepartAdmin.value
        case 'sxsadmin': return isSxsAdmin.value
        case 'teacher': return isTeacher.value
        default: return false
      }
    })
  }

  return {
    user,
    isAuthenticated,
    isSuperuser,
    isSystemAdmin,
    isSuperAdmin,
    isDepartAdmin,
    isSxsAdmin,
    isTeacher,
    userRole,
    
    updateUser,
    login,
    logout,
    checkPermission,
    hasAnyRole,
    hasAllRoles
  }
})
