<template>
  <div class="mobile-login-wrapper">
    <!-- 顶部区域 -->
    <div class="mobile-login-header">
      <h1 class="system-title">实训室使用信息管理系统</h1>
    </div>
    
    <!-- 中间区域 - 登录表单 -->
    <div class="mobile-login-main">
      <div class="login-card">
        <div class="login-title-section">
          <h2 class="login-title">账号登录</h2>
          <p class="login-subtitle">欢迎回来，请输入账号密码</p>
        </div>
        
        <van-form @submit="handleLogin" class="login-form">
          <div class="form-fields">
            <van-field
              v-model="form.username"
              name="username"
              placeholder="请输入用户名/手机号"
              left-icon="user-o"
              :rules="[{ required: true, message: '请填写用户名' }]"
              class="custom-field"
              @input="handleUsernameInput"
            />
            
            <van-field
              v-model="form.password"
              type="password"
              name="password"
              placeholder="请输入密码"
              left-icon="lock"
              :right-icon="showPassword ? 'eye-o' : 'closed-eye'"
              @click-right-icon="showPassword = !showPassword"
              :rules="[{ required: true, message: '请填写密码' }]"
              class="custom-field"
            />

            <!-- 验证码 -->
            <van-field
              v-model="form.captcha"
              name="captcha"
              placeholder="请输入验证码"
              left-icon="shield-o"
              :rules="[{ required: true, message: '请填写验证码' }]"
              class="custom-field captcha-field"
              maxlength="4"
              @input="handleCaptchaInput"
            >
              <template #button>
                <div class="captcha-display" @click="fetchCaptcha" title="点击刷新验证码">
                  <img 
                    v-if="captchaImage" 
                    :src="captchaImage" 
                    alt="验证码" 
                    class="captcha-image"
                  />
                  <span v-else class="captcha-loading">加载中...</span>
                </div>
              </template>
            </van-field>

            <!-- 记住我 -->
            <div class="remember-me-wrapper">
              <van-checkbox v-model="rememberMe" shape="square">记住用户名</van-checkbox>
            </div>
          </div>
          
          <div class="login-button-wrapper">
            <van-button 
              round 
              block 
              type="primary" 
              native-type="submit" 
              :loading="loading"
              class="login-button"
            >
              {{ loading ? '登录中...' : '登录' }}
            </van-button>
          </div>

          <div class="forgot-password-wrapper">
            <a href="javascript:void(0)" @click="showForgotPasswordDialog" class="forgot-password-link">
              忘记密码？
            </a>
          </div>
        </van-form>
      </div>
    </div>
    
    <!-- 底部区域 -->
    <div class="mobile-login-footer">
      <p class="footer-text">&copy; 2024 信息管理系统</p>
      <p class="footer-copyright">版权所有 ****学院</p>
    </div>

    <!-- 忘记密码弹窗 -->
    <van-dialog
      v-model:show="forgotPasswordVisible"
      title="忘记密码"
      show-cancel-button
      :confirmButtonText="'联系管理员'"
      :cancelButtonText="'密保找回'"
      @confirm="contactAdmin"
      @cancel="securityRecovery"
    >
      <div style="padding: 16px;">
        <p>您可以通过以下方式重置密码：</p>
        <ul style="margin: 8px 0; padding-left: 20px; color: #666;">
          <li>使用密保问题自助找回</li>
          <li>联系管理员协助重置</li>
        </ul>
        <div v-if="contactInfo.message" style="margin-top: 12px; padding: 12px; background: #f5f7fa; border-radius: 8px;">
          <p style="margin: 0; font-size: 14px;">{{ contactInfo.message }}</p>
          <div v-if="contactInfo.contact" style="margin-top: 8px;">
            <p v-if="contactInfo.contact.name" style="margin: 4px 0; font-size: 13px;">
              联系人：{{ contactInfo.contact.name }}
            </p>
            <p v-if="contactInfo.contact.phone" style="margin: 4px 0; font-size: 13px;">
              电话：{{ contactInfo.contact.phone }}
            </p>
          </div>
        </div>
      </div>
    </van-dialog>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi, useAuth } from '@/core/hooks'
import { useMobile } from '@/composables/useMobile'
import { showSuccessToast, showFailToast, showConfirmDialog } from '@/utils/mobileDialog'
import { encryptPassword, isEncryptionEnabled } from '@/core/utils/crypto'

