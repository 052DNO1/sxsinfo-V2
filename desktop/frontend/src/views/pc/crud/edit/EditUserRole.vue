<!-- 编辑用户角色 -->
<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="page-container">
        <div class="listheader custom-header">
          <span class="header-text"><el-icon><Avatar /></el-icon> {{ header || '分配角色' }}</span>
          <div class="listheader-actions">
            <el-button
              class="nav-action-btn"
              plain
              @click="smartBack"
            >
              返回
            </el-button>
            <el-button
              class="nav-action-btn"
              plain
              @click="goHome"
            >
              首页
            </el-button>
          </div>
        </div>

        <div class="unified-panel-layout">
          <div class="unified-panel">
            <div class="panel-side">
              <div class="side-header">
                <h3><el-icon><InfoFilled /></el-icon> 操作指南</h3>
                <p>请按照提示分配用户角色</p>
              </div>

              <div class="side-content">
                <div class="side-block">
                  <div class="block-title">
                    流程步骤
                  </div>
                  <div class="guide-list">
                    <div class="guide-item">
                      <div class="guide-icon">
                        1
                      </div>
                      <div class="guide-text">
                        <h4>查看用户</h4>
                        <p>确认当前用户信息</p>
                      </div>
                    </div>
                    <div class="guide-item">
                      <div class="guide-icon">
                        2
                      </div>
                      <div class="guide-text">
                        <h4>选择角色</h4>
                        <p>勾选需要分配的角色</p>
                      </div>
                    </div>
                    <div class="guide-item">
                      <div class="guide-icon">
                        3
                      </div>
                      <div class="guide-text">
                        <h4>保存配置</h4>
                        <p>确认无误后点击保存按钮</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="side-block tips-block">
                  <div class="block-title">
                    <el-icon><Warning /></el-icon> 角色说明
                  </div>
                  <ul class="tips-list">
                    <li>支持多选，用户可拥有多个角色</li>
                    <li>不同角色对应不同权限</li>
                    <li>角色变更后立即生效</li>
                    <li>请谨慎分配管理员角色</li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="panel-main">
              <div class="main-header">
                <h3><el-icon><EditPen /></el-icon> {{ header || '分配角色' }}</h3>
              </div>

              <div class="main-content">
                <div
                  v-if="loading"
                  class="loading-container"
                >
                  <el-skeleton
                    :rows="5"
                    animated
                  />
                </div>

                <el-form
                  v-else
                  :model="formData"
                  label-width="100px"
                  label-position="top"
                  class="modern-form"
                  size="large"
                  @submit.prevent="handleSubmit"
                >
                  <div class="form-section">
                    <div class="section-header">
                      <span class="section-indicator" />
                      <h4>基本信息</h4>
                    </div>
                    <el-row :gutter="24">
                      <el-col :span="12">
                        <el-form-item label="用户名">
                          <el-input
                            v-model="formData.username"
                            disabled
                          />
                        </el-form-item>
                      </el-col>
                      <el-col :span="12">
                        <el-form-item label="姓名">
                          <el-input
                            v-model="formData.nickname"
                            disabled
                          />
                        </el-form-item>
                      </el-col>
                      <el-col :span="12">
                        <el-form-item label="手机号">
                          <el-input v-model="formData.phone" />
                        </el-form-item>
                      </el-col>
                    </el-row>
                  </div>

                  <div class="form-section">
                    <div class="section-header">
                      <span class="section-indicator" />
                      <h4>角色设置</h4>
                    </div>
                    <el-form-item
                      prop="permissions"
                      class="permissions-form-item"
                    >
                      <el-checkbox-group
                        v-model="formData.permissions"
                        class="permissions-checkbox-group"
                      >
                        <label
                          v-for="option in permissionOptions"
                          :key="option.value"
                          class="permission-card"
                          :class="{ 'is-checked': formData.permissions.includes(option.value) }"
                        >
                          <el-checkbox
                            :label="option.value"
                            class="permission-checkbox"
                          >
                            <span class="permission-content">
                              <span class="permission-icon"><el-icon :size="18"><component :is="getPermissionIcon(option.label)" /></el-icon></span>
                              <span class="permission-label">{{ option.label }}</span>
                            </span>
                          </el-checkbox>
                        </label>
                      </el-checkbox-group>
                      <div class="permission-hint">
                        <el-icon><InfoFilled /></el-icon>
                        <span>支持多选，用户将同时拥有所选的所有角色权限</span>
                      </div>
                    </el-form-item>
                  </div>

                  <div class="form-actions">
                    <el-button
                      class="submit-btn-unified"
                      type="primary"
                      :loading="submitting"
                      @click="handleSubmit"
                    >
                      {{ submitting ? '正在保存...' : '保存配置' }}
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
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Index>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/core/hooks'
import { showError, showSuccess } from '@/core/utils/errorHandler'
import { getApiPath } from '@/core/utils/routeDecision'
import { useNavigation } from '@/core/utils/routeDecision'
import Index from '@/views/pc/dashboard/Index.vue'
import { InfoFilled, EditPen, Avatar, Warning, SetUp, Key, User, StarFilled, OfficeBuilding } from '@element-plus/icons-vue'
import { useAppStore } from '@/core/store/app'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()
const apiComposable = useApi('', { immediate: false })
const appStore = useAppStore()

const header = ref('分配角色')
const formData = ref({ username: '', nickname: '', phone: '', permissions: [] })
const permissionOptions = ref([])
const loading = ref(false)
const submitting = ref(false)
const message = ref('')
const messageType = ref('')
const originalTid = ref('')

