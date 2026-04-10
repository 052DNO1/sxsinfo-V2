<!-- 分配角色 -->
<template>
  <FormLayout
    title="分配角色"
    icon="UserFilled"
    :loading="loading"
    guide-title="操作指南"
    guide-sub-title="请选择要分配的角色"
    :guide-steps="guideSteps"
    :tips="tips"
    main-title="角色分配"
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
          <el-form-item label="用户名" class="custom-form-item">
            <el-input
              v-model="userInfo.username"
              disabled
              class="custom-input"
            />
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="姓名" class="custom-form-item">
            <el-input
              v-model="userInfo.nickname"
              disabled
              class="custom-input"
            />
          </el-form-item>
        </el-col>

        <el-col :span="24">
          <el-form-item label="角色" prop="role" required class="custom-form-item">
            <el-select
              v-model="formData.role"
              placeholder="请选择角色"
              style="width: 100%"
              class="custom-select"
            >
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
          {{ submitting ? '正在保存...' : '保存' }}
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
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import FormLayout from '@/views/pc/components/FormLayout.vue'
import { useNavigation } from '@/core/utils/routeDecision'
import { useApi } from '@/core/hooks'
import { showSuccess, showError } from '@/core/utils/errorHandler'

const route = useRoute()
const { smartBack } = useNavigation()
const apiComposable = useApi('', { immediate: false })

const formRef = ref(null)
const loading = ref(false)
const submitting = ref(false)
const message = ref('')
const messageType = ref('')

const userInfo = reactive({
  username: '',
  nickname: ''
})

const formData = reactive({
  role: ''
})

const formRules = [{
  required: true,
  message: '请选择角色',
  trigger: 'change'
}]

const guideSteps = [
  { title: '查看用户', description: '确认要修改角色的用户信息' },
  { title: '选择角色', description: '从下拉列表中选择新的角色' },
  { title: '保存提交', description: '确认无误后点击保存按钮' }
]

const tips = [
  '角色变更后立即生效',
  '超级管理员角色无法通过此方式分配',
  '请谨慎分配部门管理员及以上权限'
]

const roleOptions = [
  { value: 0, label: '普通用户' },
  { value: 1, label: '教师' },
  { value: 2, label: '实训室管理员' },
  { value: 4, label: '部门管理员' }
]

const loadUserInfo = async () => {
  loading.value = true
  try {
    const userId = route.params.id
    if (!userId) {
      showError('缺少用户ID')
      return
    }
    
    const response = await apiComposable.get({}, { url: `/users/${userId}/` })
    if (response && response.success !== false) {
      const data = response.data || response
      userInfo.username = data.username || ''
      userInfo.nickname = data.nickname || ''
      formData.role = data.role || ''
    }
  } catch (err) {
    showError(err.message || '加载用户信息失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const userId = route.params.id
        const response = await apiComposable.post({ role: formData.role }, { url: `/users/${userId}/update_role/` })
        if (response && response.success) {
          showSuccess(response.message || '角色分配成功')
          setTimeout(() => smartBack(), 1500)
        } else {
          message.value = response?.message || '角色分配失败'
          messageType.value = 'error'
        }
      } catch (err) {
        message.value = err.message || '角色分配失败'
        messageType.value = 'error'
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(loadUserInfo)
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
