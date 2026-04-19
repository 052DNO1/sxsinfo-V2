<!-- 新增用户 -->
<template>
  <FormLayout
    :title="header || '添加用户'"
    icon="UserFilled"
    :loading="loading"
    guide-title="操作指南"
    guide-sub-title="请按照提示填写用户信息"
    :guide-steps="guideSteps"
    :tips="tips"
    :main-title="header || '填写信息'"
    main-icon="EditPen"
  >
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
        <el-col :span="12">
          <el-form-item label="用户名" prop="username" required class="custom-form-item">
            <el-input
              v-model="formData.username"
              placeholder="请输入用户名"
              clearable
              class="custom-input"
            >
              <template #prefix>
                <el-icon class="input-icon"><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="姓名" prop="nickname" required class="custom-form-item">
            <el-input
              v-model="formData.nickname"
              placeholder="请输入姓名"
              clearable
              class="custom-input"
            >
              <template #prefix>
                <el-icon class="input-icon"><UserFilled /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="邮箱" prop="email" class="custom-form-item">
            <el-input
              type="email"
              v-model="formData.email"
              placeholder="请输入邮箱"
              clearable
              class="custom-input"
            >
              <template #prefix>
                <el-icon class="input-icon"><Message /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="手机号" prop="phone" class="custom-form-item">
            <el-input
              v-model="formData.phone"
              placeholder="请输入手机号"
              clearable
              class="custom-input"
            >
              <template #prefix>
                <el-icon class="input-icon"><Iphone /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-col>

        <el-col :span="12" v-if="!isSuperAdmin && !isSystemAdmin">
          <el-form-item label="所属部门" prop="department" required class="custom-form-item">
            <el-select
              v-model="formData.department"
              placeholder="请选择所属部门"
              style="width: 100%"
              :clearable="!isDepartAdmin"
              :disabled="isDepartAdmin"
              class="custom-select"
            >
              <template #prefix>
                <el-icon class="input-icon"><OfficeBuilding /></el-icon>
              </template>
              <el-option
                v-for="dept in departments"
                :key="dept.id"
                :label="dept.name"
                :value="dept.id"
              />
            </el-select>
          </el-form-item>
        </el-col>

        <el-col :span="12" v-if="isSystemAdmin || !isSuperAdmin">
          <el-form-item label="角色" prop="roles" required class="custom-form-item">
            <el-select
              v-model="formData.roles"
              placeholder="请选择角色"
              style="width: 100%"
              multiple
              collapse-tags
              collapse-tags-tooltip
              :max-collapse-tags="2"
              clearable
              class="custom-select"
            >
              <template #prefix>
                <el-icon class="input-icon"><UserFilled /></el-icon>
              </template>
              <el-option
                v-for="role in roleOptions"
                :key="role.value"
                :label="role.label"
                :value="role.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
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
import FormLayout from '@/views/pc/components/FormLayout.vue'
import { useNavigation } from '@/core/utils/routeDecision'
import { useAppStore } from '@/core/store/app'
import { useUserStore } from '@/core/store/user'
import { useApi } from '@/core/hooks'
import { showSuccess, showError } from '@/core/utils/errorHandler'
import { User, UserFilled, Message, Iphone, OfficeBuilding } from '@element-plus/icons-vue'

const { smartBack } = useNavigation()
const appStore = useAppStore()
const userStore = useUserStore()
const apiComposable = useApi('', { immediate: false })

const formRef = ref(null)
const loading = ref(false)
const submitting = ref(false)
const header = ref('添加用户')
const message = ref('')
const messageType = ref('')
const departments = ref([])

const guideSteps = [
  { title: '基本信息', description: '填写用户名、手机号等必填项' },
  { title: '昵称填写', description: '昵称可用于显示，建议与现实姓名一致' },
  { title: '确认提交', description: '核对信息无误后点击提交按钮' }
]

const tips = [
  '用户名建议使用工号或学号',
  '默认密码通常为用户名前6位',
  '如需批量添加，请使用导入功能',
  '* 号的为必填项'
]

const roleOptions = computed(() => {
  if (userStore.isDepartAdmin) {
    return [
      { value: 1, label: '教师' },
      { value: 2, label: '实训室管理员' }
    ]
  }
  if (userStore.user?.is_superuser) {
    return [
      { value: 16, label: '校长' },
    ]
  }
  return [
    { value: 1, label: '教师' },
    { value: 2, label: '实训室管理员' },
    { value: 4, label: '分院管理员' }
  ]
})

const formData = reactive({
  username: '',
  nickname: '',
  email: '',
  phone: '',
  department: '',
  roles: []
})

const fieldErrors = ref({})

const isSuperAdmin = computed(() => userStore.isSuperAdmin)
const isDepartAdmin = computed(() => userStore.isDepartAdmin)
const isSystemAdmin = computed(() => userStore.user?.is_superuser)

const formRules = computed(() => ({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  nickname: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  department: [{ required: !isSuperAdmin.value && !isDepartAdmin.value && !isSystemAdmin.value, message: '请选择所属部门', trigger: 'change' }],
  roles: [{ required: !isSuperAdmin.value, message: '请选择角色', trigger: 'change' }],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: ['blur', 'change'] }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的11位手机号', trigger: ['blur', 'change'] }
  ]
}))

const loadDepartments = async () => {
  try {
    const response = await apiComposable.get({}, { url: '/departments/options/' })
    if (response && response.success && response.data) {
      departments.value = response.data.departments || response.data || []
    }
  } catch (err) {
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
        if (submitData.roles && submitData.roles.length > 0) {
          submitData.role = submitData.roles.reduce((acc, r) => acc | r, 0)
          delete submitData.roles
        }
        Object.keys(submitData).forEach(key => {
          if (submitData[key] === '' || submitData[key] === null || submitData[key] === undefined) {
            delete submitData[key]
          }
        })
        if (isSuperAdmin.value || isSystemAdmin.value) {
          if (!submitData.department) {
            delete submitData.department
          }
          if (!submitData.role) {
            delete submitData.role
          }
        }
        const response = await apiComposable.post(submitData, { url: '/users/' })
        if (response && response.success) {
          showSuccess(response.message || '用户创建成功')
          appStore.triggerListRefresh('users')
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
                  username: '用户名',
                  nickname: '姓名',
                  email: '邮箱',
                  phone: '手机号',
                  department: '部门',
                  role: '角色'
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

onMounted(() => {
  if (!isSystemAdmin.value) {
    loadDepartments()
  }
  if (userStore.isDepartAdmin && userStore.user?.department_id) {
    formData.department = userStore.user.department_id
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
