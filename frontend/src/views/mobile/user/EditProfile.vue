<template>
  <div class="mobile-edit-profile-page mobile-layout">
    <van-nav-bar
      title="编辑资料"
      left-arrow
      @click-left="goBack"
      class="mobile-nav-bar"
    >
      <template #right>
        <van-button size="small" type="primary" :loading="saving" @click="handleSave">
          保存
        </van-button>
      </template>
    </van-nav-bar>

    <div v-if="loading" class="mobile-loading-container">
      <van-loading size="24px" vertical>加载中...</van-loading>
    </div>

    <div v-else class="edit-form-container">
      <!-- 头像修改 -->
      <div class="avatar-section">
        <div class="avatar-wrapper">
          <van-image
            round
            width="80px"
            height="80px"
            :src="formData.avatar || defaultAvatar"
            class="user-avatar"
          >
            <template #error>
              <van-icon name="user-o" size="40" color="#ccc" />
            </template>
          </van-image>
          <van-uploader 
            :after-read="onAvatarRead" 
            :max-count="1"
            class="avatar-uploader"
          >
            <van-icon name="photograph" class="change-avatar-icon" />
          </van-uploader>
        </div>
        <p class="avatar-tip">点击更换头像</p>
      </div>

      <!-- 编辑表单 -->
      <van-form ref="formRef" class="edit-form">
        <van-cell-group inset>
          <van-field
            v-model="formData.nickname"
            name="nickname"
            label="姓名"
            placeholder="请输入姓名"
            :rules="[{ required: true, message: '请输入姓名' }]"
            clearable
          />
          
          <van-field
            v-model="formData.email"
            name="email"
            label="邮箱"
            type="email"
            placeholder="请输入邮箱"
            :rules="[
              { pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: '请输入正确的邮箱格式' }
            ]"
            clearable
          />
          
          <van-field
            v-model="formData.phone"
            name="phone"
            label="手机号"
            type="tel"
            placeholder="请输入手机号"
            :rules="[
              { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的11位手机号' }
            ]"
            clearable
          />

          <van-field
            v-model="formData.bio"
            name="bio"
            label="个人简介"
            type="textarea"
            rows="3"
            autosize
            placeholder="介绍一下自己吧..."
            show-word-limit
            maxlength="200"
          />
        </van-cell-group>

        <!-- 提示信息 -->
        <div class="form-tips">
          <p>💡 温馨提示：</p>
          <ul>
            <li>修改后的信息需要管理员审核</li>
            <li>邮箱和手机号可用于找回密码</li>
            <li>请填写真实信息以便联系</li>
          </ul>
        </div>
      </van-form>

      <!-- 保存按钮（底部固定） -->
      <div class="save-button-area">
        <van-button
          round
          block
          type="primary"
          :loading="saving"
          :disabled="!isFormValid"
          @click="handleSave"
          class="save-button"
        >
          {{ saving ? '保存中...' : '保存修改' }}
        </van-button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi, useAuth } from '@/core/hooks'
import { useMobile } from '@/composables/useMobile'
import { showSuccessToast, showFailToast } from '@/utils/mobileDialog'

