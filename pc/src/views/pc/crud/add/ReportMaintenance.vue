<!-- 故障上报 -->
<template>
  <FormLayout
    title="设备故障上报"
    icon="Tools"
    :loading="isLoading"
    guide-title="操作指南"
    guide-sub-title="请按照提示填写故障详情"
    :guide-steps="guideSteps"
    :tips="tips"
    main-title="填写信息"
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
          <el-col :span="field.fullWidth ? 24 : 12" v-if="field.type === 'text' || field.type === 'date'">
            <el-form-item :label="field.label" :prop="field.name" :required="field.required" :error="fieldErrors[field.name]" class="custom-form-item">
              <el-input
                v-if="field.type !== 'date'"
                :type="field.type"
                v-model="formData[field.name]"
                :placeholder="field.placeholder"
                :clearable="true"
                :disabled="field.disabled"
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
            </el-form-item>
          </el-col>

          <el-col :span="12" v-else-if="field.type === 'select'">
            <el-form-item :label="field.label" :prop="field.name" :required="field.required" :error="fieldErrors[field.name]" class="custom-form-item">
              <el-select
                v-model="formData[field.name]"
                :placeholder="field.placeholder || '请选择'"
                style="width: 100%"
                clearable
                :disabled="field.disabled"
              >
                <el-option
                  v-for="option in field.options"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                  :disabled="option.disabled"
                >
                  {{ option.statusLabel || option.label }}
                </el-option>
              </el-select>
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
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FormLayout from '@/views/pc/components/FormLayout.vue'
import { useApi, useAuth } from '@/core/hooks'
import { useNavigation, getApiPath } from '@/core/utils/routeDecision'
import { Tools, Edit } from '@element-plus/icons-vue'
import { showSuccess, showError } from '@/core/utils/errorHandler'
import { formatLabOption } from '@/core/config/entityFields'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const { user } = useAuth()

const header = ref('')
const description = ref('')
const formFields = ref([])
const formData = ref({})
const fieldErrors = ref({})
const message = ref('')
const messageType = ref('')
const loading = ref(false)
const isLoading = ref(true)
const sxsAdminMap = ref({})

const apiComposable = useApi('', { immediate: false })
const { smartBack } = useNavigation()

const guideSteps = [
  { title: '选择实训室', description: '选择故障设备所在实训室' },
  { title: '填写设备编号', description: '输入故障电脑的编号' },
  { title: '描述故障', description: '详细描述设备故障情况' },
  { title: '确认提交', description: '提交后将通知管理员处理' }
]

const tips = [
  '请准确填写设备编号',
  '故障描述越详细越好',
  '提交后会自动通知管理员'
]

const fetchFormDataApi = async (params = {}) => {
  const apiPath = getApiPath(route.path, route.query, route.params)
  return await apiComposable.get(params, { url: apiPath })
}

const handleSubmit = async () => {
  loading.value = true
  fieldErrors.value = {}
  message.value = ''

  try {
    const submitData = { ...formData.value }
    
    submitData.maintaintype = 3 
    submitData.from_record = 'true'
    submitData.ismaintaind = false
    if (submitData.device_code) {
      submitData.maintainrecordcontent = `[设备编号:${submitData.device_code}] ${submitData.maintainrecordcontent || ''}`
    }

    const sxsId = submitData.laboratory
    
    let apiPath = '/work-orders/'
    const response = await apiComposable.post(submitData, { url: apiPath })

    if (response && response.success) {
      message.value = '故障上报成功！已通知管理员'
      messageType.value = 'success'
      showSuccess('故障上报成功！已通知管理员')
      setTimeout(() => {
        smartBack()
      }, 1500)
    } else {
      message.value = response.message || '上报失败'
      messageType.value = 'error'
      showError(response.message || '上报失败')
    }
  } catch (err) {
    message.value = err.response?.data?.message || '上报失败，请检查网络连接'
    messageType.value = 'error'
    showError(err.response?.data?.message || '上报失败，请检查网络连接')
    if (err.response?.data?.errors) {
      fieldErrors.value = err.response.data.errors
    }
  } finally {
    loading.value = false
  }
}

