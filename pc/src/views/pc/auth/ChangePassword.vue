<template>
  <!-- PC端使用Index组件 -->
  <Index class="pc-layout">
    <template #rightcontent>
      <el-card class="header-card" shadow="hover">
        <div class="listheader">
          <div class="header-title">
            <el-icon class="header-icon"><Lock /></el-icon>
            <span>修改密码</span>
          </div>
          
          <div class="listheader-actions">
            <el-button class="nav-action-btn" plain icon="HomeFilled" @click="goHome">首页</el-button>
          </div>
        </div>
      </el-card>

      <div class="password-container">
        <!-- Unified Split Panel Layout -->
        <div class="unified-panel-layout">
           <div class="unified-panel">
              <!-- Left Side: Prep & Guide -->
              <div class="panel-side">
                 <div class="side-header">
                    <h3><el-icon><InfoFilled /></el-icon> 安全提示</h3>
                    <p>定期修改密码可以保护您的账号安全</p>
                 </div>
                 
                 <div class="side-content">
                    <!-- New User Tip -->
                    <div v-if="isFirstLogin" class="side-block first-login-tip">
                      <div class="tip-icon-box">
                        <el-icon><Warning /></el-icon>
                      </div>
                      <div class="tip-content">
                        <div v-if="firstLoginMessage" class="tip-title">
                          {{ firstLoginMessage }}
                        </div>
                        <div class="tip-desc">
                          温馨提示：由于您是新用户，请及时修改密码，以确保您的账户安全。
                        </div>
                      </div>
                    </div>

                    <!-- Requirements -->
                    <div class="side-block">
                       <div class="block-title">1. 密码要求</div>
                       <div class="req-list">
                          <div class="req-item">
                             <span class="req-label">基本要求</span>
                             <div class="req-tags">
                                <el-tag size="small" type="danger" effect="plain">至少8个字符</el-tag>
                                <el-tag size="small" type="danger" effect="plain">包含数字</el-tag>
                             </div>
                          </div>
                          <div class="req-item">
                             <span class="req-label">强度要求</span>
                             <div class="req-tags">
                                <el-tag size="small" type="warning" effect="plain">包含小写字母</el-tag>
                                <el-tag size="small" type="warning" effect="plain">包含大写字母</el-tag>
                             </div>
                          </div>
                       </div>
                    </div>

                    <!-- Tips -->
                    <div class="side-block tips-block">
                       <div class="block-title"><el-icon><QuestionFilled /></el-icon> 常见问题</div>
                       <ul class="tips-list">
                          <li>建议使用由字母、数字和符号组成的强密码</li>
                          <li>请勿使用生日、手机号等容易被猜到的密码</li>
                          <li>如果您忘记了旧密码，请联系管理员重置</li>
                       </ul>
                    </div>
                    
                    <!-- Security Question -->
                    <div class="side-block security-block">
                       <div class="block-title">
                          <span><el-icon><Lock /></el-icon> 密保问题</span>
                          <el-tag v-if="hasSecurityQuestion" type="success" size="small" effect="dark">已设置</el-tag>
                          <el-tag v-else type="warning" size="small" effect="dark">未设置</el-tag>
                       </div>
                       <div class="security-content">
                          <p class="security-desc">
                            <el-icon><InfoFilled /></el-icon>
                            设置密保问题可在忘记密码时自助找回，无需联系管理员
                          </p>
                          <div v-if="hasSecurityQuestion" class="security-status">
                             <span class="security-label">当前问题</span>
                             <span class="security-question">{{ userSecurityQuestion }}</span>
                          </div>
                          <el-button 
                            :type="hasSecurityQuestion ? 'default' : 'primary'" 
                            plain 
                            size="default" 
                            @click="showSecurityDialog = true" 
                            class="security-btn">
                             <el-icon><Edit /></el-icon>
                             {{ hasSecurityQuestion ? '修改密保问题' : '立即设置' }}
                          </el-button>
                       </div>
                    </div>
                 </div>
              </div>

              <!-- Right Side: Action -->
              <div class="panel-main">
                 <div class="main-header">
                    <h3><el-icon><Lock /></el-icon> 重置密码</h3>
                 </div>
                 
                 <div class="main-content">
                    <div class="form-wrapper">
                      <el-form @submit.prevent="handleSubmit" :model="formData" label-position="top" class="password-form">
                        <el-form-item label="当前密码" prop="old_pwd" required>
                          <el-input
                            v-model="formData.old_pwd"
                            placeholder="请输入当前密码"
                            show-password
                            clearable
                            size="large"
                            class="custom-input"
                            @input="clearFieldError('old_pwd')"
                          />
                          <div v-if="errors.old_pwd" class="error-msg">{{ errors.old_pwd }}</div>
                        </el-form-item>

                        <el-form-item label="新密码" prop="new_pwd" required>
                          <el-input
                            v-model="formData.new_pwd"
                            placeholder="请输入新密码"
                            show-password
                            clearable
                            @input="checkPasswordRequirementsFunc"
                            size="large"
                            class="custom-input"
                          />
                          
                          <div class="password-feedback">
                            <div class="strength-bar-wrapper">
                              <div class="strength-info">
                                <span class="strength-text">安全强度</span>
                                <span :class="['strength-val', passwordStrength.className]">{{ passwordStrength.label }}</span>
                              </div>
                              <div class="strength-progress">
                                <div class="progress-track">
                                  <div class="progress-fill" :class="passwordStrength.className" :style="{ width: passwordStrength.percent + '%' }"></div>
                                </div>
                              </div>
                            </div>

                            <div class="requirements-grid">
                              <div class="req-item" :class="{ active: requirements.length }">
                                <span class="dot"></span> 至少8个字符
                              </div>
                              <div class="req-item" :class="{ active: requirements.lowercase }">
                                <span class="dot"></span> 包含小写字母
                              </div>
                              <div class="req-item" :class="{ active: requirements.uppercase }">
                                <span class="dot"></span> 包含大写字母
                              </div>
                              <div class="req-item" :class="{ active: requirements.number }">
                                <span class="dot"></span> 包含数字
                              </div>
                            </div>
                          </div>
                          <div v-if="errors.new_pwd" class="error-msg">{{ errors.new_pwd }}</div>
                        </el-form-item>

                        <el-form-item label="确认新密码" prop="confirm_pwd" required>
                          <el-input
                            v-model="formData.confirm_pwd"
                            placeholder="请再次输入新密码"
                            show-password
                            clearable
                            size="large"
                            class="custom-input"
                            @input="clearFieldError('confirm_pwd')"
                          />
                          <div v-if="formData.confirm_pwd && formData.new_pwd !== formData.confirm_pwd" class="error-msg">
                            两次输入的密码不一致
                          </div>
                          <div v-if="errors.confirm_pwd" class="error-msg">{{ errors.confirm_pwd }}</div>
                        </el-form-item>

                        <el-form-item style="margin-top: 40px;">
                          <!-- DEBUG: Removed :disabled for testing -->
                          <el-button type="primary" @click="handleSubmit" :loading="loading" class="submit-btn">
                            {{ loading ? '正在提交...' : '确认修改' }}
                          </el-button>
                        </el-form-item>
                      </el-form>
                    </div>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </template>
  </Index>

  <!-- Security Question Dialog -->
  <el-dialog v-model="showSecurityDialog" title="设置密保问题" width="500px">
    <div class="security-dialog-content">
      <el-alert type="info" :closable="false" show-icon class="security-alert">
        <template #title>
          <span class="alert-title">密保问题用于忘记密码时验证身份，请认真设置</span>
        </template>
      </el-alert>
      
      <el-form label-width="80px" class="security-form">
        <el-form-item label="密保问题" required>
          <el-select v-model="securityForm.question" placeholder="请选择密保问题" style="width: 100%">
            <el-option
              v-for="q in securityQuestions"
              :key="q"
              :label="q"
              :value="q"
            />
          </el-select>
          <div class="field-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>选择一个只有您知道答案的问题</span>
          </div>
        </el-form-item>
        
        <el-form-item label="答案" required>
          <el-input 
            v-model="securityForm.answer" 
            placeholder="请输入答案（2-50个字符）" 
            clearable 
            show-word-limit
            maxlength="50"
          />
          <div class="field-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>答案不区分大小写，请牢记您的答案</span>
          </div>
        </el-form-item>
      </el-form>
      
      <div class="security-tips">
        <div class="tips-title"><el-icon><Warning /></el-icon> 设置建议</div>
        <ul>
          <li>选择您容易记住但他人难以猜到的问题</li>
          <li>答案不要太简单，避免被轻易猜到</li>
          <li>不要使用公开信息作为答案（如公开的生日）</li>
        </ul>
      </div>
    </div>
    <template #footer>
      <el-button @click="showSecurityDialog = false">取消</el-button>
      <el-button type="primary" @click="saveSecurityQuestion" :loading="securityLoading">保存</el-button>
    </template>
  </el-dialog>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNavigation } from '@/core/utils/routeDecision'
