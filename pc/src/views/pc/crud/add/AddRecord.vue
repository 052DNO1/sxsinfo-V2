<!-- 实验室使用记录 -->
<template>
  <FormLayout
    :title="header || '添加使用记录'"
    icon="EditPen"
    :loading="isLoading"
    guide-title="操作指南"
    guide-sub-title="请按照提示填写使用记录"
    :guide-steps="guideSteps"
    :tips="tips"
    :main-title="header || '填写信息'"
    main-icon="Edit"
  >
    <el-form 
      ref="formRef"
      @submit.prevent="handleSubmit" 
      :model="formData" 
      label-width="120px" 
      label-position="top"
      class="modern-form"
      size="large">
      <el-row :gutter="24">
        <template v-for="field in formFields" :key="field.name">
          <el-col :span="field.fullWidth ? 24 : 12" v-if="field.type === 'text' || field.type === 'number' || field.type === 'date'">
            <el-form-item :label="field.label" :prop="field.name" :required="field.required" :error="fieldErrors[field.name]" class="custom-form-item">
              <el-input
                v-if="field.type !== 'date'"
                :type="field.type"
                v-model="formData[field.name]"
                :placeholder="field.placeholder"
                :clearable="true"
                class="custom-input"
              />
              <el-date-picker
                v-else
                v-model="formData[field.name]"
                type="date"
                :placeholder="field.placeholder"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
              <small v-if="field.help_text" style="color: #909399; font-size: 13px; margin-top: 4px; display: block;">{{ field.help_text }}</small>
            </el-form-item>
          </el-col>

          <el-col :span="12" v-else-if="field.type === 'select'">
            <el-form-item :label="field.label" :prop="field.name" :required="field.required" :error="fieldErrors[field.name]" class="custom-form-item">
              <el-select
                v-model="formData[field.name]"
                :placeholder="field.placeholder || '请选择'"
                style="width: 100%"
                clearable
              >
                <el-option
                  v-for="option in field.options"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
              <small v-if="field.help_text" style="color: #909399; font-size: 13px; margin-top: 4px; display: block;">{{ field.help_text }}</small>
            </el-form-item>
          </el-col>

          <el-col :span="field.fullWidth ? 24 : 12" v-else-if="field.type === 'textarea'">
            <el-form-item :label="field.label" :prop="field.name" :required="field.required" :error="fieldErrors[field.name]" class="custom-form-item">
              <el-input
                type="textarea"
                v-model="formData[field.name]"
                :placeholder="field.placeholder"
                :rows="field.rows || 4"
                :resize="field.resize"
              />
              <small v-if="field.help_text" style="color: #909399; font-size: 13px; margin-top: 4px; display: block;">{{ field.help_text }}</small>
            </el-form-item>
          </el-col>
        </template>
      </el-row>

      <div class="form-actions">
        <el-button class="submit-btn-unified" type="primary" @click="handleSubmit" :loading="loading">
          {{ loading ? '提交中...' : '立即提交' }}
        </el-button>
      </div>

      <div v-if="message" class="form-alert">
        <el-alert
          :title="message"
          :type="messageType === 'success' ? 'success' : messageType === 'error' ? 'error' : 'info'"
          :closable="true"
          show-icon
        />
      </div>
    </el-form>
  </FormLayout>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FormLayout from '@/views/pc/components/FormLayout.vue'
import { useApi } from '@/core/hooks'
import { useNavigation } from '@/core/utils/routeDecision'
import { useAppStore } from '@/core/store/app'
import { getRecordFields } from '@/core/config/entityFields'
import { showSuccess, showError, showWarning } from '@/core/utils/errorHandler'
import { EditPen, Edit } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const appStore = useAppStore()

const header = ref('')
const description = ref('')
const formFields = ref([])
const formData = ref({})
const fieldErrors = ref({})
const message = ref('')
const messageType = ref('')
const loading = ref(false)
const isLoading = ref(true)

const apiComposable = useApi('', { immediate: false })
const { goHome, smartBack } = useNavigation()

const guideSteps = [
  { title: '选择实训室', description: '选择要登记的实训室' },
  { title: '填写日期', description: '选择使用日期' },
  { title: '设备状态', description: '如实填写设备运行情况' },
  { title: '确认提交', description: '核对信息后点击提交' }
]

const tips = [
  '请如实填写设备状态',
  '如设备故障将自动跳转上报',
  '使用人数为必填项'
]

const fetchFormDataApi = async (params = {}) => {
  const apiPath = getApiPath(route.path, route.query, route.params)
  return await apiComposable.get(params, { url: apiPath })
}

