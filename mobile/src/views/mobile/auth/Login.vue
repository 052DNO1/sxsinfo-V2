<template>
  <div class="login-page">
    <div class="login-card">
      <div class="logo-section">
        <div class="logo-circle">
          <van-icon name="cluster-o" size="48" color="#3366ff" />
        </div>
        <h2 class="title">实训室信息管理系统</h2>
        <p class="sub-title">Lab Information Management System</p>
      </div>

      <!-- 登录方式切换 -->
      <div class="login-tabs">
        <div 
          class="login-tab" 
          :class="{ active: loginType === 'account' }"
          @click="loginType = 'account'"
        >
          账号登录
        </div>
        <div 
          class="login-tab" 
          :class="{ active: loginType === 'sms' }"
          @click="loginType = 'sms'"
        >
          验证码登录
        </div>
      </div>
      <!-- 账号登录表单 -->
      <div v-if="loginType === 'account'" class="form-content">
        <div class="form-item">
          <div class="form-input-wrapper">
            <van-icon name="user-o" class="input-icon" />
            <input
              type="text"
              v-model="form.username"
              placeholder="请输入用户名/手机号"
              @input="handleUsernameInput"
              class="form-input"
            />
            <span v-if="form.username" class="clear-btn" @click="form.username = ''">✕</span>
          </div>
        </div>

        <div class="form-item">
          <div class="form-input-wrapper">
            <van-icon name="lock" class="input-icon" />
            <input
              type="password"
              v-model="form.password"
              placeholder="请输入密码"
              class="form-input"
            />
            <span v-if="form.password" class="clear-btn" @click="form.password = ''">✕</span>
          </div>
        </div>

        <div class="form-item">
          <div class="form-input-wrapper captcha-wrapper">
            <van-icon name="shield-o" class="input-icon" />
            <input
              type="text"
              v-model="form.captcha"
              placeholder="请输入验证码"
              class="form-input captcha-input"
              maxlength="4"
              @input="handleCaptchaInput"
            />
            <div class="captcha-btn" @click="fetchCaptcha">
              <img v-if="captchaImage" :src="captchaImage" class="captcha-img" />
              <span v-else>刷新</span>
            </div>
          </div>
          <div class="captcha-countdown-text">{{ captchaCountdown }}秒后自动刷新</div>
        </div>
      </div>

      <!-- 验证码登录表单 -->
      <div v-else-if="loginType === 'sms'" class="form-content">
        <div class="form-item">
          <div class="form-input-wrapper">
            <van-icon name="phone-o" class="input-icon" />
            <input
              type="tel"
              v-model="form.phone"
              placeholder="请输入手机号"
              class="form-input"
            />
            <span v-if="form.phone" class="clear-btn" @click="form.phone = ''">✕</span>
          </div>
        </div>

        <div class="form-item">
          <div class="form-input-wrapper">
            <van-icon name="envelop-o" class="input-icon" />
            <input
              type="text"
              v-model="form.code"
              placeholder="请输入短信验证码"
              class="form-input"
            />
            <button class="code-btn" @click="handleSendCode">获取验证码</button>
          </div>
        </div>
      </div>

      <!-- 登录选项 -->
      <div class="login-option">
        <label class="checkbox-label">
          <input type="checkbox" v-model="rememberMe" class="checkbox-input" />
          <span class="checkbox-custom"></span>
          <span class="checkbox-text">记住我</span>
        </label>
        <span class="forget" @click="showForgotPassword">忘记密码？</span>
      </div>

      <!-- 登录按钮 -->
      <button
        class="submit-btn"
        :class="{ loading }"
        @click="handleLoginPC"
        :disabled="loading"
      >
        <span v-if="!loading">登录</span>
        <span v-else class="loading-text">
          <span class="loading-spinner"></span>
          登录中...
        </span>
      </button>

      <!-- 错误提示 -->
      <div v-if="error" class="error-bar">
        <van-icon name="warning-o" class="error-icon" />
        <span class="error-text">{{ error }}</span>
      </div>
    </div>

    <!-- 忘记密码弹窗 -->
    <div v-if="forgotPasswordVisible" class="popup-overlay" @click="forgotPasswordVisible = false">
      <div class="forgot-popup" @click.stop>
        <div class="popup-header">
          <h3 class="popup-title">忘记密码</h3>
          <button class="popup-close" @click="forgotPasswordVisible = false">✕</button>
        </div>
        
        <div class="popup-tabs">
          <div 
            class="popup-tab" 
            :class="{ active: forgotPasswordTab === 'security' }"
            @click="forgotPasswordTab = 'security'"
          >
            密保找回
          </div>
          <div 
            class="popup-tab" 
            :class="{ active: forgotPasswordTab === 'contact' }"
            @click="forgotPasswordTab = 'contact'"
          >
            联系管理员
          </div>
        </div>

        <!-- 密保找回 -->
        <div v-if="forgotPasswordTab === 'security'" class="popup-content">
          <!-- 输入用户名 -->
          <div v-if="securityStep === 'input_username'" class="step-content">
            <div class="form-item">
              <div class="form-input-wrapper">
                <input
                  type="text"
                  v-model="securityForm.username"
                  placeholder="请输入用户名"
                  class="form-input"
                />
              </div>
            </div>
            <button 
              class="action-btn primary"
              @click="checkSecurityQuestion"
              :disabled="securityLoading"
            >
              {{ securityLoading ? '处理中...' : '下一步' }}
            </button>
          </div>

          <!-- 回答密保问题 -->
          <div v-else-if="securityStep === 'answer_question'" class="step-content">
            <div class="question-notice">
              {{ securityForm.question }}
            </div>
            <div class="form-item">
              <div class="form-input-wrapper">
                <input
                  type="text"
                  v-model="securityForm.answer"
                  placeholder="请输入密保答案"
                  class="form-input"
                />
              </div>
            </div>
            <div class="btn-group">
              <button class="action-btn secondary" @click="securityStep = 'input_username'">
                上一步
              </button>
              <button 
                class="action-btn primary"
                @click="verifySecurityAnswer"
                :disabled="securityLoading"
              >
                {{ securityLoading ? '验证中...' : '验证' }}
              </button>
            </div>
          </div>

          <!-- 重置密码 -->
          <div v-else-if="securityStep === 'reset_password'" class="step-content">
            <div class="success-section">
              <van-icon name="passed" class="success-icon" color="#28a745" />
              <p class="success-text">验证成功，请设置新密码</p>
            </div>
            <div class="form-item">
              <div class="form-input-wrapper">
                <input
                  type="password"
                  v-model="securityForm.newPassword"
                  placeholder="新密码"
                  class="form-input"
                />
              </div>
            </div>
            <div class="form-item">
              <div class="form-input-wrapper">
                <input
                  type="password"
                  v-model="securityForm.confirmPassword"
                  placeholder="确认密码"
                  class="form-input"
                />
              </div>
            </div>
            <button 
              class="action-btn primary"
              @click="resetPasswordBySecurity"
              :disabled="securityLoading"
            >
              {{ securityLoading ? '重置中...' : '重置密码' }}
            </button>
          </div>

          <!-- 未设置密保问题 -->
          <div v-else-if="securityStep === 'no_question'" class="step-content">
            <div class="empty-section">
              <van-icon name="question-o" class="empty-icon" color="#666666" />
              <p class="empty-text">该用户未设置密保问题</p>
              <button class="action-btn primary" @click="forgotPasswordTab = 'contact'">
                联系管理员
              </button>
            </div>
          </div>
        </div>

        <!-- 联系管理员 -->
        <div v-else-if="forgotPasswordTab === 'contact'" class="popup-content">
          <div class="contact-section">
            <van-icon name="service-o" class="contact-icon" color="#3366ff" />
            <p class="contact-text">请联系管理员重置密码</p>
            <div v-if="contactInfo.contact" class="contact-info">
              <div class="contact-item">
                <span class="contact-label">联系人：</span>
                <span class="contact-value">{{ contactInfo.contact.name }}</span>
              </div>
              <div class="contact-item">
                <span class="contact-label">电话：</span>
                <span class="contact-value">{{ contactInfo.contact.phone }}</span>
              </div>
              <div class="contact-item">
                <span class="contact-label">邮箱：</span>
                <span class="contact-value">{{ contactInfo.contact.email }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useApi } from '@/composables/useApi'
