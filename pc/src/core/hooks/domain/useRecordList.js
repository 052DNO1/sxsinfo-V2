import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBaseCRUD } from '../base/useCRUD'
import { recordService, workOrderService } from '@/core/services/BaseService'
import { LIST_COLUMNS } from '@/core/config/listConfig'

/**
 * 使用记录列表 Hook - 直接对接后端V2
 * 支持使用记录、维护记录和故障工单三种类型
 */
export function useRecordList(options = {}) {
  const route = useRoute()
  const router = useRouter()
  
  const recordType = computed(() => {
    const path = route.path
    if (path.includes('fault')) return 'workorder'
    if (path.includes('maintain')) return 'maintain'
    return 'usage'
  })
  
  const isFaultList = computed(() => recordType.value === 'workorder')
  const isMaintainList = computed(() => recordType.value === 'maintain')
  
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
  
  const crud = useBaseCRUD({
    service: service.value,
    itemName: itemName.value,
    listType: listType.value,
    immediate: options.immediate !== false,
    ...options
  })

  const columns = computed(() => {
    if (isFaultList.value) return LIST_COLUMNS.work_orders
    if (isMaintainList.value) return LIST_COLUMNS.maintenance_records || LIST_COLUMNS.records
    return LIST_COLUMNS.records
  })
  
  const listHeader = computed(() => {
    if (isFaultList.value) return '故障工单列表'
    if (isMaintainList.value) return '维护记录列表'
    return '使用记录列表'
  })
  
  const isPaginated = ref(true)
  const showCheckbox = ref(true)
  const exportUrls = ref(null)
  
  const opt = computed(() => [
    { text: isFaultList.value ? '故障上报' : '添加记录', onclick: 'add', type: 'primary', icon: 'Plus' }
  ])
  
  const tableData = computed(() => {
    return crud.tableData.value.map(item => ({
      ...item,
      actions: [
        { text: '详情', action_type: 'detail', resource_type: recordType.value, resource_id: item.id }
      ]
    }))
  })

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

  const handleExportExcel = () => {
  }

  return { 
    ...crud,
    columns,
    tableData,
    listHeader,
    isPaginated,
    showCheckbox,
    opt,
    exportUrls,
    recordType,
    handleOptionClick,
    handleAction,
    handleExportExcel
  }
}
