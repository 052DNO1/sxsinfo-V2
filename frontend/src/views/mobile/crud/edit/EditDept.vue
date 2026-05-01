<template>
  <div class="mobile-page">
    <van-nav-bar
      title="编辑分院"
      left-arrow
      @click-left="goBack"
    >
      <template #right>
        <van-icon
          name="home-o"
          size="20"
          color="#4F6EF7"
          @click="goHome"
        />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <div class="form-hero form-hero--purple">
        <div class="form-hero-icon">
          <van-icon
            name="edit"
            size="28"
          />
        </div>
        <h2>编辑分院</h2>
        <p>修改组织架构信息</p>
      </div>

      <van-skeleton
        v-if="loading"
        :row="5"
        animated
      />

      <template v-else>
        <div class="form-section animate-fade-in-up animate-delay-1">
          <div class="section-label">
            <span>🏢</span> 基本信息
          </div>
          <van-cell-group inset>
            <van-field
              v-model="formData.name"
              label="分院名称"
              required
              clearable
              :rules="[{required:true,message:'请输入名称'}]"
            />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-2">
          <div class="section-label">
            <span>👤</span> 分配管理员
          </div>
          <van-cell-group inset>
            <div class="manager-tips">
              每个用户只能管理一个部门，可选择多个管理员
            </div>
            <div class="manager-list">
              <div 
                v-for="user in userOptions" 
                :key="user.id"
                class="manager-item"
                :class="{ active: formData.manager_ids.includes(user.id) }"
                @click="toggleManager(user.id)"
              >
                <div class="manager-avatar">
                  <van-icon
                    name="user-o"
                    size="18"
                  />
                </div>
                <div class="manager-info">
                  <span class="manager-name">{{ user.nickname || user.username }}</span>
                </div>
                <van-icon 
                  :name="formData.manager_ids.includes(user.id) ? 'checked' : 'circle'" 
                  :class="['check-icon', { checked: formData.manager_ids.includes(user.id) }]"
                  size="20"
                />
              </div>
              <van-empty
                v-if="userOptions.length === 0"
                description="暂无可选管理员"
                :image-size="60"
              />
            </div>
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-3">
          <div class="section-label">
            <span>📝</span> 其他信息
          </div>
          <van-cell-group inset>
            <van-field
              v-model="formData.description"
              rows="3"
              autosize
              type="textarea"
              label="分院描述"
              show-word-limit
              :maxlength="200"
            />
          </van-cell-group>
        </div>

        <div class="form-actions">
          <van-button
            type="primary"
            block
            round
            size="large"
            :loading="submitting"
            icon="success"
            @click="handleSubmit"
          >
            保存修改
          </van-button>
        </div>
      </template>

      <van-dialog
        v-model:show="showConflictDialog"
        title="管理员冲突提示"
        show-cancel-button
        confirm-button-text="确认更换"
        cancel-button-text="取消"
        @confirm="handleConflictConfirm"
        @cancel="handleConflictCancel"
      >
        <div class="conflict-content">
          <div class="conflict-warning">
            <van-icon
              name="warning-o"
              size="24"
              color="#FF9500"
            />
            <span>以下用户已经是其他部门的管理员</span>
          </div>
          <div class="conflict-list">
            <div
              v-for="conflict in conflicts"
              :key="conflict.user_id"
              class="conflict-item"
            >
              <div class="user-info">
                <span class="user-name">{{ conflict.nickname }}</span>
                <span class="user-depts">当前管理：{{ conflict.current_departments?.map(d => d.name).join('、') }}</span>
              </div>
            </div>
          </div>
          <p class="conflict-tip">
            是否取消这些用户原来的部门绑定，改为管理当前部门？
          </p>
        </div>
      </van-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/core/utils/routeDecision'
import { deptService } from '@/core/services/BaseService'
import { showSuccess, showError } from '@/core/utils/errorHandler'
import { showDialog } from 'vant'
import api from '@/core/api/client'

const route = useRoute()
const router = useRouter()
const { goBack, goHome, smartBack } = useNavigation()

const loading = ref(false)
const submitting = ref(false)
const userOptions = ref([])
const showConflictDialog = ref(false)
const conflicts = ref([])
const pendingData = ref(null)
const formData = ref({ 
  name: '', 
  description: '',
  manager_ids: []
})

