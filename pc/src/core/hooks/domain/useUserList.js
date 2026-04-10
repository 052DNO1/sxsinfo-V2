import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBaseCRUD } from '../base/useCRUD'
import { userService } from '@/core/services/BaseService'
import { LIST_COLUMNS } from '@/core/config/listConfig'
import { safeConfirm, showSuccess, showError } from '@/core/utils/errorHandler'
import { useApi } from '../base/useApi'
import { useUserStore } from '@/core/store/user'

export function useUserList(options = {}) {
  const router = useRouter()
  const route = useRoute()
  const userStore = useUserStore()
  const user = computed(() => userStore.user)
  const apiComposable = useApi('', { immediate: false })

  const crud = useBaseCRUD({
    service: userService,
    itemName: '用户',
    listType: 'users',
    immediate: false,
    ...options
  })

  const columns = computed(() => LIST_COLUMNS.users)

  const tableData = computed(() => {
    return crud.tableData.value.map(item => ({
      ...item,
      status_display: item.is_active
        ? { text: '正常', type: 'success' }
        : { text: '禁用', type: 'danger' },
      actions: [
        { text: '编辑', action_type: 'edit', resource_type: 'user_role', resource_id: item.id, style_class: 'btn-primary-sm' },
        { text: item.is_active ? '禁用' : '激活', action_type: 'toggle', resource_type: 'user_status', resource_id: item.id, style_class: item.is_active ? 'btn-danger-sm' : 'btn-success-sm' }
      ]
    }))
  })

  const listHeader = computed(() => {
    const isSuperAdmin = user.value?.is_super_admin || user.value?.is_superuser
    const routeId = route.params.id

    if (isSuperAdmin && routeId === '4') {
      return '部门管理员列表'
    }
    return '用户列表管理'
  })
  const showCheckbox = ref(true)
  const isPaginated = ref(true)
  const filterValue = ref('')

  const select = computed(() => {
    const isSuperAdmin = user.value?.is_super_admin || user.value?.is_superuser
    const routeId = route.params.id

    if (isSuperAdmin && routeId === '4') {
      return {
        options: [
          { id: 0, text: '全部用户' },
          { id: 4, text: '部门管理员' },
          { id: 1, text: '教师' },
          { id: 2, text: '实训室管理员' }
        ],
        defaultSelected: 4
      }
    }

    return {
      options: [
        { id: 0, text: '全部用户' },
        { id: 1, text: '教师' },
        { id: 2, text: '实训室管理员' },
        { id: 4, text: '部门管理员' }
      ]
    }
  })

  const opt = computed(() => [
    { text: '添加用户', onclick: 'add', type: 'primary', icon: 'Plus' },
    { text: '批量删除', onclick: 'batchDelete', type: 'danger', icon: 'Delete' },
    { text: '重置密码', onclick: 'batchResetPassword', type: 'warning', icon: 'Key' }
  ])

  const getDefaultParams = () => {
    const isSuperAdmin = user.value?.is_super_admin || user.value?.is_superuser
    const routeId = route.params.id

    if (isSuperAdmin && routeId === '4') {
      return { role: 4 }
    }
    
    return { role: '1,2' }
  }

  watch(() => route.params.id, () => {
    crud.loadData(getDefaultParams())
  }, { immediate: true })

  const handleAction = async (op) => {
    if (!op) return
    
    const { action_type, resource_type, resource_id, text } = op
    
    if (action_type === 'edit' && resource_type === 'user_role') {
      router.push(`/assign-role/${resource_id}/`)
    } else if (action_type === 'edit' && resource_type === 'permission') {
      router.push(`/assign-permission/${resource_id}/`)
    } else if (action_type === 'toggle' && resource_type === 'user_status') {
      try {
        await safeConfirm(`确定要${text}该用户吗？`)
        const isActive = text === '激活'
        const response = await apiComposable.post({ is_active: isActive }, { url: `/users/${resource_id}/activate/` })
        if (response && response.success) {
          showSuccess(response.message || '操作成功')
          crud.loadData(getDefaultParams())
        } else {
          showError(response?.message || '操作失败')
        }
      } catch (err) {
        if (err !== 'cancel') showError(err.message || '操作失败')
      }
    }
  }

  const handleOptionClick = async (option) => {
    if (!option) return
    
    const { onclick, text } = option
    
    if (onclick === 'add') {
      router.push('/adduser')
    } else if (onclick === 'batchDelete') {
      if (!crud.selectedRows.value || crud.selectedRows.value.length === 0) {
        showError('请先选择要删除的用户')
        return
      }
      await crud.execBatchDelete(crud.selectedRows.value)
    } else if (onclick === 'batchResetPassword') {
      await handleBatchResetPassword(crud.selectedRows.value)
    }
  }

  const handleBatchResetPassword = async (selection) => {
    if (!selection || selection.length === 0) {
      showError('请先选择要重置密码的用户')
      return
    }
    
    try {
      await safeConfirm(`确定要重置选中的 ${selection.length} 个用户的密码吗？`)
      const userIds = selection.map(item => item.id)
      const response = await apiComposable.post({ user_ids: userIds }, { url: '/auth/password/batch-reset/' })
      if (response && response.success) {
        showSuccess(response.message || '密码重置成功')
      } else {
        showError(response?.message || '密码重置失败')
      }
    } catch (err) {
      if (err !== 'cancel') showError(err.message || '密码重置失败')
    }
  }

  return { 
    ...crud,
    columns,
    tableData,
    listHeader,
    showCheckbox,
    isPaginated,
    filterValue,
    select,
    opt,
    handleAction,
    handleOptionClick,
    handleBatchResetPassword
  }
}
