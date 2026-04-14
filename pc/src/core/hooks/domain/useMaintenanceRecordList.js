import { computed } from 'vue'
import { useBaseCRUD } from '../base/useCRUD'
import { maintenanceRecordService } from '@/core/services/BaseService'
import { LIST_COLUMNS, STATUS_MAP } from '@/core/config/listConfig'

/**
 * 维护记录列表 Hook - 直接对接后端V2
 */
export function useMaintenanceRecordList(options = {}) {
  const crud = useBaseCRUD({
    service: maintenanceRecordService,
    itemName: '维护记录',
    listType: 'maintenance_records',
    immediate: options.immediate !== false,
    ...options
  })

  const columns = computed(() => LIST_COLUMNS.maintenance_records)
  
  const tableData = computed(() => {
    return crud.tableData.value.map(item => ({
      ...item,
      status_display: STATUS_MAP[item.status] || { text: item.status_display || item.status, type: 'info' },
      actions: [
        { text: '详情', action_type: 'view', resource_type: 'maintenance_record', resource_id: item.id, style_class: 'btn-info-sm' },
        { text: '编辑', action_type: 'edit', resource_type: 'maintenance_record', resource_id: item.id, style_class: 'btn-primary-sm' },
        { text: '删除', action_type: 'delete', resource_type: 'maintenance_record', resource_id: item.id, style_class: 'btn-danger-sm' }
      ]
    }))
  })

  return { 
    ...crud,
    columns,
    tableData
  }
}
