import { watch, computed } from 'vue'
import { useBaseList } from '@/composables/useBaseList'
import { adaptDeptList } from '@/utils/adapters'
import { useDelete } from '@/composables/useDelete'

export function useDeptList(apiPathOverride = '', options = {}) {
  const { immediate = true } = options
  
  const {
    listHeader, columns, tableData, select, opt, error, filterValue,
    hideBack, backUrl, showCheckbox, skipCheckbox, isPaginated,
    currentPage, totalCount, pageSize, loading, apiData, selectedRows,
    finished, refreshing,
    
    loadData,
    handleFilter,
    handleSizeChange,
    handleCurrentChange,
    getActionRoute,
    
    route, router, user, apiComposable
  } = useBaseList({
    adapter: adaptDeptList,
    baseApiPath: apiPathOverride,
    immediate: false
  })

  watch(() => route.query, (newQ, oldQ) => {
      if (JSON.stringify(newQ) !== JSON.stringify(oldQ)) {
          loadDataWithOpt()
      }
  })
  
  const localOpt = computed(() => {
    const actions = []
    if (user.value?.is_superuser) {
        actions.push({
            text: '添加部门',
            action_type: 'add',
            resource_type: 'dept',
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
      }
  }

  const { handleBatchDelete: execBatchDelete, handleDelete: execDelete } = useDelete({
    apiPath: '/userinfo/batch_deldept/',
    paramName: 'dept_ids',
    getId: (row) => row.id,
    apiPathBuilder: (item) => `/userinfo/deldept/${item.resource_id || item.id}/`,
    refresh: () => loadDataWithOpt({ page: 1 }),
    confirmMessageBuilder: (itemOrSelection) => {
      if (Array.isArray(itemOrSelection)) {
        return `确定要删除选中的 ${itemOrSelection.length} 个部门吗？此操作不可恢复！`
      }
      return `确定要删除该部门吗？此操作不可恢复！`
    },
    method: 'GET'
  })

  if (immediate) loadDataWithOpt()

  return {
    listHeader, columns, tableData, select, opt, error, filterValue,
    hideBack, backUrl, showCheckbox, skipCheckbox, isPaginated,
    currentPage, totalCount, pageSize, loading, finished, refreshing,
    
    loadData: loadDataWithOpt,
    handleFilter,
    handleSizeChange,
    handleCurrentChange,
    execBatchDelete,
    execDelete,
    getActionRoute
  }
}
