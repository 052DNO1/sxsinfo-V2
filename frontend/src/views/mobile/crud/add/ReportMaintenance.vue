<template>
  <div class="mobile-page">
    <van-nav-bar
      title="设备故障上报"
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
      <div class="form-hero form-hero--danger">
        <div class="form-hero-icon">
          <van-icon
            name="warning-o"
            size="28"
          />
        </div>
        <h2>故障上报</h2>
        <p>提交后将立即通知管理员处理</p>
      </div>

      <van-skeleton
        v-if="isLoading"
        :row="5"
        animated
      />

      <template v-else>
        <div class="form-section animate-fade-in-up animate-delay-1">
          <div class="section-label">
            <span>⚠️</span> 故障信息
          </div>
          <van-cell-group inset>
            <van-field
              v-model="formData.laboratoryText"
              is-link
              readonly
              label="实训室"
              placeholder="请选择实训室"
              required
              @click="openSxsPicker"
            />
            <van-field
              v-model="formData.device_code"
              label="设备编号"
              placeholder="请输入设备编号 (如: 01)"
              required
              clearable
            />
            <van-field
              v-model="formData.reporter"
              label="上报人"
              placeholder="请输入上报人姓名"
              required
              clearable
            />
            <van-field
              v-model="formData.maintenance_time"
              is-link
              readonly
              label="上报时间"
              placeholder="请选择日期"
              required
              @click="showDatePicker = true"
            />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-2">
          <div class="section-label">
            <span>📋</span> 故障描述
          </div>
          <van-cell-group inset>
            <van-field
              v-model="formData.description"
              rows="4"
              autosize
              type="textarea"
              label="故障描述"
              placeholder="请详细描述设备故障情况"
              required
              show-word-limit
              :maxlength="500"
            />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-3">
          <div class="section-label">
            <span>🔥</span> 优先级
          </div>
          <van-cell-group inset>
            <van-field
              v-model="priorityText"
              is-link
              readonly
              label="优先级"
              placeholder="请选择优先级"
              @click="showPriorityPicker = true"
            />
          </van-cell-group>
        </div>
      </template>

      <div class="form-actions">
        <van-button
          type="primary"
          block
          round
          size="large"
          :loading="loading"
          icon="success"
          @click="handleSubmit"
        >
          立即提交
        </van-button>
      </div>
    </div>

    <van-popup
      v-model:show="showSxsPicker"
      position="bottom"
      round
    >
      <van-picker
        title="选择实训室"
        :columns="sxsOptions"
        @confirm="onSxsConfirm"
        @cancel="showSxsPicker = false"
      />
    </van-popup>
    <van-popup
      v-model:show="showDatePicker"
      position="bottom"
      round
    >
      <van-date-picker
        v-model="selectedDate"
        title="选择上报时间"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>
    <van-popup
      v-model:show="showPriorityPicker"
      position="bottom"
      round
    >
      <van-picker
        title="选择优先级"
        :columns="priorityOptions"
        @confirm="onPriorityConfirm"
        @cancel="showPriorityPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { workOrderService, labService } from '@/core/services/BaseService'
import { useAuth } from '@/core/hooks'
import { useNavigation } from '@/core/utils/routeDecision'
import { showSuccess, showError } from '@/core/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { user } = useAuth()
const { goHome, smartBack } = useNavigation()

const loading = ref(false)
const isLoading = ref(true)
const showSxsPicker = ref(false)
const showDatePicker = ref(false)
const showPriorityPicker = ref(false)
const sxsList = ref([])
const selectedDate = ref(['2024', '01', '01'])

const formData = ref({
  laboratory_id: '', laboratoryText: '', device_code: '', reporter: '',
  maintenance_time: '', description: '', priority: 2, maintenance_type: 3
})

const sxsOptions = computed(() => sxsList.value.map(sxs => ({
  text: `${sxs.code || ''} ${sxs.name || sxs.laboratory_name}`.trim(), value: sxs.id
})))