import { useAuth } from '@/composables/useAuth'
import { translateErrorMessage, getLoginErrorMessage } from '@/utils/authUtils'
import { showSuccess, showError } from '@/utils/errorHandler'
import { withLock } from '@/utils/throttle'
import { encryptPassword, isEncryptionEnabled } from '@/utils/crypto'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const { login: authLogin, updateUser } = useAuth()

    const loginType = ref('account')
    const rememberMe = ref(true)
    const forgotPasswordVisible = ref(false)
    const forgotPasswordTab = ref('security')
    const contactLoading = ref(false)
    const contactInfo = ref({ message: '', contact: null })

    const securityStep = ref('input_username')
    const securityLoading = ref(false)
    const securityForm = ref({
      username: '',
      question: '',
      answer: '',
      resetToken: '',
      newPassword: '',
      confirmPassword: ''
    })

    const form = ref({
      username: '',
      password: '',
      captcha: '',
      captcha_key: '',
      phone: '',
      code: ''
    })
    const error = ref('')
    const loading = ref(false)
    const captchaImage = ref('')
    const captchaKey = ref('')
    const captchaCountdown = ref(60)
    let captchaTimer = null

    onMounted(() => {
      const isRemember = localStorage.getItem('sxs_remember_me') === 'true'
      rememberMe.value = isRemember
      if (isRemember) {
        const savedUser = localStorage.getItem('sxs_username')
        if (savedUser) form.value.username = savedUser
      }
      fetchCaptcha()
    })

    onUnmounted(() => {
      if (captchaTimer) {
        clearInterval(captchaTimer)
        captchaTimer = null
      }
    })

    const startCaptchaTimer = () => {
      if (captchaTimer) {
        clearInterval(captchaTimer)
      }
      captchaCountdown.value = 60
      captchaTimer = setInterval(() => {
        captchaCountdown.value--
        if (captchaCountdown.value <= 0) {
          fetchCaptcha()
        }
      }, 1000)
    }

    const fetchCaptcha = async () => {
      try {
        const { get: getCaptchaApi } = useApi('/userinfo/captcha/', { immediate: false })
        const response = await getCaptchaApi()
        if (response?.success) {
          captchaImage.value = response.captcha_image
          captchaKey.value = response.captcha_key
          form.value.captcha = ''
          startCaptchaTimer()
        } else {
          error.value = '验证码加载失败'
        }
      } catch (err) {
        error.value = '验证码加载失败'
      }
    }

    const handleUsernameInput = (event) => {
      const val = event.target.value
      form.value.username = val.replace(/[^a-zA-Z0-9@.\-_]/g, '')
    }

    const handleCaptchaInput = (event) => {
      const val = event.target.value
      form.value.captcha = val.replace(/[^a-zA-Z0-9]/g, '').toUpperCase().slice(0, 4)
    }

    const handleSendCode = () => {
      if (!form.value.phone) {
        error.value = '请输入手机号'
        return
      }
      // 模拟验证码发送
      alert('验证码已发送 (模拟)')
    }

    const showForgotPassword = async () => {
      if (!form.value.username) {
        error.value = '请先输入用户名'
        return
      }
      securityForm.value.username = form.value.username
      forgotPasswordTab.value = 'security'
      securityStep.value = 'input_username'
      forgotPasswordVisible.value = true

      try {
        const { get: api } = useApi('/userinfo/password_reset_contact/', { immediate: false })
        const res = await api({ username: form.value.username })
        contactInfo.value = res?.success
          ? { message: res.message, contact: res.contact }
          : { message: '获取失败', contact: null }
      } catch (e) {
        contactInfo.value = { message: '获取失败', contact: null }
      }
    }

    const checkSecurityQuestion = async () => {
      if (!securityForm.value.username) return showError('请输入用户名')
      securityLoading.value = true
      try {
        const { post: api } = useApi('/userinfo/get_security_question/', { immediate: false })
        const res = await api({ username: securityForm.value.username })
        if (res?.success) {
          res.has_question
            ? (securityForm.value.question = res.question) && (securityStep.value = 'answer_question')
            : (securityStep.value = 'no_question')
        }
      } finally {
        securityLoading.value = false
      }
    }

    const verifySecurityAnswer = async () => {
      if (!securityForm.value.answer) return showError('请输入答案')
      securityLoading.value = true
      try {
        const { post: api } = useApi('/userinfo/verify_security_answer/', { immediate: false })
        const res = await api({
          username: securityForm.value.username,
          answer: securityForm.value.answer
        })
        if (res?.success) {
          securityForm.value.resetToken = res.reset_token
          securityStep.value = 'reset_password'
          showSuccess('验证成功')
        }
      } finally {
        securityLoading.value = false
      }
    }

    const resetPasswordBySecurity = async () => {
      const { newPassword, confirmPassword } = securityForm.value
      if (!newPassword || !confirmPassword) return showError('请填写完整')
      if (newPassword !== confirmPassword) return showError('两次密码不一致')
      securityLoading.value = true
      try {
        const { post: api } = useApi('/userinfo/reset_password_by_security/', { immediate: false })
        const res = await api({
          reset_token: securityForm.value.resetToken,
          new_password: newPassword,
          confirm_password: confirmPassword
        })
        if (res?.success) {
          showSuccess('重置成功')
          forgotPasswordVisible.value = false
        }
      } finally {
        securityLoading.value = false
      }
    }

    const handleLoginPC = withLock(async () => {
      if (loginType.value === 'sms') {
        error.value = '暂未开放短信登录'
        return
      }
      if (!form.value.captcha) {
        error.value = '请输入验证码'
        return
      }
      loading.value = true
      error.value = ''
      try {
        const encryptedPassword = encryptPassword(form.value.password)
        const { post: loginApi } = useApi('/login/', { immediate: false, dedupe: true })
        const res = await loginApi({
          username: form.value.username,
          password: encryptedPassword,
          captcha: form.value.captcha,
          captcha_key: captchaKey.value,
          remember_me: rememberMe.value,
          encrypted: isEncryptionEnabled()
        })
        if (res?.success) {
          updateUser(res.user)
          localStorage.setItem('access_token', res.token.access)
          showSuccess(res.message || '登录成功，欢迎回来！')
          router.push(res.redirect || '/')
        } else {
          error.value = translateErrorMessage(res?.message || '登录失败')
          fetchCaptcha()
        }
      } catch (err) {
        error.value = getLoginErrorMessage(err)
        fetchCaptcha()
      } finally {
        loading.value = false
      }
    })

    return {
      form,
      error,
      loading,
      loginType,
      rememberMe,
      handleLoginPC,
      handleSendCode,
      handleUsernameInput,
      handleCaptchaInput,
      captchaImage,
      captchaCountdown,
      fetchCaptcha,
      forgotPasswordVisible,
      forgotPasswordTab,
      showForgotPassword,
      contactInfo,
      securityStep,
      securityLoading,
      securityForm,
      checkSecurityQuestion,
      verifySecurityAnswer,
      resetPasswordBySecurity
    }
  }
}
</script>

