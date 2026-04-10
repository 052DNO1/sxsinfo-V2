<!-- 新增实训室 -->
<template>
  <FormLayout
    title="添加数据"
    icon="Plus"
    :loading="loading"
    guide-title="操作指南"
    guide-sub-title="请按照提示填写实训室信息"
    :guide-steps="guideSteps"
    :tips="tips"
    :main-title="header || '填写信息'"
    :main-icon="OfficeBuilding"
  >
    <template #header-center>
      <el-radio-group v-model="activeTab" @change="handleTabChange">
        <el-radio-button value="lab">添加实训室</el-radio-button>
        <el-radio-button value="device">添加设备</el-radio-button>
        <el-radio-button value="class">添加课表</el-radio-button>
      </el-radio-group>
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
            </el-form-item>
          </el-col>

          <el-col :span="12" v-else-if="field.type === 'select'">
            <el-form-item :label="field.label" :prop="field.name" :required="field.required" :error="fieldErrors[field.name]" class="custom-form-item">
              <el-select
                v-model="formData[field.name]"
                :placeholder="field.placeholder || '请选择'"
                style="width: 100%"
                clearable
                filterable
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
                />
              </el-select>
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
import { useAuth, useApi } from '@/core/hooks'
import { iconMap as Icons } from '@/core/config/icons'
import { OfficeBuilding } from '@element-plus/icons-vue'
import { getSxsFields } from '@/core/config/entityFields'
import { showSuccess, showError } from '@/core/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { user } = useAuth()
const { smartBack } = useNavigation()
const api = useApi('', { immediate: false })

const activeTab = ref('lab')
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
  { title: '基本信息', description: '填写实训室名称、编号及工位数' },
  { title: '人员分配', description: '指定实训室管理员（可选）' },
  { title: '确认提交', description: '核对信息无误后点击提交按钮' }
]

const tips = [
  '实训室名称和编号在系统中必须唯一',
  '工位数请填写入实际可用座位数',
  '管理员需为系统中已存在的用户',
  '如需批量添加，请使用"导入实训室"功能'  
]

const loadData = async () => {
  loading.value = true
  try {
    const res = await api.get({ nopage: 1, role: 2 }, { url: '/users/' })
    const admins = res?.data?.list || res?.list || []
    
    const adminChoices = admins.map(a => ({
      value: a.id,
      label: `${a.nickname || a.username} (${a.username})`
    }))
    
    const statusChoices = [
      { value: 1, label: '可用' },
      { value: 2, label: '维护中' },
      { value: 3, label: '不可用' }
    ]
    
    formFields.value = getSxsFields({
      admin_options: adminChoices,
      status_choices: statusChoices
    })
    
    formFields.value.forEach(f => {
      formData[f.name] = f.default ?? ''
    })
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
        const submitData = { ...formData }
        if (user.value?.department_id) {
          submitData.department = user.value.department_id
        }
        
        const response = await api.post(submitData, { url: '/laboratories/' })
        
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
  if (val === 'device') {
    router.push('/add-device')
  } else if (val === 'class') {
    router.push('/addclass')
  }
}

watch(() => user.value, (newUser) => {
  if (newUser && !newUser.is_superuser && !newUser.is_departadmin) {
    router.replace('/add-device')
  }
}, { immediate: true })

onMounted(() => {
  if (user.value && !user.value.is_superuser && !user.value.is_departadmin) {
    router.replace('/add-device')
    return
  }
  loadData()
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
