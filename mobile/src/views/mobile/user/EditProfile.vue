<template>
  <div class="mobile-page">
    <van-nav-bar title="修改个人信息" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-skeleton v-if="loading" :row="5" animated />

      <van-form v-else @submit="handleSubmit">
        <van-cell-group inset title="账户信息">
          <van-field
            v-model="formData.username"
            label="用户名"
            readonly
          />
        </van-cell-group>

        <van-cell-group inset title="个人信息">
          <van-field
            v-model="formData.nikename"
            label="昵称"
            placeholder="请输入昵称"
            clearable
            :rules="[{ required: true, message: '请输入昵称' }]"
          />

          <van-field
            v-model="formData.email"
            type="email"
            label="邮箱"
            placeholder="请输入邮箱"
            required
            clearable
            :rules="emailRules"
          />

          <van-field
            v-model="formData.phone"
            type="tel"
            label="手机号"
            placeholder="请输入手机号"
            clearable
            :rules="phoneRules"
          />
        </van-cell-group>

        <van-cell-group inset title="其他信息">
          <van-field
            v-model="formData.memo"
            rows="3"
            autosize
            type="textarea"
            label="备注"
            placeholder="请输入备注"
          />
        </van-cell-group>

        <div class="form-actions">
          <van-button type="primary" block round :loading="submitting" native-type="submit">
            保存修改
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNavigation } from '@/utils/routeDecision'
import { useAuth } from '@/composables/useAuth'
import { useApi } from '@/composables/useApi'
import { showSuccess, showError } from '@/utils/errorHandler'

const router = useRouter()
const { goHome, smartBack } = useNavigation()
const { user, updateUser } = useAuth()

const loading = ref(false)
const submitting = ref(false)

const emailRules = [
  { required: true, message: '请输入邮箱' },
  { pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: '请输入正确的邮箱格式（必须包含@）' }
]

const phoneRules = [
  { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的11位手机号码' }
]

const formData = ref({
  username: '',
  nikename: '',
  email: '',
  phone: '',
  memo: ''
})

const loadUserData = async () => {
  loading.value = true
  
  if (user.value) {
    formData.value = {
      username: user.value.username || '',
      nikename: user.value.nikename || '',
      email: user.value.email || '',
      phone: user.value.phone || '',
      memo: user.value.memo || ''
    }
  }
  
  try {
    const apiComposable = useApi('', { immediate: false })
    const response = await apiComposable.get({}, { url: '/userinfo/update_userinfo/' })
    
    if (response) {
      const userData = response.user || response
      formData.value = {
        username: userData.username || user.value?.username || '',
        nikename: userData.nikename || '',
        email: userData.email || '',
        phone: userData.phone || '',
        memo: userData.memo || ''
      }
    }
  } catch (err) {
    console.error('加载用户信息失败:', err)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  submitting.value = true
  
  try {
    const submitData = {
      nikename: formData.value.nikename,
      email: formData.value.email,
      phone: formData.value.phone,
      memo: formData.value.memo
    }
    
    const apiComposable = useApi('', { immediate: false })
    const response = await apiComposable.post(submitData, { url: '/userinfo/update_userinfo/' })
    
    if (response && response.success) {
      showSuccess('保存成功')
      const updatedUser = { ...user.value, ...formData.value }
      updateUser(updatedUser)
      setTimeout(() => {
        smartBack()
      }, 1500)
    } else {
      showError(response?.message || '保存失败')
    }
  } catch (err) {
    showError(err.response?.data?.message || '保存失败')
  } finally {
    submitting.value = false
  }
}

const goBack = () => router.go(-1)

onMounted(() => {
  loadUserData()
})
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
