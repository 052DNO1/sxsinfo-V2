<template>
  <!-- 移动端直接显示内容 -->
  <div class="mobile-password-container mobile-layout">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      title="修改密码"
      left-arrow
      @click-left="goBack"
      class="mobile-nav-bar"
    />

    <!-- 表单 -->
    <van-form @submit="handleSubmitMobile" style="padding: 16px;">
      <van-cell-group inset>
        <van-field
          v-model="formData.old_pwd"
          type="password"
          name="old_pwd"
          label="当前密码"
          placeholder="请输入当前密码"
          :rules="[{ required: true, message: '请填写当前密码' }]"
          :right-icon="showOldPassword ? 'eye-o' : 'closed-eye'"
          @click-right-icon="togglePasswordVisibility('old_pwd')"
        />
        <div v-if="errors.old_pwd" style="padding: 8px 16px; color: #ee0a24; font-size: 12px;">
          {{ errors.old_pwd }}
        </div>

        <van-field
          v-model="formData.new_pwd"
          :type="showNewPassword ? 'text' : 'password'"
          name="new_pwd"
          label="新密码"
          placeholder="请输入新密码"
          :rules="[{ required: true, message: '请填写新密码' }]"
          :right-icon="showNewPassword ? 'eye-o' : 'closed-eye'"
          @click-right-icon="togglePasswordVisibility('new_pwd')"
          @input="checkPasswordRequirements"
        />
        
        <!-- 密码要求 -->
        <van-cell-group style="margin-top: 8px;">
          <van-cell title="密码要求" />
          <van-cell>
            <template #title>
              <div style="display: flex; align-items: center; gap: 8px;">
                <van-icon :name="requirements.length ? 'success' : 'cross'" :color="requirements.length ? '#07c160' : '#ee0a24'" />
                <span :style="{ color: requirements.length ? '#07c160' : '#969799' }">至少8个字符</span>
              </div>
            </template>
          </van-cell>
          <van-cell>
            <template #title>
              <div style="display: flex; align-items: center; gap: 8px;">
                <van-icon :name="requirements.lowercase ? 'success' : 'cross'" :color="requirements.lowercase ? '#07c160' : '#ee0a24'" />
                <span :style="{ color: requirements.lowercase ? '#07c160' : '#969799' }">包含小写字母</span>
              </div>
            </template>
          </van-cell>
          <van-cell>
            <template #title>
              <div style="display: flex; align-items: center; gap: 8px;">
                <van-icon :name="requirements.uppercase ? 'success' : 'cross'" :color="requirements.uppercase ? '#07c160' : '#ee0a24'" />
                <span :style="{ color: requirements.uppercase ? '#07c160' : '#969799' }">包含大写字母</span>
              </div>
            </template>
          </van-cell>
          <van-cell>
            <template #title>
              <div style="display: flex; align-items: center; gap: 8px;">
                <van-icon :name="requirements.number ? 'success' : 'cross'" :color="requirements.number ? '#07c160' : '#ee0a24'" />
                <span :style="{ color: requirements.number ? '#07c160' : '#969799' }">包含数字</span>
              </div>
            </template>
          </van-cell>
        </van-cell-group>
        
        <div v-if="errors.new_pwd" style="padding: 8px 16px; color: #ee0a24; font-size: 12px;">
          {{ errors.new_pwd }}
        </div>

        <van-field
          v-model="formData.confirm_pwd"
          :type="showConfirmPassword ? 'text' : 'password'"
          name="confirm_pwd"
          label="确认新密码"
          placeholder="请再次输入新密码"
          :rules="[
            { required: true, message: '请再次输入新密码' },
            { validator: validateConfirmPassword, message: '两次输入的密码不一致' }
          ]"
          :right-icon="showConfirmPassword ? 'eye-o' : 'closed-eye'"
          @click-right-icon="togglePasswordVisibility('confirm_pwd')"
        />
        <div v-if="errors.confirm_pwd" style="padding: 8px 16px; color: #ee0a24; font-size: 12px;">
          {{ errors.confirm_pwd }}
        </div>
      </van-cell-group>

      <div style="margin-top: 24px; padding: 0 16px;">
        <van-button
          round
          block
          type="primary"
          native-type="submit"
          :loading="loading"
          :disabled="!isFormValid"
        >
          {{ loading ? '修改中...' : '修改密码' }}
        </van-button>
      </div>
      
      <!-- 统一的新用户提示信息 -->
      <div v-if="isFirstLogin" style="margin: 16px; padding: 12px; background-color: #fff7e6; border-left: 4px solid #ff9800; border-radius: 4px;">
        <div style="display: flex; align-items: flex-start;">
          <van-icon name="info-o" style="color: #ff9800; margin-right: 8px; margin-top: 2px;" />
          <div style="color: #856404; font-size: 14px; line-height: 1.6;">
            <div v-if="firstLoginMessage" style="margin-bottom: 8px;">
              <strong>{{ firstLoginMessage }}</strong>
            </div>
            <div>
              <strong>温馨提示：</strong>由于您是新用户，请及时修改密码，以确保您的账户安全。
            </div>
          </div>
        </div>
      </div>
    </van-form>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi, useAuth, useForm } from '@/core/hooks'
import { useMobile } from '@/composables/useMobile'
import { showSuccessToast, showFailToast } from '@/utils/mobileDialog'
import { checkPasswordRequirements as checkPwdReq } from '@/core/utils/validators'