export default {
  name: 'MobileEditProfile',
  setup() {
    const router = useRouter()
    const { user, updateUser } = useAuth()
    
    // 移动端初始化
    const { init: initMobile, loadVantComponents } = useMobile()
    
    // API 实例
    const apiComposable = useApi('', { immediate: false })
    
    // UI 状态
    const formRef = ref(null)
    const loading = ref(false)
    const saving = ref(false)
    const defaultAvatar = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'

    // 表单数据
    const formData = reactive({
      nickname: '',
      email: '',
      phone: '',
      bio: '',
      avatar: ''
    })

    // 表单验证状态
    const isFormValid = computed(() => {
      return formData.nickname && formData.nickname.trim().length > 0
    })

    // 加载当前用户数据
    const loadUserData = async () => {
      loading.value = true
      
      try {
        if (user.value) {
          // 从 useAuth 获取的用户信息填充表单
          formData.nickname = user.value.nickname || ''
          formData.email = user.value.email || ''
          formData.phone = user.value.phone || ''
          formData.bio = user.value.bio || ''
          formData.avatar = user.value.avatar || ''
        }
        
        loading.value = false
      } catch (err) {
        console.error('加载用户数据失败:', err)
        loading.value = false
      }
    }

    // 头像上传处理
    const onAvatarRead = async (file) => {
      try {
        // 这里可以添加头像上传逻辑
        // 暂时使用本地预览
        if (file.content) {
          formData.avatar = file.content
          await showSuccessToast('头像已选择，保存后生效')
        }
      } catch (err) {
        console.error('头像处理失败:', err)
        await showFailToast('头像处理失败')
      }
    }

    // 保存修改
    const handleSave = async () => {
      if (saving.value) return
      
      // 表单验证
      if (formRef.value) {
        try {
          await formRef.value.validate()
        } catch (err) {
          return
        }
      }
      
      saving.value = true
      
      try {
        // 准备提交数据
        const submitData = {
          nickname: formData.nickname.trim(),
          email: formData.email.trim(),
          phone: formData.phone.trim(),
          bio: formData.bio.trim()
        }
        
        // 如果有新头像
        if (formData.avatar && !formData.avatar.startsWith('http')) {
          submitData.avatar = formData.avatar
        }

        // 调用API更新用户信息
        const response = await apiComposable.put(submitData, {
          url: '/users/profile/',
          resourceType: 'users'
        })

        if (response && response.success) {
          // 更新本地用户状态
          if (updateUser && response.data) {
            updateUser(response.data)
          }
          
          await showSuccessToast('资料更新成功')
          
          // 延迟返回上一页
          setTimeout(() => {
            router.go(-1)
          }, 1500)
        } else {
          await showFailToast(response?.message || '更新失败，请稍后重试')
        }
      } catch (err) {
        console.error('保存失败:', err)
        await showFailToast(err.message || '保存失败，请检查网络连接')
      } finally {
        saving.value = false
      }
    }

    const goBack = () => {
      router.go(-1)
    }

    // 初始化
    onMounted(() => {
      initMobile()
      loadVantComponents()
      loadUserData()
    })

    return {
      formRef,
      loading,
      saving,
      formData,
      defaultAvatar,
      isFormValid,
      onAvatarRead,
      handleSave,
      goBack
    }
  }
}
</script>

<style scoped>
@import '@/assets/css/mobile.css';

.mobile-edit-profile-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.edit-form-container {
  padding-bottom: 100px;
}

.avatar-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 30px 20px 25px;
  text-align: center;
  color: white;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 10px;
}

.user-avatar {
  border: 4px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.change-avatar-icon {
  position: absolute;
  bottom: 2px;
  right: 2px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 50%;
  padding: 6px;
  font-size: 14px;
  color: #667eea;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  cursor: pointer;
}

.avatar-uploader {
  position: absolute;
  bottom: 0;
  right: 0;
  opacity: 0;
  width: 40px;
  height: 40px;
}

.avatar-tip {
  margin: 0;
  font-size: 13px;
  opacity: 0.85;
}

.edit-form {
  margin-top: -15px;
  position: relative;
  z-index: 10;
}

.form-tips {
  margin: 16px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  border-radius: 10px;
  font-size: 13px;
  color: #555;
  line-height: 1.7;
}

.form-tips p {
  margin: 0 0 8px 0;
  font-weight: 600;
  color: #1976d2;
}

.form-tips ul {
  margin: 0;
  padding-left: 18px;
}

.form-tips li {
  margin-bottom: 4px;
}

.save-button-area {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 16px;
  background: white;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.save-button {
  height: 48px;
  font-size: 17px;
  font-weight: 600;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border: none;
  letter-spacing: 1px;
}
</style>
