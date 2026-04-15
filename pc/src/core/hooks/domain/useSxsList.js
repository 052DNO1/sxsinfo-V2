import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBaseCRUD } from '../base/useCRUD'
import { labService } from '@/core/services/BaseService'
import { LIST_COLUMNS } from '@/core/config/listConfig'
import { useUserStore } from '@/core/store/user'
import { showError, showSuccess, safeConfirm } from '@/core/utils/errorHandler'

/**
 * 实训室列表 Hook - 直接对接后端V2
 */
export function useSxsList(options = {}) {
  const router = useRouter()
  const route = useRoute()
  const userStore = useUserStore()
  const user = computed(() => userStore.user)
  
  const crud = useBaseCRUD({
    service: labService,
    itemName: '实训室',
    listType: 'labs',
    immediate: options.immediate !== false,
    ...options
  })

  const columns = computed(() => LIST_COLUMNS.laboratories)
  
  const isSxsAdmin = computed(() => {
    return user.value?.is_sxsadmin && !user.value?.is_superuser && !user.value?.is_departadmin
  })
  
  const showCheckbox = computed(() => {
    return user.value?.is_superuser || user.value?.is_departadmin
  })
  
  const selectedCount = computed(() => crud.selectedRows.value.length)
  
  const listHeader = ref('实训室列表')
  const isPaginated = ref(true)
  
  const opt = computed(() => {
    const buttons = [
      { text: '添加实训室', onclick: 'add', type: 'primary', icon: 'Plus' }
    ]
    if (showCheckbox.value) {
      buttons.push({ text: '批量删除', onclick: 'batchDelete', type: 'danger', icon: 'Delete' })
    }
    return buttons
  })
  
  const tableData = computed(() => {
    return crud.tableData.value.map(item => ({
      ...item,
      schedule_count: item.schedule_count || 0,
      admin_name: item.admin_name || '未分配',
      note: item.note || '',
      actions: [
        { text: '编辑', action_type: 'edit', resource_type: 'lab', resource_id: item.id }
      ]
    }))
  })

  const handleBatchDeleteLab = async () => {
    if (!crud.selectedRows.value || crud.selectedRows.value.length === 0) {
      showError('请先选择要删除的实训室')
      return
    }

    const selectedIds = crud.selectedRows.value.map(item => item.id)

    try {
      const impactResponse = await labService.checkDeleteImpact(selectedIds)

      if (!impactResponse || !impactResponse.success) {
        showError('检查关联数据失败')
        return
      }

      const { has_related_data, related_labs } = impactResponse.data || {}

      let confirmMessage = `确定要删除选中的 ${selectedIds.length} 个实训室吗？此操作不可恢复！`

      if (has_related_data && related_labs && related_labs.length > 0) {
        const labDetails = related_labs.map(lab =>
          `${lab.name}(${lab.code}): ${lab.schedule_count}条课表、${lab.record_count}条使用记录、${lab.order_count}条工单、${lab.equipment_count}台设备`
        ).join('\n')
        confirmMessage = `以下实训室有关联数据：\n\n${labDetails}\n\n删除将：\n- 删除课表和设备\n- 保留使用记录和工单\n\n确认删除这 ${selectedIds.length} 个实训室吗？`
      }

      const confirmed = await safeConfirm(confirmMessage)
      if (!confirmed) return

      const response = await labService.batchDelete(selectedIds)
      if (response.success) {
        showSuccess(`批量删除成功`)
        crud.loadData()
      }
    } catch (err) {
      showError(err.message || '删除失败')
    }
  }

  const handleAction = async (op) => {
    if (!op) return
    
    const { action_type, resource_id } = op
    
    if (action_type === 'edit') {
      router.push(`/edit-sxs/${resource_id}`)
    }
  }

  const handleOptionClick = async (option) => {
    if (!option) return
    
    const { onclick } = option
    
    if (onclick === 'add') {
      router.push('/addsxs')
    } else if (onclick === 'batchDelete') {
      await handleBatchDeleteLab()
    }
  }

  const handleViewRecords = (type) => {
    const labId = route.params.id || route.query.lab_id
    if (type === 'usage') {
      router.push(labId ? `/listsxsinfo/${labId}` : '/listsxsinfo')
    } else if (type === 'maintain') {
      router.push(labId ? `/listsxsmaintain/${labId}` : '/listsxsmaintain')
    } else if (type === 'fault') {
      router.push(labId ? `/listsxsfault/${labId}` : '/listsxsfault')
    }
  }

  const handleViewDevices = () => {
    router.push('/device-list')
  }

  const handleViewClassSchedule = () => {
    const labId = route.params.id || route.query.lab_id
    router.push(labId ? `/listsxsclass/${labId}` : '/listsxsclass')
  }

  return { 
    ...crud,
    columns,
    tableData,
    isSxsAdmin,
    showCheckbox,
    selectedCount,
    listHeader,
    isPaginated,
    opt,
    handleBatchDeleteLab,
    handleAction,
    handleOptionClick,
    handleViewRecords,
    handleViewDevices,
    handleViewClassSchedule
  }
}
