import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBaseCRUD } from '../base/useCRUD'
import { useAutoRefresh } from '../base/useAutoRefresh'
import { useApi } from '../base/useApi'
import { recordService, workOrderService } from '@/core/services/BaseService'
import { LIST_COLUMNS } from '@/core/config/listConfig'
import { showError } from '@/core/utils/errorHandler'
import { handleExportFromResponse } from '@/core/utils/io'

export function useRecordList(options = {}) {
  const route = useRoute()
  const router = useRouter()
  
  const isArchiveMode = computed(() => route.path.includes('view-archived'))
  
  const recordType = computed(() => {
    const typeQuery = route.query.type
    if (typeQuery) {
      if (typeQuery === 'fault') return 'archive-fault'
      if (typeQuery === 'maintain') return 'archive-maintain'
      if (typeQuery === 'usage') return 'archive-usage'
      if (typeQuery === 'class') return 'archive-class'
      if (typeQuery === 'lab_info') return 'archive-lab_info'
      if (typeQuery === 'device_info') return 'archive-device_info'
      if (typeQuery === 'user_info') return 'archive-user_info'
    }
    const path = route.path
    if (path.includes('fault')) return 'workorder'
    if (path.includes('maintain')) return 'maintain'
    return 'usage'
  })
  
  const isFaultList = computed(() => ['workorder', 'archive-fault'].includes(recordType.value))
  const isMaintainList = computed(() => ['maintain', 'archive-maintain'].includes(recordType.value))
  
  const service = computed(() => {
    if (isFaultList.value) return workOrderService
    return recordService
  })
  
  const itemName = computed(() => {
    if (isFaultList.value) return '故障工单'
    if (isMaintainList.value) return '维护记录'
    return '使用记录'
  })
  
  const listType = computed(() => {
    if (isFaultList.value) return 'work_orders'
    if (isMaintainList.value) return 'maintenance_records'
    return 'records'
  })

  const archiveTypeMap = {
    'archive-usage': 'usage',
    'archive-maintain': 'maintain',
    'archive-fault': 'fault',
    'archive-class': 'class',
    'archive-lab_info': 'lab_info',
    'archive-device_info': 'device_info',
    'archive-user_info': 'user_info'
  }

  const { get: fetchArchiveData } = useApi('', { immediate: false })
  
  const archiveTableData = ref([])
  const archiveTotalCount = ref(0)
  const archiveLoading = ref(false)
  const archiveCurrentPage = ref(1)
  const archivePageSize = ref(20)
  
  const crud = useBaseCRUD({
    service: service.value,
    itemName: itemName.value,
    listType: listType.value,
    immediate: !isArchiveMode.value,
    defaultParams: isFaultList.value ? { maintenance_type: 3 } : {},
    ...options
  })

  const { setupAutoRefresh } = useAutoRefresh(listType.value)
  setupAutoRefresh(() => crud.loadData())

  const loadArchiveData = async () => {
    if (!isArchiveMode.value) return
    
    archiveLoading.value = true
    try {
      const semesterId = route.params.id
      const typeParam = archiveTypeMap[recordType.value] || route.query.type
      const page = route.query.page || 1
      const pageSize = route.query.page_size || 20
      
      const res = await fetchArchiveData(
        { type: typeParam, page, page_size: pageSize },
        { url: `/schedules/archived/${semesterId}/` }
      )
      
      if (res && res.success) {
        const data = res.data || res
        if (data.mode === 'list' && data.list) {
          archiveTableData.value = data.list
          archiveTotalCount.value = data.total || 0
          archiveCurrentPage.value = data.page || 1
          archivePageSize.value = data.page_size || 20
        } else {
          archiveTableData.value = []
          archiveTotalCount.value = 0
        }
      } else {
        archiveTableData.value = []
        archiveTotalCount.value = 0
      }
    } catch (err) {
      archiveTableData.value = []
      archiveTotalCount.value = 0
    } finally {
      archiveLoading.value = false
    }
  }

  watch(isArchiveMode, (val) => {
    if (val) {
      loadArchiveData()
    }
  }, { immediate: true })
  
  watch(() => [route.query.page, route.query.page_size], () => {
    if (isArchiveMode.value) {
      loadArchiveData()
    }
  })

  const columns = computed(() => {
    if (isFaultList.value) return LIST_COLUMNS.work_orders
    if (isMaintainList.value) return LIST_COLUMNS.maintenance_records || LIST_COLUMNS.records
    return LIST_COLUMNS.records
  })
  
  const listHeader = computed(() => {
    if (isArchiveMode.value) {
      const typeNames = {
        'usage': '使用记录列表',
        'maintain': '维护记录列表',
        'fault': '故障工单列表',
        'class': '课表记录列表',
        'lab_info': '实训室信息列表',
        'device_info': '设备信息列表',
        'user_info': '用户信息列表'
      }
      const typeKey = archiveTypeMap[recordType.value] || route.query.type
      return typeNames[typeKey] || '归档记录列表'
    }
    if (isFaultList.value) return '故障工单列表'
    if (isMaintainList.value) return '维护记录列表'
    return '使用记录列表'
  })
  
  const isPaginated = ref(true)
  const showCheckbox = computed(() => !isArchiveMode.value)
  const exportUrls = ref(null)
  
  const opt = computed(() => {
    if (isArchiveMode.value) return []
    return [
      { text: isFaultList.value ? '故障上报' : '添加记录', onclick: 'add', type: 'primary', icon: 'Plus' }
    ]
  })
  
  const tableData = computed(() => {
    const sourceData = isArchiveMode.value ? archiveTableData.value : crud.tableData.value
    return sourceData.map(item => {
      let statusDisplay = item.status_display
      if (isFaultList.value) {
        let statusObj = { text: item.status_display || item.status, type: 'info' }
        if (item.status === 'PENDING') {
          statusObj = { text: '待处理', type: 'warning' }
        } else if (item.status === 'PROCESSING') {
          statusObj = { text: '处理中', type: 'primary' }
        } else if (item.status === 'COMPLETED') {
          statusObj = { text: '已完成', type: 'success' }
        } else if (item.status === 'CLOSED') {
          statusObj = { text: '已关闭', type: 'info' }
        }
        statusDisplay = statusObj
      }
      return {
        ...item,
        status_display: statusDisplay,
        actions: [
          { text: '详情', action_type: 'detail', resource_type: recordType.value, resource_id: item.id }
        ]
      }
    })
  })

  const loading = computed(() => isArchiveMode.value ? archiveLoading.value : crud.loading.value)
  const totalCount = computed(() => isArchiveMode.value ? archiveTotalCount.value : crud.totalCount.value)
  const currentPage = computed({
    get: () => isArchiveMode.value ? archiveCurrentPage.value : crud.currentPage.value,
    set: (val) => {
      if (isArchiveMode.value) {
        archiveCurrentPage.value = val
      } else {
        crud.currentPage.value = val
      }
    }
  })
  const pageSize = computed({
    get: () => isArchiveMode.value ? archivePageSize.value : crud.pageSize.value,
    set: (val) => {
      if (isArchiveMode.value) {
        archivePageSize.value = val
      } else {
        crud.pageSize.value = val
      }
    }
  })

  const handleSizeChange = (val) => {
    if (isArchiveMode.value) {
      router.push({ query: { ...route.query, page_size: val, page: 1 } })
    } else {
      crud.handleSizeChange(val)
    }
  }

  const handleCurrentChange = (val) => {
    if (isArchiveMode.value) {
      router.push({ query: { ...route.query, page: val } })
    } else {
      crud.handleCurrentChange(val)
    }
  }

  const handleOptionClick = async (option) => {
    if (!option) return
    if (option.onclick === 'add') {
      if (isFaultList.value) {
        router.push('/report-maintenance')
      } else {
        router.push('/add-record')
      }
    }
  }

  const handleAction = (action) => {
    if (!action) return
    
    if (action.action_type === 'detail') {
      router.push(`/record-detail/${action.resource_type}/${action.resource_id}`)
    }
  }

  const { get: fetchExportApi } = useApi('', { immediate: false })

  const handleExportExcel = async () => {
    try {
      let exportUrl = ''
      let params = { ...route.query }

      if (isFaultList.value) {
        exportUrl = '/common/export/work-orders/'
        params.maintenance_type = 3
      } else if (isMaintainList.value) {
        exportUrl = '/common/export/work-orders/'
        params.maintenance_type_not = 3
      } else {
        exportUrl = '/common/export/records/'
      }

      const response = await fetchExportApi(params, {
        url: exportUrl,
        responseType: 'blob'
      })

      const filename = isFaultList.value ? '故障工单' : (isMaintainList.value ? '维护记录' : '使用记录')
      await handleExportFromResponse(response, `${filename}_${new Date().toISOString().slice(0,10)}.xlsx`)
    } catch (err) {
      if (err === 'cancel' || err === 'close') return
      showError('导出失败: ' + (err.message || '未知错误'))
    }
  }

  return { 
    columns,
    tableData,
    listHeader,
    loading,
    error: computed(() => crud.error.value),
    totalCount,
    currentPage,
    pageSize,
    isPaginated,
    showCheckbox,
    opt,
    exportUrls,
    recordType,
    handleOptionClick,
    handleAction,
    handleExportExcel,
    handleSizeChange,
    handleCurrentChange,
    loadData: isArchiveMode.value ? loadArchiveData : crud.loadData
  }
}
