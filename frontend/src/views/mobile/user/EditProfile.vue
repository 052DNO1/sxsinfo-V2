<template>
  <div class="mobile-page">
    <van-nav-bar
      title="修改个人信息"
      left-arrow
      @click-left="goBack"
    >
      <template #right>
        <van-icon
          name="home-o"
          size="20"
          color="#4F6EF7"
          @click="goHome"
        />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <div class="form-hero form-hero--ocean">
        <div class="form-hero-icon">
          <van-icon
            name="edit"
            size="28"
          />
        </div>
        <h2>个人资料</h2>
        <p>更新您的账户信息</p>
      </div>

      <van-skeleton
        v-if="loading"
        :row="5"
        animated
      />

      <van-form
        v-else
        @submit="handleSubmit"
      >
        <div class="form-section animate-fade-in-up animate-delay-1">
          <div class="section-label">
            <span>🔐</span> 账户信息
          </div>
          <van-cell-group inset>
            <van-field
              v-model="formData.username"
              label="用户名"
              readonly
              disabled
            />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-2">
          <div class="section-label">
            <span>👤</span> 个人信息
          </div>
          <van-cell-group inset>
            <van-field
              v-model="formData.nickname"
              label="昵称"
              placeholder="请输入昵称"
              clearable
              :rules="[{required:true,message:'请输入昵称'}]"
            />
            <van-field
              v-model="formData.email"
              type="email"
              label="邮箱"
              required
              clearable
              :rules="emailRules"
            />
            <van-field
              v-model="formData.phone"
              type="tel"
              label="手机号"
              clearable
              :rules="phoneRules"
            />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-3">
          <div class="section-label">
            <span>📝</span> 其他信息
          </div>
          <van-cell-group inset>
            <van-field
              v-model="formData.memo"
              rows="3"
              autosize
              type="textarea"
              label="备注"
              show-word-limit
              :maxlength="200"
            />
          </van-cell-group>
        </div>

        <div class="form-actions">
          <van-button
            type="primary"
            block
            round
            size="large"
            :loading="submitting"
            native-type="submit"
            icon="success"
          >
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
import { useNavigation } from '@/core/utils/routeDecision'
import { useAuth } from '@/core/hooks'
import { userService } from '@/core/services/BaseService'
import { showSuccess, showError } from '@/core/utils/errorHandler'

const router = useRouter()
const { goHome, smartBack } = useNavigation()
const { user, updateUser } = useAuth()

const goBack = () => router.back()

const loading = ref(false)
const submitting = ref(false)

const emailRules = [{ required:true,message:'请输入邮箱' },{ pattern:/^[^\s@]+@[^\s@]+\.[^\s@]+$/,message:'请输入正确的邮箱格式' }]
const phoneRules = [{ pattern:/^1[3-9]\d{9}$/,message:'请输入正确的11位手机号码' }]
const formData = ref({ username:'', nickname:'', email:'', phone:'', memo:'' })

onMounted(async () => {
  loading.value = true
  if (user.value) Object.assign(formData.value, { username:user.value.username||'', nickname:user.value.nickname||user.value.nikename||'', email:user.value.email||'', phone:user.value.phone||'', memo:user.value.memo||'' })
  try {
    const res = await userService.get(user.value?.id)
    if (res?.data) Object.assign(formData.value, { username:res.data.username||'', nickname:res.data.nickname||res.data.nikename||'', email:res.data.email||'', phone:res.data.phone||'', memo:res.data.memo||'' })
  } catch(e){console.error(e)}
  finally{loading.value=false}
})

const handleSubmit = async () => {
  submitting.value = true
  try {
    await userService.update(user.value?.id, { nickname:formData.value.nickname, email:formData.value.email, phone:formData.value.phone, memo:formData.value.memo })
    showSuccess('保存成功')
    updateUser({...user.value,...formData.value})
    setTimeout(()=>smartBack(),1500)
  } catch(e){showError(e.message||'保存失败')}
  finally{submitting.value=false}
}
</script>

<style scoped>
.form-hero--ocean { background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); }
.form-hero { background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); padding: 28px 20px; margin: -12px -16px 20px; text-align: center; }
.form-hero-icon { width: 60px; height: 60px; border-radius: 50%; background: rgba(79,110,247,0.15); display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; color: #4F6EF7; backdrop-filter: blur(4px); }
.form-hero h2 { margin: 0 0 6px; font-size: 20px; font-weight: 700; color: #1a1a1a; }
.form-hero p { margin: 0; font-size: 13px; color: #4F6EF7; }
.form-section { margin-bottom: 8px; }
.section-label { display: flex; align-items: center; gap: 8px; padding: 10px 16px 6px; font-size: 13px; font-weight: 600; color: var(--mobile-text-secondary); }
.section-label span { font-size: 16px; }
</style>