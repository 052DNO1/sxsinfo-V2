<template>
  <FormLayout
    :title="header || '编辑课表'"
    icon="Notebook"
    :loading="loading"
    guide-title="操作指南"
    guide-sub-title="请按照提示修改课程信息"
    :guide-steps="guideSteps"
    :tips="tips"
    :main-title="header || '编辑课表'"
    main-icon="EditPen"
  >
    <el-form 
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
                :readonly="field.readonly"
                :disabled="field.disabled"
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
          :type="messageType === 'success' ? 'success' : messageType === 'error' ? 'error' : messageType === 'warning' ? 'warning' : 'info'"
          show-icon
          closable
        />
      </div>
    </el-form>
  </FormLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from '@/core/hooks'
import { showError, showSuccess } from '@/core/utils/errorHandler'
import { getApiPath, useNavigation } from '@/core/utils/routeDecision'
import FormLayout from '@/views/pc/components/FormLayout.vue'

const route = useRoute()
const { smartBack } = useNavigation()
const apiComposable = useApi('', { immediate: false })

const header = ref('编辑课表')
const formFields = ref([])
const formData = ref({})
const loading = ref(false)
const submitting = ref(false)
const message = ref('')
const messageType = ref('')
const originalTid = ref('')
const formRef = ref(null)

const guideSteps = [
  { title: '查看课程', description: '查看当前课程的基本信息' },
  { title: '修改内容', description: '修改需要更新的课程信息' },
  { title: '保存提交', description: '确认无误后点击保存按钮' }
]

const tips = [
  '课程名称建议清晰明确',
  '节次格式如：1-4 表示 1-4节',
  '周次格式如：1-18 表示 1-18周',
  '* 号的为必填项'
]

const loadData = async () => {
  loading.value = true
  try {
    const apiPath = getApiPath(route.path, route.query, route.params)
    
    const response = await apiComposable.get(route.query, { url: apiPath })
    
    header.value = response.header || '编辑课表'
    originalTid.value = response.original_tid || route.query.tid || '1'
    
    if (response.warning) {
      console.warn('Warning:', response.warning)
    }
    
    if (response.class) {
            const classData = response.class
            const fieldsData = response.form_fields || response.fields || {}
            const teachers = response.teachers || fieldsData.teachers
            const laboratories = response.laboratories || fieldsData.laboratories
            const weekday_choices = response.weekday_choices || fieldsData.weekday_choices
            
            const fields = []
            
            if (laboratories && laboratories.length > 0) {
                fields.push({
                    name: 'laboratory', type: 'select', label: '实训室', required: true,
                    options: laboratories.map(lab => ({ value: lab.id, label: `${lab.name} (${lab.code})` }))
                })
            } else {
                fields.push({ name: 'laboratory_id_display', type: 'text', label: '实训室', required: false, readonly: true, placeholder: classData.laboratory_name || '未分配' })
            }
            
            fields.push({ name: 'course_name', type: 'text', label: '课程名称', required: true, placeholder: '请输入课程名称' })
            
            if (weekday_choices && weekday_choices.length > 0) {
                fields.push({ name: 'weekday', type: 'select', label: '星期', required: true, options: weekday_choices })
            } else {
                fields.push({ name: 'weekday_display', type: 'text', label: '星期', required: false, readonly: true, placeholder: classData.weekday_display || '' })
            }
            
            fields.push({ name: 'time_slot', type: 'text', label: '节次', placeholder: '如：1-4' })
            fields.push({ name: 'weeks', type: 'text', label: '周次', placeholder: '如：1-18' })
            fields.push({ name: 'student_count', type: 'number', label: '人数', placeholder: '请输入人数' })
            
            fields.push({ name: 'class_name', type: 'text', label: '上课班级', placeholder: '请输入上课班级' })
            if (teachers && teachers.length > 0) {
                fields.push({
                    name: 'teacher', type: 'select', label: '分配教师',
                    options: teachers.map(t => ({ value: t.id, label: t.nickname || t.username }))
                })
            } else {
                fields.push({ name: 'teacher_name_display', type: 'text', label: '教师', required: false, readonly: true, placeholder: classData.teacher_name || '未分配' })
            }
            fields.push({ name: 'note', type: 'textarea', label: '备注', fullWidth: true })
        
        formFields.value = fields
        
        formData.value = {
            laboratory: classData.laboratory_id || '',
            course_name: classData.course_name || '',
            weekday: classData.weekday || 1,
            time_slot: classData.time_slot || '1-4',
            weeks: classData.weeks || '1-18',
            student_count: classData.student_count || 20,
            teacher: classData.teacher_id || '',
            class_name: classData.class_name || '',
            note: classData.note || ''
        }
        
        if (!laboratories || laboratories.length === 0) {
            formData.value.laboratory_id_display = classData.laboratory_name || ''
        }
        if (!weekday_choices || weekday_choices.length === 0) {
            formData.value.weekday_display = classData.weekday_display || ''
        }
        if (!teachers || teachers.length === 0) {
            formData.value.teacher_name_display = classData.teacher_name || ''
        }
        
        if (response.warning) {
          message.value = response.warning
          messageType.value = 'warning'
        }
    } else {
      message.value = '无法加载课表数据'
      messageType.value = 'error'
    }
  } catch (err) {
    console.error('Load data error:', err)
    showError(err.message)
    message.value = err.message || '加载数据失败'
    messageType.value = 'error'
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
        message.value = '修改成功'
        messageType.value = 'success'
        showSuccess('修改成功')
    } else {
        message.value = response.message || '修改失败'
        messageType.value = 'error'
        showError(response.message || '修改失败')
    }
    setTimeout(() => {
        smartBack()
    }, 1500)
  } catch (err) {
    message.value = err.message || '操作失败'
    messageType.value = 'error'
    showError(err.message || '操作失败')
    setTimeout(() => {
        smartBack()
    }, 1500)
  } finally {
    submitting.value = false
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
