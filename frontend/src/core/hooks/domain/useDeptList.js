import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBaseCRUD } from '../base/useCRUD'
import { useAutoRefresh } from '../base/useAutoRefresh'
import { deptService } from '@/core/services/BaseService'
import { LIST_COLUMNS } from '@/core/config/listConfig'

export function useDeptList(options = {}) {
  const router = useRouter()
  
  const crud = useBaseCRUD({
    service: deptService,
    itemName: '部门',
    listType: 'departments',
    immediate: options.immediate !== false,
    ...options
  })

  const { setupAutoRefresh } = useAutoRefresh('departments')
  setupAutoRefresh(() => crud.loadData())

  const columns = computed(() => LIST_COLUMNS.departments)
  
  const tableData = computed(() => {
    return crud.tableData.value.map(item => ({
      ...item,
      actions: [
        { text: '编辑', action_type: 'edit', resource_type: 'dept', resource_id: item.id, style_class: 'btn-primary-sm' }
      ]
    }))
  })

  const listHeader = ref('部门管理')
  const showCheckbox = ref(true)
  const isPaginated = ref(true)
  const filterValue = ref('')
  
  const opt = computed(() => [
    { text: '添加部门', onclick: 'add', type: 'primary', icon: 'Plus' }
  ])

  const handleOptionClick = (option) => {
    if (!option) return
    
    const { onclick } = option
    
    if (onclick === 'add') {
      router.push('/adddept')
    }
  }

  return { 
    ...crud,
    columns,
    tableData,
    listHeader,
    showCheckbox,
    isPaginated,
    filterValue,
    opt,
    handleOptionClick
  }
}
