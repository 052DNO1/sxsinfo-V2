import { computed, watch } from 'vue'
import { useBaseList } from '@/composables/useBaseList'
import { adaptSxsList } from '@/utils/adapters'
import { useDelete } from '@/composables/useDelete'
import { decideRouteByActionType, decideBackRoute } from '@/utils/routeDecision'
import { getButtonType, getButtonIcon, isActionDisabled } from '@/utils/tableHelpers'

export function useSxsList(apiPathOverride = '', options = {}) {
  const { immediate = true } = options
  
  const {
    listHeader, columns, tableData, select, opt, error, filterValue,
    hideBack, backUrl, showCheckbox, skipCheckbox, isPaginated,
    currentPage, totalCount, pageSize, loading, apiData, selectedRows,
    finished, refreshing, selectedCount,
    
    loadData,
    handleFilter,
    handleSizeChange,
    handleCurrentChange,
    handleSelectionChange,
    getActionRoute,
    
    route, router, user, apiComposable
  } = useBaseList({
    adapter: adaptSxsList,
    baseApiPath: apiPathOverride,
    immediate: false,
    onDataLoaded: (response, isLoadMore) => {
      if (!isLoadMore && response) {
        const isOnlySxsAdmin = user.value?.is_sxsadmin && !user.value?.is_superuser && !user.value?.is_departadmin
        showCheckbox.value = !isOnlySxsAdmin
        skipCheckbox.value = isOnlySxsAdmin
      }
    }
  })
  
  watch(() => route.query, (newQ, oldQ) => {
    if (JSON.stringify(newQ) !== JSON.stringify(oldQ)) {
      loadData()
    }
  })
  
  const smartBack = () => {
    const backPath = decideBackRoute(route.path, route.query)
    router.push(backPath).catch(() => router.go(-1))
  }
  
  const goHome = () => {
    router.push('/').catch(() => {
      router.replace('/').catch(() => { window.location.href = '/' })
    })
  }

  const isSxsAdmin = computed(() => {
    return user.value?.is_sxsadmin && !user.value?.is_superuser && !user.value?.is_departadmin
  })

  const currentQtype = computed(() => {
    if (route.path.includes('/listsxs/')) {
      const match = route.path.match(/\/listsxs\/(\d+)/)
      return match ? match[1] : '4'
    }
    return '4'
  })

  const showBackButton = computed(() => {
    if (user.value?.is_superuser) return false
    if (hideBack.value) return false
    return true
  })

  const { handleDelete: execDelete, handleBatchDelete: execBatchDeleteLab } = useDelete({
    apiPathBuilder: (item) => `/sxs/delsxs/${item.id}/`,
    getId: (row) => row.id,
    handleItemDelete: async (id) => {
      await apiComposable.get({}, { url: `/sxs/delsxs/${id}/`, autoHandleError: false })
    },
    refresh: () => loadData({ page: 1 }),
    confirmMessageBuilder: (itemOrSelection) => {
      if (Array.isArray(itemOrSelection)) {
        return `确定要删除选中的 ${itemOrSelection.length} 个实训室吗？\n注意：与之关联的课表也将一并被删除！此操作不可恢复！`
      }
      return `确定要删除 "${itemOrSelection.name || itemOrSelection.sxsname || '该实训室'}" 吗？\n注意：与之关联的课表也将一并被删除！此操作不可恢复！`
    },
    method: 'GET'
  })

  const handleBatchDeleteLabAction = async () => {
    await execBatchDeleteLab(selectedRows.value)
  }

  const handleDeleteAction = async (action) => {
    if (action.resource_type === 'sxs') {
       await execDelete({ ...action, name: '该实训室' })
    } else {
      console.error('❌ SxsList: 未知的删除资源类型:', action.resource_type)
    }
  }

  const handleAction = async (action) => {
    if (!action) return
    
    if (action.action_type === 'delete') {
      await handleDeleteAction(action)
      return
    }
    
    if (action.action_type === 'import') {
      router.push('/import/sxs')
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

  const handleOptionClick = async (option) => {
    if (option.action_type === 'import') {
      router.push('/import/sxs')
      return
    }

    if (option.action_type === 'export') {
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

  const handleViewDevices = () => {
    router.push({
      path: '/device-list',
      query: {
        ...route.query,
        back_url: route.fullPath
      }
    })
  }

  const goBack = () => {
    if (apiData.value?.back_action) {
      const backAction = apiData.value.back_action
      const backPath = decideRouteByActionType(
        backAction.action_type,
        backAction.resource_type,
        backAction.context || {}
      )
      if (backPath) {
        router.push(backPath).catch(() => smartBack())
        return
      }
    }
    smartBack()
  }

  const formatCellContent = (content) => (content === null || content === undefined) ? '-' : content

  if (immediate) loadData()

  return {
    listHeader, columns, tableData, select, opt, error, filterValue,
    showCheckbox, skipCheckbox, isPaginated, currentPage, totalCount, pageSize,
    loading, selectedRows, selectedCount, isSxsAdmin, showBackButton,
    finished, refreshing,
    
    loadData,
    handleSelectionChange,
    handleFilter,
    handleSizeChange,
    handleCurrentChange,
    handleOptionClick,
    handleAction,
    handleBatchDeleteLab: handleBatchDeleteLabAction,
    handleViewDevices,
    goBack,
    goHome,
    smartBack,
    getButtonType,
    getButtonIcon,
    isActionDisabled,
    formatCellContent,
    getActionRoute
  }
}
