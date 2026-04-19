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
    <div class="page-container">
      <div class="user-panel">
        <div class="user-avatar-circle">
          <span class="avatar-letter">{{ userInfo.nickname ? userInfo.nickname.charAt(0).toUpperCase() : '?' }}</span>
        </div>
        <div class="user-details">
          <div class="user-info-row">
            <span class="label">用户名</span>
            <span class="value">{{ userInfo.username || '加载中...' }}</span>
          </div>
          <div class="user-info-row">
            <span class="label">姓名</span>
            <span class="value name-value">
              <el-icon><User /></el-icon>
              {{ userInfo.nickname || '未设置' }}
            </span>
          </div>
        </div>
      </div>

      <div class="role-selection-area">
        <div class="section-header-v2">
          <div class="header-left">
            <span class="header-icon">🎭</span>
            <span class="header-title">角色配置</span>
          </div>
          <div class="header-right">
            <span class="header-desc">点击卡片选择/取消角色</span>
          </div>
        </div>
        
        <div class="role-grid-v2">
          <div
            v-for="role in filteredRoleOptions"
            :key="role.value"
            :class="['role-item-v2', { 'is-active': formData.roles.includes(role.value) }]"
            @click="toggleRole(role.value)"
          >
            <div class="item-bg-gradient"></div>
            <div class="item-content">
              <div class="item-icon-container">
                <span class="item-emoji">{{ role.icon }}</span>
                <span v-if="formData.roles.includes(role.value)" class="item-check-badge">
                  <el-icon><Check /></el-icon>
                </span>
              </div>
              <span class="item-label">{{ role.label }}</span>
            </div>
          </div>
        </div>

        <div class="selection-summary-v2">
          <div v-if="formData.roles.length > 0" class="summary-box-v2">
            <div class="summary-left">
              <div class="summary-icon-v2">✅</div>
            </div>
            <div class="summary-right">
              <span class="summary-title-v2">已选择</span>
              <span class="summary-roles-v2">{{ selectedRolesText }}</span>
            </div>
          </div>
          <div v-else class="empty-hint-v2">
            <div class="hint-icon-v2">💡</div>
            <span>请至少选择一个角色</span>
          </div>
        </div>

        <div class="action-buttons-v2">
          <el-button 
            type="primary" 
            size="large"
            @click="handleSubmit" 
            :loading="submitting" 
            class="submit-button-v2"
            :disabled="formData.roles.length === 0"
          >
            <span class="btn-content">
              <el-icon><DocumentChecked /></el-icon>
              <span>确认分配角色</span>
            </span>
          </el-button>
        </div>
      </div>
    </div>

    <div v-if="message" class="message-container">
      <el-alert
        :title="message"
        :type="messageType === 'success' ? 'success' : messageType === 'error' ? 'error' : 'info'"
        show-icon
        closable
      />
    </div>
  </FormLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { User, Check, DocumentChecked } from '@element-plus/icons-vue'
import FormLayout from '@/views/pc/components/FormLayout.vue'
import { useNavigation } from '@/core/utils/routeDecision'
import { useApi } from '@/core/hooks'
import { showSuccess, showError } from '@/core/utils/errorHandler'
import { useUserStore } from '@/core/store/user'
import { useAppStore } from '@/core/store/app'

const route = useRoute()
const { smartBack } = useNavigation()
const apiComposable = useApi('', { immediate: false })
const userStore = useUserStore()
const appStore = useAppStore()

const loading = ref(false)
const submitting = ref(false)
const message = ref('')
const messageType = ref('')

const userInfo = reactive({
  username: '',
  nickname: ''
})

const formData = reactive({
  roles: []
})

const guideSteps = [
  { title: '查看用户', description: '确认要修改角色的用户信息' },
  { title: '选择角色', description: '勾选需要分配的角色（可多选）' },
  { title: '保存提交', description: '确认无误后点击保存按钮' }
]

const tips = [
  '角色变更后立即生效',
  '超级管理员角色无法通过此方式分配',
  '请谨慎分配分院管理员及以上权限'
]

const allRoleOptions = [
  { value: 1, label: '教师', icon: '👨‍🏫' },
  { value: 2, label: '实训室管理员', icon: '🔧' },
  { value: 4, label: '分院管理员', icon: '👔' }
]

const filteredRoleOptions = computed(() => {
  if (userStore.isSuperAdmin || userStore.isSuperuser) {
    return allRoleOptions.filter(r => r.value === 4)
  }
  if (userStore.isDepartAdmin) {
    return allRoleOptions.filter(r => r.value === 1 || r.value === 2)
  }
  return allRoleOptions
})

