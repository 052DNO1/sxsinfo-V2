import { ref, computed, onMounted, onActivated, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/core/hooks'
import { useNavigation } from '@/core/utils/routeDecision'

export function useAssignPermission() {
  const route = useRoute()
  const router = useRouter()
  const { post: assignPermissionApi, get: fetchPermissionApi } = useApi('', { immediate: false })
  const { smartBack } = useNavigation()
  
  const formData = ref({
    username: '',
    nickname: '',
    permissions: []
  })
  const errors = ref({})
  const loading = ref(false)
  const isLoading = ref(true)
  const permissionOptions = ref([])
  const isDepartAdmin = ref(false)
  const originalTid = ref('')

  const filteredPermissionOptions = computed(() => {
    const options = permissionOptions.value || []
    return options.filter(option => {
      if (!option || typeof option !== 'object' || !option.hasOwnProperty('value')) {
        return false
      }
      if (isDepartAdmin.value && option.value === 4) {
        return false
      }
      return true
    })
  })

  const loadData = async () => {
    isLoading.value = true
    try {
      const userId = route.params.id
      if (!userId) {
        isLoading.value = false
        return
      }
      
      const apiPath = `/users/${userId}/assign_permission/`
      const response = await fetchPermissionApi(route.query, { url: apiPath })
      
      if (response && response.user) {
        const currentPermissions = Array.isArray(response.current_permissions) 
          ? response.current_permissions 
          : (response.current_permissions ? [response.current_permissions] : [])
        
        formData.value.username = response.user.username || ''
        formData.value.nickname = response.user.nickname || ''
        formData.value.permissions = currentPermissions
        
        const choices = response.permission_choices || []
        let processedChoices = []
        
        if (Array.isArray(choices)) {
          processedChoices = choices.map(choice => {
            if (typeof choice === 'object' && choice.value !== undefined && choice.label !== undefined) {
              return choice
            } else if (Array.isArray(choice) && choice.length === 2) {
              return { value: choice[0], label: choice[1] }
            }
            return null
          }).filter(Boolean)
        } else if (choices && typeof choices === 'object') {
          processedChoices = Object.keys(choices).map(key => ({
            value: parseInt(key) || key,
            label: choices[key]
          }))
        }
        
        permissionOptions.value = processedChoices
        isDepartAdmin.value = response.is_departadmin || false
        originalTid.value = response.original_tid || route.query.tid || '1'
      }
    } catch (err) {
    } finally {
      isLoading.value = false
    }
  }

  const handleSubmit = async (showSuccess, showError) => {
    loading.value = true
    errors.value = {}

    try {
      const userId = route.params.id
      if (!userId) {
        if (showError) await showError('缺少用户ID参数')
        return
      }
      
      const apiPath = `/users/${userId}/assign_permission/`
      const submitData = {
        ...formData.value,
        original_tid: originalTid.value || route.query.tid || '1'
      }
      
      const response = await assignPermissionApi(submitData, { url: apiPath })
      
      if (response.success) {
        if (showSuccess) await showSuccess(response.message || '权限分配成功')
        setTimeout(() => {
          smartBack()
        }, 1500)
      } else {
        if (showError) await showError(response.message || '权限分配失败')
        if (response.errors) {
          errors.value = response.errors
        }
      }
    } catch (err) {
      if (showError) await showError(err.message || '权限分配失败')
      if (err.response?.data?.errors) {
        errors.value = err.response.data.errors
      }
    } finally {
      loading.value = false
    }
  }

  onMounted(loadData)
  
  onActivated(loadData)
  
  watch(
    () => [route.params.id, route.query.tid],
    ([newId, newTid], [oldId, oldTid]) => {
      if (newId && newId !== oldId) {
        loadData()
      }
    },
    { immediate: false }
  )

  return {
    formData,
    errors,
    loading,
    isLoading,
    permissionOptions,
    isDepartAdmin,
    originalTid,
    filteredPermissionOptions,
    loadData,
    handleSubmit,
    smartBack
  }
}
