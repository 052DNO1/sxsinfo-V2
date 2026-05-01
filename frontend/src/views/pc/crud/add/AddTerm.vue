<!-- 新增学期 -->
<template>
  <FormLayout
    :title="header || '添加学期'"
    icon="Calendar"
    :loading="loading"
    guide-title="操作指南"
    guide-sub-title="请按照提示填写学期信息"
    :guide-steps="guideSteps"
    :tips="tips"
    tips-title="重要提示"
    :main-title="header || '填写信息'"
    main-icon="Calendar"
  >
    <div style="margin-bottom: 24px;">
      <el-alert
        title="请仔细确认学期起止时间"
        type="warning"
        :closable="false"
        show-icon
      >
        <template #default>
          <div style="line-height: 1.6; margin-top: 4px; font-size: 13px;">
            如果要设为当前学期，请确保当前没有未归档的学期，否则需要先归档现有学期。
          </div>
        </template>
      </el-alert>
    </div>

    <el-form 
      ref="formRef"
      :model="formData" 
      label-width="100px" 
      label-position="top"
      class="modern-form"
      size="large"
      @submit.prevent="handleSubmit"
    >
      <el-row :gutter="24">
        <template
          v-for="field in formFields"
          :key="field.name"
        >
          <el-col
            v-if="field.type === 'text' || field.type === 'date'"
            :span="field.fullWidth ? 24 : 12"
          >
            <el-form-item
              :label="field.label"
              :prop="field.name"
              :required="field.required"
              class="custom-form-item"
            >
              <el-input
                v-if="field.type !== 'date'"
                v-model="formData[field.name]"
                :type="field.type"
                :placeholder="field.placeholder"
                clearable
                class="custom-input"
              >
                <template
                  v-if="field.icon"
                  #prefix
                >
                  <el-icon class="input-icon">
                    <component :is="Icons[field.icon] || Icons.Edit" />
                  </el-icon>
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
            </el-form-item>
          </el-col>

          <el-col
            v-else-if="field.type === 'select'"
            :span="12"
          >
            <el-form-item
              :label="field.label"
              :prop="field.name"
              :required="field.required"
              class="custom-form-item"
            >
              <el-select
                v-model="formData[field.name]"
                :placeholder="field.placeholder || '请选择'"
                style="width: 100%"
                clearable
                class="custom-select"
              >
                <el-option
                  v-for="option in field.options"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </template>
      </el-row>

      <div class="form-actions">
        <el-button
          class="submit-btn-unified"
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
        >
          {{ submitting ? '正在提交...' : '立即创建' }}
        </el-button>
      </div>

      <div
        v-if="message"
        class="form-alert"
      >
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
import { ref, onMounted, reactive } from 'vue'
import FormLayout from '@/views/pc/components/FormLayout.vue'
import { useNavigation } from '@/core/utils/routeDecision'
import { iconMap as Icons } from '@/core/config/icons'
import { getTermFields } from '@/core/config/entityFields'
import { useAppStore } from '@/core/store/app'
import { useApi } from '@/core/hooks'
import { showSuccess, showError, safeAlert } from '@/core/utils/errorHandler'

const { smartBack } = useNavigation()
const appStore = useAppStore()
const apiComposable = useApi('', { immediate: false })

const formRef = ref(null)
const loading = ref(false)
const submitting = ref(false)
const header = ref('添加学期')
const message = ref('')
const messageType = ref('')

const guideSteps = [
  { title: '基本信息', description: '填写学期名称（如2024-2025第一学期）' },
  { title: '时间设置', description: '设定学期的开始和结束日期' },
  { title: '状态确认', description: '确认是否设为当前学期' }
]

const tips = [
  '请仔细核对起止日期，这关系到考勤统计',
  '设为"当前学期"会自动将旧学期归档',
  '建议在学期开始前提前创建'
]

const formFields = ref(getTermFields({}))
const formData = reactive({
  name: '',
  start_date: '',
  end_date: '',
  is_current: true
})
const fieldErrors = ref({})

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (formData.is_current) {
        try {
          const currentTermResponse = await apiComposable.get({}, { url: '/semesters/current/' })
          if (currentTermResponse && currentTermResponse.success && currentTermResponse.data?.current_semester) {
            const currentTerm = currentTermResponse.data.current_semester
            if (currentTerm && !currentTerm.is_archived) {
              await safeAlert(
                `当前学期「${currentTerm.name}」未归档，无法创建新的当前学期。请先将当前学期归档后再创建新学期。`,
                '无法创建当前学期',
                'warning'
              )
              return
            }
          }
        } catch (err) {
        }
      }
      
      submitting.value = true
      message.value = ''
      try {
        const response = await apiComposable.post(formData, { url: '/semesters/' })
        if (response && response.success) {
          showSuccess(response.message || '学期创建成功')
          if (formData.is_current) {
            appStore.triggerTermRefresh()
          }
          appStore.triggerListRefresh('semesters')
          setTimeout(() => {
            smartBack()
          }, 1500)
        } else {
          const errorMsg = response?.message || '创建失败'
          showError(errorMsg)
          message.value = errorMsg
          messageType.value = 'error'
        }
      } catch (err) {
        let errorMsg = '创建失败'
        if (err.response?.data?.message) {
          errorMsg = err.response.data.message
        } else if (err.response?.data?.errors) {
          const errors = err.response.data.errors
          if (typeof errors === 'object') {
            const errorMessages = Object.entries(errors)
              .map(([field, messages]) => {
                const fieldNames = {
                  name: '学期名称',
                  start_date: '开始日期',
                  end_date: '结束日期',
                  is_current: '当前学期'
                }
                const fieldName = fieldNames[field] || field
                return `${fieldName}: ${Array.isArray(messages) ? messages.join(', ') : messages}`
              })
            errorMsg = errorMessages.join('\n')
          } else {
            errorMsg = errors
          }
        } else if (err.message) {
          errorMsg = err.message
        }
        showError(errorMsg)
        message.value = errorMsg
        messageType.value = 'error'
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