const selectedRolesText = computed(() => {
  const selected = filteredRoleOptions.value
    .filter(role => formData.roles.includes(role.value))
    .map(role => role.label)
  return selected.join(' + ')
})

const toggleRole = (roleValue) => {
  const index = formData.roles.indexOf(roleValue)
  if (index > -1) {
    formData.roles.splice(index, 1)
  } else {
    formData.roles.push(roleValue)
  }
}

const parseRoleToRoles = (roleValue) => {
  const roles = []
  if (roleValue & 1) roles.push(1)
  if (roleValue & 2) roles.push(2)
  if (roleValue & 4) roles.push(4)
  return roles
}

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
      const currentRole = data.role || 0
      formData.roles = parseRoleToRoles(currentRole)
    }
  } catch (err) {
    showError(err.message || '加载用户信息失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (formData.roles.length === 0) {
    showError('请选择角色')
    return
  }

  submitting.value = true
  try {
    const userId = route.params.id
    const roleValue = formData.roles.reduce((acc, role) => acc | role, 0)
    const response = await apiComposable.post({ role: roleValue }, { url: `/users/${userId}/update_role/` })
    if (response && response.success) {
      showSuccess(response.message || '角色分配成功')
      appStore.notifyDataChange('users')
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

onMounted(loadUserInfo)
</script>

<style scoped>
.page-container {
  width: 100%;
}

.user-panel {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 28px 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #fff 100%);
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  margin-bottom: 28px;
}

.user-avatar-circle {
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.avatar-letter {
  color: #fff;
  font-size: 32px;
  font-weight: 600;
}

.user-details {
  flex: 1;
}

.user-info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.user-info-row .label {
  font-size: 14px;
  color: #909399;
  min-width: 60px;
}

.user-info-row .value {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.name-value {
  display: flex;
  align-items: center;
  gap: 6px;
}

.role-selection-area {
  margin-top: 8px;
}

.section-header-v2 {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: linear-gradient(90deg, #ecf5ff 0%, #fff 100%);
  border-radius: 10px;
  border-left: 4px solid #409eff;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 24px;
}

.header-title {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
}

.header-desc {
  font-size: 13px;
  color: #909399;
}

.role-grid-v2 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  margin-bottom: 28px;
}

.role-item-v2 {
  position: relative;
  border-radius: 16px;
  padding: 28px 24px;
  background: #fff;
  border: 2px solid #e4e7ed;
  cursor: pointer;
  transition: all 0.2s ease;
  overflow: hidden;
}

.role-item-v2:hover {
  border-color: #91ccff;
  background: #f5faff;
}

.role-item-v2.is-active {
  border-color: #409eff;
  background: #ecf5ff;
}

.item-bg-gradient {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.08) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.2s ease;
  pointer-events: none;
}

.role-item-v2:hover .item-bg-gradient,
.role-item-v2.is-active .item-bg-gradient {
  opacity: 1;
}

.item-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.item-icon-container {
  position: relative;
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-emoji {
  font-size: 48px;
  line-height: 1;
}

.item-check-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 28px;
  height: 28px;
  background: #67c23a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
}

.item-label {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
  transition: color 0.2s ease;
}

.role-item-v2.is-active .item-label {
  color: #409eff;
}

.selection-summary-v2 {
  margin-bottom: 28px;
}

.summary-box-v2 {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: linear-gradient(90deg, #f0f9eb 0%, #e8f7e3 100%);
  border: 1px solid #c2e7b0;
  border-radius: 12px;
}

.summary-left {
  flex-shrink: 0;
}

.summary-icon-v2 {
  font-size: 28px;
}

.summary-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-title-v2 {
  font-size: 13px;
  color: #67c23a;
  font-weight: 500;
}

.summary-roles-v2 {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
}

.empty-hint-v2 {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 12px;
}

.hint-icon-v2 {
  font-size: 24px;
}

.empty-hint-v2 span {
  font-size: 14px;
  color: #f56c6c;
}

.action-buttons-v2 {
  text-align: center;
  padding-top: 8px;
}

.submit-button-v2 {
  min-width: 220px;
  height: 50px;
  font-size: 16px;
  font-weight: 700;
  border-radius: 12px;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border: none;
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.35);
}

.submit-button-v2:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.message-container {
  margin-top: 24px;
}
</style>