<style scoped>
/* 全局样式重置 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* 登录页面容器 */
.login-page {
  min-height: 100vh;
  background: #f8f9fa;
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 登录卡片 */
.login-card {
  width: 100%;
  max-width: 400px;
  background: #ffffff;
  border-radius: 20px;
  padding: 32px 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

/* Logo 部分 */
.logo-section {
  text-align: center;
  margin-bottom: 36px;
}

.logo-circle {
  width: 96px;
  height: 96px;
  background: #e8f0ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 4px 16px rgba(51, 102, 255, 0.1);
}

.logo-icon {
  font-size: 48px;
}

.title {
  font-size: 24px;
  font-weight: 700;
  color: #333333;
  margin: 0 0 8px;
  letter-spacing: 0.5px;
}

.sub-title {
  font-size: 14px;
  color: #999999;
  margin: 0;
  font-weight: 400;
}

/* 登录方式切换 */
.login-tabs {
  display: flex;
  margin-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.login-tab {
  flex: 1;
  text-align: center;
  padding: 12px 0;
  font-size: 16px;
  font-weight: 500;
  color: #666666;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

.login-tab.active {
  color: #3366ff;
  font-weight: 600;
}

.login-tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20%;
  width: 60%;
  height: 3px;
  background: #3366ff;
  border-radius: 1.5px;
}

/* 表单内容 */
.form-content {
  margin-bottom: 20px;
}

.form-item {
  margin-bottom: 20px;
}

/* 表单输入框 */
.form-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 0 16px;
  transition: all 0.3s ease;
}

.form-input-wrapper:focus-within {
  border-color: #3366ff;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(51, 102, 255, 0.1);
}

.input-icon {
  font-size: 20px;
  margin-right: 12px;
  color: #666666;
}

.input-icon.van-icon {
  font-size: 20px;
}

.form-input {
  flex: 1;
  height: 48px;
  border: none;
  outline: none;
  font-size: 16px;
  color: #333333;
  background: transparent;
}

.form-input::placeholder {
  color: #999999;
}

/* 清除按钮 */
.clear-btn {
  font-size: 18px;
  color: #999999;
  cursor: pointer;
  padding: 4px;
  transition: color 0.2s ease;
}

.clear-btn:hover {
  color: #666666;
}

/* 验证码输入 */
.captcha-wrapper {
  gap: 8px;
}

.captcha-input {
  flex: 1;
  min-width: 0;
}

.captcha-btn {
  flex-shrink: 0;
  width: 80px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
}

.captcha-btn:hover {
  border-color: #3366ff;
}

.captcha-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.captcha-countdown-text {
  font-size: 12px;
  color: #3366ff;
  text-align: right;
  margin-top: 4px;
}

/* 验证码按钮 */
.code-btn {
  padding: 6px 16px;
  background: #3366ff;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.code-btn:hover {
  background: #2554e0;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(51, 102, 255, 0.2);
}

/* 登录选项 */
.login-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

/* 自定义复选框 */
.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #666666;
}

.checkbox-input {
  display: none;
}

.checkbox-custom {
  width: 16px;
  height: 16px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  margin-right: 8px;
  position: relative;
  transition: all 0.3s ease;
}

.checkbox-input:checked + .checkbox-custom {
  background: #3366ff;
  border-color: #3366ff;
}

.checkbox-input:checked + .checkbox-custom::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #ffffff;
  font-size: 12px;
  font-weight: bold;
}

