import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

export function useAuth() {
  const store = useUserStore()
  const { 
    user, isAuthenticated, isSuperuser, isDepartAdmin, 
    isSxsAdmin, isTeacher, userRole 
  } = storeToRefs(store)

  return {
    user, isAuthenticated, isSuperuser, isDepartAdmin, isSxsAdmin, isTeacher, userRole,
    updateUser: store.updateUser,
    login: store.login,
    logout: store.logout,
    checkPermission: store.checkPermission,
    hasAnyRole: store.hasAnyRole,
    hasAllRoles: store.hasAllRoles
  }
}