export default {
  name: 'MobileLogin',
  setup() {
    const router = useRouter()
    const { login: authLogin, updateUser } = useAuth()
    
    const form = ref({
      username: '',
      password: '',
      captcha: ''
    })
    const loading = ref(false)
    const showPassword = ref(false)
    const rememberMe = ref(true)
    const forgotPasswordVisible = ref(false)
    
    // 验证码相关
    const captchaImage = ref('')
    const captchaKey = ref('')
    let captchaTimer = null
    
    // 联系信息
    const contactInfo = ref({
      message: '',
      contact: null
    })
    
    const { loadVantComponents, init: initMobile } = useMobile()

    // 获取验证码
    const fetchCaptcha = async () => {
      try {
        const { get: getCaptchaApi } = useApi('/auth/captcha/', { immediate: false })
        const response = await getCaptchaApi()
        
        if (response && response.success && response.data) {
          captchaImage.value = response.data.captcha_image
          captchaKey.value = response.data.captcha_key
          form.value.captcha = ''
          startCaptchaTimer()
        } else {
          showFailToast('验证码加载失败，请刷新重试')
        }
      } catch (err) {
        showFailToast('验证码加载失败，请检查网络连接')
      }
    }

    const startCaptchaTimer = () => {
      if (captchaTimer) {
        clearInterval(captchaTimer)
      }
      captchaTimer = setInterval(() => {
        fetchCaptcha()
      }, 60000) // 60秒后自动刷新
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

    // 显示忘记密码对话框
    const showForgotPasswordDialog = async () => {
      if (!form.value.username) {
        showFailToast('请先输入用户名')
        return
      }
      
      forgotPasswordVisible.value = true
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
      }
    }

    // 联系管理员
    const contactAdmin = () => {
      forgotPasswordVisible.value = false
      showSuccessToast('请联系管理员重置密码')
    }

    // 密保找回（简化版）
    const securityRecovery = () => {
      forgotPasswordVisible.value = false
      showSuccessToast('密保找回功能开发中，请联系管理员')
    }

    // 登录处理
    const handleLogin = async () => {
      loading.value = true
      
      try {
        const encryptedPassword = encryptPassword(form.value.password)
        
        const { post: loginApi } = useApi('/auth/login/', { immediate: false })
        const response = await loginApi({
          username: form.value.username,
          password: encryptedPassword,
          captcha: form.value.captcha.toUpperCase(),
          captcha_key: captchaKey.value,
          remember_me: rememberMe.value,
          encrypted: isEncryptionEnabled()
        })
        
        if (response && response.success && response.data) {
          if (response.data.user) {
            updateUser(response.data.user)
          }
          
          // 存储Token
          if (response.data.access_token) {
             localStorage.setItem('access_token', response.data.access_token)
             if (response.data.refresh_token) localStorage.setItem('refresh_token', response.data.refresh_token)
          } else {
             showFailToast('登录异常：未获取到安全令牌')
             loading.value = false
             return
          }

          // 首次登录标记
          if (response.data.first_login !== undefined) {
            sessionStorage.setItem('first_login', String(response.data.first_login))
          }
          
          // 记住我
          if (rememberMe.value) {
            localStorage.setItem('sxs_remember_me', 'true')
            localStorage.setItem('sxs_username', form.value.username)
          } else {
            localStorage.removeItem('sxs_remember_me')
            localStorage.removeItem('sxs_username')
          }
          
          await showSuccessToast({ message: '登录成功', duration: 2000 })
          
          const redirectPath = response.data.redirect || '/'
          setTimeout(() => {
            router.push(redirectPath)
          }, 2000)
        } else {
          const errorMsg = response?.message || '登录失败'
          showFailToast(errorMsg)
          fetchCaptcha()
        }
      } catch (err) {
        console.error('Login error:', err)
        let errorMsg = '登录失败'
        if (err.response?.data?.message) {
          errorMsg = err.response.data.message
        } else if (err.message) {
          errorMsg = err.message
        }
        showFailToast(errorMsg)
        fetchCaptcha()
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      sessionStorage.removeItem('auth_redirecting')
      
      // 检查记住我
      const isRemember = localStorage.getItem('sxs_remember_me') === 'true'
      rememberMe.value = isRemember
      
      if (isRemember) {
        const savedUser = localStorage.getItem('sxs_username')
        if (savedUser) form.value.username = savedUser
      }
      
      const cleanup = initMobile()
      onUnmounted(() => {
        cleanup()
        if (captchaTimer) clearInterval(captchaTimer)
      })
      
      setTimeout(() => {
        loadVantComponents()
        fetchCaptcha()
      }, 200)
    })

    return {
      form,
      loading,
      showPassword,
      rememberMe,
      forgotPasswordVisible,
      contactInfo,
      captchaImage,
      fetchCaptcha,
      handleUsernameInput,
      handleCaptchaInput,
      showForgotPasswordDialog,
      contactAdmin,
      securityRecovery,
      handleLogin
    }
  }
}
</script>

<style scoped>
.mobile-login-wrapper {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
}

.mobile-login-header {
  padding: 60px 20px 40px;
  text-align: center;
}

.system-title {
  color: white;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.mobile-login-main {
  flex: 1;
  padding: 0 20px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-bottom: 40px;
}

.login-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.15);
  width: 100%;
  max-width: 400px;
  padding: 32px 24px;
}

.login-title-section {
  text-align: center;
  margin-bottom: 28px;
}

.login-title {
  font-size: 22px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.login-subtitle {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.form-fields {
  margin-bottom: 20px;
}

.custom-field {
  margin-bottom: 16px !important;
  border-radius: 10px;
  overflow: hidden;
}

.captcha-field .van-field__body {
  display: flex;
  align-items: center;
  gap: 12px;
}

.captcha-display {
  min-width: 120px;
  height: 40px;
  background: #f0f9eb;
  border: 1px solid #b3e19d;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  flex-shrink: 0;
}

.captcha-display:active {
  transform: scale(0.95);
}

.captcha-image {
  width: 120px;
  height: 40px;
  object-fit: contain;
}

.captcha-loading {
  font-size: 12px;
  color: #67c23a;
}

.remember-me-wrapper {
  margin: 12px 0 20px;
  padding: 0 4px;
}

.login-button-wrapper {
  margin-top: 8px;
}

.login-button {
  height: 48px;
  font-size: 17px;
  font-weight: 500;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border: none;
  letter-spacing: 2px;
}

.forgot-password-wrapper {
  text-align: right;
  margin-top: 16px;
}

.forgot-password-link {
  color: #667eea;
  font-size: 14px;
  text-decoration: none;
}

.forgot-password-link:active {
  opacity: 0.7;
}

.mobile-login-footer {
  text-align: center;
  padding: 30px 20px;
  color: rgba(255,255,255,0.8);
}

.footer-text {
  font-size: 14px;
  margin: 0 0 6px 0;
}

.footer-copyright {
  font-size: 12px;
  margin: 0;
  opacity: 0.7;
}
</style>