import { Check, Close, Warning, InfoFilled, Lock, Back, HomeFilled, Edit, QuestionFilled } from '@element-plus/icons-vue'
import { useApi, useForm, useAuth } from '@/core/hooks'
import Index from '@/views/pc/dashboard/Index.vue'
import { showError, showWarning, showSuccess } from '@/core/utils/errorHandler'
import { validatePasswordStrength, checkPasswordRequirements } from '@/core/utils/validators'

export default {
  name: 'ChangePassword',
  components: {
    Index,
    Check,
    Close,
    Warning,
    InfoFilled,
    Lock,
    Back,
    HomeFilled,
    Edit,
    QuestionFilled
  },
  setup() {
    const router = useRouter()
    
    const { smartBack, goHome } = useNavigation()
    const { user, updateUser } = useAuth()
    
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
            const response = await changePasswordApi(data)
            if (response && response.success) {
              await showSuccess('密码修改成功，请重新登录')
              router.push('/login')
            } else {
              await showError(response?.message || '修改失败')
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
    
    const showSecurityDialog = ref(false)
    const securityLoading = ref(false)
    const securityForm = ref({
      question: '',
      answer: ''
    })
    const securityQuestions = ref([
      '您的母亲姓名是？',
      '您的父亲姓名是？',
      '您的出生城市是？',
      '您的第一所学校名称是？',
      '您最喜欢的颜色是？',
      '您的宠物名字是？',
      '您的配偶姓名是？',
      '您的小学班主任姓名是？'
    ])
    
    const hasSecurityQuestion = computed(() => {
      return user.value?.security_question && user.value.security_question !== ''
    })
    
    const userSecurityQuestion = computed(() => {
      return user.value?.security_question || ''
    })

    const isFormValid = computed(() => {
      return (
        formData.old_pwd &&
        formData.new_pwd &&
        formData.confirm_pwd &&
        formData.new_pwd === formData.confirm_pwd &&
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

    const checkPasswordRequirementsFunc = () => {
      clearFieldError('new_pwd')
      const pwd = formData.new_pwd
      requirements.value = checkPasswordRequirements(pwd)
    }

    const passwordStrength = computed(() => {
      const pwd = formData.new_pwd || ''
      return validatePasswordStrength(pwd)
    })

    const handleSubmit = async () => {
      if (!formData.old_pwd) {
        showError('请输入当前密码')
        return
      }
      if (!formData.new_pwd) {
        showError('请输入新密码')
        return
      }
      if (!formData.confirm_pwd) {
        showError('请确认新密码')
        return
      }
      if (formData.new_pwd !== formData.confirm_pwd) {
        showError('两次输入的密码不一致')
        return
      }
      if (!Object.values(requirements.value).every(v => v)) {
        const missing = []
        if (!requirements.value.length) missing.push('至少8个字符')
        if (!requirements.value.lowercase) missing.push('包含小写字母')
        if (!requirements.value.uppercase) missing.push('包含大写字母')
        if (!requirements.value.number) missing.push('包含数字')
        showError(`密码强度不足，需要：${missing.join('、')}`)
        return
      }
      
      try {
        await formHandleSubmit()
      } catch (e) {
        // 错误已由 useApi 处理
      }
    }

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
    
    const saveSecurityQuestion = async () => {
      if (!securityForm.value.question) {
        showError('请选择密保问题')
        return
      }
      if (!securityForm.value.answer) {
        showError('请输入答案')
        return
      }
      
      securityLoading.value = true
      try {
        const { post: saveApi } = useApi('/auth/security-question/', { immediate: false })
        const response = await saveApi({
          question: securityForm.value.question,
          answer: securityForm.value.answer
        })
        
        if (response && response.success) {
          const savedQuestion = securityForm.value.question
          showSuccess('设置成功')
          showSecurityDialog.value = false
          securityForm.value = { question: '', answer: '' }
          updateUser({ ...user.value, security_question: savedQuestion })
        } else {
          showError(response?.message || '设置失败')
        }
      } catch (err) {
        showError('设置失败')
      } finally {
        securityLoading.value = false
      }
    }

    onMounted(async () => {
      const savedFirstLogin = sessionStorage.getItem('first_login')
      if (savedFirstLogin === 'true') {
        isFirstLogin.value = true
        await fetchFirstLoginInfo()
      } else {
        await fetchFirstLoginInfo()
      }
    })

    return {
      formData,
      errors,
      loading,
      showNewPassword,
      showConfirmPassword,
      showOldPassword,
      requirements,
      passwordStrength,
      isFormValid,
      firstLoginMessage,
      isFirstLogin,
      togglePasswordVisibility,
      checkPasswordRequirementsFunc,
      handleSubmit,
      smartBack,
      goHome,
      clearFieldError,
      showSecurityDialog,
      securityLoading,
      securityForm,
      securityQuestions,
      hasSecurityQuestion,
      userSecurityQuestion,
      saveSecurityQuestion
    }
  }
}
</script>

<style scoped>
  

/* Override the global container limit if needed */
  .password-container {
    max-width: 100% !important;
    padding: 20px;
    position: relative;
    z-index: 1;
  }

.header-card {
  margin-bottom: 20px;
  border-radius: 12px;
  border: none;
}

.listheader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.header-title {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.header-icon {
  margin-right: 10px;
  color: #1890ff;
  font-size: 24px;
}

.listheader-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

/* Unified Panel Layout */
.unified-panel-layout {
  display: flex;
  justify-content: center;
  padding: 0;
  min-height: auto;
}

.unified-panel {
  width: 100%;
  max-width: 1600px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
  border: 1px solid #ebeef5;
  display: flex;
  overflow: hidden;
  height: calc(100vh - 140px);
  max-height: 700px;
  min-height: 500px;
  margin-top: 10px;
}

/* Left Side: Prep & Guide */
.panel-side {
  flex: 0 0 400px;
  background-color: #f8f9fb;
  border-right: 1px solid #eef0f5;
  display: flex;
  flex-direction: column;
}

.side-header {
  padding: 24px 24px 16px;
  border-bottom: 1px solid #eef0f5;
}

.side-header h3 {
  margin: 0 0 6px;
  font-size: 18px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.side-header p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.side-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.side-block {
  display: flex;
  flex-direction: column;
}

.block-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
}

.req-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.req-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.req-label {
  font-size: 12px;
  color: #909399;
}

.req-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tips-block {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
}

.tips-list {
  margin: 0;
  padding-left: 18px;
  font-size: 13px;
  color: #606266;
}

.tips-list li {
  margin-bottom: 6px;
  line-height: 1.5;
}

/* Right Side: Action */
.panel-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

.main-header {
  padding: 24px 32px;
  border-bottom: 1px solid #f5f7fa;
}

.main-header h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-content {
  flex: 1;
  padding: 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center; /* Center content vertically */
  overflow-y: auto;
}

.form-wrapper {
  width: 100%;
  max-width: 500px;
}

.password-form :deep(.el-form-item) {
  margin-bottom: 24px;
}

.password-form :deep(.el-form-item__label) {
  padding-bottom: 8px;
  font-size: 15px;
  color: #606266;
  font-weight: 500;
}

.custom-input :deep(.el-input__wrapper) {
  padding: 8px 16px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  transition: all 0.2s;
  background-color: #fcfcfc;
}

.custom-input :deep(.el-input__wrapper:hover) {
  background-color: #fff;
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  background-color: #fff;
  box-shadow: 0 0 0 1px #409eff inset !important; /* Brand color */
}

.custom-input :deep(.el-input__inner) {
  height: 32px;
  font-size: 15px;
  font-weight: 500;
}

.error-msg {
  color: #f56c6c;
  font-size: 13px;
  margin-top: 6px;
  line-height: 1.4;
}

/* Password Strength Bar */
.password-feedback {
  margin-top: 12px;
}

.strength-bar-wrapper {
  margin-bottom: 20px;
}

.strength-info {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  margin-bottom: 8px;
  color: #909399;
}

.strength-val {
  font-weight: 600;
  font-size: 13px;
}
.strength-val.weak { color: #f56c6c; }
.strength-val.medium { color: #e6a23c; }
.strength-val.good { color: #67c23a; }
.strength-val.strong { color: #67c23a; }

.strength-progress {
  height: 4px;
  background: #f0f2f5;
  border-radius: 2px;
  overflow: hidden;
}

.progress-track {
  height: 100%;
  width: 100%;
}

.progress-fill {
  height: 100%;
  border-radius: 2px;
  transition: all 0.3s ease;
}
.progress-fill.weak { background: #f56c6c; }
.progress-fill.medium { background: #e6a23c; }
.progress-fill.good { background: #67c23a; }
.progress-fill.strong { background: #67c23a; }

/* Requirements Grid */
.requirements-grid {
  display: flex;
  flex-wrap: nowrap; /* 强制不换行 */
  justify-content: space-between; /* 两端对齐或改成 flex-start + gap */
  gap: 12px;
}

.req-item {
  display: flex;
  align-items: center;
  font-size: 12px; /* 稍微调小一点以确保能放下 */
  color: #909399;
  transition: all 0.3s;
  white-space: nowrap; /* 防止文字折行 */
}

.req-item .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #dcdfe6;
  margin-right: 8px;
  transition: all 0.3s;
}

.req-item.active {
  color: #67c23a;
}

.req-item.active .dot {
  background: #67c23a;
  box-shadow: 0 0 0 2px rgba(103, 194, 58, 0.2);
}

/* Submit Button */
.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
  letter-spacing: 1px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s;
}

.submit-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

.submit-btn:active {
  transform: translateY(0);
}

/* First Login Tip */
.first-login-tip {
  padding: 16px;
  background: #fff8e6;
  border-radius: 8px;
  display: flex;
  gap: 12px;
  border: 1px solid #ffeed0;
}

.tip-icon-box {
  color: #faad14;
  font-size: 20px;
  padding-top: 2px;
}

.tip-content {
  flex: 1;
}

.tip-title {
  font-weight: 600;
  color: #d48806;
  margin-bottom: 4px;
  font-size: 14px;
}

.tip-desc {
  font-size: 13px;
  color: #d48806;
  line-height: 1.5;
  opacity: 0.9;
}

/* Security Question Block */
.security-block {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #7dd3fc;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(56, 189, 248, 0.1);
}

.security-block .block-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.security-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.security-desc {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  margin: 0;
  font-size: 13px;
  color: #0369a1;
  line-height: 1.5;
}

.security-desc .el-icon {
  margin-top: 2px;
  flex-shrink: 0;
}

.security-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 6px;
}

.security-label {
  font-size: 13px;
  color: #64748b;
  flex-shrink: 0;
}

.security-question {
  font-size: 13px;
  color: #1e40af;
  font-weight: 500;
}

.security-btn {
  align-self: flex-start;
  margin-top: 4px;
}

/* Security Dialog Styles */
.security-dialog-content {
  padding: 0 8px;
}

.security-alert {
  margin-bottom: 20px;
}

.security-alert .alert-title {
  font-size: 14px;
  font-weight: 500;
}

.security-form {
  margin-bottom: 16px;
}

.security-form .el-form-item {
  margin-bottom: 20px;
}

.field-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}

.field-tip .el-icon {
  font-size: 14px;
}

.security-tips {
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px 16px;
}

.security-tips .tips-title {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
}

.security-tips ul {
  margin: 0;
  padding-left: 18px;
  font-size: 12px;
  color: #909399;
  line-height: 1.8;
}

@media (max-width: 900px) {
  .unified-panel {
    flex-direction: column;
    height: auto;
    max-height: none;
  }
  .panel-side {
    flex: none;
    border-right: none;
    border-bottom: 1px solid #eef0f5;
  }
}
</style>