.checkbox-text {
  user-select: none;
}

/* 忘记密码 */
.forget {
  font-size: 14px;
  color: #3366ff;
  cursor: pointer;
  transition: color 0.2s ease;
}

.forget:hover {
  color: #2554e0;
  text-decoration: underline;
}

/* 登录按钮 */
.submit-btn {
  width: 100%;
  height: 48px;
  background: #3366ff;
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-btn:hover:not(:disabled) {
  background: #2554e0;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(51, 102, 255, 0.3);
}

.submit-btn:disabled {
  background: #c0c7d2;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 加载状态 */
.submit-btn.loading {
  background: #3366ff;
  opacity: 0.8;
}

.loading-text {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误提示 */
.error-bar {
  background: #fff5f5;
  border: 1px solid #ffd6d6;
  border-radius: 8px;
  padding: 12px 16px;
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-icon {
  font-size: 16px;
  color: #ff4757;
}

.error-text {
  flex: 1;
  font-size: 14px;
  color: #ff4757;
  line-height: 1.4;
}

/* 弹窗遮罩 */
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 999;
}

/* 忘记密码弹窗 */
.forgot-popup {
  width: 100%;
  max-height: 80vh;
  background: #ffffff;
  border-radius: 20px 20px 0 0;
  padding: 24px;
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.15);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 弹窗头部 */
.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.popup-title {
  font-size: 18px;
  font-weight: 600;
  color: #333333;
  margin: 0;
}

.popup-close {
  font-size: 24px;
  color: #999999;
  cursor: pointer;
  background: none;
  border: none;
  padding: 4px;
  transition: color 0.2s ease;
}

.popup-close:hover {
  color: #666666;
}

/* 弹窗标签页 */
.popup-tabs {
  display: flex;
  margin-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.popup-tab {
  flex: 1;
  text-align: center;
  padding: 12px 0;
  font-size: 15px;
  font-weight: 500;
  color: #666666;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

.popup-tab.active {
  color: #3366ff;
  font-weight: 600;
}

.popup-tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 25%;
  width: 50%;
  height: 3px;
  background: #3366ff;
  border-radius: 1.5px;
}

/* 弹窗内容 */
.popup-content {
  max-height: 400px;
  overflow-y: auto;
}

.step-content {
  padding: 8px 0;
}

/* 密保问题提示 */
.question-notice {
  background: #e8f0ff;
  border: 1px solid #d6e4ff;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  font-size: 14px;
  color: #3366ff;
  line-height: 1.4;
}

/* 按钮组 */
.btn-group {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

/* 操作按钮 */
.action-btn {
  flex: 1;
  height: 44px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn.primary {
  background: #3366ff;
  color: #ffffff;
}

.action-btn.primary:hover:not(:disabled) {
  background: #2554e0;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(51, 102, 255, 0.2);
}

.action-btn.secondary {
  background: #f8f9fa;
  color: #666666;
  border: 1px solid #e9ecef;
}

.action-btn.secondary:hover {
  background: #e9ecef;
  border-color: #dee2e6;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 成功提示 */
.success-section {
  text-align: center;
  margin-bottom: 24px;
  padding: 20px 0;
}

.success-icon {
  font-size: 48px;
  margin-bottom: 12px;
  display: block;
}

.success-text {
  font-size: 16px;
  font-weight: 500;
  color: #28a745;
  margin: 0;
}

/* 空状态 */
.empty-section {
  text-align: center;
  padding: 40px 0;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
}

.empty-text {
  font-size: 16px;
  color: #666666;
  margin-bottom: 24px;
}

/* 联系管理员 */
.contact-section {
  text-align: center;
  padding: 20px 0;
}

.contact-icon {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
}

.contact-text {
  font-size: 16px;
  color: #666666;
  margin-bottom: 24px;
}

/* 联系信息 */
.contact-info {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 16px;
  text-align: left;
  margin-top: 16px;
}

.contact-item {
  display: flex;
  margin-bottom: 12px;
  align-items: center;
}

.contact-item:last-child {
  margin-bottom: 0;
}

.contact-label {
  font-size: 14px;
  color: #666666;
  min-width: 60px;
}

.contact-value {
  font-size: 14px;
  color: #333333;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 375px) {
  .login-card {
    padding: 24px 20px;
  }
  
  .logo-circle {
    width: 80px;
    height: 80px;
  }
  
  .logo-icon {
    font-size: 40px;
  }
  
  .title {
    font-size: 22px;
  }
  
  .form-input-wrapper {
    padding: 0 14px;
  }
  
  .form-input {
    height: 44px;
    font-size: 15px;
  }
  
  .submit-btn {
    height: 44px;
    font-size: 15px;
  }
}
</style>