import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBaseCRUD } from '../base/useCRUD'
import { useAutoRefresh } from '../base/useAutoRefresh'
import { useApi } from '../base/useApi'
import { workOrderService } from '@/core/services/BaseService'
import { LIST_COLUMNS, STATUS_MAP } from '@/core/config/listConfig'
import { showError } from '@/core/utils/errorHandler'
import { handleExportFromResponse } from '@/core/utils/io'

/**
 * 维护记录列表 Hook - 使用 WorkOrder API
 * 过滤 maintenance_type != 3 的工单（维护工单）
 */
export function useMaintenanceRecordList(options = {}) {
  const router = useRouter()
  const route = useRoute()

  const crud = useBaseCRUD({
    service: workOrderService,
    itemName: '维护记录',
    listType: 'work_orders',
    immediate: options.immediate !== false,
    defaultParams: { maintenance_type_not: 3 },
    ...options
  })

  const { setupAutoRefresh } = useAutoRefresh('maintenances')
  setupAutoRefresh(() => crud.loadData())

  const { get: fetchExportApi } = useApi('', { immediate: false })

  const handleExportExcel = async () => {
    try {
      const params = { ...route.query, maintenance_type_not: 3 }
      const response = await fetchExportApi(params, {
        url: '/common/export/work-orders/',
        responseType: 'blob'
      })

      await handleExportFromResponse(response, `维护记录_${new Date().toISOString().slice(0,10)}.xlsx`)
    } catch (err) {
      if (err === 'cancel' || err === 'close') return
      showError('导出失败: ' + (err.message || '未知错误'))
    }
  }

  const columns = computed(() => LIST_COLUMNS.maintenance_records)
  
  const tableData = computed(() => {
    return crud.tableData.value.map(item => {
      const statusText = item.status_display || item.status
      let statusObj = { text: statusText, type: 'info' }

      if (item.status === 'PENDING') {
        statusObj = { text: '待处理', type: 'warning' }
      } else if (item.status === 'PROCESSING') {
        statusObj = { text: '处理中', type: 'primary' }
      } else if (item.status === 'COMPLETED') {
        statusObj = { text: '已完成', type: 'success' }
      } else if (item.status === 'CLOSED') {
        statusObj = { text: '已关闭', type: 'info' }
      }

      return {
        ...item,
        status_display: statusObj,
        actions: [
          { text: '详情', action_type: 'view', resource_type: 'work_order', resource_id: item.id, style_class: 'btn-info-sm' }
        ]
      }
    })
  })

  const handleAction = (action) => {
    if (!action) return

    if (action.action_type === 'view') {
      router.push(`/workorder/${action.resource_id}`)
    }
  }

  return {
    ...crud,
    columns,
    tableData,
    handleAction,
    handleExportExcel
  }
}
