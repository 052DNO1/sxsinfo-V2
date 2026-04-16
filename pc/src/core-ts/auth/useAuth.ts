/**
 * 认证相关组合式函数
 */

import { useUserStore } from '../store/user'
import { storeToRefs } from 'pinia'
import type { User } from '../types'
import type { Ref, ComputedRef } from 'vue'

interface UseAuthReturn {
  user: Ref<User>
  isAuthenticated: ComputedRef<boolean>
  isSuperuser: ComputedRef<boolean>
  isDepartAdmin: ComputedRef<boolean>
  isSxsAdmin: ComputedRef<boolean>
  isTeacher: ComputedRef<boolean>
  userRole: ComputedRef<string>
  updateUser: (userData: User) => void
  login: (credentials: { username: string; password: string }) => Promise<any>
  logout: (options?: { redirectToLogin?: boolean }) => Promise<void>
  checkPermission: (requiredRoles: string | string[]) => boolean
  hasAnyRole: (requiredRoles: string | string[]) => boolean
  hasAllRoles: (roles: string[]) => boolean
}

export function useAuth(): UseAuthReturn {
  const store = useUserStore()
  
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
    user,
    isAuthenticated,
    isSuperuser,
    isDepartAdmin,
    isSxsAdmin,
    isTeacher,
    userRole,
    
    updateUser: store.updateUser,
    login: store.login,
    logout: store.logout,
    checkPermission: store.checkPermission,
    hasAnyRole: store.hasAnyRole,
    hasAllRoles: store.hasAllRoles
  }
}

export default useAuth
