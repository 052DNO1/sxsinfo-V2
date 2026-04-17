import { watch, computed, ref } from 'vue'
import { useBaseList } from '@/composables/useBaseList'
import { adaptTermList } from '@/utils/adapters'
import { useDelete } from '@/composables/useDelete'
import { decideRouteByActionType } from '@/utils/routeDecision'
import { safeConfirm, showSuccess, showError } from '@/utils/errorHandler'
import { useAppStore } from '@/stores/app'

export function useTermList(apiPathOverride = '', options = {}) {
  const { immediate = true } = options
  const appStore = useAppStore()
  
  const {
    listHeader, columns, tableData, select, opt, error, filterValue,
    hideBack, backUrl, showCheckbox, skipCheckbox, isPaginated,
    currentPage, totalCount, pageSize, loading, apiData, selectedRows,
    finished, refreshing,
    
    loadData,
    handleFilter,
    handleSizeChange,
    handleCurrentChange,
    getActionRoute: baseGetActionRoute,
    
    route, router, user, apiComposable
  } = useBaseList({
    adapter: adaptTermList,
    baseApiPath: apiPathOverride,
    immediate: false
  })

  watch(() => route.query, (newQ, oldQ) => {
      if (JSON.stringify(newQ) !== JSON.stringify(oldQ)) {
          loadData()
      }
  })
  
  const localOpt = computed(() => {
    const actions = []
    if (user.value?.is_superuser) {
        actions.push({
            text: '添加学期',
            action_type: 'add',
            resource_type: 'term',
            style_class: 'btn-primary',
            icon: 'Plus'
        })
    }
    return actions
  })

  const loadDataWithOpt = async (options = {}) => {
      await loadData(options)
      
      if (!options.isLoadMore) {
        skipCheckbox.value = true
        
        if (!opt.value) opt.value = []
        const existingTexts = new Set(opt.value.map(o => o.text))
        
        localOpt.value.forEach(localAction => {
            if (!existingTexts.has(localAction.text)) {
                opt.value.unshift(localAction)
            }
        })
      }
  }

  const { handleDelete: execDelete } = useDelete({
    apiPathBuilder: (item) => `/userinfo/delterm/${item.resource_id || item.id}/`,
    refresh: () => loadDataWithOpt({ page: 1 }),
    method: 'GET'
  })

  const handleTermAction = async (action) => {
      const actionText = action.text || ''
      let confirmMessage = '确定要执行此操作吗？'
      
      if (actionText.includes('取消当前学期')) {
        confirmMessage = '确定要取消当前学期吗？取消后系统将没有当前学期。'
      } else if (actionText.includes('设为当前学期')) {
        confirmMessage = '确定要将此学期设为当前学期吗？'
      }
      
      try {
        await safeConfirm(confirmMessage)
        
        let apiPath = ''
        if (action.url) {
            apiPath = action.url
            if (apiPath.startsWith('/api/')) apiPath = apiPath.substring(4)
        } else if (action.resource_id) {
            if (actionText.includes('取消当前学期')) {
                apiPath = `/userinfo/unsetterm/${action.resource_id}/`
            } else if (actionText.includes('设为当前学期')) {
                apiPath = `/userinfo/currentterm/${action.resource_id}/`
            }
        }
        
        if (!apiPath) throw new Error('无法获取操作地址')
        
        let httpMethod = 'get'
        let requestData = null
        if (actionText.includes('设为当前学期')) {
            httpMethod = 'post'
            requestData = { is_current: true }
        }
        
        const response = httpMethod === 'post' 
          ? await apiComposable.post(requestData, { url: apiPath })
          : await apiComposable.get({}, { url: apiPath })
          
        if (response && response.success) {
            await showSuccess(response.message || '操作成功')
            appStore.triggerTermRefresh()
            loadDataWithOpt({ page: 1 })
        } else {
            await showError(response?.message || '操作失败')
        }
      } catch (err) {
          if (err !== 'cancel') await showError(err.message || '操作失败')
      }
  }

  const getActionRoute = (action) => {
     return baseGetActionRoute(action)
  }

  if (immediate) loadDataWithOpt()

  return {
    listHeader, columns, tableData, select, opt, error, filterValue,
    hideBack, backUrl, showCheckbox, skipCheckbox, isPaginated,
    currentPage, totalCount, pageSize, loading, finished, refreshing,
    
    loadData: loadDataWithOpt,
    handleFilter,
    handleSizeChange,
    handleCurrentChange,
    execDelete,
    handleTermAction,
    getActionRoute
  }
}
