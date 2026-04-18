import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBaseCRUD } from '../base/useCRUD'
import { useAutoRefresh } from '../base/useAutoRefresh'
import { userService } from '@/core/services/BaseService'
import { LIST_COLUMNS } from '@/core/config/listConfig'
import { safeConfirm, showSuccess, showError } from '@/core/utils/errorHandler'
import { useApi } from '../base/useApi'
import { useUserStore } from '@/core/store/user'
import { cacheManager } from '@/core/services/cacheManager'

const BASE_USER_COLUMNS = [
  { label: '用户名', prop: 'username', minWidth: '120', show: true },
  { label: '姓名', prop: 'nickname', minWidth: '120', show: true },
  { label: '邮箱', prop: 'email', minWidth: '180', show: true },
  { label: '手机号', prop: 'phone', minWidth: '120', show: true },
  { label: '角色', prop: 'role_display', minWidth: '150', show: true }
]

const DEPARTMENT_COLUMN = { label: '管理的部门', prop: 'department_name', minWidth: '150', show: true }
const LABORATORY_COLUMN = { label: '管理的实训室', prop: 'managed_laboratories', minWidth: '200', show: true }
const STATUS_COLUMN = { label: '状态', prop: 'status_display', minWidth: '100', show: true, isStatus: true }
const ACTION_COLUMN = { label: '操作', prop: 'actions', minWidth: '250', show: true, isAction: true }

const ROLE_MAP = {
  1: '教师',
  2: '实训室管理员',
  4: '部门管理员',
  16: '超级管理员',
  32: '系统管理员'
}

const formatRoleDisplay = (role) => {
  if (!role) return '-'
  const roles = []
  for (const [value, name] of Object.entries(ROLE_MAP)) {
    if (role & parseInt(value)) {
      roles.push(name)
    }
  }
  return roles.length > 0 ? roles.join('、') : '-'
}

