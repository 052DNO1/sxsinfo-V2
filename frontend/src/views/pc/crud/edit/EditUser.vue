<!-- 编辑用户 -->
<template>
  <FormLayout
    :title="header || '编辑用户'"
    icon="User"
    :loading="loading"
    :show-back="false"
    guide-title="操作指南"
    guide-sub-title="请按照提示修改用户信息"
    :guide-steps="guideSteps"
    :tips="tips"
    :main-title="isSelfEdit ? '修改资料' : '编辑用户'"
    main-icon="EditPen"
  >
    <template #side-extra v-if="isAdminEdit && !isSelfEdit">
      <div class="side-block">
        <div class="block-title" style="color: #f56c6c;"><el-icon><WarningFilled /></el-icon> 管理员注意事项</div>
        <ul class="tips-list">
          <li>修改他人信息请谨慎操作</li>
          <li>删除用户操作不可恢复</li>
          <li>重置密码后请及时通知用户</li>
        </ul>
      </div>
    </template>

    <el-form 
      ref="formRef"
      :model="formData" 
      :rules="formRules"
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
                :type="field.type"
                v-model="formData[field.name]"
                :placeholder="field.placeholder"
                clearable
                :readonly="field.readonly"
                :disabled="field.readonly"
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
                <el-option
                  v-for="option in (field.options || [])"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
              <div v-if="field.help_text" class="help-text">{{ field.help_text }}</div>
            </el-form-item>
          </el-col>
        </template>
      </el-row>

      <div class="form-section" v-if="isAdminEdit && !isSelfEdit">
        <div class="section-header">
          <span class="section-indicator warning"></span>
          <h4>管理操作</h4>
        </div>
        <div class="admin-actions">
          <el-button type="warning" plain size="default" @click="handleResetPassword">重置密码</el-button>
          <el-button type="danger" plain size="default" @click="handleDeleteUser">删除用户</el-button>
        </div>
      </div>

      <div class="form-actions">
        <el-button class="submit-btn-unified" type="primary" @click="handleSubmit" :loading="submitting">
          {{ submitting ? '正在保存...' : '保存修改' }}
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
import { computed, watch, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FormLayout from '@/views/pc/components/FormLayout.vue'
import { useAuth, useDelete, useApi, useEntityForm } from '@/core/hooks'
import { useNavigation } from '@/core/utils/routeDecision'
import { showError, showSuccess, safeConfirm } from '@/core/utils/errorHandler'
import { User, EditPen, WarningFilled } from '@element-plus/icons-vue'
import { VALIDATION_RULES } from '@/core/config/entityFields'
import { useAppStore } from '@/core/store/app'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)

const { user, updateUser } = useAuth()
const { smartBack } = useNavigation()
const apiComposable = useApi('', { immediate: false })
const appStore = useAppStore()

const isSelfEdit = computed(() => route.path === '/update-user')
const isAdminEdit = computed(() => route.path.startsWith('/update/'))

const guideSteps = [
  { title: '查看信息', description: '查看当前用户的基本信息' },
  { title: '修改内容', description: '修改需要更新的用户信息' },
  { title: '保存提交', description: '确认无误后点击保存按钮' }
]

const tips = [
  '请填写真实有效的姓名和联系方式',
  '邮箱将用于接收重要通知',
  '手机号码方便紧急情况下联系',
  '带 * 号的为必填项'
]

const getUserId = () => {
    const match = route.path.match(/^\/update\/(\d+)$/)
    if (match && match[1]) return match[1]
    return route.params.id
}

const transformFields = (rawFields, response) => {
    if (isSelfEdit.value) {
        return [
          { name: 'username', type: 'text', label: '用户名', placeholder: '请输入用户名', required: true },
          { name: 'nickname', type: 'text', label: '姓名', placeholder: '请输入姓名', required: true },
          { name: 'email', type: 'email', label: '邮箱', placeholder: '请输入邮箱', required: true, rules: VALIDATION_RULES.email },
          { name: 'phone', type: 'tel', label: '电话', placeholder: '请输入电话', required: false, rules: VALIDATION_RULES.phoneOptional }
        ]
    } else {
        return [
          { name: 'username', type: 'text', label: '用户名', placeholder: '用户名', required: true, readonly: true },
          { name: 'nickname', type: 'text', label: '姓名', placeholder: '请输入姓名', required: true },
          { 
            name: 'role', 
            type: 'select', 
            label: '角色', 
            required: true, 
            options: [
              { value: 1, label: '教师' }, 
              { value: 2, label: '实训室管理员' }, 
              { value: 3, label: '普通用户' }
            ] 
          }
        ]
    }
}