const loadData = async () => {
  loading.value = true
  try {
    const apiPath = getApiPath(route.path, route.query, route.params)
    const response = await apiComposable.get(route.query, { url: apiPath })
    
    originalTid.value = response.original_tid || route.query.tid || '1'
    
    if (response.user) {
        formData.value.username = response.user.username
        formData.value.nickname = response.user.nickname
        formData.value.phone = response.user.phone || ''
        
        let options = response.permission_choices || []
        if (!Array.isArray(options) && typeof options === 'object') {
            options = Object.keys(options).map(k => ({ value: parseInt(k), label: options[k] }))
        }
        options = options.map(o => {
            if (Array.isArray(o)) return { value: o[0], label: o[1] }
            return o
        })
         
        if (options.length === 0) {
            options = [{ value: 1, label: '教师' }, { value: 2, label: '实训室管理员' }]
            if (!response.is_departadmin) options.push({ value: 4, label: '分院管理员' })
        }
        permissionOptions.value = options

        let current = response.current_permissions || []
        if (!Array.isArray(current)) current = [current]
        formData.value.permissions = current
    }
  } catch (err) {
    showError(err.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  submitting.value = true
  message.value = ''
  try {
     const apiPath = getApiPath(route.path, route.query, route.params)
     const submitData = { ...formData.value, original_tid: originalTid.value }
     const response = await apiComposable.post(submitData, { url: apiPath })
     if (response.success) {
         message.value = '角色分配成功'
         messageType.value = 'success'
         showSuccess('角色分配成功')
         appStore.notifyDataChange('users')
         setTimeout(() => {
             smartBack()
         }, 1500)
     } else {
         message.value = response.message || '操作失败'
         messageType.value = 'error'
         showError(response.message || '操作失败')
     }
  } catch (err) {
      message.value = err.message || '操作失败'
      messageType.value = 'error'
      showError(err.message || '操作失败')
  } finally {
      submitting.value = false
  }
}

const getPermissionIcon = (label) => {
  const iconMap = {
    '超级管理员': StarFilled,
    '分院管理员': OfficeBuilding,
    '实训室管理员': SetUp,
    '教师': Avatar,
    '任课教师': Avatar,
    '普通用户': User
  }
  return iconMap[label] || Key
}

onMounted(loadData)
</script>

<style scoped>
.page-container {
  padding: 20px;
  max-width: 100%;
}

.custom-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0;
}

.header-text {
  font-weight: bold;
  font-size: 18px;
  color: #1a1a1a;
}

.listheader-actions {
  display: flex;
  gap: 12px;
}

.unified-panel-layout {
  display: flex;
  justify-content: center;
  padding: 0;
  min-height: auto;
}

.unified-panel {
  width: 100%;
  max-width: 1600px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
  border: 1px solid #ebeef5;
  display: flex;
  overflow: hidden;
  height: calc(100vh - 140px);
  max-height: 700px;
  min-height: 500px;
  margin-top: 10px;
}

.panel-side {
  flex: 0 0 400px;
  background-color: #f8f9fb;
  border-right: 1px solid #eef0f5;
  display: flex;
  flex-direction: column;
}

.side-header {
  padding: 24px 24px 16px;
  border-bottom: 1px solid #eef0f5;
}

.side-header h3 {
  margin: 0 0 6px;
  font-size: 18px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.side-header p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.side-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
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
}

.guide-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.guide-item {
  display: flex;
  gap: 16px;
}

.guide-icon {
  width: 28px;
  height: 28px;
  background: #e6e8eb;
  color: #606266;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.guide-text h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  color: #303133;
  font-weight: 600;
}

.guide-text p {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.4;
}

.tips-block {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
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

.panel-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  overflow-y: auto;
}

.main-header {
  padding: 24px 32px;
  border-bottom: 1px solid #f5f7fa;
  flex-shrink: 0;
}

.main-header h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-content {
  flex: 1;
  padding: 32px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

.modern-form {
  max-width: 100%;
}

.form-section {
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.section-indicator {
  width: 4px;
  height: 18px;
  background-color: #409eff;
  border-radius: 2px;
  margin-right: 10px;
}

.section-header h4 {
  font-size: 16px;
  color: #303133;
  margin: 0;
}

.permissions-checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.permission-card {
  display: block;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  padding: 12px 12px;
  background: #ffffff;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
  cursor: pointer;
}

.permission-card:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
}

.permission-card.is-checked {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.permission-checkbox {
  width: 100%;
}

:deep(.permission-checkbox .el-checkbox__label) {
  width: 100%;
}

.permission-content {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  color: var(--el-text-color-primary);
}

.permission-icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--el-fill-color-light);
  font-size: 18px;
}

.permission-label {
  font-weight: 600;
}

.permission-hint {
  margin-top: 10px;
  display: inline-flex;
  gap: 6px;
  align-items: center;
  color: #909399;
  font-size: 14px;
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

.loading-container {
  padding: 20px 0;
}

@media (max-width: 992px) {
  .unified-panel {
    flex-direction: column;
    height: auto;
    max-height: none;
  }
  
  .panel-side {
    flex: none;
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #eef0f5;
  }
  
  .guide-list {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 20px;
  }
  
  .guide-item {
    flex: 1;
    min-width: 200px;
  }
  
  .main-content {
    padding: 20px;
  }
  
  .permissions-checkbox-group {
    grid-template-columns: 1fr;
  }
}
</style>