const submitFormDataApi = async (data = {}) => {
  let apiPath = getApiPath(route.path, route.query, route.params)
  return await apiComposable.post(data, { url: apiPath })
}

const handleSubmit = async () => {
  loading.value = true
  fieldErrors.value = {}
  message.value = ''

  try {
    const submitData = { ...formData.value }
    const response = await submitFormDataApi(submitData)
    
    if (response && response.success) {
      const shouldRedirect = response.redirect_to_report === true || 
                           response.redirect_to_report === 'true' ||
                           (response.redirect_to_report !== undefined && response.redirect_to_report !== false)

      if (shouldRedirect && response.report_info) {
        message.value = '使用记录创建成功，正在跳转到维护上报页面...'
        messageType.value = 'success'
        showSuccess('使用记录创建成功，正在跳转到维护上报页面...')
        loading.value = true
        
        const reportInfo = response.report_info
        const queryParams = {
          laboratory_id: String(reportInfo.laboratory_id),
          created_at: reportInfo.created_at,
          content: encodeURIComponent(reportInfo.content || ''),
          memo: encodeURIComponent(reportInfo.memo || ''),
          from_record: 'true'
        }
        
        setTimeout(() => {
          const queryString = new URLSearchParams(queryParams).toString()
          window.location.href = `/report-maintenance?${queryString}`
        }, 500)
        return
      }

      message.value = response.message || '创建成功'
      messageType.value = 'success'
      showSuccess(message.value)
      appStore.triggerListRefresh('records')
      setTimeout(() => {
        smartBack()
      }, 1500)
    } else {
      message.value = response.message || '创建失败'
      messageType.value = 'error'
      showError(message.value)
      if (response.errors) {
        fieldErrors.value = response.errors
      }
    }
  } catch (err) {
    message.value = err.response?.data?.message || '创建失败，请检查网络连接'
    messageType.value = 'error'
    showError(message.value)
    if (err.response?.data?.errors) {
      fieldErrors.value = err.response.data.errors
    }
  } finally {
    loading.value = false
  }
}

const loadFormData = async () => {
  isLoading.value = true
  message.value = ''
  
  try {
    const params = { ...route.query }
    const response = await fetchFormDataApi(params)
    
    if (response && response.success === false) {
      throw new Error(response.message || 'API返回失败')
    }
    
    header.value = response.header || response.title || '添加使用记录'
    description.value = response.description || '登记实训室使用情况'
    
    let fieldsData = response?.form_fields || response || {}
    
    if (!fieldsData.sxs_list || fieldsData.sxs_list.length === 0) {
      let sxsList = []
      try {
        const res = await apiComposable.get({ nopage: 1 }, { url: '/laboratories/' })
        if (res && res.items) sxsList = res.items
        else if (res && res.data && res.data.list) sxsList = res.data.list
      } catch (e) {
        // Ignore
      }
      
      if (sxsList.length === 0) {
        try {
          const res = await apiComposable.get({ nopage: 1 }, { url: '/laboratories/' })
          if (res && res.items) sxsList = res.items
          else if (res && res.data && res.data.list) sxsList = res.data.list
        } catch (e) {
        }
      }
      
      if (sxsList.length > 0) {
        fieldsData = { ...fieldsData, sxs_list: sxsList }
      }
    }
    
    const convertedFields = getRecordFields(fieldsData)
    formFields.value = convertedFields
    
    const initialData = {}
    formFields.value.forEach(field => {
      initialData[field.name] = field.default !== undefined ? field.default : ''
    })
    
    formData.value = initialData
  } catch (err) {
    message.value = `加载表单失败：${err.message}`
    messageType.value = 'error'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadFormData()
})

watch(() => formData.value.sxsdevice_status, async (newVal) => {
  if (newVal === '故障') {
    const queryParams = {
      laboratory_id: formData.value.laboratory ? String(formData.value.laboratory) : '',
      created_at: formData.value.date || '',
      from_record: 'true'
    }
    
    await showWarning('您选择了设备状态为【故障】，系统将自动跳转至故障上报页面', '设备故障提醒')
    const queryString = new URLSearchParams(queryParams).toString()
    router.push(`/report-maintenance?${queryString}`)
  }
})
</script>

<style scoped>
.modern-form {
  max-width: 100%;
}

.custom-form-item {
  margin-bottom: 24px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133 !important;
  padding-bottom: 8px !important;
}

.form-actions {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f5f7fa;
}

.submit-btn-unified {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 22px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.form-alert {
  margin-top: 24px;
}
</style>
