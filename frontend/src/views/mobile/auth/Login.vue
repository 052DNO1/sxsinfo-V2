<template>
  <div class="login-page">
    <!-- 顶部装饰背景 -->
    <div class="login-header">
      <div class="header-bg"></div>
      <div class="header-content">
        <div class="logo-wrapper">
          <div class="logo-circle">
            <van-icon name="cluster-o" size="42" color="#FFFFFF" />
          </div>
        </div>
        <h1 class="app-title">智慧实训室</h1>
        <p class="app-subtitle">实训室信息管理系统 V2</p>
      </div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- 登录方式切换 -->
      <div class="login-tabs">
        <div 
          class="tab-item" 
          :class="{ active: loginType === 'account' }"
          @click="loginType = 'account'"
        >
          账号登录
        </div>
        <div 
          class="tab-item" 
          :class="{ active: loginType === 'sms' }"
          @click="loginType = 'sms'"
        >
          验证码
        </div>
      </div>

      <!-- 账号登录表单 -->
      <div v-if="loginType === 'account'" class="form-section">
        <div class="input-group">
          <div class="input-field">
            <van-icon name="user-o" size="20" color="#909399" />
            <input
              type="text"
              v-model="form.username"
              placeholder="请输入用户名/手机号"
              @input="handleUsernameInput"
              class="form-input"
            />
            <span v-if="form.username" class="clear-icon" @click="form.username = ''">
              <van-icon name="cross" size="14" />
            </span>
          </div>
        </div>

        <div class="input-group">
          <div class="input-field">
            <van-icon name="lock" size="20" color="#909399" />
            <input
              type="password"
              v-model="form.password"
              placeholder="请输入密码"
              class="form-input"
            />
            <span v-if="form.password" class="clear-icon" @click="form.password = ''">
              <van-icon name="cross" size="14" />
            </span>
          </div>
        </div>

        <div class="input-group captcha-group">
          <div class="input-field input-captcha">
            <van-icon name="shield-o" size="20" color="#909399" />
            <input
              type="text"
              v-model="form.captcha"
              placeholder="请输入验证码"
              class="form-input"
              maxlength="4"
              @input="handleCaptchaInput"
            />
          </div>
          
          <!-- 大尺寸验证码 -->
          <div class="captcha-box" @click="fetchCaptcha">
            <img v-if="captchaImage" :src="captchaImage" class="captcha-image" alt="验证码" />
            <div v-else class="captcha-placeholder">
              <van-icon name="replay" size="24" color="#4F6EF7" />
              <span>点击刷新</span>
            </div>
          </div>
        </div>

        <div class="captcha-hint" v-if="captchaCountdown > 0 && captchaCountdown < 60">
          <van-icon name="clock-o" size="12" />
          {{ captchaCountdown }}秒后自动刷新
        </div>
      </div>

      <!-- 验证码登录表单 -->
      <div v-else-if="loginType === 'sms'" class="form-section">
        <div class="input-group">
          <div class="input-field">
            <van-icon name="phone-o" size="20" color="#909399" />
            <input
              type="tel"
              v-model="form.phone"
              placeholder="请输入手机号"
              class="form-input"
            />
            <span v-if="form.phone" class="clear-icon" @click="form.phone = ''">
              <van-icon name="cross" size="14" />
            </span>
          </div>
        </div>

        <div class="input-group sms-group">
          <div class="input-field input-sms">
            <van-icon name="envelop-o" size="20" color="#909399" />
            <input
              type="text"
              v-model="form.code"
              placeholder="请输入短信验证码"
              class="form-input"
            />
          </div>
          <button class="send-code-btn" @click="handleSendCode">
            获取验证码
          </button>
        </div>
      </div>

      <!-- 登录选项 -->
      <div class="options-row">
        <label class="remember-me" @click="rememberMe = !rememberMe">
          <div class="checkbox-custom" :class="{ checked: rememberMe }">
            <van-icon v-if="rememberMe" name="success" size="12" color="#fff" />
          </div>
          <span>记住我</span>
        </label>
        <span class="forgot-link" @click="showForgotPassword">忘记密码？</span>
      </div>

      <!-- 登录按钮 -->
      <button
        class="login-btn"
        :class="{ loading }"
        @click="handleLoginPC"
        :disabled="loading"
      >
        <span v-if="!loading">登 录</span>
        <span v-else class="btn-loading">
          <van-loading size="18px" color="#ffffff" />
          登录中...
        </span>
      </button>

      <!-- 错误提示 -->
      <transition name="slide-fade">
        <div v-if="error" class="error-toast">
          <van-icon name="warning-o" size="16" color="#FF3B30" />
          <span>{{ error }}</span>
        </div>
      </transition>
    </div>

    <!-- 忘记密码弹窗 -->
    <van-popup v-model:show="forgotPasswordVisible" position="bottom" round safe-area-inset-bottom>
      <div class="popup-container">
        <div class="popup-header">
          <h3>忘记密码</h3>
          <van-icon name="cross" size="22" color="#999" @click="forgotPasswordVisible = false" style="cursor:pointer" />
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

        <!-- 密保找回内容 -->
        <div v-if="forgotPasswordTab === 'security'" class="popup-body">
          <div v-if="securityStep === 'input_username'" class="step-content">
            <div class="input-group">
              <div class="input-field">
                <van-icon name="user-o" size="20" color="#909399" />
                <input type="text" v-model="securityForm.username" placeholder="请输入用户名" class="form-input" />
              </div>
            </div>
            <button class="action-btn primary-btn" @click="checkSecurityQuestion" :disabled="securityLoading">
              {{ securityLoading ? '处理中...' : '下一步' }}
            </button>
          </div>

          <div v-else-if="securityStep === 'answer_question'" class="step-content">
            <div class="question-box">
              <van-icon name="question-o" size="18" color="#4F6EF7" />
              {{ securityForm.question }}
            </div>
            <div class="input-group">
              <div class="input-field">
                <van-icon name="edit" size="20" color="#909399" />
                <input type="text" v-model="securityForm.answer" placeholder="请输入密保答案" class="form-input" />
              </div>
            </div>
            <div class="btn-row">
              <button class="action-btn secondary-btn" @click="securityStep = 'input_username'">上一步</button>
              <button class="action-btn primary-btn" @click="verifySecurityAnswer" :disabled="securityLoading">
                {{ securityLoading ? '验证中...' : '验证' }}
              </button>
            </div>
          </div>

          <div v-else-if="securityStep === 'reset_password'" class="step-content">
            <div class="success-hint">
              <van-icon name="passed" size="32" color="#07C160" />
              <p>验证成功，请设置新密码</p>
            </div>
            <div class="input-group">
              <div class="input-field">
                <van-icon name="lock" size="20" color="#909399" />
                <input type="password" v-model="securityForm.newPassword" placeholder="新密码" class="form-input" />
              </div>
            </div>
            <div class="input-group">
              <div class="input-field">
                <van-icon name="lock" size="20" color="#909399" />
                <input type="password" v-model="securityForm.confirmPassword" placeholder="确认密码" class="form-input" />
              </div>
            </div>
            <button class="action-btn primary-btn" @click="resetPasswordBySecurity" :disabled="securityLoading">
              {{ securityLoading ? '重置中...' : '重置密码' }}
            </button>
          </div>

          <div v-else-if="securityStep === 'no_question'" class="step-content">
            <div class="empty-state">
              <van-icon name="info-o" size="48" color="#C0C4CC" />
              <p>该用户未设置密保问题</p>
              <button class="action-btn primary-btn" @click="forgotPasswordTab = 'contact'">联系管理员</button>
            </div>
          </div>
        </div>

        <!-- 联系管理员内容 -->
        <div v-else-if="forgotPasswordTab === 'contact'" class="popup-body">
          <div class="contact-card">
            <van-icon name="service-o" size="40" color="#4F6EF7" />
            <p>请联系管理员重置密码</p>
            <div v-if="contactInfo.contact" class="contact-info-list">
              <div class="contact-info-item">
                <span class="label">联系人：</span>
                <span class="value">{{ contactInfo.contact.name }}</span>
              </div>
              <div class="contact-info-item">
                <span class="label">电话：</span>
                <span class="value">{{ contactInfo.contact.phone }}</span>
              </div>
              <div class="contact-info-item">
                <span class="label">邮箱：</span>
                <span class="value">{{ contactInfo.contact.email }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useApi, useAuth } from '@/core/hooks'
