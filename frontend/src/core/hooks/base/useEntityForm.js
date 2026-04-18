import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showSuccess, showError } from '@/core/utils/errorHandler'
import { useApi } from '@/core/hooks/base/useApi'
import { useAppStore } from '@/core/store/app'

/**
 * 通用实体表单 Composable (兼容版)
 * 支持两种调用方式：
 * 1. useEntityForm({ service, getFields, ... }) - 核心模式
 * 2. useEntityForm(getFields, options) - 视图模式
 */
export function useEntityForm(arg1, arg2) {
  let options = {}
  
  if (typeof arg1 === 'function') {
    options = { getFields: arg1, ...arg2 }
  } else {
    options = arg1 || {}
  }

  const {
    service,
    getFields,
    onSuccess,
    listType,
    dataMapper = (d) => d,
    configTransformFn
  } = options

  const route = useRoute()
  const router = useRouter()
  const api = useApi('', { immediate: false })
  const appStore = useAppStore()
  
  const loading = ref(false)
  const submitting = ref(false)
  const formFields = ref([])
  const formData = reactive({})
  const fieldErrors = ref({})
  const message = ref('')
  const messageType = ref('')
  const header = ref('')
  const description = ref('')

  const loadData = async () => {
    loading.value = true
    try {
      const id = route.params.id
      let response
      
      if (service) {
        response = id ? await service.get(id) : await service.list({ schema_only: 1 })
      } else if (getFields) {
        formFields.value = getFields({}, {})
        formFields.value.forEach(f => {
          formData[f.name] = f.default ?? ''
        })
        loading.value = false
        return
      }

      if (response) {
        header.value = response.header || response.title || (id ? '编辑' : '新增')
        description.value = response.description || ''
        
        const rawFields = response.form_fields || response.data || response
        formFields.value = configTransformFn ? configTransformFn(rawFields, response) : getFields(rawFields)
        
        const initialData = id ? dataMapper(response.data || response) : (response.initial_data || {})
        formFields.value.forEach(f => {
          formData[f.name] = initialData[f.name] ?? f.default ?? ''
        })
      }
    } catch (err) {
      message.value = err.message
      messageType.value = 'error'
    } finally {
      loading.value = false
    }
  }

  const handleSubmit = async () => {
    submitting.value = true
    fieldErrors.value = {}
    message.value = ''
    try {
      const id = route.params.id
      let response
      
      if (service) {
        response = id ? await service.update(id, formData) : await service.create(formData)
      }
      
      if (response && response.success !== false) {
        showSuccess(response.message || '保存成功')
        if (listType) {
          appStore.triggerListRefresh(listType)
        }
        if (onSuccess) onSuccess(response, formData)
        else router.back()
      } else if (response) {
        message.value = response.message || '操作失败'
        messageType.value = 'error'
        if (response.errors) fieldErrors.value = response.errors
      }
    } catch (err) {
      message.value = err.message || '提交失败'
      messageType.value = 'error'
      if (err.response?.data?.errors) fieldErrors.value = err.response.data.errors
    } finally {
      submitting.value = false
    }
  }

  const formRules = computed(() => {
    const rules = {}
    formFields.value.forEach(f => {
      if (f.rules) rules[f.name] = f.rules
      else if (f.required) rules[f.name] = [{ required: true, message: `请输入${f.label}`, trigger: 'blur' }]
    })
    return rules
  })

  onMounted(loadData)

  return { 
    loading, submitting, formFields, formData, fieldErrors, 
    message, messageType, header, description, formRules, 
    handleSubmit, loadData 
  }
}
