<!-- 新增设备 -->
<template>
  <FormLayout
    title="添加数据"
    icon="Plus"
    :loading="loading"
    guide-title="操作指南"
    guide-sub-title="请按照提示填写设备信息"
    :guide-steps="guideSteps"
    :tips="tips"
    main-title="填写信息"
    :main-icon="Monitor"
  >
    <template #header-center>
      <el-radio-group v-model="activeTab" @change="handleTabChange">
        <el-radio-button v-if="!isSxsAdmin" value="lab">添加实训室</el-radio-button>
        <el-radio-button value="device">添加设备</el-radio-button>
        <el-radio-button value="class">添加课表</el-radio-button>
      </el-radio-group>
    </template>

    <el-form 
      ref="formRef"
      :model="formData" 
      label-width="100px" 
      label-position="top"
      class="modern-form"
      size="large"
      @submit.prevent="handleSubmit">
      
      <el-row :gutter="24">
        <template v-for="field in formFields" :key="field.name">
          <el-col :span="field.fullWidth ? 24 : 12" v-if="field.type === 'text' || field.type === 'number'">
            <el-form-item :label="field.label" :prop="field.name" :required="field.required" :error="fieldErrors[field.name]" class="custom-form-item">
              <el-input
                :type="field.type"
                v-model="formData[field.name]"
                :placeholder="field.placeholder"
                clearable
                :disabled="field.disabled"
                class="custom-input"
              >
                <template #prefix v-if="field.icon">
                  <el-icon class="input-icon"><component :is="Icons[field.icon] || Icons.Edit" /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>

          <el-col :span="12" v-else-if="field.type === 'select'">
            <el-form-item :label="field.label" :prop="field.name" :required="field.required" :error="fieldErrors[field.name]" class="custom-form-item">
              <el-select
                v-model="formData[field.name]"
                :placeholder="field.placeholder || '请选择'"
                style="width: 100%"
                clearable
                filterable
                class="custom-select"
              >
                <template #prefix v-if="field.icon">
                  <el-icon class="input-icon"><component :is="Icons[field.icon] || Icons.Edit" /></el-icon>
                </template>
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
                resize="none"
                class="custom-textarea"
              />
            </el-form-item>
          </el-col>
        </template>
      </el-row>

      <div class="form-actions">
        <el-button class="submit-btn-unified" type="primary" @click="handleSubmit" :loading="submitting">
          {{ submitting ? '正在提交...' : '立即创建' }}
        </el-button>
      </div>

      <div v-if="message" class="form-alert">
        <el-alert
          :title="message"
          :type="messageType === 'success' ? 'success' : messageType === 'error' ? 'error' : 'info'"
          show-icon
          closable
        />
      </div>
    </el-form>
  </FormLayout>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import FormLayout from '@/views/pc/components/FormLayout.vue'
import { useNavigation } from '@/core/utils/routeDecision'
import { useAuth } from '@/core/hooks'
import { useApi } from '@/core/hooks'
import { getDeviceFields, formatLabOption } from '@/core/config/entityFields'
import { iconMap as Icons } from '@/core/config/icons'
import { Monitor } from '@element-plus/icons-vue'
import { showSuccess, showError } from '@/core/utils/errorHandler'
import { useUserStore } from '@/core/store/user'

const router = useRouter()
const route = useRoute()
const { smartBack } = useNavigation()
const apiComposable = useApi('', { immediate: false })
const userStore = useUserStore()

const isSxsAdmin = computed(() => userStore.isSxsAdmin)

const activeTab = ref('device')
const loading = ref(true)
const submitting = ref(false)
const formData = reactive({ status: 'NORMAL' })
const fieldErrors = ref({})
const message = ref('')
const messageType = ref('')
const formFields = ref(getDeviceFields())
const formRef = ref(null)

const guideSteps = [
  { title: '基本信息', description: '填写设备编号、名称及品牌型号' },
  { title: '位置分配', description: '选择设备所属实训室' },
  { title: '确认提交', description: '核对信息无误后点击提交按钮' }
]

const tips = [
  '设备编号在所属实训室内不可重复',
  '请如实填写设备配置信息',
  '如需批量添加，请使用"导入设备"功能'
]

const fetchLabs = async () => {
  loading.value = true
  let list = []

  try {
    const res = await apiComposable.get({ nopage: 1 }, { url: '/laboratories/', cache: false })
    if (res && res.data?.list) list = res.data.list
  } catch (e) {
    // Ignore
  }

  if (list.length === 0) {
    try {
       const res = await apiComposable.get({ nopage: 1 }, { url: '/laboratories/', cache: false })
      if (res && res.data?.list) list = res.data.list
    } catch (e) {
    }
  }

  if (list.length > 0) {
    const field = formFields.value.find(f => f.name === 'laboratory')
    if (field) {
      field.options = list.map(formatLabOption)
    }
  }
  loading.value = false
}

const submitForm = async () => {
  submitting.value = true
  fieldErrors.value = {}
  message.value = ''
  
  try {
    const url = '/equipments/'
    const response = await apiComposable.post({ ...formData }, { url })
    
    if (response && response.success !== false) {
      message.value = response.message || '创建成功'
      messageType.value = 'success'
      showSuccess(response.message || '创建成功')
      setTimeout(() => {
        const labId = formData.laboratory || route.query.laboratory_id
        if (labId) {
          router.push({ path: '/device-list', query: { sxsid: labId } })
        } else {
          smartBack()
        }
      }, 1500)
    } else {
      message.value = response.message || '创建失败'
      messageType.value = 'error'
      showError(response.message || '创建失败')
      if (response.errors) {
        fieldErrors.value = response.errors
      }
    }
    return response
  } catch (err) {
    message.value = err.response?.data?.message || '创建失败'
    messageType.value = 'error'
    showError(err.response?.data?.message || '创建失败')
    if (err.response?.data?.errors) {
      fieldErrors.value = err.response.data.errors
    }
    throw err
  } finally {
    submitting.value = false
  }
}

const handleTabChange = (val) => {
  if (val === 'lab') {
    router.push('/addsxs')
  } else if (val === 'class') {
    router.push('/addclass')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      await submitForm()
    }
  })
}

onMounted(() => {
  fetchLabs().then(() => {
    const labId = route.query.laboratory_id
    if (labId) {
      formData.laboratory = Number(labId)
    }
  })
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

.input-icon {
  font-size: 16px;
  color: #a8abb2;
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
