<template>
  <div class="mobile-page">
    <van-nav-bar title="添加学期" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-notice-bar left-icon="warning-o" color="#ff976a" background="#fffbe8">
        请仔细确认学期起止时间，如果这是新的当前学期，系统将自动把旧的当前学期（如果存在）设为非当前状态。
      </van-notice-bar>

      <van-cell-group inset title="基本信息">
        <van-field
          v-model="formData.termname"
          label="学期名称"
          placeholder="如：2024-2025第一学期"
          required
          clearable
        />
        
        <van-field
          v-model="formData.startdate"
          is-link
          readonly
          label="开始日期"
          placeholder="请选择开始日期"
          @click="showStartPicker = true"
          required
        />
        
        <van-field
          v-model="formData.enddate"
          is-link
          readonly
          label="结束日期"
          placeholder="请选择结束日期"
          @click="showEndPicker = true"
          required
        />
      </van-cell-group>

      <van-cell-group inset title="状态设置">
        <van-cell title="设为当前学期">
          <template #right-icon>
            <van-switch v-model="formData.iscurrent" />
          </template>
        </van-cell>
      </van-cell-group>

      <div class="form-actions">
        <van-button type="primary" block round :loading="submitting" @click="handleSubmit">
          立即创建
        </van-button>
      </div>
    </div>

    <van-popup v-model:show="showStartPicker" position="bottom" round>
      <van-date-picker
        title="选择开始日期"
        v-model="selectedStartDate"
        @confirm="onStartConfirm"
        @cancel="showStartPicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showEndPicker" position="bottom" round>
      <van-date-picker
        title="选择结束日期"
        v-model="selectedEndDate"
        @confirm="onEndConfirm"
        @cancel="showEndPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/utils/routeDecision'
import { useApi } from '@/composables/useApi'
import { useAppStore } from '@/stores/app'
import { showSuccess, showError } from '@/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()
const appStore = useAppStore()

const submitting = ref(false)
const showStartPicker = ref(false)
const showEndPicker = ref(false)

const today = new Date()
const selectedStartDate = ref([
  String(today.getFullYear()),
  String(today.getMonth() + 1).padStart(2, '0'),
  String(today.getDate()).padStart(2, '0')
])
const selectedEndDate = ref([
  String(today.getFullYear()),
  String(today.getMonth() + 6).padStart(2, '0'),
  String(today.getDate()).padStart(2, '0')
])

const formData = ref({
  termname: '',
  startdate: '',
  enddate: '',
  iscurrent: false
})

const onStartConfirm = ({ selectedValues }) => {
  formData.value.startdate = selectedValues.join('-')
  showStartPicker.value = false
}

const onEndConfirm = ({ selectedValues }) => {
  formData.value.enddate = selectedValues.join('-')
  showEndPicker.value = false
}

const handleSubmit = async () => {
  if (!formData.value.termname) {
    showError('请输入学期名称')
    return
  }
  if (!formData.value.startdate) {
    showError('请选择开始日期')
    return
  }
  if (!formData.value.enddate) {
    showError('请选择结束日期')
    return
  }
  
  submitting.value = true
  
  try {
    const submitData = {
      termname: formData.value.termname,
      startdate: formData.value.startdate,
      enddate: formData.value.enddate,
      iscurrent: formData.value.iscurrent
    }
    
    const apiComposable = useApi('', { immediate: false })
    const response = await apiComposable.post(submitData, { url: '/userinfo/addterm/' })
    
    if (response && response.success) {
      if (formData.value.iscurrent) {
        appStore.triggerTermRefresh()
      }
      showSuccess('学期创建成功')
      setTimeout(() => {
        smartBack()
      }, 1500)
    } else {
      showError(response?.message || '创建失败')
    }
  } catch (err) {
    showError(err.response?.data?.message || '创建失败')
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.mobile-page {
  min-height: 100vh;
  background: #f7f8fa;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  padding-bottom: 100px;
}

.form-actions {
  padding: 16px;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}
</style>
