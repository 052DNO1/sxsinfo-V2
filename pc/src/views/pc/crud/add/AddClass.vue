<!-- 新增班级 -->
<template>
  <FormLayout
    title="添加数据"
    icon="Plus"
    :loading="loading"
    guide-title="操作指南"
    guide-sub-title="请按照提示填写课程安排信息"
    :guide-steps="guideSteps"
    :tips="tips"
    :main-title="header || '填写信息'"
    :main-icon="Reading"
  >
    <template #header-center>
      <el-radio-group v-model="activeTab" @change="handleTabChange">
        <el-radio-button value="lab">添加实训室</el-radio-button>
        <el-radio-button value="device">添加设备</el-radio-button>
        <el-radio-button value="class">添加课表</el-radio-button>
      </el-radio-group>
    </template>

    <template #header-actions>
      <el-button type="primary" link @click="goToImport"><el-icon><Download /></el-icon> 批量导入</el-button>
    </template>

    <el-form 
      ref="formRef"
      :model="formData" 
      label-width="100px" 
      label-position="top"
      class="modern-form"
      size="large"
      @submit.prevent="handleSubmit">
      
      <el-row :gutter="24">
        <template v-for="field in formFields" :key="field.name">
          <el-col :span="field.fullWidth ? 24 : 12" v-if="field.type === 'text' || field.type === 'number'">
            <el-form-item :label="field.label" :prop="field.name" :required="field.required" :error="fieldErrors[field.name]" class="custom-form-item">
              <el-input
                :type="field.type"
                v-model="formData[field.name]"
                :placeholder="field.placeholder"
                clearable
                :disabled="field.disabled"
                class="custom-input"
              >
                <template #prefix v-if="field.icon">
                  <el-icon class="input-icon"><component :is="Icons[field.icon] || Icons.Edit" /></el-icon>
                </template>
              </el-input>
              <div v-if="field.help_text" class="help-text">{{ field.help_text }}</div>
            </el-form-item>
          </el-col>

          <el-col :span="12" v-else-if="field.type === 'select'">
            <el-form-item :label="field.label" :prop="field.name" :required="field.required" :error="fieldErrors[field.name]" class="custom-form-item">
              <el-select
                v-model="formData[field.name]"
                :placeholder="field.placeholder || '请选择'"
                style="width: 100%"
                :clearable="!field.disabled"
                :filterable="!field.disabled"
                :disabled="field.disabled"
                class="custom-select"
              >
                <template #prefix v-if="field.icon">
                  <el-icon class="input-icon"><component :is="Icons[field.icon] || Icons.Edit" /></el-icon>
                </template>
                <el-option
                  v-for="option in field.options"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                  :disabled="option.disabled"
                >
                  {{ option.statusLabel || option.label }}
                </el-option>
              </el-select>
              <div v-if="field.help_text" class="help-text">{{ field.help_text }}</div>
            </el-form-item>
          </el-col>

          <el-col :span="field.fullWidth ? 24 : 12" v-else-if="field.type === 'textarea'">
            <el-form-item :label="field.label" :prop="field.name" :required="field.required" :error="fieldErrors[field.name]" class="custom-form-item">
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
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FormLayout from '@/views/pc/components/FormLayout.vue'
import { useNavigation } from '@/core/utils/routeDecision'
import { useApi } from '@/core/hooks'
import { iconMap as Icons } from '@/core/config/icons'
import { Reading, Download } from '@element-plus/icons-vue'
import { getClassFields } from '@/core/config/entityFields'
import { showSuccess, showError } from '@/core/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { smartBack } = useNavigation()
const api = useApi('', { immediate: false })

const activeTab = ref('class')
const formRef = ref(null)
const loading = ref(true)
const submitting = ref(false)
const formFields = ref([])
const formData = reactive({})
const fieldErrors = ref({})
const message = ref('')
const messageType = ref('')
const header = ref('填写信息')

const guideSteps = [
  { title: '课程信息', description: '填写课程名称、上课时间及周次' },
  { title: '资源分配', description: '选择上课实训室及任课教师' },
  { title: '确认提交', description: '系统将自动检测时间冲突' }
]

const tips = [
  '同一实训室在同一时间段不能安排两门课程',
  '任课教师需为系统中已存在的用户',
  '如需批量安排课程，请点击右上角的批量导入'
]

const goToImport = () => {
  const sxsid = route.params.sxsid || route.query.sxsid
  if (sxsid) {
    router.push(`/import-class/${sxsid}`)
  } else {
    router.push('/import-class')
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const [labsRes, teachersRes] = await Promise.all([
      api.get({ nopage: 1 }, { url: '/laboratories/', cache: false }),
      api.get({ nopage: 1, role: '1,2' }, { url: '/users/', cache: false })
    ])
    
    const labs = labsRes?.data?.list || labsRes?.list || []
    const teachers = teachersRes?.data?.list || teachersRes?.list || []
    
    const teacherOptions = teachers.map(t => ({ value: t.id, label: t.nickname || t.username }))
    
    formFields.value = getClassFields({
      lab_options: labs,
      teacher_options: teacherOptions
    })
    
    formFields.value.forEach(f => {
      formData[f.name] = f.default ?? ''
    })
    
    const sxsid = route.params.sxsid || route.query.sxsid
    if (sxsid) {
      formData.laboratory = parseInt(sxsid)
      const labField = formFields.value.find(f => f.name === 'laboratory')
      if (labField) {
        labField.disabled = true
      }
    }
    
    const weekday = route.query.weekday
    const period = route.query.period
    if (weekday) formData.weekday = parseInt(weekday)
    if (period) formData.time_slot = period
    
  } catch (err) {
    showError('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      fieldErrors.value = {}
      message.value = ''
      
      try {
        const response = await api.post({ ...formData }, { url: '/schedules/' })
        
        if (response && response.success !== false) {
          message.value = response.message || '创建成功'
          messageType.value = 'success'
          showSuccess(response.message || '创建成功')
          setTimeout(() => {
            smartBack()
          }, 1500)
        } else {
          message.value = response.message || '创建失败'
          messageType.value = 'error'
          showError(response.message || '创建失败')
          if (response.errors) {
            fieldErrors.value = response.errors
          }
        }
      } catch (err) {
        message.value = err.response?.data?.message || '创建失败'
        messageType.value = 'error'
        showError(err.response?.data?.message || '创建失败')
        if (err.response?.data?.errors) {
          fieldErrors.value = err.response.data.errors
        }
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleTabChange = (val) => {
  if (val === 'lab') {
    router.push('/addsxs')
  } else if (val === 'device') {
    router.push('/add-device')
  }
}

onMounted(loadData)
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
</style>