export function useUserList(options = {}) {
  const router = useRouter()
  const route = useRoute()
  const userStore = useUserStore()
  const user = computed(() => userStore.user)
  const apiComposable = useApi('', { immediate: false })

  const crud = useBaseCRUD({
    service: userService,
    itemName: '用户',
    listType: 'users',
    immediate: false,
    skipAutoLoad: true,
    ...options
  })

  const { setupAutoRefresh } = useAutoRefresh('users')
  setupAutoRefresh(() => loadDataWithFilter())

  const isSuperAdmin = computed(() => user.value?.is_super_admin)
  const isSystemAdmin = computed(() => user.value?.is_superuser)
  const isDepartmentAdmin = computed(() => user.value?.is_department_admin)

  const columns = computed(() => {
    const cols = [...BASE_USER_COLUMNS]
    
    if (isSystemAdmin.value || isSuperAdmin.value) {
      cols.push(DEPARTMENT_COLUMN)
    } else if (isDepartmentAdmin.value) {
      cols.push(LABORATORY_COLUMN)
    }
    
    cols.push(STATUS_COLUMN)
    cols.push(ACTION_COLUMN)
    
    return cols
  })

  const tableData = computed(() => {
    return crud.tableData.value.map(item => {
      const actions = [
        { text: '编辑', action_type: 'edit', resource_type: 'user_role', resource_id: item.id, style_class: 'btn-primary-sm' },
        { text: item.is_active ? '禁用' : '激活', action_type: 'toggle', resource_type: 'user_status', resource_id: item.id, style_class: item.is_active ? 'btn-danger-sm' : 'btn-success-sm' }
      ]
      
      if (isSystemAdmin.value) {
        actions.shift()
      }
      
      return {
        ...item,
        role_display: formatRoleDisplay(item.role),
        managed_laboratories: item.managed_laboratories && item.managed_laboratories !== '-' 
          ? item.managed_laboratories 
          : '暂无管理实训室',
        status_display: item.is_active
          ? { text: '正常', type: 'success' }
          : { text: '禁用', type: 'danger' },
        actions
      }
    })
  })

  const listHeader = computed(() => {
    return '用户管理'
  })
  const showCheckbox = ref(true)
  const isPaginated = ref(true)
  const filterValue = ref('')
  const selectedDepartmentId = ref(0)
  const selectedRoleId = ref(0)

  const { data: deptData, execute: fetchDepts } = useApi('/departments/?nopage=true', { immediate: false })

  const loadDepartments = async () => {
    await fetchDepts()
  }

  const departmentOptions = computed(() => {
    const options = [{ id: 0, text: '全部部门' }]
    if (deptData.value) {
      let depts = deptData.value.list || deptData.value.results || deptData.value || []
      if (!Array.isArray(depts)) {
        depts = []
      }
      depts.forEach(dept => {
        if (dept && dept.id && dept.name) {
          options.push({ id: dept.id, text: dept.name })
        }
      })
    }
    return options
  })

  onMounted(() => {
    loadDepartments()
  })

  const select = computed(() => {
    if (isSystemAdmin.value) {
      return {
        options: [
          { id: 0, text: '全部用户' },
          { id: 32, text: '系统管理员' },
          { id: 16, text: '超级管理员' },
          { id: 4, text: '部门管理员' },
          { id: 2, text: '实训室管理员' },
          { id: 1, text: '教师' }
        ],
        departmentOptions: departmentOptions.value,
        defaultSelected: 0,
        defaultDepartmentSelected: 0,
        showDepartmentFilter: true
      }
    }

    if (isSuperAdmin.value) {
      return {
        options: [
          { id: 4, text: '部门管理员' }
        ],
        defaultSelected: 4
      }
    }

    if (isDepartmentAdmin.value) {
      return {
        options: [
          { id: 0, text: '全部用户' },
          { id: 2, text: '实训室管理员' },
          { id: 1, text: '教师' }
        ],
        defaultSelected: 0
      }
    }

    return {
      options: [
        { id: 0, text: '全部用户' },
        { id: 1, text: '教师' },
        { id: 2, text: '实训室管理员' }
      ]
    }
  })

  const opt = computed(() => {
    const buttons = [
      { text: '添加用户', onclick: 'add', type: 'primary', icon: 'Plus' },
      { text: '重置密码', onclick: 'batchResetPassword', type: 'warning', icon: 'Key' }
    ]
    if (!isSystemAdmin.value) {
      buttons.splice(1, 0, { text: '批量删除', onclick: 'batchDelete', type: 'danger', icon: 'Delete' })
    }
    return buttons
  })

  const getDefaultParams = () => {
    if (isSystemAdmin.value) {
      const params = {}
      if (selectedDepartmentId.value && selectedDepartmentId.value !== 0) {
        params.department_id = selectedDepartmentId.value
      }
      if (selectedRoleId.value && selectedRoleId.value !== 0) {
        params.role = selectedRoleId.value
      }
      return params
    }
    
    if (isSuperAdmin.value) {
      return { role: 4 }
    }
    
    if (isDepartmentAdmin.value) {
      return {}
    }
    
    return { role: '1,2' }
  }

  const loadDataWithFilter = (params = {}) => {
    crud.loadData({ 
      ...getDefaultParams(), 
      page: crud.currentPage.value,
      page_size: crud.pageSize.value,
      ...params 
    })
  }

  watch(() => route.params.id, () => {
    crud.currentPage.value = 1
    loadDataWithFilter()
  }, { immediate: true })

  watch([() => crud.currentPage.value, () => crud.pageSize.value], (newVals, oldVals) => {
    if (oldVals && (newVals[0] !== oldVals[0] || newVals[1] !== oldVals[1])) {
      loadDataWithFilter()
    }
  })

  watch(selectedDepartmentId, () => {
    crud.currentPage.value = 1
    loadDataWithFilter()
  })

  watch(selectedRoleId, () => {
    crud.currentPage.value = 1
    loadDataWithFilter()
  })

  const handleAction = async (op) => {
    if (!op) return
    
    const { action_type, resource_type, resource_id, text } = op
    
    if (action_type === 'edit' && resource_type === 'user_role') {
      router.push(`/assign-role/${resource_id}/`)
    } else if (action_type === 'edit' && resource_type === 'permission') {
      router.push(`/assign-permission/${resource_id}/`)
    } else if (action_type === 'toggle' && resource_type === 'user_status') {
      const confirmed = await safeConfirm(`确定要${text}该用户吗？`)
      if (!confirmed) return
      
      const isActive = text === '激活'
      const response = await apiComposable.post({ is_active: isActive }, { 
        url: `/users/${resource_id}/activate/`,
        resourceType: 'users'
      })
      if (response && response.success) {
        showSuccess(response.message || '操作成功')
      } else {
        showError(response?.message || '操作失败')
      }
    }
  }

  const handleOptionClick = async (option) => {
    if (!option) return
    
    const { onclick, text } = option
    
    if (onclick === 'add') {
      router.push('/adduser')
    } else if (onclick === 'batchDelete') {
      if (!crud.selectedRows.value || crud.selectedRows.value.length === 0) {
        showError('请先选择要删除的用户')
        return
      }
      const confirmed = await safeConfirm(`确定要删除选中的 ${crud.selectedRows.value.length} 个用户吗？`)
      if (!confirmed) return
      
      const ids = crud.selectedRows.value.map(item => item.id)
      const response = await apiComposable.post({ ids }, {
        url: '/users/batch_delete/',
        resourceType: 'users'
      })
      if (response && response.success) {
        showSuccess(response.message || '批量删除成功')
        crud.selectedRows.value = []
        loadDataWithFilter()
      } else {
        showError(response?.message || '删除失败')
      }
    } else if (onclick === 'batchResetPassword') {
      await handleBatchResetPassword(crud.selectedRows.value)
    }
  }

  const handleBatchResetPassword = async (selection) => {
    if (!selection || selection.length === 0) {
      showError('请先选择要重置密码的用户')
      return
    }
    
    const confirmed = await safeConfirm(`确定要重置选中的 ${selection.length} 个用户的密码吗？`)
    if (!confirmed) return
    
    const userIds = selection.map(item => item.id)
    const response = await apiComposable.post({ user_ids: userIds }, { url: '/auth/password/batch-reset/' })
    if (response && response.success) {
      showSuccess(response.message || '密码重置成功')
    } else {
      showError(response?.message || '密码重置失败')
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
    select,
    opt,
    handleAction,
    handleOptionClick,
    handleBatchResetPassword,
    selectedDepartmentId,
    selectedRoleId
  }
}
