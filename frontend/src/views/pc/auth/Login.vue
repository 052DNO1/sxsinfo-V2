<!-- 用户登录页面 -->
<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-left">
        <div class="login-welcome">
          <h1>欢迎使用</h1>
          <h2>实训室信息管理系统</h2>
          <p>Lab Information Management System</p>
          <div class="decoration-circle"></div>
          <div class="decoration-circle-2"></div>
        </div>
      </div>
      
      <div class="login-right">
        <el-card class="login-card" shadow="never">
          <div class="login-header">
            <h3>用户登录</h3>
            <p>User Login</p>
          </div>

          <el-tabs v-model="loginType" stretch class="login-tabs-element">
            <el-tab-pane label="账号登录" name="account"></el-tab-pane>
            <el-tab-pane label="验证码登录" name="sms"></el-tab-pane>
          </el-tabs>

          <el-form @submit.prevent="handleLoginPC" :model="form" class="login-form" size="large">
            <!-- Account Login Fields -->
            <template v-if="loginType === 'account'">
              <el-form-item prop="username">
                <el-input 
                  v-model="form.username" 
                  placeholder="请输入用户名/手机号"
                  prefix-icon="User"
                  clearable
                  @input="handleUsernameInput"
                />
              </el-form-item>
              <el-form-item prop="password">
                <el-input 
                  type="password"
                  v-model="form.password" 
                  placeholder="请输入密码"
                  prefix-icon="Lock"
                  show-password
                  clearable
                />
              </el-form-item>
              <!-- Captcha -->
              <el-form-item prop="captcha">
                <div class="captcha-wrapper">
                  <el-input 
                    ref="captchaInputRef"
                    v-model="form.captcha" 
                    placeholder="请输入验证码"
                    class="captcha-input"
                    prefix-icon="Key"
                    maxlength="4"
                    @input="handleCaptchaInput"
                    @keyup.enter="handleLoginPC"
                    clearable
                  />
                  <div class="captcha-right">
                    <div class="captcha-display" @click="fetchCaptcha" title="点击刷新验证码">
                      <img 
                        v-if="captchaImage" 
                        :src="captchaImage" 
                        alt="验证码" 
                        class="captcha-image"
                      />
                      <span v-else class="captcha-loading">加载中...</span>
                    </div>
                    <div class="captcha-refresh">
                      <a href="javascript:void(0)" @click="fetchCaptcha">看不清？换一换</a> 
                      <span v-if="captchaLoaded" class="captcha-countdown">{{ captchaCountdown }}s后刷新</span>
                      <span v-else class="captcha-countdown captcha-error">点击刷新</span>
                    </div>
                  </div>
                </div>
              </el-form-item>
            </template>

            <!-- SMS Login Fields -->
            <template v-if="loginType === 'sms'">
              <el-form-item prop="phone">
                <el-input 
                  v-model="form.phone" 
                  placeholder="请输入手机号"
                  prefix-icon="Iphone"
                  clearable
                />
              </el-form-item>
              <el-form-item prop="code">
                <el-input 
                  v-model="form.code" 
                  placeholder="请输入验证码"
                  prefix-icon="Message"
                >
                  <template #append>
                    <el-button @click="handleSendCode" class="verify-code-btn">获取验证码</el-button>
                  </template>
                </el-input>
              </el-form-item>
            </template>

            <div class="login-options">
              <el-checkbox v-model="rememberMe">记住密码</el-checkbox>
              <a class="forgot-pwd" href="javascript:void(0)" @click="showForgotPasswordDialog">
                {{ loginType === 'sms' ? '收不到验证码?' : '忘记密码?' }}
              </a>
            </div>

            <el-dialog
              v-model="forgotPasswordDialogVisible"
              title="忘记密码"
              width="480px"
              :close-on-click-modal="true"
              center
            >
              <div class="forgot-password-content" v-loading="contactLoading">
                <el-tabs v-model="forgotPasswordTab" class="forgot-tabs">
                  <el-tab-pane label="密保找回" name="security">
                    <div v-if="securityStep === 'input_username'" class="security-step">
                      <el-form-item label="用户名">
                        <el-input v-model="securityForm.username" placeholder="请输入用户名" clearable />
                      </el-form-item>
                      <el-button type="primary" @click="checkSecurityQuestion" :loading="securityLoading">
                        下一步                
                      </el-button>
                    </div>
                    
                    <div v-else-if="securityStep === 'answer_question'" class="security-step">
                      <el-alert type="info" :closable="false" show-icon class="question-alert">
                        <template #title>{{ securityForm.question }}</template>
                      </el-alert>
                      <el-form-item label="答案">
                        <el-input v-model="securityForm.answer" placeholder="请输入密保答案" clearable />
                      </el-form-item>
                      <div class="step-buttons">
                        <el-button @click="securityStep = 'input_username'">上一步</el-button>
                        <el-button type="primary" @click="verifySecurityAnswer" :loading="securityLoading">
                          验证
                        </el-button>
                      </div>
                    </div>
                    
                    <div v-else-if="securityStep === 'reset_password'" class="security-step">
                      <el-result icon="success" title="验证成功" sub-title="请设置新密码">
                        <template #extra>
                          <el-form label-width="80px">
                            <el-form-item label="新密码">
                              <el-input v-model="securityForm.newPassword" type="password" placeholder="请输入新密码" show-password />
                            </el-form-item>
                            <el-form-item label="确认密码">
                              <el-input v-model="securityForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
                            </el-form-item>
                          </el-form>
                          <div class="step-buttons">
                            <el-button type="primary" @click="resetPasswordBySecurity" :loading="securityLoading">
                              重置密码
                            </el-button>
                          </div>
                        </template>
                      </el-result>
                    </div>
                    
                    <div v-else-if="securityStep === 'no_question'" class="security-step">
                      <el-empty description="该用户未设置密保问题">
                        <template #image>
                          <el-icon :size="60" color="#909399"><WarningFilled /></el-icon>
                        </template>
                        <el-button type="primary" @click="forgotPasswordTab = 'contact'">
                          请联系管理员
                        </el-button>
                      </el-empty>
                    </div>
                  </el-tab-pane>
                  
                  <el-tab-pane label="联系管理员" name="contact">
                    <el-icon class="warning-icon"><WarningFilled /></el-icon>
                    <p class="tip-text">{{ contactInfo.message || '如需重置密码，请联系管理员' }}</p>
                    <div class="contact-info" v-if="contactInfo.contact">
                      <p><el-icon><User /></el-icon> 联系人：{{ contactInfo.contact.name }}</p>
                      <p><el-icon><Phone /></el-icon> 电话：{{ contactInfo.contact.phone }}</p>
                      <p><el-icon><Message /></el-icon> 邮箱：{{ contactInfo.contact.email }}</p>
                      <p v-if="contactInfo.contact.depart"><el-icon><OfficeBuilding /></el-icon> 所属：{{ contactInfo.contact.depart }}</p>
                    </div>
                    <el-alert type="info" :closable="false" show-icon>
                      <template #title>管理员将验证您的身份后协助重置密码</template>
                    </el-alert>
                  </el-tab-pane>
                </el-tabs>
              </div>
              <template #footer>
                <el-button @click="forgotPasswordDialogVisible = false">关闭</el-button>
              </template>
            </el-dialog>

            <el-form-item>
              <el-button type="primary" class="login-button" @click="handleLoginPC" :loading="loading" round>
                {{ loading ? '登录中...' : '立即登录' }}
              </el-button>
            </el-form-item>

          </el-form>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useApi } from '@/core/hooks'
