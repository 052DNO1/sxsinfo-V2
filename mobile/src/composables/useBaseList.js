/**
 * 通用列表基础 Composable
 * 
 * 这是所有列表页面的核心基础，封装了列表页面的通用逻辑：
 * 1. 数据加载和状态管理
 * 2. 分页处理
 * 3. 筛选功能
 * 4. 操作按钮处理
 * 5. 移动端无限滚动支持
 * 
 * 对于新手：
 * - Composable 是 Vue 3 推荐的代码复用方式
 * - 这个文件是所有 useXxxList 的基础
 * - 通过 adapter 参数适配不同的数据格式
 * - 支持PC端分页和移动端无限滚动两种模式
 * 
 * 使用示例：
 * ```js
 * import { useBaseList } from '@/composables/useBaseList'
 * import { adaptTermList } from '@/utils/adapters'
 * 
 * const {
 *   tableData,      // 列表数据
 *   columns,        // 列配置
 *   loading,        // 加载状态
 *   loadData,       // 加载数据方法
 *   handleFilter,   // 筛选方法
 *   currentPage,    // 当前页码
 *   totalCount,     // 总条数
 * } = useBaseList({
 *   adapter: adaptTermList,  // 数据适配器
 *   immediate: true,         // 立即加载
 * })
 * ```
 */

import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'
import { getApiPath, decideRouteByActionType } from '@/utils/routeDecision'
import { useAuth } from '@/composables/useAuth'

/**
 * 通用列表 Composable
 * 
 * @param {Object} options - 配置选项
 * @param {Function} options.adapter - 数据适配器函数，将后端数据转换为前端格式
 * @param {String} options.baseApiPath - 可选的 API 路径覆盖
 * @param {Function} options.onDataLoaded - 数据加载完成回调
 * @param {Boolean} options.immediate - 是否立即加载数据（默认 false）
 * @param {Object} options.defaultParams - 默认查询参数
 * @returns {Object} 列表相关的状态和方法
 */
