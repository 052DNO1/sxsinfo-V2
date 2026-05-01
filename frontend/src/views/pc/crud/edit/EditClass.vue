<!-- 编辑课表 -->
<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="page-container">
        <div class="listheader custom-header">
          <span class="header-text"><el-icon><EditPen /></el-icon> {{ header || '编辑课表' }}</span>
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
                <p>请按照提示修改课表信息</p>
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
                        <h4>查看信息</h4>
                        <p>查看当前课表的基本信息</p>
                      </div>
                    </div>
                    <div class="guide-item">
                      <div class="guide-icon">
                        2
                      </div>
                      <div class="guide-text">
                        <h4>修改内容</h4>
                        <p>修改需要更新的课表信息</p>
                      </div>
                    </div>
                    <div class="guide-item">
                      <div class="guide-icon">
                        3
                      </div>
                      <div class="guide-text">
                        <h4>保存提交</h4>
                        <p>确认无误后点击保存按钮</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="side-block tips-block">
                  <div class="block-title">
                    <el-icon><Warning /></el-icon> 注意事项
                  </div>
                  <ul class="tips-list">
                    <li>课程名称建议清晰明确</li>
                    <li>节次格式如：1-4 表示 1-4节</li>
                    <li>周次格式如：1-18 表示 1-18周</li>
                    <li>带 * 号的为必填项</li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="panel-main">
              <div class="main-header">
                <h3><el-icon><EditPen /></el-icon> {{ header || '编辑课表' }}</h3>
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
                  ref="formRef"
                  :model="formData"
                  label-width="80px"
                  label-position="top"
                  class="modern-form"
                  size="large"
                  @submit.prevent="handleSubmit"
                >
                  <el-row :gutter="24">
                    <template
                      v-for="field in formFields"
                      :key="field.name"
                    >
                      <el-col
                        v-if="['text', 'email', 'tel', 'number', 'date', 'password'].includes(field.type)"
                        :span="field.fullWidth ? 24 : 12"
                      >
                        <el-form-item
                          :label="field.label"
                          :prop="field.name"
                          :required="field.required"
                          class="custom-form-item"
                        >
                          <el-input
                            v-model="formData[field.name]"
                            :type="field.type"
                            :placeholder="field.placeholder"
                            clearable
                            class="custom-input"
                          />
                          <div
                            v-if="field.help_text"
                            class="help-text"
                          >
                            {{ field.help_text }}
                          </div>
                        </el-form-item>
                      </el-col>

                      <el-col
                        v-else-if="field.type === 'select'"
                        :span="12"
                      >
                        <el-form-item
                          :label="field.label"
                          :prop="field.name"
                          :required="field.required"
                          class="custom-form-item"
                        >
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
                              :disabled="option.disabled"
                            >
                              {{ option.statusLabel || option.label }}
                            </el-option>
                          </el-select>
                          <div
                            v-if="field.help_text"
                            class="help-text"
                          >
                            {{ field.help_text }}
                          </div>
                        </el-form-item>
                      </el-col>

                      <el-col
                        v-else-if="field.type === 'textarea'"
                        :span="field.fullWidth ? 24 : 12"
                      >
                        <el-form-item
                          :label="field.label"
                          :prop="field.name"
                          :required="field.required"
                          class="custom-form-item"
                        >
                          <el-input
                            v-model="formData[field.name]"
                            type="textarea"
                            :placeholder="field.placeholder"
                            :rows="field.rows || 4"
                            resize="none"
                            class="custom-textarea"
                          />
                          <div
                            v-if="field.help_text"
                            class="help-text"
                          >
                            {{ field.help_text }}
                          </div>
                        </el-form-item>
                      </el-col>
                    </template>
                  </el-row>

                  <div class="form-actions">
                    <el-button
                      class="submit-btn-unified"
                      type="primary"
                      :loading="submitting"
                      @click="handleSubmit"
                    >
                      {{ submitting ? '正在保存...' : '保存修改' }}
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
import { useRoute } from 'vue-router'
import { useApi } from '@/core/hooks'
import { showError, showSuccess } from '@/core/utils/errorHandler'
import { useNavigation } from '@/core/utils/routeDecision'
import Index from '@/views/pc/dashboard/Index.vue'
import { InfoFilled, EditPen, Warning } from '@element-plus/icons-vue'
import { formatLabOption } from '@/core/config/entityFields'

