import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useBaseCRUD } from '../base/useCRUD'
import { useAutoRefresh } from '../base/useAutoRefresh'
import { useApi } from '../base/useApi'
import { scheduleService, labService } from '@/core/services/BaseService'
import { LIST_COLUMNS } from '@/core/config/listConfig'
import { showError } from '@/core/utils/errorHandler'
import { handleExportFromResponse } from '@/core/utils/io'

export function useClassList(options = {}) {
  const route = useRoute()
  
  const crud = useBaseCRUD({
    service: scheduleService,
    itemName: '课程',
    listType: 'schedules',
    immediate: options.immediate !== false,
    ...options
  })

  const { setupAutoRefresh } = useAutoRefresh('schedules')
  setupAutoRefresh(() => crud.loadData())

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
        { text: '删除', action_type: 'delete', resource_type: 'schedule', resource_id: item.id, resource_name: item.course_name, style_class: 'btn-danger-sm' }
      ]
    }))
  })

  const loadAllData = async () => {
    allDataLoading.value = true
    try {
      const params = { nopage: 'true' }
      if (filterValue.value) {
        params.laboratory_id = filterValue.value
      }
      const response = await scheduleService.list(params)
      if (response?.success && response.data?.list) {
        allClassData.value = response.data.list
      } else if (response?.list) {
        allClassData.value = response.list
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

  watch(filterValue, (newVal) => {
    loadAllData()
  }, { immediate: true })

  const handleFilter = (value) => {
    filterValue.value = value
    crud.handleFilter(value, 'filter_sxs')
    loadAllData()
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

  const execDelete = async (item, nameField = 'name') => {
    const itemId = item.id
    await crud.execDelete(item, nameField)
    allClassData.value = allClassData.value.filter(c => c.id !== itemId)
    await loadAllData()
  }

  const execBatchDelete = async (selection, idParam = 'ids') => {
    const idsToRemove = selection.map(item => item.id)
    await crud.execBatchDelete(selection, idParam)
    allClassData.value = allClassData.value.filter(c => !idsToRemove.includes(c.id))
    await loadAllData()
  }

  const { get: fetchExportApi } = useApi('', { immediate: false })

  const handleExportExcel = async () => {
    try {
      const params = { ...route.query }
      if (filterValue.value) {
        params.laboratory_id = filterValue.value
      }
      const response = await fetchExportApi(params, {
        url: '/common/export/schedules/',
        responseType: 'blob'
      })

      await handleExportFromResponse(response, `课表记录_${new Date().toISOString().slice(0,10)}.xlsx`)
    } catch (err) {
      if (err === 'cancel' || err === 'close') return
      showError('导出失败: ' + (err.message || '未知错误'))
    }
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
    getActionRoute,
    handleExportExcel,
    execDelete,
    execBatchDelete
  }
}