const convertFormFields = (fieldsData) => {
  if (!fieldsData) {
    fieldsData = {}
  }
  const fields = []
  const currentUser = fieldsData.current_user_name || (user.value ? (user.value.nickname || user.value.username) : '')
  
  if (fieldsData.laboratories && fieldsData.laboratories.length > 0) {
    fieldsData.laboratories.forEach(lab => {
      const adminId = typeof lab.administrator === 'object' ? lab.administrator?.id : lab.administrator
      if (lab.id) {
        sxsAdminMap.value[lab.id] = {
          adminId: adminId,
          name: lab.name,
          no: lab.room_number
        }
      }
    })
    
    fields.push({
      name: 'laboratory',
      type: 'select',
      label: '实训室名称',
      placeholder: '请选择实训室',
      required: true,
      options: fieldsData.laboratories.map(formatLabOption)
    })
  } else if (fieldsData.current_laboratory) {
    const lab = fieldsData.current_laboratory
    const adminId = typeof lab.administrator === 'object' ? lab.administrator?.id : lab.administrator
    if (lab.id) {
      sxsAdminMap.value[lab.id] = {
        adminId: adminId,
        name: lab.name,
        no: lab.room_number
      }
    }
    
    fields.push({
      name: 'laboratory',
      type: 'select',
      label: '实训室名称',
      placeholder: lab.name,
      required: true,
      default: lab.id,
      disabled: true,
      options: [formatLabOption(lab)]
    })
  } else {
    fields.push({
      name: 'laboratory',
      type: 'select',
      label: '实训室名称',
      placeholder: '暂无可用实训室',
      required: true,
      options: [],
      disabled: true
    })
  }
  
  fields.push({
    name: 'device_code',
    type: 'text',
    label: '电脑编号',
    placeholder: '请输入电脑编号(如 01)',
    required: true
  })

  fields.push({
    name: 'reporter',
    type: 'text',
    label: '上报人',
    placeholder: '请输入上报人姓名',
    required: true,
    default: currentUser
  })

  fields.push({
    name: 'maintainrequestdate',
    type: 'date',
    label: '上报时间',
    placeholder: '请选择日期',
    required: true,
    default: fieldsData.defaults?.maintainrequestdate || new Date().toISOString().split('T')[0]
  })
  
  fields.push({
    name: 'maintainrecordcontent',
    type: 'textarea',
    label: '故障描述',
    placeholder: '请描述设备故障情况',
    required: true,
    rows: 4,
    fullWidth: true
  })
  
  return fields
}

const loadFormData = async () => {
  isLoading.value = true
  message.value = ''
  
  try {
    const params = { ...route.query }
    params.is_fault_report = 'true'
    
    const response = await fetchFormDataApi(params)
    
    if (response && response.success === false) {
      throw new Error(response.message || 'API返回失败')
    }
    
    header.value = '设备故障上报'
    description.value = '请填写设备故障详情'
    
    const fieldsData = response?.form_fields || response || {}
    const convertedFields = convertFormFields(fieldsData)
    formFields.value = convertedFields
    
    const initialData = {}
    formFields.value.forEach(field => {
      initialData[field.name] = field.default !== undefined ? field.default : ''
    })

    if (route.query?.from_record === 'true') {
      if (route.query.maintainrequestdate) initialData.maintainrequestdate = route.query.maintainrequestdate
      if (route.query.maintainrecordcontent) {
        let content = decodeURIComponent(route.query.maintainrecordcontent)
        if (content.includes('设备状态异常：')) content = ''
        initialData.maintainrecordcontent = content
      }
      if (route.query.sxsid && route.query.sxsid !== '0') {
        initialData.laboratory = parseInt(route.query.laboratory_id)
      }
    }
    
    formData.value = initialData
  } catch (err) {
    message.value = `加载表单失败：${err.message}`
    messageType.value = 'error'
    formFields.value = convertFormFields({
      current_user_name: user.value?.nickname || user.value?.username || ''
    })
    const initialData = {}
    formFields.value.forEach(field => {
      initialData[field.name] = field.default !== undefined ? field.default : ''
    })
    formData.value = initialData
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadFormData()
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
