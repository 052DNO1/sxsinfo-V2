<template>
  <div class="mobile-page">
    <van-nav-bar title="编辑用户" left-arrow @click-left="goBack">
      <template #right><van-icon name="home-o" size="20" color="#4F6EF7" @click="goHome" /></template>
    </van-nav-bar>

    <div class="page-content">
      <div class="form-hero form-hero--hero">
        <div class="form-hero-icon"><van-icon name="edit" size="28" /></div>
        <h2>编辑用户</h2>
        <p>修改用户信息与角色</p>
      </div>

      <van-skeleton v-if="loading" :row="5" animated />

      <van-form v-else @submit="handleSubmit">
        <div class="form-section animate-fade-in-up animate-delay-1">
          <div class="section-label"><span>👤</span> 基本信息</div>
          <van-cell-group inset>
            <van-field v-model="form.username" label="用户名" disabled />
            <van-field v-model="form.nickname" label="昵称" disabled />
            <van-field v-model="form.email" type="email" label="邮箱" disabled />
            <van-field v-model="form.phone" label="手机号" disabled />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-2">
          <div class="section-label"><span>🛡️</span> 角色设置</div>
          <van-cell-group inset>
            <div class="role-grid">
              <div class="role-item" :class="{ active: roles.includes('teacher') }" @click="toggleRole('teacher')">
                <van-icon name="certificate" size="20" /><span>教师</span>
              </div>
              <div class="role-item" :class="{ active: roles.includes('sxsadmin') }" @click="toggleRole('sxsadmin')">
                <van-icon name="manager-o" size="20" /><span>实训室管理员</span>
              </div>
              <div class="role-item" :class="{ active: roles.includes('departadmin') }" @click="toggleRole('departadmin')">
                <van-icon name="hotel-o" size="20" /><span>分院管理员</span>
              </div>
            </div>
          </van-cell-group>
        </div>

        <div class="form-actions">
          <van-button type="primary" block round size="large" native-type="submit" :loading="submitting" icon="success">保存修改</van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/core/utils/routeDecision'
import { userService } from '@/core/services/BaseService'
import { showSuccess, showError } from '@/core/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { goBack, goHome } = useNavigation()

const loading = ref(false)
const submitting = ref(false)
const roles = ref([])
const form = ref({ username: '', nickname: '', email: '', phone: '', role: 1 })

const toggleRole = (role) => {
  const idx = roles.value.indexOf(role)
  if (idx >= 0) roles.value.splice(idx, 1)
  else roles.value.push(role)
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await userService.get(route.params.id)
    if (res?.data) {
      const d = res.data
      form.value = { username: d.username || '', nickname: d.nickname || '', email: d.email || '', phone: d.phone || '' }
      const role = d.role || 1
      roles.value = []
      if (role & 1) roles.value.push('teacher')
      if (role & 2) roles.value.push('sxsadmin')
      if (role & 4) roles.value.push('departadmin')
    }
  } finally { loading.value = false }
})

const handleSubmit = async () => {
  submitting.value = true
  try {
    let role = 1
    if (roles.value.includes('sxsadmin')) role |= 2
    if (roles.value.includes('departadmin')) role |= 4
    await userService.update(route.params.id, { ...form.value, role })
    showSuccess('保存成功')
    setTimeout(() => goBack(), 1000)
  } catch (e) { showError('保存失败') }
  finally { submitting.value = false }
}
</script>

<style scoped>
.form-hero--hero { background: #EEF2FF; }
.form-hero { background: #F7F8FA; padding: 28px 20px; margin: -12px -16px 20px; text-align: center; border-radius: 0 0 16px 16px; }
.form-hero-icon { width: 60px; height: 60px; border-radius: 50%; background: #EEF2FF; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; color: #4F6EF7; }
.form-hero h2 { margin: 0 0 6px; font-size: 20px; font-weight: 700; color: #1A1A1A; }
.form-hero p { margin: 0; font-size: 13px; color: rgba(255,255,255,0.8); }

.form-section { margin-bottom: 8px; }
.section-label { display: flex; align-items: center; gap: 8px; padding: 10px 16px 6px; font-size: 13px; font-weight: 600; color: var(--mobile-text-secondary); }
.section-label span { font-size: 16px; }

.role-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; padding: 14px 4px; }
.role-item {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 14px 8px; border-radius: var(--mobile-radius-md);
  border: 2px solid var(--mobile-border);
  transition: all 0.25s ease; cursor: pointer;
}
.role-item .van-icon { color: var(--mobile-text-hint); }
.role-item span { font-size: 11px; color: var(--mobile-text-secondary); font-weight: 500; }
.role-item.active { border-color: var(--mobile-primary); background: var(--mobile-primary-bg); }
.role-item.active .van-icon { color: var(--mobile-primary); }
.role-item.active span { color: var(--mobile-primary); font-weight: 600; }
</style>