export function useBaseList(options = {}) {
  // 解构配置选项
  const {
    adapter,           // 数据适配器：将后端数据转换为 { columns, data } 格式
    baseApiPath = '',  // API 路径（可选，默认从路由自动推断）
    onDataLoaded,      // 数据加载完成回调
    immediate = false, // 是否立即加载
    defaultParams = {} // 默认查询参数
  } = options

  // ==================== 路由和认证 ====================
  const route = useRoute()
  const router = useRouter()
  const { user } = useAuth()
  const apiComposable = useApi('', { immediate: false })

  // ==================== 响应式状态 ====================
  
  /** 列表标题 */
  const listHeader = ref('')
  
  /** 列配置（表格列定义） */
  const columns = ref([])
  
  /** 表格数据 */
  const tableData = ref([])
  
  /** 筛选配置 */
  const select = ref(null)
  
  /** 操作按钮配置 */
  const opt = ref([])
  
  /** 错误信息 */
  const error = ref('')
  
  /** 筛选值 */
  const filterValue = ref('')
  
  /** 是否隐藏返回按钮 */
  const hideBack = ref(false)
  
  /** 返回URL */
  const backUrl = ref('')
  
  /** 是否显示多选框 */
  const showCheckbox = ref(false)
  
  /** 是否跳过多选框 */
  const skipCheckbox = ref(false)
  
  /** 是否分页 */
  const isPaginated = ref(false)
  
  /** 当前页码 */
  const currentPage = ref(1)
  
  /** 总条数 */
  const totalCount = ref(0)
  
  /** 每页条数 */
  const pageSize = ref(10)
  
  /** 加载状态 */
  const loading = ref(false)
  
  /** 原始 API 响应数据 */
  const apiData = ref(null)
  
  /** 选中的行数据 */
  const selectedRows = ref([])
  
  // ==================== 移动端专用状态 ====================
  
  /** 无限滚动是否完成 */
  const finished = ref(false)
  
  /** 下拉刷新状态 */
  const refreshing = ref(false)

  // ==================== 计算属性 ====================
  
  /** 选中行数量 */
  const selectedCount = computed(() => selectedRows.value.length)

  // ==================== 核心方法 ====================

  /**
   * 加载数据
   * 
   * @param {Object|Boolean} options - 配置选项或旧格式的布尔值
   * @param {Number} options.page - 指定页码（PC端分页）
   * @param {Boolean} options.isLoadMore - 是否为"加载更多"（移动端无限滚动）
   * 
   * 支持的调用方式：
   * - loadData() - 加载第一页
   * - loadData({ page: 2 }) - 加载指定页
   * - loadData({ isLoadMore: true }) - 加载更多（移动端无限滚动）
   * - loadData(true) - 旧格式，加载更多（兼容）
   * 
   * 执行流程：
   * 1. 确定API路径
   * 2. 构建查询参数
   * 3. 发起请求
   * 4. 使用适配器转换数据
   * 5. 更新状态
   */
  const loadData = async (options = {}) => {
    const { page, isLoadMore } = typeof options === 'object' 
      ? { page: options.page, isLoadMore: options.isLoadMore || false }
      : { page: undefined, isLoadMore: options === true }
    
    if (!isLoadMore) {
      loading.value = true
      error.value = ''
      finished.value = false
      tableData.value = []
      currentPage.value = 1
    }

    try {
      const effectivePath = baseApiPath || getApiPath(route.path, route.query, route.params)
      
      if (!effectivePath) {
        error.value = '无法确定API路径，请检查页面地址'
        loading.value = false
        finished.value = true
        return
      }

      let effectivePage
      if (isLoadMore) {
        effectivePage = currentPage.value + 1
      } else if (page !== undefined) {
        effectivePage = page
      } else {
        effectivePage = 1
      }
      
      const effectivePageSize = route.query.page_size ? parseInt(route.query.page_size) : pageSize.value

      const queryParams = {
        ...defaultParams,
        page: effectivePage,
        page_size: effectivePageSize,
        pagesize: effectivePageSize
      }
      
      const response = await apiComposable.get(queryParams, { url: effectivePath })
      apiData.value = response

      if (Array.isArray(response)) {
        const newData = response
        if (isLoadMore) {
          tableData.value = [...tableData.value, ...newData]
        } else {
          tableData.value = newData
        }
        totalCount.value = response.length
        isPaginated.value = false
        finished.value = true
      } else if (response && typeof response === 'object') {
        listHeader.value = response.listheader || ''
        
        let newData = []
        if (adapter) {
          const adapted = adapter(response)
          newData = adapted.data || []
          
          if (!isLoadMore) {
            columns.value = adapted.columns
            if (adapted.page_obj) response.page_obj = adapted.page_obj
            if (adapted.paginator) response.paginator = adapted.paginator
            if (adapted.is_paginated !== undefined) response.is_paginated = adapted.is_paginated
          }
        } else {
          newData = response.data || response.results || []
        }

        if (isLoadMore) {
          tableData.value = [...tableData.value, ...newData]
        } else {
          tableData.value = newData
        }

        if (!isLoadMore) {
          select.value = response.select || null
          opt.value = response.opt || []
          error.value = response.error || ''
          hideBack.value = response.hide_back || false
          backUrl.value = response.back_url || ''
          
          if (response.show_checkbox !== undefined) {
            showCheckbox.value = response.show_checkbox
          } else {
            showCheckbox.value = columns.value.length > 0
          }
          
          skipCheckbox.value = response.skip_checkbox || false
        }
        
        // 总是更新总条数，无论是否是加载更多
        const respTotal = response.paginator?.count || response.page_obj?.paginator?.count || 0
        const respPerPage = response.paginator?.per_page || response.page_obj?.paginator?.per_page || 10
        
        totalCount.value = respTotal || tableData.value.length
        pageSize.value = respPerPage
        
        if (!isLoadMore) {
          isPaginated.value = response.is_paginated !== undefined ? response.is_paginated : (respTotal > respPerPage)
          currentPage.value = response.page_obj?.number || 1
          
          if (select.value && select.value.name) {
            const queryVal = route.query[select.value.name]
            if (queryVal !== undefined) {
              if (select.value.options) {
                const option = select.value.options.find(o => String(o.id) === String(queryVal))
                filterValue.value = option ? option.id : queryVal
              } else {
                filterValue.value = queryVal
              }
            } else {
              filterValue.value = ''
            }
          }
        } else {
          currentPage.value = effectivePage
        }
        
        // 检查是否所有数据都已加载
        if (newData.length === 0 || tableData.value.length >= totalCount.value) {
          finished.value = true
        }
        // 如果返回的数据条数小于每页条数，也应该标记为完成
        if (newData.length < pageSize.value) {
          finished.value = true
        }
      } else {
        error.value = '响应数据格式错误'
        finished.value = true
      }

      if (onDataLoaded) {
        onDataLoaded(response, isLoadMore)
      }

    } catch (err) {
      error.value = '加载数据失败：' + (err.message || '未知错误')
      finished.value = true
    } finally {
      loading.value = false
      refreshing.value = false
    }
  }

  // ==================== 事件处理方法 ====================

  /**
   * 处理筛选
   * 
   * 直接重新加载数据，不通过路由变化触发
   */
  const handleFilter = async () => {
    if (!select.value) return
    loadData()
  }

  /**
   * 处理每页条数变化
   * @param {number} val - 新的每页条数
   */
  const handleSizeChange = async (val) => {
    pageSize.value = val
    const { pagesize, ...restQuery } = route.query
    const newQuery = { ...restQuery, page_size: val, page: 1 }
    await router.push({ query: newQuery })
  }

  /**
   * 处理页码变化
   * @param {number} val - 新的页码
   */
  const handleCurrentChange = async (val) => {
    currentPage.value = val
    await loadData({ page: val })
  }

  /**
   * 处理多选变化
   * @param {Array} selection - 选中的行数据
   */
  const handleSelectionChange = (selection) => {
    selectedRows.value = selection
  }

  /**
   * 获取操作对应的路由
   * 
   * @param {Object} action - 操作配置对象
   * @returns {string|null} 路由路径
   * 
   * 根据操作的 action_type 和 resource_type 决定跳转路由
   */
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
  
  /**
   * 处理通用操作按钮点击
   * @param {Object} option - 操作配置
   */
  const handleGenericOptionClick = async (option) => {
    const navUrl = getActionRoute(option)
    if (navUrl) {
      try {
        await router.push(navUrl)
      } catch (err) {
        window.location.href = navUrl
      }
    }
  }

  // ==================== 初始化 ====================
  
  // 如果设置了立即加载，则立即执行
  if (immediate) {
    loadData()
  }

  // ==================== 返回值 ====================
  
  return {
    // 状态
    listHeader, columns, tableData, select, opt, error, filterValue,
    hideBack, backUrl, showCheckbox, skipCheckbox, isPaginated,
    currentPage, totalCount, pageSize, loading, apiData, selectedRows,
    finished, refreshing,
    
    // 计算属性
    selectedCount,
    
    // 方法
    loadData,
    handleFilter,
    handleSizeChange,
    handleCurrentChange,
    handleSelectionChange,
    getActionRoute,
    handleGenericOptionClick,
    
    // 核心引用（供子 composable 使用）
    route, router, user, apiComposable
  }
}
