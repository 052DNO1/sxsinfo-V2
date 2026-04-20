<template>
  <div class="mobile-page">
    <van-nav-bar title="修改密码" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-notice-bar v-if="isFirstLogin" left-icon="warning-o" color="#ff976a" background="#fffbe8">
        {{ firstLoginMessage || '由于您是新用户，请及时修改密码' }}
      </van-notice-bar>

      <van-cell-group inset title="密码要求">
        <van-cell title="至少8个字符" :value="requirements.length ? '✓' : ''" :value-class="requirements.length ? 'success-text' : ''" />
        <van-cell title="包含小写字母" :value="requirements.lowercase ? '✓' : ''" :value-class="requirements.lowercase ? 'success-text' : ''" />
        <van-cell title="包含大写字母" :value="requirements.uppercase ? '✓' : ''" :value-class="requirements.uppercase ? 'success-text' : ''" />
        <van-cell title="包含数字" :value="requirements.number ? '✓' : ''" :value-class="requirements.number ? 'success-text' : ''" />
      </van-cell-group>

      <van-cell-group inset title="修改密码">
        <van-field
          v-model="formData.old_pwd"
          type="password"
          label="当前密码"
          placeholder="请输入当前密码"
          clearable
          required
        />
        
        <van-field
          v-model="formData.new_pwd"
          type="password"
          label="新密码"
          placeholder="请输入新密码"
          clearable
          required
          @update:model-value="checkPasswordRequirementsFunc"
        />
        
        <van-field
          v-model="formData.confirm_pwd"
          type="password"
          label="确认密码"
          placeholder="请再次输入新密码"
          clearable
          required
        />
      </van-cell-group>

      <van-cell-group inset title="密保问题">
        <van-cell :title="hasSecurityQuestion ? '已设置' : '未设置'" :value="userSecurityQuestion" is-link @click="showSecurityDialog = true">
          <template #icon>
            <van-icon :name="hasSecurityQuestion ? 'passed' : 'warning-o'" :color="hasSecurityQuestion ? '#07c160' : '#ff976a'" style="margin-right: 8px" />
          </template>
        </van-cell>
      </van-cell-group>

      <div class="form-actions">
        <van-button type="primary" block round :loading="loading" @click="handleSubmit">
          确认修改
        </van-button>
      </div>
    </div>

    <van-popup v-model:show="showSecurityDialog" position="bottom" round style="height: 60%">
      <div class="security-popup">
        <van-nav-bar title="设置密保问题" left-arrow @click-left="showSecurityDialog = false" />
        
        <van-cell-group inset>
          <van-field
            v-model="securityForm.question"
            is-link
            readonly
            label="密保问题"
            placeholder="请选择密保问题"
            @click="showQuestionPicker = true"
          />
          
          <van-field
            v-model="securityForm.answer"
            label="答案"
            placeholder="请输入答案（2-50个字符）"
            maxlength="50"
            show-word-limit
          />
        </van-cell-group>

        <div class="popup-actions">
          <van-button type="primary" block :loading="securityLoading" @click="saveSecurityQuestion">
            保存
          </van-button>
        </div>
      </div>
    </van-popup>

    <van-popup v-model:show="showQuestionPicker" position="bottom" round>
      <van-picker
        title="选择密保问题"
        :columns="securityQuestions"
        @confirm="onQuestionConfirm"
        @cancel="showQuestionPicker = false"
      />
    </van-popup>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNavigation } from '@/core/utils/routeDecision'
import { useApi, useForm, useAuth } from '@/core/hooks'
import { showError, showSuccess } from '@/core/utils/errorHandler'
import { checkPasswordRequirements, validatePasswordStrength } from '@/core/utils/validators'

export default {
  name: 'ChangePassword',
  setup() {
    const router = useRouter()
    const { smartBack, goHome } = useNavigation()
    const { user, updateUser, logout } = useAuth()
    
    const { post: changePasswordApi } = useApi('/auth/password/change/', { immediate: false })
    const { form: formData, errors, isSubmitting: formLoading, handleSubmit: formHandleSubmit, clearFieldError } = useForm(
      { old_pwd: '', new_pwd: '', confirm_pwd: '' },
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
              showSuccess('密码修改成功，请重新登录')
              await logout()
            } else {
              showError(response?.message || '修改失败')
            }
          } catch (err) {
            throw err
          }
        }
      }
    )
    
    const loading = computed(() => formLoading.value)
    const requirements = ref({ length: false, lowercase: false, uppercase: false, number: false })
    const firstLoginMessage = ref('')
    const isFirstLogin = ref(false)
    
    const showSecurityDialog = ref(false)
    const showQuestionPicker = ref(false)
    const securityLoading = ref(false)
    const securityForm = ref({ question: '', answer: '' })
    const securityQuestions = ref([
      { text: '您的母亲姓名是？' },
      { text: '您的父亲姓名是？' },
      { text: '您的出生城市是？' },
      { text: '您的第一所学校名称是？' },
      { text: '您最喜欢的颜色是？' },
      { text: '您的宠物名字是？' },
      { text: '您的配偶姓名是？' },
      { text: '您的小学班主任姓名是？' }
    ])
    
    const hasSecurityQuestion = computed(() => user.value?.security_question && user.value.security_question !== '')
    const userSecurityQuestion = computed(() => user.value?.security_question || '')

    const isFormValid = computed(() => {
      return (
        formData.old_pwd &&
        formData.new_pwd &&
        formData.confirm_pwd &&
        formData.new_pwd === formData.confirm_pwd &&
        Object.values(requirements.value).every(v => v)
      )
    })

    const checkPasswordRequirementsFunc = () => {
      requirements.value = checkPasswordRequirements(formData.new_pwd)
    }

    const handleSubmit = async () => {
      if (!isFormValid.value) {
        showError('请确保密码符合要求')
        return
      }
      await formHandleSubmit()
    }

    const onQuestionConfirm = ({ selectedOptions }) => {
      securityForm.value.question = selectedOptions[0].text
      showQuestionPicker.value = false
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

    const goBack = () => router.go(-1)

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
      formData, errors, loading, requirements, firstLoginMessage, isFirstLogin,
      showSecurityDialog, showQuestionPicker, securityLoading, securityForm, securityQuestions,
      hasSecurityQuestion, userSecurityQuestion,
      checkPasswordRequirementsFunc, handleSubmit, saveSecurityQuestion, onQuestionConfirm,
      goBack, goHome
    }
  }
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

.success-text {
  color: #07c160;
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

.security-popup {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.popup-actions {
  padding: 16px;
  margin-top: auto;
}
</style>
