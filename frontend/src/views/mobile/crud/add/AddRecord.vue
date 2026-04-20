<template>
  <div class="mobile-page">
    <van-nav-bar title="添加使用记录" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" color="#4F6EF7" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <div class="form-hero form-hero--green">
        <div class="form-hero-icon"><van-icon name="notes-o" size="28" /></div>
        <h2>使用记录</h2>
        <p>记录实训室使用情况</p>
      </div>

      <van-form @submit="handleSubmit">
        <div class="form-section animate-fade-in-up animate-delay-1">
          <div class="section-label"><span>🏫</span> 实训室与时间</div>
          <van-cell-group inset>
            <van-field v-model="formData.laboratoryText" is-link readonly label="实训室" placeholder="请选择实训室" required @click="showSxsPicker = true" />
            <van-field v-model="formData.usage_date" is-link readonly label="使用日期" placeholder="请选择日期" required @click="showDatePicker = true" />
            <van-field v-model="formData.time_slot" label="时间段" placeholder="如: 08:00-10:00 或 1-2节" required />
            <van-field v-model="formData.student_count" type="number" label="使用人数" placeholder="请输入使用人数" required />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-2">
          <div class="section-label"><span>💻</span> 设备状态</div>
          <van-cell-group inset>
            <van-field v-model="deviceStatusText" is-link readonly label="设备状态" placeholder="请选择设备状态" required @click="showStatusPicker = true" />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-3">
          <div class="section-label"><span>📝</span> 详细描述</div>
          <van-cell-group inset>
            <van-field v-model="formData.content" rows="3" autosize type="textarea" label="使用内容" placeholder="请输入使用内容描述" />
            <van-field v-model="formData.note" rows="2" autosize type="textarea" label="备注" placeholder="请输入备注信息" />
          </van-cell-group>
        </div>

        <div class="form-tips">
          <van-notice-bar left-icon="info-o" color="#1989fa" background="#ecf9ff">请如实填写设备状态，如设备故障将自动跳转上报</van-notice-bar>
        </div>

        <div class="form-actions">
          <van-button type="primary" block round size="large" :loading="loading" @click="handleSubmit" icon="success">提交记录</van-button>
        </div>
      </van-form>
    </div>

    <van-popup v-model:show="showSxsPicker" position="bottom" round><van-picker title="选择实训室" :columns="sxsOptions" @confirm="onSxsConfirm" @cancel="showSxsPicker = false" /></van-popup>
    <van-popup v-model:show="showDatePicker" position="bottom" round><van-date-picker title="选择日期" v-model="selectedDate" @confirm="onDateConfirm" @cancel="showDatePicker = false" /></van-popup>
    <van-popup v-model:show="showStatusPicker" position="bottom" round><van-picker title="选择设备状态" :columns="statusOptions" @confirm="onStatusConfirm" @cancel="showStatusPicker = false" /></van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { recordService, labService } from '@/core/services/BaseService'
import { showSuccess, showError, showWarning } from '@/core/utils/errorHandler'
import { useNavigation } from '@/core/utils/routeDecision'

const route = useRoute()
const router = useRouter()
const { goHome, goBack, smartBack } = useNavigation()

const loading = ref(false)
const showSxsPicker = ref(false)
const showDatePicker = ref(false)
const showStatusPicker = ref(false)
const sxsList = ref([])
const selectedDate = ref(['2024', '01', '01'])

const formData = ref({ laboratory_id: '', laboratoryText: '', usage_date: '', time_slot: '', student_count: '', device_status: 'NORMAL', content: '', note: '' })

const sxsOptions = computed(() => sxsList.value.map(item => ({ text: `${item.code || ''} ${item.name || item.laboratory_name}`.trim(), value: item.id })))
const statusOptions = [{ text: '正常', value: 'NORMAL' }, { text: '异常/故障', value: 'FAULTY' }]
const deviceStatusText = computed(() => statusOptions.find(o => o.value === formData.value.device_status)?.text || '正常')

const onSxsConfirm = ({ selectedOptions }) => { const s = selectedOptions[0]; formData.value.laboratory_id = s.value; formData.value.laboratoryText = s.text; showSxsPicker.value = false }
const onDateConfirm = ({ selectedValues }) => { formData.value.usage_date = selectedValues.join('-'); showDatePicker.value = false }
const onStatusConfirm = ({ selectedOptions }) => { formData.value.device_status = selectedOptions[0].value; showStatusPicker.value = false }

const handleSubmit = async () => {
  if (!formData.value.laboratory_id) { showError('请选择实训室'); return }
  if (!formData.value.usage_date) { showError('请选择使用日期'); return }
  if (!formData.value.student_count) { showError('请输入使用人数'); return }
  
  loading.value = true
  try {
    await recordService.create({ laboratory_id: formData.value.laboratory_id, usage_date: formData.value.usage_date, time_slot: formData.value.time_slot, student_count: parseInt(formData.value.student_count), device_status: formData.value.device_status, content: formData.value.content, note: formData.value.note })
    
    if (formData.value.device_status === 'FAULTY') {
      showSuccess('记录创建成功，正在跳转到故障上报...')
      setTimeout(() => router.push({ path: '/report-maintenance', query: { sxsid: formData.value.laboratory_id, maintainrequestdate: formData.value.usage_date } }), 500)
      return
    }
    
    showSuccess('记录创建成功')
    setTimeout(() => router.push('/'), 1500)
  } catch (err) { showError(err.message || '创建失败') }
  finally { loading.value = false }
}

const loadSxsList = async () => {
  try {
    const res = await labService.getOptions({ force_all: 'true' })
    if (res && res.success && res.data && res.data.options) {
      sxsList.value = res.data.options.filter(opt => opt.id !== '').map(opt => ({
        id: opt.id,
        code: opt.code || '',
        name: opt.name || opt.text || '',
        laboratory_name: opt.name || opt.text || ''
      }))
    }
  } catch (e) {
    console.error('Failed to load sxs list', e)
  }
}

watch(() => formData.value.device_status, async (newVal) => {
  if (newVal === 'FAULTY') {
    await showWarning('您选择了设备状态为【异常/故障】，系统将自动跳转至故障上报页面')
    router.push({ path: '/report-maintenance', query: { sxsid: formData.value.laboratory_id, maintainrequestdate: formData.value.usage_date } })
  }
})

onMounted(() => {
  loadSxsList()
  const today = new Date()
  selectedDate.value = [String(today.getFullYear()), String(today.getMonth() + 1).padStart(2, '0'), String(today.getDate()).padStart(2, '0')]
  formData.value.usage_date = selectedDate.value.join('-')
  if (route.query.sxsid) formData.value.laboratory_id = parseInt(route.query.sxsid)
})
</script>

<style scoped>
.form-hero { background: #F7F8FA; padding: 28px 20px; margin: -12px -16px 20px; text-align: center; border-radius: 0 0 16px 16px; }
.form-hero--green { background: #E8F8EE; }
.form-hero-icon { width: 60px; height: 60px; border-radius: 50%; background: #E8F8EE; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; color: #07C160; }
.form-hero h2 { margin: 0 0 6px; font-size: 20px; font-weight: 700; color: #1A1A1A; }
.form-hero p { margin: 0; font-size: 13px; color: #666666; }
.form-section { margin-bottom: 8px; }
.section-label { display: flex; align-items: center; gap: 8px; padding: 10px 16px 6px; font-size: 13px; font-weight: 600; color: var(--mobile-text-secondary); }
.section-label span { font-size: 16px; }
.form-tips { margin: 12px 0; }
</style>