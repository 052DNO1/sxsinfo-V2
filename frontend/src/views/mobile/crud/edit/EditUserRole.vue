<template>
  <div class="mobile-page">
    <van-nav-bar
      title="编辑角色"
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
      <div class="form-hero form-hero--hero">
        <div class="form-hero-icon">
          <van-icon
            name="shield-o"
            size="28"
          />
        </div>
        <h2>用户角色</h2>
        <p>管理用户权限与角色</p>
      </div>

      <van-skeleton
        v-if="loading"
        :row="5"
        animated
      />

      <template v-else>
        <div class="info-section animate-fade-in-up animate-delay-1">
          <div class="section-label">
            <span>👤</span> 用户信息
          </div>
          <div class="info-card">
            <div class="info-row">
              <span class="info-label">用户名</span><span class="info-value bold">{{ user?.username }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">昵称</span><span class="info-value">{{ user?.nickname || user?.nikename || '-' }}</span>
            </div>
          </div>
        </div>

        <div class="info-section animate-fade-in-up animate-delay-2">
          <div class="section-label">
            <span>🛡️</span> 角色设置
          </div>
          <div class="role-switch-list">
            <div
              v-for="role in roles"
              :key="role.key"
              class="role-switch-item"
            >
              <div class="role-info">
                <van-icon
                  v-if="role.key===1"
                  name="certificate"
                  size="18"
                />
                <van-icon
                  v-else-if="role.key===2"
                  name="manager-o"
                  size="18"
                />
                <van-icon
                  v-else
                  name="hotel-o"
                  size="18"
                />
                <span>{{ role.label }}</span>
              </div>
              <van-switch v-model="role.value" />
            </div>
          </div>
        </div>

        <div class="form-actions">
          <van-button
            type="primary"
            block
            round
            size="large"
            :loading="submitting"
            icon="success"
            @click="handleSubmit"
          >
            保存角色
          </van-button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { userService } from '@/core/services/BaseService'
import { useNavigation } from '@/core/utils/routeDecision'
import { showSuccess, showError } from '@/core/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()

const loading = ref(false)
const submitting = ref(false)
const user = ref(null)
const roles = ref([])

const loadData = async () => {
  loading.value = true
  try {
    const res = await userService.get(route.params.id)
    if (res?.data) {
      const d = res.data
      user.value = { username: d.username, nickname: d.nickname || d.nikename }
      const role = d.role || 0
      roles.value = [
        { key: 1, label: '教师', value: (role & 1) !== 0 },
        { key: 2, label: '实训室管理员', value: (role & 2) !== 0 },
        { key: 4, label: '分院管理员', value: (role & 4) !== 0 }
      ]
    }
  } catch (e) { showError('加载失败') }
  finally { loading.value = false }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    let roleValue = 0
    roles.value.forEach(r => { if (r.value) roleValue |= r.key })
    await userService.update(route.params.id, { role: roleValue })
    showSuccess('保存成功'); setTimeout(() => smartBack(), 1500)
  } catch (e) { showError(e.message||'保存失败') }
  finally { submitting.value = false }
}
</script>

<style scoped>
.form-hero--hero { background: #EEF2FF; }
.form-hero { background: #F7F8FA; padding: 28px 20px; margin: -12px -16px 20px; text-align: center; border-radius: 0 0 16px 16px; }
.form-hero-icon { width: 60px; height: 60px; border-radius: 50%; background: #EEF2FF; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; color: #4F6EF7; }
.form-hero h2 { margin: 0 0 6px; font-size: 20px; font-weight: 700; color: #1A1A1A; }
.form-hero p { margin: 0; font-size: 13px; color: rgba(255,255,255,0.8); }

.info-section { margin-bottom: 8px; }
.section-label { display: flex; align-items: center; gap: 8px; padding: 10px 16px 6px; font-size: 13px; font-weight: 600; color: var(--mobile-text-secondary); }
.section-label span { font-size: 16px; }

.info-card { background: var(--mobile-card); border-radius: var(--mobile-radius-lg); box-shadow: var(--mobile-shadow-sm); overflow: hidden; }
.info-row { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; }
.info-row:not(:last-child) { border-bottom: 1px solid var(--mobile-border); }
.info-label { font-size: 13px; color: var(--mobile-text-hint); }
.info-value { font-size: 14px; font-weight: 500; color: var(--mobile-text-primary); }
.info-value.bold { font-weight: 600; font-size: 15px; }

.role-switch-list { background: var(--mobile-card); border-radius: var(--mobile-radius-lg); box-shadow: var(--mobile-shadow-sm); overflow: hidden; }
.role-switch-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px; border-bottom: 1px solid var(--mobile-border);
}
.role-switch-item:last-child { border-bottom: none; }
.role-switch-item .role-info { display: flex; align-items: center; gap: 10px; font-size: 14px; font-weight: 500; color: var(--mobile-text-primary); }
.role-switch-item .role-info .van-icon { color: var(--mobile-primary); }
</style>