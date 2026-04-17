<template>
  <div class="mobile-page">
    <van-nav-bar title="添加分院" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-notice-bar left-icon="info-o" color="#1989fa" background="#ecf9ff">
        请填写分院基本信息，带 * 为必填项
      </van-notice-bar>

      <van-cell-group inset title="基本信息">
        <van-field
          v-model="formData.departname"
          label="分院名称"
          placeholder="请输入分院名称"
          required
          clearable
        />
      </van-cell-group>

      <van-cell-group inset title="其他信息">
        <van-field
          v-model="formData.departdemo"
          rows="3"
          autosize
          type="textarea"
          label="分院描述"
          placeholder="请输入分院描述"
        />
      </van-cell-group>

      <div class="form-actions">
        <van-button type="primary" block round :loading="submitting" @click="handleSubmit">
          立即创建
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/utils/routeDecision'
import { useApi } from '@/composables/useApi'
import { showSuccess, showError } from '@/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()

const submitting = ref(false)

const formData = ref({
  departname: '',
  departdemo: ''
})

const handleSubmit = async () => {
  if (!formData.value.departname) {
    showError('请输入分院名称')
    return
  }
  
  submitting.value = true
  
  try {
    const submitData = {
      departname: formData.value.departname,
      departdemo: formData.value.departdemo
    }
    
    const apiComposable = useApi('', { immediate: false })
    const response = await apiComposable.post(submitData, { url: '/userinfo/adddept/' })
    
    if (response && response.success) {
      showSuccess('分院创建成功')
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
