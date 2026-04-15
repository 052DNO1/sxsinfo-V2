import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBaseCRUD } from '../base/useCRUD'
import { useApi } from '../base/useApi'
import { maintenanceRecordService } from '@/core/services/BaseService'
import { LIST_COLUMNS, STATUS_MAP } from '@/core/config/listConfig'
import { showError } from '@/core/utils/errorHandler'
import { handleExportFromResponse } from '@/core/utils/io'

/**
 * 维护记录列表 Hook - 直接对接后端V2
 */
export function useMaintenanceRecordList(options = {}) {
  const router = useRouter()
  const route = useRoute()

  const crud = useBaseCRUD({
    service: maintenanceRecordService,
    itemName: '维护记录',
    listType: 'maintenance_records',
    immediate: options.immediate !== false,
    ...options
  })

  const { get: fetchExportApi } = useApi('', { immediate: false })

  const handleExportExcel = async () => {
    try {
      const params = { ...route.query }
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

      if (item.status === 'maintained') {
        statusObj = { text: '已维护', type: 'success' }
      } else if (item.status === 'pending') {
        statusObj = { text: '待维护', type: 'warning' }
      } else if (item.status === 'processing') {
        statusObj = { text: '维护中', type: 'primary' }
      }

      return {
        ...item,
        status_display: statusObj,
        actions: [
          { text: '详情', action_type: 'view', resource_type: 'maintenance_record', resource_id: item.id, style_class: 'btn-info-sm' }
        ]
      }
    })
  })

  const handleAction = (action) => {
    if (!action) return

    if (action.action_type === 'view') {
      router.push(`/record-detail/${action.resource_type}/${action.resource_id}`)
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