export default {
  name: 'MobileChangePassword',
  setup() {
    const router = useRouter()
    const { user, updateUser, logout } = useAuth()
    
    const { post: changePasswordApi } = useApi('/auth/password/change/', { immediate: false })
    
    const { form: formData, errors, isSubmitting: formLoading, handleSubmit: formHandleSubmit, clearFieldError } = useForm(
      {
        old_pwd: '',
        new_pwd: '',
        confirm_pwd: ''
      },
      {
        onSubmit: async (data) => {
          try {
            const refreshToken = localStorage.getItem('refresh_token')
            const response = await changePasswordApi({
              ...data,
              refresh_token: refreshToken
            })
            
            if (response && response.success) {
              sessionStorage.removeItem('first_login')
              await showSuccessToast('密码修改成功，请重新登录')
              await logout()
            } else {
              await showFailToast(response?.message || '修改失败')
            }
          } catch (err) {
            throw err
          }
        }
      }
    )
    
    const loading = computed(() => formLoading.value)
    const showNewPassword = ref(false)
    const showConfirmPassword = ref(false)
    const showOldPassword = ref(false)
    const requirements = ref({
      length: false,
      lowercase: false,
      uppercase: false,
      number: false
    })
    const firstLoginMessage = ref('')
    const isFirstLogin = ref(false)
    
    // 移动端检测
    const { loadVantComponents, init: initMobile } = useMobile()
    
    // 验证确认密码（移动端）
    const validateConfirmPassword = (val) => {
      return val === formData.value.new_pwd
    }

    const isFormValid = computed(() => {
      return (
        formData.value.old_pwd &&
        formData.value.new_pwd &&
        formData.value.confirm_pwd &&
        formData.value.new_pwd === formData.value.confirm_pwd &&
        Object.values(requirements.value).every(v => v)
      )
    })

    const togglePasswordVisibility = (field) => {
      if (field === 'new_pwd') {
        showNewPassword.value = !showNewPassword.value
      } else if (field === 'confirm_pwd') {
        showConfirmPassword.value = !showConfirmPassword.value
      } else if (field === 'old_pwd') {
        showOldPassword.value = !showOldPassword.value
      }
    }

    const checkPasswordRequirements = () => {
      clearFieldError('new_pwd')
      const pwd = formData.value.new_pwd
      requirements.value = checkPwdReq(pwd)
    }

    const goBack = () => {
      router.go(-1)
    }

    // 移动端提交处理
    const handleSubmitMobile = async () => {
      if (!formData.value.old_pwd) {
        showFailToast('请输入当前密码')
        return
      }
      if (!formData.value.new_pwd) {
        showFailToast('请输入新密码')
        return
      }
      if (!formData.value.confirm_pwd) {
        showFailToast('请确认新密码')
        return
      }
      if (formData.value.new_pwd !== formData.value.confirm_pwd) {
        showFailToast('两次输入的密码不一致')
        return
      }
      if (!Object.values(requirements.value).every(v => v)) {
        showFailToast('请满足所有密码要求')
        return
      }
      
      try {
        await formHandleSubmit()
      } catch (err) {
        // 错误已由 useApi 处理
      }
    }

    // 获取首次登录提示信息（使用useAuth中的user数据）
    const fetchFirstLoginInfo = async () => {
      try {
        if (user.value && user.value.first_login !== undefined) {
          const isFirst = user.value.first_login === true || user.value.first_login === 'true' || user.value.first_login === 1
          isFirstLogin.value = isFirst
          if (isFirst && user.value.first_login_message) {
            firstLoginMessage.value = user.value.first_login_message
          }
        } else {
          const savedFirstLogin = sessionStorage.getItem('first_login')
          if (savedFirstLogin === 'true') {
            isFirstLogin.value = true
          } else {
            isFirstLogin.value = false
          }
        }
      } catch (err) {
        isFirstLogin.value = false
      }
    }

    onMounted(async () => {
      // 初始化移动端检测
      const cleanupMobile = initMobile()
      onUnmounted(() => {
        if (cleanupMobile) cleanupMobile()
      })
      
      // 首先尝试从 sessionStorage 读取首次登录状态（从登录响应中获取）
      const savedFirstLogin = sessionStorage.getItem('first_login')
      if (savedFirstLogin === 'true') {
        console.log('从 sessionStorage 读取到 first_login: true')
        isFirstLogin.value = true
        // 仍然调用 API 获取详细消息
        await fetchFirstLoginInfo()
      } else {
        // 如果没有保存的状态，调用 API 获取
        await fetchFirstLoginInfo()
      }
      
      // 如果检测到移动端，预加载 Vant 组件
      setTimeout(() => {
        loadVantComponents()
      }, 200)
    })

    return {
      formData,
      errors,
      loading,
      showNewPassword,
      showConfirmPassword,
      showOldPassword,
      requirements,
      isFormValid,
      firstLoginMessage,
      isFirstLogin,
      togglePasswordVisibility,
      checkPasswordRequirements,
      handleSubmitMobile,
      validateConfirmPassword,
      goBack
    }
  }
}
</script>

<style scoped>
@import '@/assets/css/mobile.css';

/* 移动端样式 */
.mobile-password-container {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 50px;
}
</style>
