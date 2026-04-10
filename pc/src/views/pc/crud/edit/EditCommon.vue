<!-- 通用编辑页面 -->
<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="page-container">
        <div class="listheader custom-header">
          <span class="header-text"><el-icon><EditPen /></el-icon> {{ header || '编辑' }}</span>
          <div class="listheader-actions">
            <el-button class="nav-action-btn" plain @click="smartBack">返回</el-button>
            <el-button class="nav-action-btn" plain @click="goHome">首页</el-button>
          </div>
        </div>

        <div class="unified-panel-layout">
          <div class="unified-panel">
            <div class="panel-side">
              <div class="side-header">
                <h3><el-icon><InfoFilled /></el-icon> 操作指南</h3>
                <p>请按照提示修改信息</p>
              </div>

              <div class="side-content">
                <div class="side-block">
                  <div class="block-title">流程步骤</div>
                  <div class="guide-list">
                    <div class="guide-item">
                      <div class="guide-icon">1</div>
                      <div class="guide-text">
                        <h4>查看信息</h4>
                        <p>查看当前记录的基本信息</p>
                      </div>
                    </div>
                    <div class="guide-item">
                      <div class="guide-icon">2</div>
                      <div class="guide-text">
                        <h4>修改内容</h4>
                        <p>修改需要更新的信息</p>
                      </div>
                    </div>
                    <div class="guide-item">
                      <div class="guide-icon">3</div>
                      <div class="guide-text">
                        <h4>保存提交</h4>
                        <p>确认无误后点击保存按钮</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="side-block tips-block">
                  <div class="block-title"><el-icon><Warning /></el-icon> 注意事项</div>
                  <ul class="tips-list">
                    <li>请确保信息填写准确</li>
                    <li>修改后立即生效</li>
                    <li>部分字段可能不可修改</li>
                    <li>�?* 号的为必填项</li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="panel-main">
              <div class="main-header">
                <h3><el-icon><EditPen /></el-icon> {{ header || '编辑' }}</h3>
              </div>

              <div class="main-content">
                <div v-if="loading" class="loading-container">
                  <el-skeleton :rows="5" animated />
                </div>

                <el-form 
                  v-else
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
                        <el-form-item :label="field.label" :prop="field.name" :required="field.required" class="custom-form-item">
                          <el-input
                            :type="field.type"
                            v-model="formData[field.name]"
                            :placeholder="field.placeholder"
                            clearable
                            class="custom-input"
                          />
                          <div v-if="field.help_text" class="help-text">{{ field.help_text }}</div>
                        </el-form-item>
                      </el-col>

                      <el-col :span="12" v-else-if="field.type === 'select'">
                        <el-form-item :label="field.label" :prop="field.name" :required="field.required" class="custom-form-item">
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
                          <div v-if="field.help_text" class="help-text">{{ field.help_text }}</div>
                        </el-form-item>
                      </el-col>

                      <el-col :span="field.fullWidth ? 24 : 12" v-else-if="field.type === 'textarea'">
                        <el-form-item :label="field.label" :prop="field.name" :required="field.required" class="custom-form-item">
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
                    </template>
                  </el-row>

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
import { InfoFilled, EditPen, Warning } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()
const apiComposable = useApi('', { immediate: false })

const header = ref('')
const formFields = ref([])
const formData = ref({})
const loading = ref(false)
const submitting = ref(false)
const message = ref('')
const messageType = ref('')
const originalTid = ref('')
const formRef = ref(null)

const loadData = async () => {
  loading.value = true
  try {
    const apiPath = getApiPath(route.path, route.query, route.params)
    const response = await apiComposable.get(route.query, { url: apiPath })
    
    header.value = response.header || '编辑'
    originalTid.value = response.original_tid || route.query.tid || '1'
    
    if (response.form_fields) {
        formFields.value = Array.isArray(response.form_fields) ? response.form_fields : []
        formData.value = { ...response.form_data }
    }
  } catch (err) { 
    showError(err.message) 
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
        message.value = '操作成功'
        messageType.value = 'success'
        showSuccess('操作成功')
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
}
</style>
