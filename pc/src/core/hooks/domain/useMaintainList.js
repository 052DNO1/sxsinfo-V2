import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBaseCRUD } from '../base/useCRUD'
import { workOrderService } from '@/core/services/BaseService'
import { LIST_COLUMNS, STATUS_MAP } from '@/core/config/listConfig'

/**
 * 维护工单列表 Hook - 直接对接后端V2
 */
export function useMaintainList(options = {}) {
  const router = useRouter()
  
  const crud = useBaseCRUD({
    service: workOrderService,
    itemName: '工单',
    listType: 'work_orders',
    immediate: options.immediate !== false,
    ...options
  })

  const columns = computed(() => LIST_COLUMNS.work_orders)

  const tableData = computed(() => {
    return crud.tableData.value.map(item => {
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
      router.push(`/record-detail/${action.resource_type}/${action.resource_id}`)
    }
  }

  return {
    ...crud,
    columns,
    tableData,
    handleAction
  }
}