const priorityOptions = [
  { text: '低', value: 1 }, { text: '中', value: 2 },
  { text: '高', value: 3 }, { text: '紧急', value: 4 }
]

const priorityText = computed(() => priorityOptions.find(o => o.value === formData.value.priority)?.text || '中')

const openSxsPicker = () => { showSxsPicker.value = true }

const onSxsConfirm = ({ selectedOptions }) => {
  const s = selectedOptions[0]
  formData.value.laboratory_id = s.value
  formData.value.laboratoryText = s.text
  showSxsPicker.value = false
}

const onDateConfirm = ({ selectedValues }) => { formData.value.maintenance_time = selectedValues.join('-'); showDatePicker.value = false }
const onPriorityConfirm = ({ selectedOptions }) => { formData.value.priority = selectedOptions[0].value; showPriorityPicker.value = false }

const loadFormData = async () => {
  isLoading.value = true
  try {
    const response = await labService.getOptions({ force_all: 'true' })
    if (response && response.success && response.data && response.data.options) {
      sxsList.value = response.data.options.filter(opt => opt.id !== '').map(opt => ({
        id: opt.id,
        name: opt.name || opt.text || '',
        code: opt.code || '',
        room_number: opt.room_number || ''
      }))
      formData.value.reporter = user.value?.nickname || user.value?.nikename || user.value?.username || ''
      formData.value.maintenance_time = new Date().toISOString().split('T')[0]
      
      if (route.query?.from_record === 'true') {
        if (route.query.maintainrequestdate) formData.value.maintenance_time = route.query.maintainrequestdate
        if (route.query.sxsid && route.query.sxsid !== '0') {
          formData.value.laboratory_id = parseInt(route.query.sxsid)
          const sxs = sxsList.value.find(s => s.id === parseInt(route.query.sxsid))
          if (sxs) formData.value.laboratoryText = `${sxs.code || ''} ${sxs.name}`.trim()
        }
      }
    }
  } catch (err) { showError('加载表单失败') }
  finally { isLoading.value = false }
}

const handleSubmit = async () => {
  if (!formData.value.laboratory_id) { showError('请选择实训室'); return }
  if (!formData.value.device_code) { showError('请输入设备编号'); return }
  if (!formData.value.reporter) { showError('请输入上报人'); return }
  if (!formData.value.maintenance_time) { showError('请选择上报时间'); return }
  if (!formData.value.description) { showError('请填写故障描述'); return }
  
  loading.value = true
  try {
    const title = `设备故障上报 - ${formData.value.device_code}`
    await workOrderService.create({
      title,
      laboratory_id: formData.value.laboratory_id,
      description: `[设备编号:${formData.value.device_code}] ${formData.value.description}`,
      maintenance_type: formData.value.maintenance_type,
      priority: formData.value.priority
    })
    showSuccess('故障上报成功！已通知管理员')
    setTimeout(() => router.push('/'), 1500)
  } catch (err) { showError(err.message || '上报失败') }
  finally { loading.value = false }
}

const goBack = () => router.go(-1)

onMounted(() => {
  const today = new Date()
  selectedDate.value = [String(today.getFullYear()), String(today.getMonth() + 1).padStart(2, '0'), String(today.getDate()).padStart(2, '0')]
  loadFormData()
})
</script>

<style scoped>
.form-hero--danger { background: #FFEBE9; }
.form-hero { background: #F7F8FA; padding: 28px 20px; margin: -12px -16px 20px; text-align: center; border-radius: 0 0 16px 16px; }
.form-hero-icon { width: 60px; height: 60px; border-radius: 50%; background: #FFEBE9; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; color: #FF3B30; }
.form-hero h2 { margin: 0 0 6px; font-size: 20px; font-weight: 700; color: #1A1A1A; }
.form-hero p { margin: 0; font-size: 13px; color: rgba(255,255,255,0.8); }
.form-section { margin-bottom: 8px; }
.section-label { display: flex; align-items: center; gap: 8px; padding: 10px 16px 6px; font-size: 13px; font-weight: 600; color: var(--mobile-text-secondary); }
.section-label span { font-size: 16px; }
</style>