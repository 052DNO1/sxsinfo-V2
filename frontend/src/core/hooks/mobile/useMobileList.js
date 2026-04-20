/**
 * 移动端列表Hook适配器
 * 
 * 将PC端的 useBaseCRUD/domain hooks 适配为移动端 Vant UI 所需的格式
 * 复用PC端的 BaseService、缓存、自动刷新等全部能力
 */

import { ref, computed } from 'vue'
import { useBaseCRUD } from '@/core/hooks/base/useCRUD'
import { LIST_COLUMNS } from '@/core/config/listConfig'
import { STATUS_MAP } from '@/core/config/listConfig'
import { showSuccess, showError } from '@/core/utils/errorHandler'

/**
 * 移动端通用列表Hook
 * @param {Object} options
 * @param {Object} options.service - BaseService实例
 * @param {String} options.listType - 列表类型(对应LIST_COLUMNS的key)
 * @param {String} options.itemName - 项目名称(用于提示)
 * @param {Object} options.defaultParams - 默认查询参数
 * @param {Boolean} options.immediate - 是否立即加载
 */
export function useMobileList(options = {}) {
  const {
    service,
    listType,
    itemName = '项目',
    defaultParams = {},
    immediate = true,
    transformItem = null,
    onItemClick = null,
    onAddClick = null
  } = options

  const crud = useBaseCRUD({
    service,
    immediate,
    defaultParams,
    itemName,
    listType
  })

  // 从配置获取列定义
  const columns = computed(() => LIST_COLUMNS[listType] || [])

  // 转换后的数据（可选）
  const displayData = computed(() => {
    if (!transformItem) return crud.tableData.value
    return crud.tableData.value.map(item => transformItem(item))
  })

  // 状态文本获取
  const getStatusText = (status) => {
    if (!status) return ''
    if (typeof status === 'object' && status.text) return status.text
    const mapEntry = Object.entries(STATUS_MAP).find(([k]) => 
      status.toString().toLowerCase().includes(k.toLowerCase())
    )
    return mapEntry ? mapEntry[1].text : status
  }

  const getStatusType = (status) => {
    if (!status) return 'default'
    if (typeof status === 'object' && status.type) return status.type
    const mapEntry = Object.entries(STATUS_MAP).find(([k]) => 
      status.toString().toLowerCase().includes(k.toLowerCase())
    )
    return mapEntry ? mapEntry[1].type : 'default'
  }

  // 点击处理
  const handleItemClick = (item) => {
    if (onItemClick) {
      onItemClick(item, crud.router)
    }
  }

  // 添加按钮点击
  const handleAddClick = () => {
    if (onAddClick) {
      onAddClick(crud.router)
    }
  }

  // 分页处理
  const handlePageChange = async (page) => {
    await crud.loadData({ page })
  }

  // 下拉刷新
  const handleRefresh = async () => {
    await crud.loadData()
  }

  return {
    // 原始CRUD数据和方法
    ...crud,

    // 移动端专用
    columns,
    displayData,
    
    // 状态工具
    getStatusText,
    getStatusType,

    // 事件处理
    handleItemClick,
    handleAddClick,
    handlePageChange,
    handleRefresh,

    // 计算属性
    isPaginated: computed(() => crud.totalCount.value > 0),
    isEmpty: computed(() => !crud.loading.value && crud.tableData.value.length === 0),
    hasError: computed(() => !!crud.error.value)
  }
}

/**
 * 快速创建列表Hook的工厂函数
 */
export function createMobileList(config) {
  return useMobileList(config)
}
