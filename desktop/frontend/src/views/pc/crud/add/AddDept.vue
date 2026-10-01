<!-- 新增分院 -->
<template>
  <FormLayout
    :title="header || '添加部门'"
    icon="OfficeBuilding"
    :loading="loading"
    guide-title="操作指南"
    guide-sub-title="请按照提示填写部门信息"
    :guide-steps="guideSteps"
    :tips="tips"
    :main-title="header || '填写信息'"
    main-icon="OfficeBuilding"
  >
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
            v-if="field.type === 'text'"
            :span="field.fullWidth ? 24 : 12"
          >
            <el-form-item
              :label="field.label"
              :prop="field.name"
              :required="field.required"
              :error="fieldErrors[field.name]"
              class="custom-form-item"
            >
              <el-input
                v-model="formData[field.name]"
                :placeholder="field.placeholder"
                clearable
                class="custom-input"
              >
                <template #prefix>
                  <el-icon class="input-icon">
                    <component :is="Icons[field.icon] || Icons.Document" />
                  </el-icon>
                </template>
              </el-input>
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
              :error="fieldErrors[field.name]"
              class="custom-form-item"
            >
              <el-select
                v-model="formData[field.name]"
                :placeholder="field.placeholder || '请选择'"
                style="width: 100%"
                clearable
                :multiple="field.multiple"
                class="custom-select"
              >
                <el-option
                  v-for="option in field.options"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
              <div
                v-if="field.help_text"
                class="help-text"
              >
                {{ field.help_text }}
              </div>
            </el-form-item>
          </el-col>

          <el-col
            v-else-if="field.type === 'textarea'"
            :span="field.fullWidth ? 24 : 12"
          >
            <el-form-item
              :label="field.label"
              :prop="field.name"
              :required="field.required"
              :error="fieldErrors[field.name]"
              class="custom-form-item"
            >
              <el-input
                v-model="formData[field.name]"
                type="textarea"
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

    <el-dialog
      v-model="showConflictDialog"
      title="管理员冲突提示"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="conflict-content">
        <el-alert
          type="warning"
          :closable="false"
          show-icon
        >
          <template #title>
            以下用户已经是其他部门的管理员：
          </template>
        </el-alert>
        <div class="conflict-list">
          <div
            v-for="conflict in conflicts"
            :key="conflict.user_id"
            class="conflict-item"
          >
            <div class="user-info">
              <span class="user-name">{{ conflict.nickname }}</span>
              <span class="user-depts">
                当前管理：{{ conflict.current_departments.map(d => d.name).join('、') }}
              </span>
            </div>
          </div>
        </div>
        <p class="conflict-tip">
          是否取消这些用户原来的部门绑定，改为管理当前部门？
        </p>
      </div>
      <template #footer>
        <el-button @click="handleConflictCancel">
          取消
        </el-button>
        <el-button
          type="primary"
          @click="handleConflictConfirm"
        >
          确认更换
        </el-button>
      </template>
    </el-dialog>
  </FormLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import FormLayout from '@/views/pc/components/FormLayout.vue'
import { useNavigation } from '@/core/utils/routeDecision'
import { iconMap as Icons } from '@/core/config/icons'
import { getDeptFields } from '@/core/config/entityFields'
import { useAppStore } from '@/core/store/app'
import { useApi } from '@/core/hooks'
import { showSuccess, showError } from '@/core/utils/errorHandler'

const { smartBack } = useNavigation()
const appStore = useAppStore()
const apiComposable = useApi('', { immediate: false })

const formRef = ref(null)
const loading = ref(false)
const submitting = ref(false)
const header = ref('添加部门')
const message = ref('')
const messageType = ref('')
const showConflictDialog = ref(false)
const conflicts = ref([])
const pendingData = ref(null)

const guideSteps = [
  { title: '基本信息', description: '填写部门名称（如：计算机学院）' },
  { title: '部门描述', description: '填写部门职责或简介（可选）' },
  { title: '确认提交', description: '核对信息无误后点击提交按钮' }
]

const tips = [
  '部门名称在系统中必须唯一',
  '部门创建后可进行人员分配',
  '建议填写详细的部门描述以便管理',
  '每个用户只能管理一个部门'
]

const formFields = ref(getDeptFields({}))
const formData = reactive({
  name: '',
  code: '',
  managers: [],
  description: ''
})
const fieldErrors = ref({})

const loadUsers = async () => {
  loading.value = true
  try {
    const response = await apiComposable.get({}, { url: '/users/?nopage=true&role=4' })
    if (response && response.success !== false) {
      const usersData = response.data || response
      const userList = usersData.list || usersData
      formFields.value = getDeptFields({
        user_options: userList
      })
    }
  } catch (err) {
    console.error('加载用户列表失败', err)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      message.value = ''
      try {
        const submitData = { ...formData }
        if (!submitData.code || submitData.code.trim() === '') {
          submitData.code = null
        }
        
        const response = await apiComposable.post(submitData, { url: '/departments/' })
        
        if (response?.data?.requires_confirmation) {
          conflicts.value = response.data.conflicts
          pendingData.value = { ...formData }
          showConflictDialog.value = true
          submitting.value = false
          return
        }
        
        if (response && response.success) {
          showSuccess(response.message || '部门创建成功')
          appStore.triggerListRefresh('departments')
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
                  name: '部门名称',
                  code: '部门代码',
                  description: '部门描述'
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

const handleConflictCancel = () => {
  showConflictDialog.value = false
  conflicts.value = []
  pendingData.value = null
}

const handleConflictConfirm = async () => {
  showConflictDialog.value = false
  submitting.value = true
  try {
    const submitData = { ...pendingData.value, force_update: true }
    if (!submitData.code || submitData.code.trim() === '') {
      submitData.code = null
    }
    
    const response = await apiComposable.post(submitData, { url: '/departments/' })
    
    if (response && response.success) {
      showSuccess('部门创建成功，已更新管理员绑定')
      appStore.triggerListRefresh('departments')
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
    const errorMsg = err.message || '创建失败'
    showError(errorMsg)
    message.value = errorMsg
    messageType.value = 'error'
  } finally {
    submitting.value = false
    conflicts.value = []
    pendingData.value = null
  }
}

onMounted(loadUsers)
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

.conflict-content {
  padding: 10px 0;
}

.conflict-list {
  margin: 16px 0;
  max-height: 200px;
  overflow-y: auto;
}

.conflict-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  margin-bottom: 8px;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-name {
  font-weight: 500;
  color: #303133;
}

.user-depts {
  font-size: 12px;
  color: #909399;
}

.conflict-tip {
  font-size: 14px;
  color: #606266;
  margin-top: 12px;
}
</style>