import { translateErrorMessage, getLoginErrorMessage } from '@/core/utils/authUtils'
import { showSuccess, showError } from '@/core/utils/errorHandler'
import { encryptPassword, isEncryptionEnabled } from '@/core/utils/crypto'

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
      if (captchaTimer) clearInterval(captchaTimer)
      captchaCountdown.value = 60
      captchaTimer = setInterval(() => {
        captchaCountdown.value--
        if (captchaCountdown.value <= 0) fetchCaptcha()
      }, 1000)
    }

    const fetchCaptcha = async () => {
      try {
        const { get: getCaptchaApi } = useApi('/auth/captcha/', { immediate: false })
        const response = await getCaptchaApi()
        if (response?.success && response?.data) {
          captchaImage.value = response.data.captcha_image
          captchaKey.value = response.data.captcha_key
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
      form.value.username = event.target.value.replace(/[^a-zA-Z0-9@.\-_]/g, '')
    }

    const handleCaptchaInput = (event) => {
      form.value.captcha = event.target.value.replace(/[^a-zA-Z0-9]/g, '').toUpperCase().slice(0, 4)
    }

    const handleSendCode = () => {
      if (!form.value.phone) { error.value = '请输入手机号'; return }
      alert('验证码已发送 (模拟)')
    }

    const showForgotPassword = async () => {
      if (!form.value.username) { error.value = '请先输入用户名'; return }
      securityForm.value.username = form.value.username
      forgotPasswordTab.value = 'security'
      securityStep.value = 'input_username'
      forgotPasswordVisible.value = true

      try {
        const { get: api } = useApi('/auth/password-reset-contact/', { immediate: false })
        const res = await api({ username: form.value.username })
        contactInfo.value = res?.success && res?.data
          ? { message: res.message, contact: res.data.contact }
          : { message: '获取失败', contact: null }
      } catch (e) {
        contactInfo.value = { message: '获取失败', contact: null }
      }
    }

    const checkSecurityQuestion = async () => {
      if (!securityForm.value.username) return showError('请输入用户名')
      securityLoading.value = true
      try {
        const { post: api } = useApi('/auth/security-question/user/', { immediate: false })
        const res = await api({ username: securityForm.value.username })
        if (res?.success && res?.data) {
          res.data.has_question
            ? (securityForm.value.question = res.data.question) && (securityStep.value = 'answer_question')
            : (securityStep.value = 'no_question')
        }
      } finally { securityLoading.value = false }
    }

    const verifySecurityAnswer = async () => {
      if (!securityForm.value.answer) return showError('请输入答案')
      securityLoading.value = true
      try {
        const { post: api } = useApi('/auth/security-question/verify/', { immediate: false })
        const res = await api({ username: securityForm.value.username, answer: securityForm.value.answer })
        if (res?.success && res?.data) {
          securityForm.value.resetToken = res.data.reset_token
          securityStep.value = 'reset_password'
          showSuccess('验证成功')
        }
      } finally { securityLoading.value = false }
    }

    const resetPasswordBySecurity = async () => {
      const { newPassword, confirmPassword } = securityForm.value
      if (!newPassword || !confirmPassword) return showError('请填写完整')
      if (newPassword !== confirmPassword) return showError('两次密码不一致')
      securityLoading.value = true
      try {
        const { post: api } = useApi('/auth/password/reset-by-security/', { immediate: false })
        const res = await api({ reset_token: securityForm.value.resetToken, new_password: newPassword, confirm_password: confirmPassword })
        if (res?.success) { showSuccess('重置成功'); forgotPasswordVisible.value = false }
      } finally { securityLoading.value = false }
    }

    const handleLoginPC = async () => {
      if (loginType.value === 'sms') { error.value = '暂未开放短信登录'; return }
      if (!form.value.captcha) { error.value = '请输入验证码'; return }
      loading.value = true; error.value = ''
      try {
        const encryptedPassword = encryptPassword(form.value.password)
        const { post: loginApi } = useApi('/auth/login/', { immediate: false, dedupe: true })
        const res = await loginApi({
          username: form.value.username,
          password: encryptedPassword,
          captcha: form.value.captcha,
          captcha_key: captchaKey.value,
          remember_me: rememberMe.value,
          encrypted: isEncryptionEnabled()
        })
        if (res?.success && res?.data) {
          if (res.data.user) updateUser(res.data.user)
          if (res.data.access_token) {
            localStorage.setItem('access_token', res.data.access_token)
            if (res.data.refresh_token) localStorage.setItem('refresh_token', res.data.refresh_token)
          }
          if (res.data.user && res.data.user.first_login !== undefined) sessionStorage.setItem('first_login', String(res.data.user.first_login))
          if (rememberMe.value) {
            localStorage.setItem('sxs_remember_me', 'true')
            localStorage.setItem('sxs_username', form.value.username)
          } else {
            localStorage.removeItem('sxs_remember_me')
            localStorage.removeItem('sxs_username')
          }
          router.push(res.data.redirect || '/')
        } else {
          error.value = translateErrorMessage(res?.message || '登录失败')
          fetchCaptcha()
        }
      } catch (err) {
        error.value = getLoginErrorMessage(err)
        fetchCaptcha()
      } finally { loading.value = false }
    }

    return {
      form, error, loading, loginType, rememberMe, handleLoginPC, handleSendCode,
      handleUsernameInput, handleCaptchaInput, captchaImage, captchaCountdown, fetchCaptcha,
      forgotPasswordVisible, forgotPasswordTab, showForgotPassword, contactInfo,
      securityStep, securityLoading, securityForm, checkSecurityQuestion, verifySecurityAnswer, resetPasswordBySecurity
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #E8EEFF 0%, #F5F7FA 50%, #FFFFFF 100%);
  position: relative;
  overflow-x: hidden;
}

/* 顶部装饰区域 */
.login-header {
  position: relative;
  padding: 60px 24px 80px;
  overflow: hidden;
}

.header-bg {
  position: absolute;
  top: -80px;
  right: -80px;
  width: 280px;
  height: 280px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(79, 110, 247, 0.15) 0%, rgba(79, 110, 247, 0.05) 100%);
}

.header-bg::before {
  content: '';
  position: absolute;
  bottom: -40px;
  left: -40px;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(122, 114, 239, 0.1) 0%, transparent 100%);
}

