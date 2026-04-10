<!-- 新增维护记录 -->
<template>
  <FormLayout
    :title="header || '添加维护记录'"
    icon="Tools"
    :loading="loading"
    guide-title="操作指南"
    guide-sub-title="请按照提示填写维护记录信息"
    :guide-steps="guideSteps"
    :tips="tips"
    :main-title="header || '填写信息'"
    main-icon="EditPen"
  >
    <el-form 
      ref="formRef"
      :model="formData" 
      label-width="80px" 
      label-position="top"
      class="modern-form"
      size="large"
      @submit.prevent="handleSubmit">
      
      <el-row :gutter="24">
        <template v-for="field in formFields" :key="field.name">
          <el-col :span="field.fullWidth ? 24 : 12" v-if="['text', 'email', 'tel', 'number', 'date', 'password'].includes(field.type)">
            <el-form-item :label="field.label" :prop="field.name" :required="field.required" :error="fieldErrors[field.name]" class="custom-form-item">
              <el-input
                v-if="field.type !== 'date'"
                :type="field.type"
                v-model="formData[field.name]"
                :placeholder="field.placeholder"
                clearable
                class="custom-input"
              >
                <template #prefix v-if="field.icon">
                  <el-icon class="input-icon"><component :is="Icons[field.icon]" /></el-icon>
                </template>
              </el-input>
              <el-date-picker
                v-else
                v-model="formData[field.name]"
                type="date"
                :placeholder="field.placeholder"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
                class="custom-input"
              />
              <div v-if="field.help_text" class="help-text">{{ field.help_text }}</div>
            </el-form-item>
          </el-col>

          <el-col :span="12" v-else-if="field.type === 'select'">
            <el-form-item :label="field.label" :prop="field.name" :required="field.required" :error="fieldErrors[field.name]" class="custom-form-item">
              <el-select
                v-model="formData[field.name]"
                :placeholder="field.placeholder || '请选择'"
                style="width: 100%"
                clearable
                class="custom-select"
              >
                <template #prefix v-if="field.icon">
                  <el-icon class="input-icon"><component :is="Icons[field.icon]" /></el-icon>
                </template>
                <el-option
                  v-for="option in field.options"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
              <div v-if="field.help_text" class="help-text">{{ field.help_text }}</div>
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
              <div v-if="field.help_text" class="help-text">{{ field.help_text }}</div>
            </el-form-item>
          </el-col>

          <el-col :span="12" v-else-if="field.type === 'checkbox'">
            <el-form-item :label="field.label" :prop="field.name" :error="fieldErrors[field.name]" class="custom-form-item">
              <el-checkbox v-model="formData[field.name]" class="custom-checkbox">
                {{ field.checkboxText || field.label }}
              </el-checkbox>
              <div v-if="field.help_text" class="help-text">{{ field.help_text }}</div>
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
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import FormLayout from '@/views/pc/components/FormLayout.vue'
import { useNavigation, getApiPath } from '@/core/utils/routeDecision'
import { iconMap as Icons } from '@/core/config/icons'
import { Tools, EditPen } from '@element-plus/icons-vue'
import { getMaintainFields } from '@/core/config/entityFields'
import { useEntityForm, useApi } from '@/core/hooks'
import { showSuccess, showError } from '@/core/utils/errorHandler'

const route = useRoute()
const { smartBack } = useNavigation()

const formRef = ref(null)

const guideSteps = [
  { title: '选择实训室', description: '选择需要维护的实训室' },
  { title: '填写维护信息', description: '填写维护时间、类型和内容' },
  { title: '确认提交', description: '核对信息无误后点击提交按钮' }
]

const tips = [
  '维护类型根据实际情况选择',
  '维护内容请详细描述',
  '已维护选项默认勾选',
  '带 * 号的为必填项'
]

const {
  header,
  formFields,
  formData,
  fieldErrors,
  message,
  messageType,
  loading,
  submitting
} = useEntityForm(getMaintainFields, {
  configTransformFn: (rawFields, response) => {
    return getMaintainFields(rawFields)
  },
  onSuccess: (response, data) => {
    setTimeout(() => {
      smartBack()
    }, 1500)
  },
  listType: 'work_orders'
})

const apiComposable = useApi('', { immediate: false })

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      fieldErrors.value = {}
      message.value = ''
      
      try {
        let apiPath = getApiPath(route.path, route.query, route.params)
        const submitData = { ...formData }
        
        if ((route.query?.laboratory_id === '0' || route.query?.laboratory_id === 0 || route.path.match(/\/report-issue\/0/))) {
          if (submitData.laboratory) {
            apiPath = '/work-orders/'
          } else {
            message.value = '请选择实训室'
            messageType.value = 'error'
            submitting.value = false
            return
          }
        }
        
        const response = await apiComposable.post(submitData, { url: apiPath })
        
        if (response && response.success) {
          message.value = response.message || '创建成功'
          messageType.value = 'success'
          showSuccess(response.message || '创建成功')
          setTimeout(() => {
            smartBack()
          }, 1500)
        } else {
          message.value = response.message || '创建失败'
          messageType.value = 'error'
          showError(response.message || '创建失败')
          if (response.errors) {
            fieldErrors.value = response.errors
          }
        }
      } catch (err) {
        message.value = err.response?.data?.message || '创建失败，请检查网络连接'
        messageType.value = 'error'
        showError(err.response?.data?.message || '创建失败，请检查网络连接')
        if (err.response?.data?.errors) {
          fieldErrors.value = err.response.data.errors
        }
      } finally {
        submitting.value = false
      }
    }
  })
}
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

.help-text {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
  line-height: 1.4;
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
