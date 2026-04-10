import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useBaseCRUD } from '../base/useCRUD'
import { scheduleService, labService } from '@/core/services/BaseService'
import { LIST_COLUMNS } from '@/core/config/listConfig'

/**
 * 课程列表 Hook - 直接对接后端V2
 */
export function useClassList(options = {}) {
  const route = useRoute()
  
  const crud = useBaseCRUD({
    service: scheduleService,
    itemName: '课程',
    listType: 'schedules',
    immediate: options.immediate !== false,
    ...options
  })

  const filterValue = ref(route.query.filter_sxs || '')
  const allClassData = ref([])
  const allDataLoading = ref(false)
  const labOptions = ref([])
  
  const select = computed(() => {
    return {
      name: 'filter_sxs',
      options: labOptions.value
    }
  })
  
  const opt = computed(() => [
    { text: '添加课程', onclick: 'addClass', type: 'primary', icon: 'Plus' }
  ])
  
  const hideBack = ref(false)
  const backUrl = ref('')
  const showCheckbox = ref(true)
  const skipCheckbox = ref(false)
  const isPaginated = ref(true)

  const columns = computed(() => LIST_COLUMNS.schedules)
  
  const tableData = computed(() => {
    return crud.tableData.value.map(item => ({
      ...item,
      actions: [
        { text: '编辑', action_type: 'edit', resource_type: 'schedule', resource_id: item.id, style_class: 'btn-primary-sm' },
        { text: '删除', action_type: 'delete', resource_type: 'schedule', resource_id: item.id, style_class: 'btn-danger-sm' }
      ]
    }))
  })

  const loadAllData = async () => {
    allDataLoading.value = true
    try {
      const response = await scheduleService.list({ nopage: 1, ...route.query })
      if (response?.success && response.data?.list) {
        allClassData.value = response.data.list
      } else if (response?.items) {
        allClassData.value = response.items
      } else if (Array.isArray(response)) {
        allClassData.value = response
      }
    } catch (err) {
    } finally {
      allDataLoading.value = false
    }
  }

  const loadLabOptions = async () => {
    try {
      const response = await labService.list({ nopage: 1 })
      if (response?.success && response.data?.list) {
        labOptions.value = response.data.list.map(item => ({
          id: item.id,
          text: item.name
        }))
      } else if (response?.items) {
        labOptions.value = response.items.map(item => ({
          id: item.id,
          text: item.name
        }))
      } else if (Array.isArray(response)) {
        labOptions.value = response.map(item => ({
          id: item.id,
          text: item.name
        }))
      }
    } catch (err) {
    }
  }

  onMounted(() => {
    loadLabOptions()
  })

  const handleFilter = (value) => {
    filterValue.value = value
    crud.handleFilter(value, 'filter_sxs')
  }

  const getActionRoute = (action) => {
    if (!action) return null
    
    if (action.action_type === 'edit') {
      return `/edit-class/${action.resource_id}`
    }
    if (action.onclick === 'addClass') {
      const sxsid = filterValue.value || route.params.id || ''
      return sxsid ? `/addclass/${sxsid}` : '/addclass'
    }
    
    return null
  }

  return { 
    ...crud,
    columns,
    tableData,
    filterValue,
    select,
    opt,
    hideBack,
    backUrl,
    showCheckbox,
    skipCheckbox,
    isPaginated,
    allClassData,
    allDataLoading,
    loadAllData,
    handleFilter,
    getActionRoute
  }
}