.header-content {
  position: relative;
  z-index: 1;
  text-align: center;
}

.logo-wrapper {
  margin-bottom: 16px;
}

.logo-circle {
  width: 88px;
  height: 88px;
  border-radius: 24px;
  background: linear-gradient(135deg, #4F6EF7 0%, #6B8AFF 100%);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(79, 110, 247, 0.35);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.app-title {
  margin: 0 0 6px;
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  letter-spacing: -0.5px;
}

.app-subtitle {
  margin: 0;
  font-size: 14px;
  color: #666;
  font-weight: 400;
}

/* 登录卡片 */
.login-card {
  margin: -40px 20px 0;
  background: white;
  border-radius: 24px;
  padding: 28px 24px 32px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 2;
}

/* Tab切换 */
.login-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 28px;
  background: #f5f7fa;
  border-radius: 12px;
  padding: 4px;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 12px 0;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.25s ease;
}

.tab-item.active {
  background: white;
  color: #4F6EF7;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* 表单区域 */
.form-section {
  margin-bottom: 20px;
}

.input-group {
  margin-bottom: 16px;
}

.input-field {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #f8f9fa;
  border: 1.5px solid #e9ecef;
  border-radius: 14px;
  padding: 0 18px;
  transition: all 0.25s ease;
}

.input-field:focus-within {
  border-color: #4F6EF7;
  background: white;
  box-shadow: 0 0 0 4px rgba(79, 110, 247, 0.08);
}

.form-input {
  flex: 1;
  height: 52px;
  border: none;
  outline: none;
  font-size: 16px;
  color: #303133;
  background: transparent;
}

.form-input::placeholder {
  color: #c0c4cc;
}

.clear-icon {
  cursor: pointer;
  padding: 4px;
  color: #c0c4cc;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.clear-icon:active {
  color: #909399;
}

/* 验证码组 - 大尺寸验证码 */
.captcha-group {
  display: flex;
  gap: 12px;
  align-items: stretch;
}

.input-captcha {
  flex: 1;
  min-width: 0;
}

.captcha-box {
  width: 120px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 1.5px solid #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.25s ease;
  flex-shrink: 0;
}

.captcha-box:active {
  transform: scale(0.96);
  border-color: #4F6EF7;
}

.captcha-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

.captcha-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #4F6EF7;
  font-size: 11px;
  font-weight: 600;
}

