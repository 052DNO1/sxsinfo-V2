<template>
  <div class="mobile-page">
    <van-nav-bar
      title="添加学期"
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
      <div class="form-hero form-hero--success">
        <div class="form-hero-icon">
          <van-icon
            name="calendar-o"
            size="28"
          />
        </div>
        <h2>新增学期</h2>
        <p>设置学期时间范围</p>
      </div>

      <van-form @submit="handleSubmit">
        <div class="form-section animate-fade-in-up animate-delay-1">
          <div class="section-label">
            <span>📅</span> 学期信息
          </div>
          <van-cell-group inset>
            <van-field
              v-model="form.name"
              label="名称"
              placeholder="如: 2024-2025学年第一学期"
              required
              clearable
              :rules="[{required:true,message:'请输入学期名称'}]"
            />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-2">
          <div class="section-label">
            <span>⏱️</span> 时间范围
          </div>
          <van-cell-group inset>
            <van-field
              v-model="startText"
              is-link
              readonly
              label="开始日期"
              required
              @click="showStartPicker = true"
            />
            <van-field
              v-model="endText"
              is-link
              readonly
              label="结束日期"
              required
              @click="showEndPicker = true"
            />
          </van-cell-group>
          
          <div class="date-range-hint">
            <van-icon
              name="info-o"
              size="14"
            /> 
            <span>学期时长：{{ calcDuration }} 天</span>
          </div>
        </div>

        <div class="form-actions">
          <van-button
            type="primary"
            block
            round
            size="large"
            native-type="submit"
            :loading="submitting"
            icon="success"
          >
            立即创建
          </van-button>
        </div>
      </van-form>
    </div>

    <van-popup
      v-model:show="showStartPicker"
      position="bottom"
      round
    >
      <van-date-picker
        v-model="startDate"
        title="开始日期"
        @confirm="(o) => { form.start_date = o.selectedValues.join('-'); startText = o.selectedValues.join('-'); showStartPicker = false }"
        @cancel="showStartPicker=false"
      />
    </van-popup>
    <van-popup
      v-model:show="showEndPicker"
      position="bottom"
      round
    >
      <van-date-picker
        v-model="endDate"
        title="结束日期"
        @confirm="(o) => { form.end_date = o.selectedValues.join('-'); endText = o.selectedValues.join('-'); showEndPicker = false }"
        @cancel="showEndPicker=false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useNavigation } from '@/core/utils/routeDecision'
import { semesterService } from '@/core/services/BaseService'
import { showSuccess, showError } from '@/core/utils/errorHandler'

const router = useRouter()
const { goBack, goHome } = useNavigation()

const submitting = ref(false)
const showStartPicker = ref(false)
const showEndPicker = ref(false)

const today = new Date()
const startDate = ref([String(today.getFullYear()), String(today.getMonth()+1).padStart(2,'0'), String(today.getDate()).padStart(2,'0')])
const endDate = ref([String(today.getFullYear()+1), String(today.getMonth()+1).padStart(2,'0'), String(today.getDate()).padStart(2,'0')])
const startText = ref(startDate.value.join('-'))
const endText = ref(endDate.value.join('-'))

const form = ref({ name: '', start_date: startDate.value.join('-'), end_date: endDate.value.join('-') })

const calcDuration = computed(() => {
  if (!form.value.start_date || !form.value.end_date) return 0
  const diff = new Date(form.value.end_date) - new Date(form.value.start_date)
  return Math.ceil(diff / 86400000)
})

const handleSubmit = async () => {
  if (!form.value.name) return showError('请输入名称')
  submitting.value = true
  try {
    await semesterService.create(form.value)
    showSuccess('创建成功')
    setTimeout(() => goBack(), 1000)
  } catch (e) { showError('创建失败') }
  finally { submitting.value = false }
}
</script>

<style scoped>
.form-hero--success { background: #E8F8EE; }
.form-hero { background: #F7F8FA; padding: 28px 20px; margin: -12px -16px 20px; text-align: center; border-radius: 0 0 16px 16px; }
.form-hero-icon { width: 60px; height: 60px; border-radius: 50%; background: #E8F8EE; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; color: #07C160; }
.form-hero h2 { margin: 0 0 6px; font-size: 20px; font-weight: 700; color: #1A1A1A; }
.form-hero p { margin: 0; font-size: 13px; color: rgba(255,255,255,0.8); }

.form-section { margin-bottom: 8px; }
.section-label { display: flex; align-items: center; gap: 8px; padding: 10px 16px 6px; font-size: 13px; font-weight: 600; color: var(--mobile-text-secondary); }
.section-label span { font-size: 16px; }

.date-range-hint {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 16px; margin: 0 16px;
  font-size: 12px; color: var(--mobile-text-hint);
  background: var(--mobile-success-bg);
  border-radius: var(--mobile-radius-sm);
}
</style>