const route = useRoute()
const { goHome, smartBack } = useNavigation()
const apiComposable = useApi('', { immediate: false })

const header = ref('编辑课表')
const formFields = ref([])
const formData = ref({})
const loading = ref(false)
const submitting = ref(false)
const message = ref('')
const messageType = ref('')

const WEEKDAY_OPTIONS = [
  { value: 1, label: '周一' },
  { value: 2, label: '周二' },
  { value: 3, label: '周三' },
  { value: 4, label: '周四' },
  { value: 5, label: '周五' },
  { value: 6, label: '周六' },
  { value: 7, label: '周日' }
]

const loadData = async () => {
  loading.value = true
  try {
    const scheduleId = route.params.id

    const [scheduleResponse, formOptionsResponse] = await Promise.all([
      apiComposable.get({}, { url: `/schedules/${scheduleId}/` }),
      apiComposable.get({}, { url: '/schedules/form_options/', cache: false })
    ])

    const data = scheduleResponse.data || scheduleResponse
    const optionsData = formOptionsResponse.data || formOptionsResponse

    header.value = data.header || '编辑课表'

    const teachers = optionsData.teachers || []
    const laboratories = optionsData.laboratories || []

    const teacherOptions = teachers.map(t => ({
      value: t.id,
      label: t.nickname || t.username || `教师${t.id}`
    }))

    const labOptions = laboratories.map(formatLabOption)

    const formDataRaw = data.form_data || data

    formFields.value = [
      {
        name: 'laboratory_id',
        type: 'select',
        label: '实训室',
        required: true,
        options: labOptions.length > 0 ? labOptions : [formatLabOption({ id: formDataRaw.laboratory_id, name: formDataRaw.laboratory_name || '未知实训室' })]
      },
      {
        name: 'course_name',
        type: 'text',
        label: '课程名称',
        required: true,
        placeholder: '请输入课程名称'
      },
      {
        name: 'weekday',
        type: 'select',
        label: '星期',
        required: true,
        options: WEEKDAY_OPTIONS
      },
      {
        name: 'time_slot',
        type: 'select',
        label: '节次',
        required: true,
        options: [
          { value: '1-2', label: '1-2节（上午第1-2节）' },
          { value: '3-4', label: '3-4节（上午第3-4节）' },
          { value: '5-6', label: '5-6节（下午第1-2节）' },
          { value: '7-8', label: '7-8节（下午第3-4节）' },
          { value: '9-10', label: '9-10节（晚上）' },
          { value: '1-4', label: '1-4节（上午连课）' },
          { value: '5-8', label: '5-8节（下午连课）' },
          { value: '1-6', label: '1-6节（全天）' },
          { value: '1-8', label: '1-8节（全天含晚自习）' }
        ]
      },
      {
        name: 'weeks',
        type: 'text',
        label: '周次',
        placeholder: '如：1-18'
      },
      {
        name: 'student_count',
        type: 'number',
        label: '人数',
        placeholder: '请输入人数'
      },
      {
        name: 'class_name',
        type: 'text',
        label: '上课班级',
        placeholder: '请输入上课班级'
      },
      {
        name: 'teacher_id',
        type: 'select',
        label: '任课教师',
        required: false,
        options: teacherOptions.length > 0 ? teacherOptions : [{ value: formDataRaw.teacher_id, label: formDataRaw.teacher_name || '未分配' }]
      },
      {
        name: 'note',
        type: 'textarea',
        label: '备注',
        fullWidth: true,
        placeholder: '请输入备注'
      }
    ]

    formData.value = {
      laboratory_id: formDataRaw.laboratory_id || '',
      course_name: formDataRaw.course_name || '',
      weekday: formDataRaw.weekday || 1,
      time_slot: formDataRaw.time_slot || '1-4',
      weeks: formDataRaw.weeks || '1-18',
      student_count: formDataRaw.student_count || 20,
      class_name: formDataRaw.class_name || '',
      teacher_id: formDataRaw.teacher_id || '',
      note: formDataRaw.note || ''
    }

  } catch (err) {
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
    const scheduleId = route.params.id
    const submitData = { ...formData.value }
    const response = await apiComposable.put(submitData, { url: `/schedules/${scheduleId}/` })

    if (response.success) {
      message.value = '修改成功'
      messageType.value = 'success'
      showSuccess('修改成功')
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
