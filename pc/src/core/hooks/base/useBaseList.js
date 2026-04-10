/**
 * 通用列表基础 Composable
 */
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from './useApi'
import { getApiPath, decideRouteByActionType } from '@/core/utils/routeDecision'
import { useAuth } from '@/core/auth/useAuth'

/**
 * 通用列表 Composable
 * 
 * @param {Object} options - 配置选项
 * @param {Function} options.adapter - 数据适配器函数
 * @param {String} options.baseApiPath - API 路径
 * @param {Function} options.onDataLoaded - 数据加载完成回调
 * @param {Boolean} options.immediate - 是否立即加载
 * @param {Object} options.defaultParams - 默认查询参数
 * @returns {Object} 列表相关的状态和方法
 */
export function useBaseList(options = {}) {
  const {
    adapter,
    baseApiPath = '',
    onDataLoaded,
    immediate = false,
    defaultParams = {}
  } = options

  const route = useRoute()
  const router = useRouter()
  const { user } = useAuth()
  const apiComposable = useApi('', { immediate: false })

  // ---------------- 状态定义 ----------------
  const listHeader = ref('')
  const columns = ref([])
  const tableData = ref([])
  const select = ref(null)
  const opt = ref([])
  const error = ref('')
  const filterValue = ref('')
  const hideBack = ref(false)
  const backUrl = ref('')
  const showCheckbox = ref(false)
  const skipCheckbox = ref(false)
  const isPaginated = ref(false)
  const currentPage = ref(1)
  const totalCount = ref(0)
  const pageSize = ref(10)
  const loading = ref(false)
  const apiData = ref(null)
  const selectedRows = ref([])
  
  const selectedCount = computed(() => selectedRows.value.length)

  // ---------------- 核心加载 ----------------
  const loadData = async (options = {}) => {
    const { page } = typeof options === 'object' ? options : { page: options }
    
    loading.value = true
    error.value = ''
    tableData.value = []

    try {
      const effectivePath = baseApiPath || getApiPath(route.path, route.query, route.params)
      
      if (!effectivePath) {
        error.value = '无法确定API路径'
        loading.value = false
        return
      }

      const effectivePage = page !== undefined ? page : 1
      const effectivePageSize = route.query.page_size ? parseInt(route.query.page_size) : pageSize.value

      const queryParams = {
        ...defaultParams,
        page: effectivePage,
        page_size: effectivePageSize
      }
      
      const response = await apiComposable.get(queryParams, { url: effectivePath })
      apiData.value = response

      if (Array.isArray(response)) {
        tableData.value = response
        totalCount.value = response.length
        isPaginated.value = false
      } else if (response && typeof response === 'object') {
        listHeader.value = response.listheader || ''
        
        let newData = []
        if (adapter) {
          const adapted = adapter(response)
          newData = adapted.data || []
          columns.value = adapted.columns || []
        } else {
          newData = response.data || response.results || []
        }

        tableData.value = newData
        select.value = response.select || null
        opt.value = response.opt || []
        error.value = response.error || ''
        hideBack.value = response.hide_back || false
        backUrl.value = response.back_url || ''
        showCheckbox.value = response.show_checkbox !== undefined ? response.show_checkbox : columns.value.length > 0
        skipCheckbox.value = response.skip_checkbox || false
        
        const respTotal = response.paginator?.count || response.data?.pagination?.total || 0
        const respPerPage = response.paginator?.per_page || response.data?.pagination?.page_size || 10
        
        totalCount.value = respTotal || tableData.value.length
        pageSize.value = respPerPage
        isPaginated.value = response.is_paginated !== undefined ? response.is_paginated : (respTotal > respPerPage)
        currentPage.value = response.page_obj?.number || response.data?.pagination?.page || 1
      }

      if (onDataLoaded) onDataLoaded(response)
    } catch (err) {
      error.value = '加载失败：' + (err.message || '未知错误')
    } finally {
      loading.value = false
    }
  }

  // ---------------- 方法定义 ----------------
  const handleFilter = async () => {
    if (!select.value) return
    loadData()
  }

  const handleSizeChange = async (val) => {
    pageSize.value = val
    await router.push({ query: { ...route.query, page_size: val, page: 1 } })
  }

  const handleCurrentChange = async (val) => {
    currentPage.value = val
    await loadData({ page: val })
  }

  const handleSelectionChange = (selection) => {
    selectedRows.value = selection
  }

  const getActionRoute = (action) => {
    if (!action) return null
    if (action.action_type && action.resource_type) {
      const context = {
        ...action.context,
        resource_id: action.resource_id,
        id: action.resource_id
      }
      if (route.query.qtype !== undefined) {
        context.qtype = route.query.qtype
      }
      return decideRouteByActionType(action.action_type, action.resource_type, context, {})
    }
    return action.url || null
  }

  if (immediate) loadData()

  return {
    listHeader, columns, tableData, select, opt, error, filterValue,
    hideBack, backUrl, showCheckbox, skipCheckbox, isPaginated,
    currentPage, totalCount, pageSize, loading, apiData, selectedRows,
    selectedCount,
    loadData, handleFilter, handleSizeChange, handleCurrentChange, handleSelectionChange,
    getActionRoute,
    route, router, user, apiComposable
  }
}