const dataMapper = (response) => {
    const userData = response.user || response
    const data = {
        nickname: userData.nickname || '',
        email: userData.email || '',
        phone: userData.phone || '',
        username: userData.username || '',
        role: response.current_role !== undefined ? response.current_role : (userData.role || 3)
    }
    
    if (!isSelfEdit.value) {
        data.original_tid = response.original_tid || route.query.tid || '1'
    }
    
    return data
}

const {
  header,
  formFields,
  formData,
  fieldErrors,
  message,
  messageType,
  loading,
  submitting,
  handleSubmit: submitForm,
  loadData,
  formRules
} = useEntityForm(transformFields, {
  dataMapper,
  onSuccess: (response, submitData) => {
      if (isSelfEdit.value) {
         const updatedUser = { ...user.value, ...submitData }
         updateUser(updatedUser)
         router.push('/')
      } else {
         smartBack()
      }
  }
})

const loadUserData = async () => {
    loading.value = true
    try {
        const userId = getUserId()
        let response
        
        if (isSelfEdit.value) {
            response = await apiComposable.get({}, { url: '/users/profile/' })
        } else if (userId) {
            response = await apiComposable.get({}, { url: `/users/${userId}/` })
        }
        
        if (response && response.success !== false) {
            header.value = isSelfEdit.value ? '修改用户信息' : '编辑用户'
            formFields.value = transformFields(null, response)
            
            const initialData = dataMapper(response.data || response)
            formFields.value.forEach(f => {
                formData[f.name] = initialData[f.name] ?? ''
            })
        }
    } catch (err) {
        message.value = err.message || '加载失败'
        messageType.value = 'error'
    } finally {
        loading.value = false
    }
}

onMounted(loadUserData)

watch(loading, (newVal) => {
    if (!newVal && isSelfEdit.value) {
        header.value = '修改用户信息'
    } else if (!newVal && !header.value) {
        header.value = '编辑用户'
    }
})

const handleSubmit = async () => {
    if (!formRef.value) {
      await doSubmit()
      return
    }
    
    await formRef.value.validate(async (valid) => {
      if (valid) {
        await doSubmit()
      }
    })
}

const doSubmit = async () => {
    submitting.value = true
    try {
        const userId = getUserId()
        let response
        
        if (isSelfEdit.value) {
            response = await apiComposable.put(formData, { url: '/users/profile/' })
        } else if (userId) {
            response = await apiComposable.put(formData, { url: `/users/${userId}/` })
        }
        
        if (response && response.success !== false) {
            showSuccess(response.message || '保存成功')
            if (isSelfEdit.value) {
                const updatedUser = { ...user.value, ...formData }
                updateUser(updatedUser)
                router.push('/')
            } else {
                appStore.notifyDataChange('users')
                smartBack()
            }
        } else {
            message.value = response?.message || '操作失败'
            messageType.value = 'error'
        }
    } catch (err) {
        message.value = err.message || '提交失败'
        messageType.value = 'error'
    } finally {
        submitting.value = false
    }
}

const { handleDelete: execDelete } = useDelete({
  apiPathBuilder: (userId) => `/users/${userId}/`,
  refresh: () => {
    appStore.notifyDataChange('users')
    smartBack()
  }, 
  confirmMessageBuilder: () => '确定要删除该用户吗？此操作不可逆！'
})

const handleResetPassword = async () => {
  const userId = getUserId()
  if (!await safeConfirm('确定要重置该用户的密码吗？')) return
  try {
    const res = await apiComposable.post({ user_id: userId }, { url: '/auth/password/reset/' })
    if (res.success) showSuccess(res.message)
    else showError(res.message)
  } catch (err) { showError(err.message) }
}

const handleDeleteUser = async () => {
  const userId = getUserId()
  await execDelete(userId)
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

.help-text {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
  line-height: 1.4;
}

.form-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px dashed #eee;
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.section-indicator {
  width: 4px;
  height: 18px;
  background-color: #409eff;
  border-radius: 2px;
  margin-right: 10px;
}

.section-indicator.warning {
  background-color: #f56c6c;
}

.section-header h4 {
  font-size: 14px;
  color: #303133;
  margin: 0;
}

.admin-actions {
  display: flex;
  gap: 10px;
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

.side-block {
  display: flex;
  flex-direction: column;
}

.block-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tips-list {
  margin: 0;
  padding-left: 18px;
  font-size: 13px;
  color: #606266;
}

.tips-list li {
  margin-bottom: 6px;
  line-height: 1.5;
}
</style>
