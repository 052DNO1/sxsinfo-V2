import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/core/store/user'
import { useAppStore } from '@/core/store/app'
import { safeConfirm, showSuccess, showError } from '@/core/utils/errorHandler'

/**
 * 通用 CRUD Composable - 直接对接后端V2
 * 
 * @param {Object} options - 配置选项
 * @param {Object} options.service - 服务对象 (BaseService 实例)
 * @param {Boolean} options.immediate - 是否立即加载数据（默认 false）
 * @param {Object} options.defaultParams - 默认查询参数
 * @param {String} options.itemName - 提示语中的项目名称 (如 "实训室")
 * @param {String} options.listType - 列表类型，用于自动刷新（如 'users', 'semesters'）
 * @returns {Object} CRUD 相关的状态和方法
 */
export function useBaseCRUD(options = {}) {
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
  const user = computed(() => userStore.user)

  // ---------------- 状态定义 ----------------
  const tableData = ref([])
  const loading = ref(false)
  const error = ref('')
  const totalCount = ref(0)
  const pageSize = ref(20)
  const currentPage = ref(1)
  const totalPages = ref(1)
  const selectedRows = ref([])

  // ---------------- 核心加载 ----------------
  const loadData = async (params = {}) => {
    loading.value = true
    error.value = ''
    
    try {
      const { _t, ...restQuery } = route.query
      const queryParams = {
        ...defaultParams,
        ...restQuery,
        ...params,
        page: params.page || restQuery.page || 1,
        page_size: params.page_size || restQuery.page_size || pageSize.value
      }

      // 直接调用后端API
      const response = await service.list(queryParams)
      
      // 直接处理后端V2格式: { success, data: { list, pagination: { total, page, page_size, total_pages } } }
      if (response && response.success && response.data) {
        const { list, pagination } = response.data
        tableData.value = list || []
        totalCount.value = pagination?.total || 0
        currentPage.value = pagination?.page || 1
        pageSize.value = pagination?.page_size || 20
        totalPages.value = pagination?.total_pages || 1
      } else {
        tableData.value = []
        totalCount.value = 0
      }

      if (onDataLoaded) onDataLoaded(response)
    } catch (err) {
      error.value = err.message || '加载失败'
      tableData.value = []
      totalCount.value = 0
    } finally {
      loading.value = false
    }
  }

  // ---------------- 通用操作 ----------------
  const execDelete = async (item, nameField = 'name') => {
    const name = item[nameField] || itemName
    const confirmed = await safeConfirm(`确定要删除 "${name}" 吗？此操作不可恢复！`)
    if (!confirmed) return
    try {
      const response = await service.delete(item.id)
      if (response.success) {
        showSuccess('删除成功')
        loadData()
      }
    } catch (err) {
      showError(err.message || '删除失败')
    }
  }

  const execBatchDelete = async (selection, idParam = 'ids') => {
    if (!selection || !selection.length) return
    const confirmed = await safeConfirm(`确定要删除选中的 ${selection.length} 个${itemName} 吗？`)
    if (!confirmed) return
    try {
      const ids = selection.map(item => item.id)
      const response = await service.batchDelete(ids, idParam)
      if (response.success) {
        showSuccess('批量删除成功')
        loadData()
      }
    } catch (err) {
      showError(err.message || '删除失败')
    }
  }

  // ---------------- 分页处理 ----------------
  const handleSizeChange = (val) => {
    pageSize.value = val
    router.push({ query: { ...route.query, page_size: val, page: 1 } })
  }

  const handleCurrentChange = (val) => {
    currentPage.value = val
    router.push({ query: { ...route.query, page: val } })
  }

  const handleFilter = (filterValue, filterName = 'search') => {
    router.push({ query: { ...route.query, [filterName]: filterValue, page: 1 } })
  }

  // ---------------- 生命周期 ----------------
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
    // 状态
    tableData, loading, error, totalCount, pageSize, currentPage, totalPages,
    selectedRows, user, route, router,
    
    // 方法
    loadData, handleSizeChange, handleCurrentChange, handleFilter,
    execDelete, execBatchDelete,
    handleSelectionChange: (val) => selectedRows.value = val,
    goBack: () => router.back(),
    goHome: () => router.push('/')
  }
}
