import { ref, computed } from 'vue'
import { useBaseList } from '@/composables/useBaseList'
import { adaptUserList } from '@/utils/adapters'
import { getButtonType, getButtonIcon, getButtonBg, filterActionButtons } from '@/utils/tableHelpers'
import { useDelete } from '@/composables/useDelete'
import { decideRouteByActionType } from '@/utils/routeDecision'
import { safeConfirm, safeAlert, showSuccess, showError, showWarning, formatBatchResult } from '@/utils/errorHandler'
import { useAuth } from '@/composables/useAuth'

export function useUserList(options = {}) {
  const {
    listHeader, columns, tableData, select, opt, error, filterValue,
    hideBack, backUrl, showCheckbox, skipCheckbox, isPaginated,
    currentPage, totalCount, pageSize, loading, apiData, selectedRows,
    refreshing,
    
    loadData,
    handleFilter,
    handleSizeChange,
    handleCurrentChange,
    handleSelectionChange,
    getActionRoute,
    
    route, router, user, apiComposable
  } = useBaseList({
    adapter: adaptUserList,
    baseApiPath: options.baseApiPath
  })
  
  const multipleSelection = selectedRows

  const localOpt = computed(() => {
    const actions = []
    if (user.value?.is_superuser) {
        actions.push({
            text: '添加用户',
            action_type: 'add',
            resource_type: 'user',
            style_class: 'btn-primary',
            icon: 'Plus'
        })
    }
    return actions
  })

  const loadDataWithOpt = async (options = {}) => {
      await loadData(options)
      
      if (!options.isLoadMore) {
        if (!opt.value) opt.value = []
        const existingTexts = new Set(opt.value.map(o => o.text))
        
        localOpt.value.forEach(localAction => {
            if (!existingTexts.has(localAction.text)) {
                opt.value.unshift(localAction)
            }
        })
        
        if (opt.value && opt.value.length > 0) {
          opt.value = filterActionButtons(opt.value)
        }
      }
  }

  const { handleBatchDelete: execBatchDelete } = useDelete({
    apiPath: '/userinfo/batch_deluser/',
    paramName: 'user_ids',
    getId: (row) => row.id,
    refresh: () => loadDataWithOpt({ page: 1 }),
    confirmMessageBuilder: (selection) => `确定要删除选中的 ${selection.length} 项吗？此操作不可恢复！`
  })

  const handleBatchDelete = async (selection) => {
    if (!selection || selection.length === 0) {
      await showWarning('请至少选择一项进行删除')
      return
    }

    await execBatchDelete(selection)
  }

  const isActionDisabled = (action) => {
    try {
      const currentUserId = user.value?.id
      if (!currentUserId || !action) return false
      const text = action.text || ''
      const isRoleOrPerm = action.resource_type === 'user' || action.resource_type === 'user_role' || text.includes('分配角色') || text.includes('分配权限')
      if (!isRoleOrPerm) return false
      const targetId = action.resource_id || action.context?.id || action.context?.userid
      return String(targetId) === String(currentUserId)
    } catch (e) {
      return false
    }
  }

  const handleActivateAction = async (action) => {
    const actionText = action.text || ''
    let confirmMessage = actionText.includes('禁用') ? '确定要禁用该用户吗？' : '确定要激活该用户吗？'
    const confirmed = await safeConfirm(confirmMessage)
    if (!confirmed) return
    
    let apiPath = ''
    if (action.resource_id) {
      const isactive = actionText.includes('禁用') ? 0 : 1
      apiPath = `/userinfo/activate/${action.resource_id}/${isactive}/`
    } else if (action.url) {
      apiPath = action.url
    }
    
    try {
      const response = await apiComposable.get({}, { url: apiPath })
      if (response && response.success) {
        await showSuccess(response.message || '操作成功')
        await loadDataWithOpt({ page: 1 })
      } else {
        await showError(response?.message || '操作失败')
      }
    } catch (err) {
      await showError(err)
    }
  }

  const handleBatchResetPassword = async (selection) => {
    if (!selection || selection.length === 0) {
      await showWarning('请至少选择一项进行重置密码')
      return
    }
    
    const userIds = selection.map(row => row.id)
    const confirmMessage = `确定要重置选中的 ${userIds.length} 个用户的密码为默认密码（用户名前6位）吗？`
    const confirmed = await safeConfirm(confirmMessage)
    if (!confirmed) return
    
    const successUsers = []
    const failedUsers = []
    
    for (const userId of userIds) {
      try {
        const url = `/userinfo/resetpassword/${userId}/`
        const response = await apiComposable.get({}, { url })
        if (response && response.success) {
          successUsers.push(userId)
        } else {
          failedUsers.push({ id: userId, reason: response?.message || '重置密码失败' })
        }
      } catch (err) {
        failedUsers.push({ id: userId, reason: err.message })
      }
    }
    
    const resultMessage = formatBatchResult({
      successItems: successUsers,
      failedItems: failedUsers,
      successLabel: '用户',
      failedLabel: '用户'
    })
    if (resultMessage) await safeAlert(resultMessage)
    if (successUsers.length > 0) await loadDataWithOpt({ page: 1 })
  }

  const handleOptionClick = async (option) => {
    if ((option.text && option.text.includes('批量/删除')) || (option.onclick && option.onclick === 'batchDelete')) {
      await handleBatchDelete(selectedRows.value)
      return
    }
    
    if (option.action_type === 'add') {
       const typeid = route.params.id || route.query.typeid || option.context?.typeid || '0'
       router.push(`/adduser/${typeid}`)
       return
    }
    
    const navUrl = getActionRoute(option)
    if (navUrl) {
      try {
        await router.push(navUrl)
      } catch (err) {
        window.location.href = navUrl
      }
    }
  }

  const handleAction = async (action) => {
      if (!action || isActionDisabled(action)) return
      const actionText = action.text || ''
      
      if (action.action_type === 'delete') {
        await showWarning('请使用批量删除功能进行删除')
        return
      }
      
      if (actionText.includes('禁用') || actionText.includes('激活')) {
        await handleActivateAction(action)
        return
      }
      
      const navUrl = getActionRoute(action)
      if (navUrl) {
        try {
          await router.push(navUrl)
        } catch (err) {
          window.location.href = navUrl
        }
      }
  }

  return {
    listHeader, columns, tableData, select, opt, error, filterValue,
    showCheckbox, skipCheckbox, isPaginated, currentPage, totalCount, pageSize,
    loading, multipleSelection, hideBack, refreshing,
    
    loadData: loadDataWithOpt,
    handleFilter,
    handleActivateAction,
    handleBatchResetPassword,
    handleBatchDelete,
    isActionDisabled,
    getActionRoute,
    getButtonType,
    getButtonIcon,
    getButtonBg,
    handleSizeChange,
    handleCurrentChange,
    handleOptionClick,
    handleAction
  }
}