const toggleManager = (userId) => {
  const idx = formData.value.manager_ids.indexOf(userId)
  if (idx >= 0) {
    formData.value.manager_ids.splice(idx, 1)
  } else {
    formData.value.manager_ids.push(userId)
  }
}

const loadUserOptions = async () => {
  try {
    const res = await api.get('/users/', { nopage: true, role: 4 })
    if (res?.data?.list) {
      userOptions.value = res.data.list
    }
  } catch (e) {
    console.error('加载用户列表失败', e)
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      loadUserOptions()
    ])
    
    const res = await deptService.get(route.params.id)
    if (res?.data) { 
      formData.value.name = res.data.name || ''
      formData.value.description = res.data.description || ''
      formData.value.manager_ids = res.data.manager_ids || []
    }
  } catch (e) { showError('加载失败') }
  finally { loading.value = false }
})

const handleSubmit = async () => {
  if (!formData.value.name) return showError('请输入名称')
  submitting.value = true
  try {
    const submitData = {
      name: formData.value.name,
      description: formData.value.description,
      manager_ids: formData.value.manager_ids
    }
    
    const response = await deptService.update(route.params.id, submitData)
    
    if (response?.data?.requires_confirmation) {
      conflicts.value = response.data.conflicts
      pendingData.value = { ...formData.value }
      showConflictDialog.value = true
      submitting.value = false
      return
    }
    
    if (response?.success !== false) {
      showSuccess('保存成功'); setTimeout(()=>smartBack(),1500)
    } else {
      showError(response?.message || '保存失败')
    }
  } catch (e) { showError(e.message||'保存失败') }
  finally { submitting.value = false }
}

const handleConflictConfirm = async () => {
  showConflictDialog.value = false
  submitting.value = true
  try {
    const submitData = {
      name: pendingData.value.name,
      description: pendingData.value.description,
      manager_ids: pendingData.value.manager_ids,
      force_update: true
    }
    const response = await deptService.update(route.params.id, submitData)
    if (response?.success !== false) {
      showSuccess('保存成功，已更新管理员绑定'); setTimeout(()=>smartBack(),1500)
    } else {
      showError(response?.message || '保存失败')
    }
  } catch (e) { showError(e.message||'保存失败') }
  finally { submitting.value = false }
}

const handleConflictCancel = () => {
  showConflictDialog.value = false
  conflicts.value = []
  pendingData.value = null
}
</script>

<style scoped>
.form-hero--purple { background: #EEF2FF; }
.form-hero { background: #F7F8FA; padding: 28px 20px; margin: -12px -16px 20px; text-align: center; border-radius: 0 0 16px 16px; }
.form-hero-icon { width: 60px; height: 60px; border-radius: 50%; background: #EEF2FF; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; color: #4F6EF7; }
.form-hero h2 { margin: 0 0 6px; font-size: 20px; font-weight: 700; color: #1A1A1A; }
.form-hero p { margin: 0; font-size: 13px; color: #666666; }
.form-section { margin-bottom: 8px; }
.section-label { display: flex; align-items: center; gap: 8px; padding: 10px 16px 6px; font-size: 13px; font-weight: 600; color: var(--mobile-text-secondary); }
.section-label span { font-size: 16px; }

.manager-tips {
  font-size: 12px;
  color: #909399;
  padding: 8px 16px;
  background: #f5f7fa;
  margin-bottom: 8px;
}

.manager-list {
  padding: 4px 0;
}

.manager-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 1px solid #f5f7fa;
}

.manager-item:last-child {
  border-bottom: none;
}

.manager-item.active {
  background: #f0f7ff;
}

.manager-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  flex-shrink: 0;
}

.manager-item.active .manager-avatar {
  background: #e6f0ff;
  color: #4F6EF7;
}

.manager-info {
  flex: 1;
  min-width: 0;
}

.manager-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.check-icon {
  color: #c0c4cc;
  flex-shrink: 0;
}

.check-icon.checked {
  color: #4F6EF7;
}

.conflict-content {
  padding: 16px;
}

.conflict-warning {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #FFF5E6;
  border-radius: 8px;
  margin-bottom: 16px;
  color: #FF9500;
  font-size: 14px;
}

.conflict-list {
  max-height: 150px;
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
  font-size: 14px;
}

.user-depts {
  font-size: 12px;
  color: #909399;
}

.conflict-tip {
  font-size: 14px;
  color: #606266;
  margin-top: 12px;
  text-align: center;
}
</style>