.captcha-hint {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #4F6EF7;
  margin-top: 8px;
  opacity: 0.85;
}

/* 短信验证码 */
.sms-group {
  display: flex;
  gap: 12px;
  align-items: stretch;
}

.input-sms {
  flex: 1;
  min-width: 0;
}

.send-code-btn {
  width: 110px;
  height: 52px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #4F6EF7 0%, #6B8AFF 100%);
  color: white;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  flex-shrink: 0;
  white-space: nowrap;
}

.send-code-btn:active {
  transform: scale(0.96);
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.3);
}

/* 选项行 */
.options-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
}

.checkbox-custom {
  width: 20px;
  height: 20px;
  border: 2px solid #dcdfe6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.checkbox-custom.checked {
  background: linear-gradient(135deg, #4F6EF7 0%, #6B8AFF 100%);
  border-color: #4F6EF7;
}

.forgot-link {
  font-size: 14px;
  color: #4F6EF7;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.forgot-link:active {
  opacity: 0.7;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  height: 54px;
  border: none;
  border-radius: 16px;
  background: linear-gradient(135deg, #4F6EF7 0%, #6B8AFF 100%);
  color: white;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 20px rgba(79, 110, 247, 0.3);
  letter-spacing: 2px;
}

.login-btn:active:not(:disabled) {
  transform: scale(0.98);
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.25);
}

.login-btn:disabled {
  background: #c0c4cc;
  box-shadow: none;
  cursor: not-allowed;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 错误提示 */
.error-toast {
  margin-top: 16px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #FFF5F5 0%, #FFEDED 100%);
  border: 1px solid #FFD6D6;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #FF3B30;
  line-height: 1.4;
}

.slide-fade-enter-active, .slide-fade-leave-active {
  transition: all 0.3s ease;
}
.slide-fade-enter-from, .slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* 弹窗样式 */
.popup-container {
  padding: 24px;
  max-height: 85vh;
  overflow-y: auto;
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.popup-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}

.popup-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  background: #f5f7fa;
  border-radius: 10px;
  padding: 4px;
}

.popup-tab {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.popup-tab.active {
  background: white;
  color: #4F6EF7;
  font-weight: 600;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.popup-body {
  min-height: 200px;
}

.step-content {
  padding: 8px 0;
}

.question-box {
  background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
  border: 1px solid #d6e4ff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  font-size: 15px;
  color: #4F6EF7;
  line-height: 1.5;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-weight: 500;
}

.success-hint {
  text-align: center;
  margin-bottom: 24px;
  padding: 24px 0;
}

.success-hint p {
  margin: 12px 0 0;
  font-size: 15px;
  color: #07C160;
  font-weight: 500;
}

.btn-row {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.action-btn {
  flex: 1;
  height: 48px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.primary-btn {
  background: linear-gradient(135deg, #4F6EF7 0%, #6B8AFF 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.25);
}

.primary-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.secondary-btn {
  background: #f5f7fa;
  color: #666;
  border: 1px solid #e9ecef;
}

.secondary-btn:active {
  background: #e9ecef;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.empty-state p {
  margin: 16px 0 24px;
  font-size: 15px;
  color: #909399;
}

.contact-card {
  text-align: center;
  padding: 24px 0;
}

.contact-card p {
  margin: 16px 0 24px;
  font-size: 15px;
  color: #666;
}

.contact-info-list {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
  text-align: left;
}

.contact-info-item {
  display: flex;
  margin-bottom: 12px;
  font-size: 14px;
}

.contact-info-item:last-child {
  margin-bottom: 0;
}

.contact-info-item .label {
  color: #909399;
  min-width: 56px;
}

.contact-info-item .value {
  color: #303133;
  font-weight: 500;
}

/* 响应式适配 */
@media (max-width: 375px) {
  .login-card {
    margin: -36px 16px 0;
    padding: 24px 20px 28px;
  }
  
  .logo-circle {
    width: 76px;
    height: 76px;
  }
  
  .app-title {
    font-size: 24px;
  }
  
  .form-input {
    height: 48px;
    font-size: 15px;
  }
  
  .captcha-box {
    width: 100px;
    height: 48px;
  }
  
  .send-code-btn {
    width: 96px;
    height: 48px;
  }
  
  .login-btn {
    height: 50px;
    font-size: 16px;
  }
}
</style>