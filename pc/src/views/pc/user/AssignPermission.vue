<!-- 分配用户权限 -->
<template>
  <Index>
    <template #rightcontent>
      <div class="modern-form-container assign-permission-page">
        <div class="modern-form-panel">
          <div class="form-header">
            <div class="form-icon"><el-icon :size="48"><Lock /></el-icon></div>
            <h2 class="form-title">为用户分配权限</h2>
            <p class="form-subtitle">请配置用户的角色权限，这将决定用户在系统中的操作范围</p>
          </div>

          <el-form @submit.prevent="handleSubmit" :model="formData" label-width="100px" label-position="top" class="modern-form">
            <div class="form-section">
              <h4 class="section-title">
                <el-icon class="section-icon"><Document /></el-icon> 基本信息
              </h4>
              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="用户名">
                    <el-input
                      v-model="formData.username"
                      size="large"
                      class="custom-input"
                      disabled
                      prefix-icon="User"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="姓名">
                    <el-input
                      v-model="formData.nickname"
                      size="large"
                      class="custom-input"
                      disabled
                      prefix-icon="Postcard"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </div>

            <div class="form-section">
              <h4 class="section-title">
                <el-icon class="section-icon"><Lock /></el-icon> 权限设置
              </h4>
              <el-form-item prop="permissions" class="permissions-form-item">
                <el-checkbox-group v-model="formData.permissions" class="permissions-checkbox-group">
                  <label
                    v-for="(option, index) in filteredPermissionOptions"
                    :key="index"
                    class="permission-card"
                    :class="{ 'is-checked': formData.permissions.includes(option.value) }">
                    <el-checkbox
                      :label="option.value"
                      class="permission-checkbox">
                      <span class="permission-content">
                        <span class="permission-icon"><el-icon :size="18"><component :is="getPermissionIcon(option.label)" /></el-icon></span>
                        <span class="permission-label">{{ option.label }}</span>
                      </span>
                    </el-checkbox>
                  </label>
                </el-checkbox-group>
                <div v-if="errors.permissions" class="permission-error">
                  {{ errors.permissions }}
                </div>
                <div class="permission-hint">
                  <el-icon><InfoFilled /></el-icon>
                  <span>可以选择多个权限，用户将同时拥有所选的所有权限组合</span>
                </div>
              </el-form-item>
            </div>

            <div class="form-footer">
              <el-button class="action-btn" type="primary" size="large" @click="handleSubmit" :loading="loading" round>
                {{ loading ? '提交中...' : '保存配置' }}
              </el-button>
              <el-button class="action-btn" size="large" @click="smartBack" round>
                取消返回
              </el-button>
            </div>
          </el-form>
        </div>
      </div>
    </template>
  </Index>
</template>

<script setup>
import { useAssignPermission } from '@/core/hooks'
import { showSuccess, showError } from '@/core/utils/errorHandler'
import Index from '@/views/pc/dashboard/Index.vue'
import { User, Postcard, InfoFilled, Lock, Document, UserFilled, Key, Avatar, SetUp, StarFilled, OfficeBuilding } from '@element-plus/icons-vue'

const { formData, errors, loading, filteredPermissionOptions, handleSubmit: baseHandleSubmit, smartBack } = useAssignPermission()

const getPermissionIcon = (label) => {
  const iconMap = {
    '超级管理员': StarFilled,
    '分院管理员': OfficeBuilding,
    '实训室管理员': SetUp,
    '教师': Avatar
  }
  return iconMap[label] || Key
}

const handleSubmit = () => baseHandleSubmit(showSuccess, showError)
</script>

<style scoped>
.modern-form-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  min-height: calc(100vh - 140px);
}

.modern-form-panel {
  width: 100%;
  max-width: 800px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
  border: 1px solid #ebeef5;
  overflow: hidden;
}

.form-header {
  padding: 24px 32px;
  border-bottom: 1px solid #f5f7fa;
  text-align: center;
}

.form-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.form-title {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.form-subtitle {
  margin: 8px 0 0;
  color: #909399;
  font-size: 14px;
}

.modern-form {
  padding: 24px 32px;
}

.form-section {
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 16px;
  color: #303133;
}

.permissions-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.permission-card {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.permission-card:hover {
  border-color: #409eff;
}

.permission-card.is-checked {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.permission-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.permission-icon {
  font-size: 20px;
}

.permission-label {
  font-size: 14px;
}

.permission-error {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 8px;
}

.permission-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  color: #909399;
  font-size: 12px;
}

.form-footer {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding-top: 24px;
  border-top: 1px solid #f5f7fa;
}

.action-btn {
  min-width: 120px;
}
</style>
