/**
 * 通用列表基础 Composable
 */
import { ref, computed, type Ref, type ComputedRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from './useApi'
import { getApiPath, decideRouteByActionType } from '../../utils/routeDecision'
import { useAuth } from '../../auth/useAuth'
import type { UseBaseListOptions, TableColumn, Action, User } from '../../types'

interface UseBaseListReturn {
  listHeader: Ref<string>
  columns: Ref<TableColumn[]>
  tableData: Ref<any[]>
  select: Ref<any>
  opt: Ref<any[]>
  error: Ref<string>
  filterValue: Ref<string>
  hideBack: Ref<boolean>
  backUrl: Ref<string>
  showCheckbox: Ref<boolean>
  skipCheckbox: Ref<boolean>
  isPaginated: Ref<boolean>
  currentPage: Ref<number>
  totalCount: Ref<number>
  pageSize: Ref<number>
  loading: Ref<boolean>
  apiData: Ref<any>
  selectedRows: Ref<any[]>
  selectedCount: ComputedRef<number>
  loadData: (options?: any) => Promise<void>
  handleFilter: () => Promise<void>
  handleSizeChange: (val: number) => Promise<void>
  handleCurrentChange: (val: number) => Promise<void>
  handleSelectionChange: (selection: any[]) => void
  getActionRoute: (action: Action | null) => string | null
  route: ReturnType<typeof useRoute>
  router: ReturnType<typeof useRouter>
  user: ComputedRef<User>
  apiComposable: ReturnType<typeof useApi>
}

export function useBaseList(options: UseBaseListOptions = {}): UseBaseListReturn {
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

  const listHeader = ref('')
  const columns = ref<TableColumn[]>([])
  const tableData = ref<any[]>([])
  const select = ref<any>(null)
  const opt = ref<any[]>([])
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
  const apiData = ref<any>(null)
  const selectedRows = ref<any[]>([])
  
  const selectedCount = computed(() => selectedRows.value.length)

  const loadData = async (options: any = {}): Promise<void> => {
    const { page } = typeof options === 'object' ? options : { page: options }
    
    loading.value = true
    error.value = ''
    tableData.value = []

    try {
      const effectivePath = baseApiPath || getApiPath(route.path, route.query as Record<string, any>, route.params as Record<string, any>)
      
      if (!effectivePath) {
        error.value = '无法确定API路径'
        loading.value = false
        return
      }

      const effectivePage = page !== undefined ? page : 1
      const effectivePageSize = route.query.page_size ? parseInt(route.query.page_size as string) : pageSize.value

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
        
        let newData: any[] = []
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
    } catch (err: any) {
      error.value = '加载失败：' + (err.message || '未知错误')
    } finally {
      loading.value = false
    }
  }

  const handleFilter = async (): Promise<void> => {
    if (!select.value) return
    loadData()
  }

  const handleSizeChange = async (val: number): Promise<void> => {
    pageSize.value = val
    await router.push({ query: { ...route.query, page_size: val, page: 1 } })
  }

  const handleCurrentChange = async (val: number): Promise<void> => {
    currentPage.value = val
    await loadData({ page: val })
  }

  const handleSelectionChange = (selection: any[]): void => {
    selectedRows.value = selection
  }

  const getActionRoute = (action: Action | null): string | null => {
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
    listHeader,
    columns,
    tableData,
    select,
    opt,
    error,
    filterValue,
    hideBack,
    backUrl,
    showCheckbox,
    skipCheckbox,
    isPaginated,
    currentPage,
    totalCount,
    pageSize,
    loading,
    apiData,
    selectedRows,
    selectedCount,
    loadData,
    handleFilter,
    handleSizeChange,
    handleCurrentChange,
    handleSelectionChange,
    getActionRoute,
    route,
    router,
    user,
    apiComposable
  }
}

export default useBaseList
