import { ref, reactive, onMounted, computed, type Ref, type ComputedRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showSuccess, showError } from '../../utils/errorHandler'
import { useApi } from './useApi'
import { useAppStore } from '../../store/app'
import type { UseEntityFormOptions, FormField } from '../../types'

interface UseEntityFormReturn {
  loading: Ref<boolean>
  submitting: Ref<boolean>
  formFields: Ref<FormField[]>
  formData: Record<string, any>
  fieldErrors: Ref<Record<string, string>>
  message: Ref<string>
  messageType: Ref<string>
  header: Ref<string>
  description: Ref<string>
  formRules: ComputedRef<Record<string, any[]>>
  handleSubmit: () => Promise<void>
  loadData: () => Promise<void>
}

export function useEntityForm(arg1: UseEntityFormOptions | ((data: any, response: any) => FormField[]), arg2?: UseEntityFormOptions): UseEntityFormReturn {
  let options: UseEntityFormOptions = {}
  
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
  const formFields = ref<FormField[]>([])
  const formData = reactive<Record<string, any>>({})
  const fieldErrors = ref<Record<string, string>>({})
  const message = ref('')
  const messageType = ref('')
  const header = ref('')
  const description = ref('')

  const loadData = async (): Promise<void> => {
    loading.value = true
    try {
      const id = route.params.id as string | undefined
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
        header.value = (response as any).header || (response as any).title || (id ? '编辑' : '新增')
        description.value = (response as any).description || ''
        
        const rawFields = (response as any).form_fields || (response as any).data || response
        formFields.value = configTransformFn ? configTransformFn(rawFields, response) : (getFields ? getFields(rawFields, response) : [])
        
        const initialData = id ? dataMapper((response as any).data || response) : ((response as any).initial_data || {})
        formFields.value.forEach(f => {
          formData[f.name] = initialData[f.name] ?? f.default ?? ''
        })
      }
    } catch (err: any) {
      message.value = err.message
      messageType.value = 'error'
    } finally {
      loading.value = false
    }
  }

  const handleSubmit = async (): Promise<void> => {
    submitting.value = true
    fieldErrors.value = {}
    message.value = ''
    try {
      const id = route.params.id as string | undefined
      let response
      
      if (service) {
        response = id ? await service.update(id, formData) : await service.create(formData)
      }
      
      if (response && (response as any).success !== false) {
        showSuccess((response as any).message || '保存成功')
        if (listType) {
          appStore.triggerListRefresh(listType)
        }
        if (onSuccess) onSuccess(response, formData)
        else router.back()
      } else if (response) {
        message.value = (response as any).message || '操作失败'
        messageType.value = 'error'
        if ((response as any).errors) fieldErrors.value = (response as any).errors
      }
    } catch (err: any) {
      message.value = err.message || '提交失败'
      messageType.value = 'error'
      if (err.response?.data?.errors) fieldErrors.value = err.response.data.errors
    } finally {
      submitting.value = false
    }
  }

  const formRules = computed(() => {
    const rules: Record<string, any[]> = {}
    formFields.value.forEach(f => {
      if (f.rules) rules[f.name] = f.rules
      else if (f.required) rules[f.name] = [{ required: true, message: `请输入${f.label}`, trigger: 'blur' }]
    })
    return rules
  })

  onMounted(loadData)

  return { 
    loading,
    submitting,
    formFields,
    formData,
    fieldErrors, 
    message,
    messageType,
    header,
    description,
    formRules, 
    handleSubmit,
    loadData 
  }
}

export default useEntityForm