import { useAuth } from '@/core/hooks'
import { User, Lock, Key, Iphone, Message, Phone, WarningFilled, OfficeBuilding, InfoFilled } from '@element-plus/icons-vue'
import { translateErrorMessage, getLoginErrorMessage } from '@/core/utils/authUtils'
import { showSuccess, showError } from '@/core/utils/errorHandler'
import { ElNotification } from 'element-plus'
import { encryptPassword, isEncryptionEnabled } from '@/core/utils/crypto'

export default {
  name: 'Login',
  components: {
    User, Lock, Key, Iphone, Message, Phone, WarningFilled, OfficeBuilding, InfoFilled
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    const { login: authLogin, updateUser } = useAuth()
    
    const loginType = ref('account') // 'account' | 'sms'
    const rememberMe = ref(true)
    const forgotPasswordDialogVisible = ref(false)
    const forgotPasswordTab = ref('security')
    const contactLoading = ref(false)
    const contactInfo = ref({
      message: '',
      contact: null
    })
    
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
    const loading = ref(false)
    const captchaImage = ref('')
    const captchaKey = ref('')
    const captchaCountdown = ref(60)
    const captchaLoaded = ref(false)
    let captchaTimer = null

    const captchaInputRef = ref(null)

    onMounted(() => {
      document.body.classList.add('login-page')
      
      // 检查记住我
      const isRemember = localStorage.getItem('sxs_remember_me') === 'true'
      rememberMe.value = isRemember
      
      if (isRemember) {
        const savedUser = localStorage.getItem('sxs_username')
        // const savedPass = localStorage.getItem('sxs_password') // 已弃用不安全密码存储
        
        if (savedUser) form.value.username = savedUser
        // 密码需用户重新输入，或依赖浏览器自带的密码管理?
      }
    })
    onUnmounted(() => {
      document.body.classList.remove('login-page')
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
        captchaLoaded.value = false
        const { get: getCaptchaApi } = useApi('/auth/captcha/', { immediate: false })
        const response = await getCaptchaApi()
        
        if (response && response.success && response.data) {
          captchaImage.value = response.data.captcha_image
          captchaKey.value = response.data.captcha_key
          form.value.captcha = ''
          captchaLoaded.value = true
          startCaptchaTimer()
        } else {
          showError('验证码加载失败，请刷新重试')
        }
      } catch (err) {
        showError('验证码加载失败，请检查网络连接')
      }
    }

    const handleUsernameInput = (value) => {
      if (value) {
        form.value.username = value.replace(/[^a-zA-Z0-9@.\-_]/g, '')
      }
    }

    const handleCaptchaInput = (value) => {
      if (value) {
        form.value.captcha = value.replace(/[^a-zA-Z0-9]/g, '').toUpperCase().slice(0, 4)
      }
    }

    const handleSendCode = () => {
      if (!form.value.phone) {
        showError('请输入手机号')
        return
      }
      showSuccess('验证码已发送')
    }

    const showForgotPasswordDialog = async () => {
      if (!form.value.username) {
        showError('请先输入用户名')
        return
      }
      
      securityForm.value.username = form.value.username
      forgotPasswordTab.value = 'security'
      securityStep.value = 'input_username'
      forgotPasswordDialogVisible.value = true
      
      contactLoading.value = true
      contactInfo.value = { message: '正在查询联系人信息...', contact: null }
      
      try {
        const { get: getContactApi } = useApi('/auth/password-reset-contact/', { immediate: false })
        const response = await getContactApi({ username: form.value.username })
        
        if (response && response.success && response.data) {
          contactInfo.value = {
            message: response.message || '如需重置密码，请联系以下管理员',
            contact: response.data.contact
          }
        } else {
          contactInfo.value = {
            message: response?.message || '获取联系人信息失败',
            contact: null
          }
        }
      } catch (err) {
        contactInfo.value = {
          message: '获取联系人信息失败，请稍后重试',    
          contact: null
        }
      } finally {
        contactLoading.value = false
      }
    }
    
    const checkSecurityQuestion = async () => {
      if (!securityForm.value.username) {
        showError('请输入用户名')
        return
      }
      
      securityLoading.value = true
      try {
        const { post: getQuestionApi } = useApi('/auth/security-question/user/', { immediate: false })
        const response = await getQuestionApi({ username: securityForm.value.username })
        
        if (response && response.success && response.data) {
          if (response.data.has_question) {
            securityForm.value.question = response.data.question
            securityStep.value = 'answer_question'
          } else {
            securityStep.value = 'no_question'
          }
        } else {
          showError(response?.message || '查询失败')
        }
      } catch (err) {
        showError('查询失败，请稍后重试')
      } finally {
        securityLoading.value = false
      }
    }
    
    const verifySecurityAnswer = async () => {
      if (!securityForm.value.answer) {
        showError('请输入密保答案')
        return
      }
      
      securityLoading.value = true
      try {
        const { post: verifyApi } = useApi('/auth/security-question/verify/', { immediate: false })
        const response = await verifyApi({
          username: securityForm.value.username,
          answer: securityForm.value.answer
        })
        
        if (response && response.success && response.data) {
          securityForm.value.resetToken = response.data.reset_token
          securityStep.value = 'reset_password'
          showSuccess('验证成功')
        } else {
          showError(response?.message || '验证失败')
        }
      } catch (err) {
        showError('验证失败，请稍后重试')
      } finally {
        securityLoading.value = false
      }
    }
    
    const resetPasswordBySecurity = async () => {
      if (!securityForm.value.newPassword || !securityForm.value.confirmPassword) {
        showError('请填写完整信息')
        return
      }
      
      if (securityForm.value.newPassword !== securityForm.value.confirmPassword) {
        showError('两次密码不一致')
        return
      }
      
      securityLoading.value = true
      try {
        const { post: resetApi } = useApi('/auth/password/reset-by-security/', { immediate: false })
        const response = await resetApi({
          reset_token: securityForm.value.resetToken,
          new_password: securityForm.value.newPassword,
          confirm_password: securityForm.value.confirmPassword
        })
        
        if (response && response.success) {
          showSuccess('密码重置成功，请使用新密码登录')
          forgotPasswordDialogVisible.value = false
          securityStep.value = 'input_username'
          securityForm.value = {
            username: '',
            question: '',
            answer: '',
            resetToken: '',
            newPassword: '',
            confirmPassword: ''
          }
        } else {
          showError(response?.message || '重置失败')
        }
      } catch (err) {
        showError('重置失败，请稍后重试')
      } finally {
        securityLoading.value = false
      }
    }

    const handleLoginPC = async () => {
      if (loginType.value === 'sms') {
        if (!form.value.phone || !form.value.code) {
           showError('请输入手机号和验证码')
           return
        }
        showError('验证码登录功能暂未开放，请使用账号密码登录')
        return
      }

      const captchaValue = String(form.value.captcha || '').trim().toUpperCase()
      if (!captchaValue) {
        showError('请输入验证码')
        return
      }

      if (!captchaKey.value) {
        showError('验证码已过期，请刷新')
        fetchCaptcha()
        return
      }

      loading.value = true
      
      try {
        const encryptedPassword = encryptPassword(form.value.password)
        
        const { post: loginApi } = useApi('/auth/login/', { immediate: false })
        const response = await loginApi({
          username: form.value.username,
          password: encryptedPassword,
          captcha: captchaValue,
          captcha_key: captchaKey.value,
          remember_me: rememberMe.value,
          encrypted: isEncryptionEnabled()
        })
        
        if (response && response.success && response.data) {
          if (response.data.user) {
            updateUser(response.data.user)
          }
          if (response.data.access_token) {
             localStorage.setItem('access_token', response.data.access_token)
             if (response.data.refresh_token) localStorage.setItem('refresh_token', response.data.refresh_token)
          } else {
             showError('登录异常：未获取到安全令牌')
             loading.value = false
             return
          }

          if (response.data.first_login !== undefined) {
            sessionStorage.setItem('first_login', String(response.data.first_login))
          }
          
          if (rememberMe.value) {
            localStorage.setItem('sxs_remember_me', 'true')
            localStorage.setItem('sxs_username', form.value.username)
          } else {
            localStorage.removeItem('sxs_remember_me')
            localStorage.removeItem('sxs_username')
          }
          localStorage.removeItem('sxs_password')
          
          showSuccess(response.message || '登录成功，欢迎回来！')
          
          const redirectPath = response.data.redirect || '/'
          router.push(redirectPath)
        } else {
          const errorMsg = response?.message || '登录失败'
          showError(translateErrorMessage(errorMsg))
          fetchCaptcha()
          if (captchaInputRef.value) {
            captchaInputRef.value.focus()
          }
        }
      } catch (err) {
        const errorMsg = getLoginErrorMessage(err)
        showError(errorMsg)
        fetchCaptcha()
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      sessionStorage.removeItem('auth_redirecting')
      fetchCaptcha()
    })

    return {
      form,
      loading,
      loginType,
      rememberMe,
      handleLoginPC,
      handleSendCode,
      handleUsernameInput,
      handleCaptchaInput,
      captchaImage,
      captchaKey,
      captchaCountdown,
      captchaLoaded,
      fetchCaptcha,
      captchaInputRef,
      forgotPasswordDialogVisible,
      forgotPasswordTab,
      showForgotPasswordDialog,
      contactLoading,
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
.login-container {
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f2f5 0%, #e6f7ff 100%);
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: -100px;
  right: -100px;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(24,144,255,0.1) 0%, rgba(255,255,255,0) 70%);
  z-index: 0;
}

.login-container::after {
  content: '';
  position: absolute;
  bottom: -100px;
  left: -100px;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(54,207,201,0.1) 0%, rgba(255,255,255,0) 70%);
  z-index: 0;
}

.login-content {
  display: flex;
  width: 1000px;
  height: 600px;
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  z-index: 1;
  position: relative;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.login-welcome {
  color: #fff;
  text-align: center;
  z-index: 2;
  padding: 40px;
}

.login-welcome h1 {
  font-size: 36px;
  margin: 0 0 10px;
  font-weight: 300;
}

.login-welcome h2 {
  font-size: 32px;
  margin: 0 0 20px;
  font-weight: 700;
  letter-spacing: 2px;
}

.login-welcome p {
  font-size: 16px;
  opacity: 0.8;
  letter-spacing: 1px;
}

.loading-tip {
  margin-top: 30px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

.loading-tip .tip-icon {
  font-size: 16px;
}

.decoration-circle {
  position: absolute;
  top: -50px;
  left: -50px;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.decoration-circle-2 {
  position: absolute;
  bottom: -80px;
  right: -80px;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #fff;
}

.login-card {
  width: 100%;
  max-width: 400px;
  border: none;
}

:deep(.el-card__body) {
  padding: 0;
}

.login-header {
  margin-bottom: 30px;
  text-align: left;
}

.login-header h3 {
  font-size: 24px;
  color: #1a1a1a;
  margin: 0 0 8px;
  font-weight: 600;
}

.login-header p {
  font-size: 14px;
  color: #999;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.login-tabs-element {
  margin-bottom: 30px;
}

/* 移除旧的 login-tabs 样式 */

.login-form {
  margin-top: 20px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  background: #f5f7fa;
  box-shadow: none !important;
  border: 1px solid transparent;
  padding: 8px 15px;
  transition: all 0.3s;
}

:deep(.el-input__wrapper.is-focus) {
  background: #fff;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1) !important;
}

.captcha-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.captcha-input {
  flex: 1;
}

.captcha-input :deep(.el-input__wrapper) {
  padding: 4px 15px;
}

.captcha-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.captcha-display {
  min-width: 140px;
  height: 40px;
  background: #f0f9eb;
  border: 1px solid #b3e19d;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  overflow: hidden;
  position: relative;
}

.captcha-display:hover {
  background: #f6ffed;
}

.captcha-image {
  width: 140px;
  height: 40px;
  object-fit: contain;
}

.captcha-loading {
  font-size: 12px;
  color: #67c23a;
}

.captcha-refresh {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.captcha-refresh a {
  font-size: 11px;
  color: #909399;
  text-decoration: none;
  line-height: 1.2;
}

.captcha-refresh a:hover {
  color: #1890ff;
}

.captcha-countdown {
  font-size: 11px;
  color: #1890ff;
  line-height: 1.2;
}

.captcha-countdown.captcha-error {
  color: #ff4d4f;
  cursor: pointer;
}

.captcha-countdown.captcha-error:hover {
  text-decoration: underline;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.forgot-pwd {
  font-size: 14px;
  color: #1890ff;
  text-decoration: none;
}

.forgot-pwd:hover {
  text-decoration: underline;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 24px;
  background: linear-gradient(90deg, #1890ff 0%, #36cfc9 100%);
  border: none;
  margin-top: 10px;
  transition: all 0.3s;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(24, 144, 255, 0.3);
}

.forgot-password-content {
  text-align: center;
  padding: 10px 0;
}

.forgot-password-content .warning-icon {
  font-size: 48px;
  color: #e6a23c;
  margin-bottom: 16px;
}

.forgot-password-content .tip-text {
  font-size: 16px;
  color: #303133;
  margin-bottom: 20px;
}

.forgot-password-content .contact-info {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  text-align: left;
}

.forgot-password-content .contact-info p {
  margin: 8px 0;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 8px;
}

.forgot-password-content .contact-info .el-icon {
  color: #1890ff;
}

.forgot-tabs {
  min-height: 280px;
}

.security-step {
  padding: 10px 0;
}

.security-step .el-form-item {
  margin-bottom: 16px;
}

.security-step .el-button {
  width: 100%;
  margin-top: 8px;
}

.step-buttons {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.step-buttons .el-button {
  flex: 1;
  margin-top: 0;
}

.question-alert {
  margin-bottom: 16px;
}

.question-alert :deep(.el-alert__title) {
  font-size: 15px;
  font-weight: 500;
}

@media (max-width: 900px) {
  .login-content {
    width: 90%;
    height: auto;
    flex-direction: column;
  }
  
  .login-left {
    padding: 40px 20px;
    min-height: 200px;
  }
  
  .login-right {
    padding: 40px 20px;
  }
}
</style>
