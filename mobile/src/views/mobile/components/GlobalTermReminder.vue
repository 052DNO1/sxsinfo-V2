<template>
  <van-popup
    v-model:show="visible"
    position="center"
    :close-on-click-overlay="false"
    round
    style="width: 85%; max-width: 320px"
  >
    <div class="reminder-content">
      <van-icon name="warning-o" size="48" color="#ff976a" />
      <h3 class="reminder-title">学期设置提醒</h3>
      <p class="reminder-text">
        当前未设置"当前学期"
      </p>
      <p class="reminder-desc">
        系统检测到当前没有活动的学期，或者当前学期已归档。作为超级管理员，请立即设置新的当前学期。
      </p>
    </div>
    <div class="reminder-actions">
      <van-button type="primary" block @click="goToSetTerm">立即去设置</van-button>
      <van-button type="default" block @click="handleLogout" style="margin-top: 8px">退出登录</van-button>
    </div>
  </van-popup>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useApi } from '@/composables/useApi'
import { useAuth } from '@/composables/useAuth'
import { useAppStore } from '@/stores/app'

const visible = ref(false)
const router = useRouter()
const route = useRoute()
const { logout } = useAuth()
const appStore = useAppStore()
const { get: checkTermStatusApi } = useApi('/userinfo/check_term_status/', { immediate: false })

const checkTermStatus = async () => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('token') || sessionStorage.getItem('token')
  
  if (!token || route.path.includes('/login')) {
    visible.value = false
    return
  }

  if (route.path === '/addterm') {
    visible.value = false
    return
  }

  try {
    const res = await checkTermStatusApi()
    if (res && res.success) {
      const { is_superuser, has_current_term } = res
      if (has_current_term) {
        visible.value = false
      } else if (is_superuser && !has_current_term) {
        visible.value = true
      } else {
        visible.value = false
      }
    }
  } catch (err) {
    console.error('Check term status error:', err)
    visible.value = false
  }
}

const goToSetTerm = () => {
  visible.value = false
  router.push('/addterm')
}

const handleLogout = async () => {
  visible.value = false
  await logout()
}

onMounted(() => {
  setTimeout(checkTermStatus, 500)
})

watch(() => appStore.refreshTermTrigger, () => {
  checkTermStatus()
})

watch(() => route.path, (newPath) => {
  if (newPath && !newPath.includes('/login') && newPath !== '/addterm') {
    setTimeout(checkTermStatus, 300)
  }
})
</script>

<style scoped>
.reminder-content {
  padding: 24px 20px 16px;
  text-align: center;
}

.reminder-title {
  font-size: 18px;
  font-weight: 600;
  color: #323233;
  margin: 16px 0 8px;
}

.reminder-text {
  font-size: 16px;
  color: #323233;
  font-weight: 500;
  margin: 0;
}

.reminder-desc {
  font-size: 14px;
  color: #969799;
  line-height: 1.6;
  margin: 12px 0 0;
}

.reminder-actions {
  padding: 0 20px 20px;
}
</style>
