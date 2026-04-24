<template>
  <div class="mobile-page">
    <van-nav-bar title="添加维护记录" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" color="#4F6EF7" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <div class="form-hero form-hero--warm">
        <div class="form-hero-icon"><van-icon name="setting-o" size="28" /></div>
        <h2>维护记录</h2>
        <p>记录设备维护与保养</p>
      </div>

      <van-form @submit="onSubmit">
        <div class="form-section animate-fade-in-up animate-delay-1">
          <div class="section-label"><span>🏫</span> 基本信息</div>
          <van-cell-group inset>
            <van-field v-model="formData.laboratoryText" is-link readonly label="实训室" placeholder="请选择实训室" required @click="showLabPicker = true" :rules="[{ required: true, message: '请选择实训室' }]" />
            <van-field v-model="formData.maintenance_date" label="维护日期" type="date" placeholder="请选择维护日期" :rules="[{ required: true, message: '请选择维护日期' }]" />
            <van-field v-model="maintenanceTypeText" is-link readonly label="维护类型" placeholder="请选择维护类型" required @click="showTypePicker = true" :rules="[{ required: true, message: '请选择维护类型' }]" />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-2">
          <div class="section-label"><span>📝</span> 维护详情</div>
          <van-cell-group inset>
            <van-field v-model="formData.description" type="textarea" label="维护内容/描述" placeholder="请输入维护内容描述" rows="4" show-word-limit :maxlength="500" :rules="[{ required: true, message: '请输入维护内容' }]" />
          </van-cell-group>
        </div>

        <div class="form-actions">
          <van-button type="primary" block round size="large" native-type="submit" :loading="loading" icon="success">提交</van-button>
        </div>
      </van-form>
    </div>

    <van-popup v-model:show="showLabPicker" position="bottom" round><van-picker title="选择实训室" :columns="labOptions" @confirm="onLabConfirm" @cancel="showLabPicker = false" /></van-popup>
    <van-popup v-model:show="showTypePicker" position="bottom" round><van-picker title="选择维护类型" :columns="typeOptions" @confirm="onTypeConfirm" @cancel="showTypePicker = false" /></van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { workOrderService, labService } from '@/core/services/BaseService'
import { useNavigation } from '@/core/utils/routeDecision'
import { showSuccessToast, showFailToast } from 'vant'

const router = useRouter()
const route = useRoute()
const { goHome, smartBack } = useNavigation()

const loading = ref(false)
const showLabPicker = ref(false)
const showTypePicker = ref(false)
const formData = ref({ laboratory_id: '', laboratoryText: '', maintenance_date: '', maintenance_type: 1, description: '' })
const labList = ref([])

const labOptions = computed(() => labList.value.map(lab => ({ text: `${lab.code || ''} ${lab.name || lab.laboratory_name}`.trim(), value: lab.id })))
const typeOptions = [{ text: '日常维护', value: 1 }, { text: '定期保养', value: 2 }, { text: '故障维修', value: 3 }, { text: '设备升级', value: 4 }]
const maintenanceTypeText = computed(() => typeOptions.find(o => o.value === formData.value.maintenance_type)?.text || '日常维护')

const loadLabList = async () => {
  try {
    const response = await labService.list({ nopage: true })
    if (response && response.list) labList.value = response.list
  } catch (err) { console.error('Load lab list error:', err) }
}

const onLabConfirm = ({ selectedOptions }) => { formData.value.laboratory_id = selectedOptions[0].value; formData.value.laboratoryText = selectedOptions[0].text; showLabPicker.value = false }
const onTypeConfirm = ({ selectedOptions }) => { formData.value.maintenance_type = selectedOptions[0].value; showTypePicker.value = false }

const onSubmit = async () => {
  if (!formData.value.laboratory_id) { showToast('请选择实训室'); return }
  try {
    loading.value = true
    const title = formData.value.description.substring(0, 50) || '维护记录'
    await workOrderService.create({ title, laboratory_id: formData.value.laboratory_id, maintenance_type: formData.value.maintenance_type, description: formData.value.description })
    showSuccessToast('添加成功')
    setTimeout(() => smartBack(), 1000)
  } catch (err) { console.error('Submit error:', err); showFailToast(err.message || '添加失败') }
  finally { loading.value = false }
}
const goBack = () => router.go(-1)

onMounted(() => {
  loadLabList()
  if (route.query.laboratory_id) formData.value.laboratory_id = parseInt(route.query.laboratory_id)
})
</script>

<style scoped>
.form-hero { background: #F7F8FA; padding: 28px 20px; margin: -12px -16px 20px; text-align: center; border-radius: 0 0 16px 16px; }
.form-hero-icon { width: 60px; height: 60px; border-radius: 50%; background: #FFF5E6; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; color: #FF9500; }
.form-hero h2 { margin: 0 0 6px; font-size: 20px; font-weight: 700; color: #1A1A1A; }
.form-hero p { margin: 0; font-size: 13px; color: rgba(255,255,255,0.8); }
.form-section { margin-bottom: 8px; }
.section-label { display: flex; align-items: center; gap: 8px; padding: 10px 16px 6px; font-size: 13px; font-weight: 600; color: var(--mobile-text-secondary); }
.section-label span { font-size: 16px; }
</style>