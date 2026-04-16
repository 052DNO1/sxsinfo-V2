import { ref, computed, watch, type Ref, type ComputedRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../store/user'
import { useAppStore } from '../../store/app'
import { safeConfirm, showSuccess, showError } from '../../utils/errorHandler'
import { cacheManager } from '../../services/cacheManager'
import type { UseCRUDOptions, ApiResponse, PaginatedResponse, User } from '../../types'

interface UseCRUDReturn<T> {
  tableData: Ref<T[]>
  loading: Ref<boolean>
  error: Ref<string>
  totalCount: Ref<number>
  pageSize: Ref<number>
  currentPage: Ref<number>
  totalPages: Ref<number>
  selectedRows: Ref<T[]>
  user: ComputedRef<User>
  route: ReturnType<typeof useRoute>
  router: ReturnType<typeof useRouter>
  loadData: (params?: Record<string, any>) => Promise<void>
  handleSizeChange: (val: number) => void
  handleCurrentChange: (val: number) => void
  handleFilter: (filterValue: any, filterName?: string) => void
  execDelete: (item: T, nameField?: string) => Promise<void>
  execBatchDelete: (selection: T[], idParam?: string) => Promise<void>
  handleSelectionChange: (val: T[]) => void
  goBack: () => void
  goHome: () => void
}

export function useBaseCRUD<T extends { id?: number | string }>(options: UseCRUDOptions = {}): UseCRUDReturn<T> {
  const {
    service,
    immediate = false,
    defaultParams = {},
    itemName = '项目',
    listType,
    onDataLoaded,
    skipAutoLoad = false
  } = options

  const route = useRoute()
  const router = useRouter()
  const userStore = useUserStore()
  const appStore = useAppStore()
  const user = computed(() => userStore.user as User)

  const tableData = ref<T[]>([])
  const loading = ref(false)
  const error = ref('')
  const totalCount = ref(0)
  const pageSize = ref(20)
  const currentPage = ref(1)
  const totalPages = ref(1)
  const selectedRows = ref<T[]>([])

  const loadData = async (params: Record<string, any> = {}): Promise<void> => {
    loading.value = true
    error.value = ''
    
    try {
      const { _t, ...restQuery } = route.query as Record<string, any>
      const queryParams = {
        ...defaultParams,
        ...restQuery,
        ...params,
        page: params.page || restQuery.page || 1,
        page_size: params.page_size || restQuery.page_size || pageSize.value
      }

      const response = await service?.list(queryParams) as ApiResponse<PaginatedResponse<T>> | null
      
      if (response && response.success && response.data) {
        const data = response.data
        const pagination = data.pagination || {}
        tableData.value = data.list || []
        totalCount.value = pagination.total || 0
        currentPage.value = pagination.page || 1
        pageSize.value = pagination.page_size || 20
        totalPages.value = pagination.total_pages || 1
      } else {
        tableData.value = []
        totalCount.value = 0
      }

      if (onDataLoaded) onDataLoaded(response)
    } catch (err: any) {
      error.value = err.message || '加载失败'
      tableData.value = []
      totalCount.value = 0
    } finally {
      loading.value = false
    }
  }

  const execDelete = async (item: T, nameField: string = 'name'): Promise<void> => {
    const name = (item as any)[nameField] || itemName
    const confirmed = await safeConfirm(`确定要删除 "${name}" 吗？此操作不可恢复！`)
    if (!confirmed) return
    try {
      const response = await service?.delete(item.id as number) as ApiResponse | undefined
      if (response?.success) {
        showSuccess('删除成功')
        
        if (listType) {
          cacheManager.clearByResourceType(listType)
          cacheManager.triggerRefresh(listType)
        }
        
        loadData()
      }
    } catch (err: any) {
      showError(err.message || '删除失败')
    }
  }

  const execBatchDelete = async (selection: T[], idParam: string = 'ids'): Promise<void> => {
    if (!selection || !selection.length) return
    const confirmed = await safeConfirm(`确定要删除选中的 ${selection.length} 个${itemName} 吗？`)
    if (!confirmed) return
    try {
      const ids = selection.map(item => item.id)
      const response = await service?.batchDelete(ids as number[], idParam) as ApiResponse | undefined
      if (response?.success) {
        showSuccess('批量删除成功')
        
        if (listType) {
          cacheManager.clearByResourceType(listType)
          cacheManager.triggerRefresh(listType)
        }
        
        loadData()
      }
    } catch (err: any) {
      showError(err.message || '删除失败')
    }
  }

  const handleSizeChange = (val: number): void => {
    pageSize.value = val
    router.push({ query: { ...route.query, page_size: val, page: 1 } })
  }

  const handleCurrentChange = (val: number): void => {
    currentPage.value = val
    router.push({ query: { ...route.query, page: val } })
  }

  const handleFilter = (filterValue: any, filterName: string = 'search'): void => {
    router.push({ query: { ...route.query, [filterName]: filterValue, page: 1 } })
  }

  if (!skipAutoLoad) {
    watch(() => route.fullPath, (newPath, oldPath) => {
      if (!oldPath || newPath !== oldPath) {
        loadData()
      }
    }, { immediate: immediate })
  }

  if (listType) {
    watch(() => appStore.listRefreshTriggers[listType], (newVal, oldVal) => {
      if (newVal && newVal !== oldVal) {
        loadData()
      }
    })
  }

  return {
    tableData,
    loading,
    error,
    totalCount,
    pageSize,
    currentPage,
    totalPages,
    selectedRows,
    user,
    route,
    router,
    
    loadData,
    handleSizeChange,
    handleCurrentChange,
    handleFilter,
    execDelete,
    execBatchDelete,
    handleSelectionChange: (val: T[]) => { selectedRows.value = val },
    goBack: () => router.back(),
    goHome: () => router.push('/')
  }
}

export default useBaseCRUD
