<template>
  <div class="mobile-page">
    <van-nav-bar
      title="添加分院"
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
      <div class="form-hero form-hero--purple">
        <div class="form-hero-icon">
          <van-icon
            name="hotel-o"
            size="28"
          />
        </div>
        <h2>新增分院</h2>
        <p>创建新的组织架构单元</p>
      </div>

      <van-form @submit="handleSubmit">
        <div class="form-section animate-fade-in-up animate-delay-1">
          <div class="section-label">
            <span>🏢</span> 基本信息
          </div>
          <van-cell-group inset>
            <van-field
              v-model="formData.name"
              label="分院名称"
              placeholder="请输入分院名称"
              required
              clearable
              :rules="[{ required: true, message: '请输入分院名称' }]"
            />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-2">
          <div class="section-label">
            <span>📝</span> 其他信息
          </div>
          <van-cell-group inset>
            <van-field
              v-model="formData.description"
              rows="3"
              autosize
              type="textarea"
              label="分院描述"
              placeholder="请输入分院描述"
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
            立即创建
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/core/utils/routeDecision'
import { deptService } from '@/core/services/BaseService'
import { showSuccess, showError } from '@/core/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()

const submitting = ref(false)
const formData = ref({ name: '', description: '' })

const handleSubmit = async () => {
  if (!formData.value.name) { showError('请输入分院名称'); return }
  submitting.value = true
  try {
    await deptService.create(formData.value)
    showSuccess('分院创建成功')
    setTimeout(() => smartBack(), 1500)
  } catch (err) { showError(err.message || '创建失败') }
  finally { submitting.value = false }
}
const goBack = () => { router.go(-1) }
</script>

<style scoped>
.form-hero--purple { background: #EEF2FF; }
.form-hero { background: #F7F8FA; padding: 28px 20px; margin: -12px -16px 20px; text-align: center; border-radius: 0 0 16px 16px; }
.form-hero-icon { width: 60px; height: 60px; border-radius: 50%; background: #EEF2FF; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; color: #4F6EF7; }
.form-hero h2 { margin: 0 0 6px; font-size: 20px; font-weight: 700; color: #1A1A1A; }
.form-hero p { margin: 0; font-size: 13px; color: #666666; }
.form-section { margin-bottom: 8px; }
.section-label { display: flex; align-items: center; gap: 8px; padding: 10px 16px 6px; font-size: 13px; font-weight: 600; color: var(--mobile-text-secondary); }
.section-label span { font-size: 16px; }
</style>