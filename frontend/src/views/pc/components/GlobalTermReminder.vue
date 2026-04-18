<!-- 学期提醒弹窗 -->
<template>
  <el-dialog
    v-model="visible"
    title="学期设置提醒"
    width="400px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    center
    align-center
    class="term-reminder-dialog"
    append-to-body
  >
    <div style="text-align: center; padding: 10px 0;">
      <el-icon :size="48" color="#E6A23C" style="margin-bottom: 16px;"><WarningFilled /></el-icon>
      <p style="font-size: 16px; line-height: 1.6; color: #303133; font-weight: bold;">
        当前未设置“当前学期?
      </p>
      <p style="font-size: 14px; line-height: 1.6; color: #606266; margin-top: 8px;">
        系统检测到当前没有活动的学期，或者当前学期已归档?br>
        作为超级管理员，请立即设置新的当前学期，以确保系统功能正常?
      </p>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" @click="goToSetTerm" size="large" class="action-btn">
          立即去设?
        </el-button>
        <el-button @click="handleSkip" size="large" class="action-btn">
          暂不设置
        </el-button>
        <el-button type="danger" plain @click="handleLogout" size="large" class="action-btn">
          退出登?
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { WarningFilled } from '@element-plus/icons-vue'
import { useApi, useAuth } from '@/core/hooks'
import { showConfirm } from '@/core/utils/errorHandler'
import { useAppStore } from '@/core/store/app'

const visible = ref(false)
const router = useRouter()
const route = useRoute()
const { logout } = useAuth()
const appStore = useAppStore()
const { get: checkTermStatusApi } = useApi('/semesters/current/', { immediate: false })

const checkTermStatus = async () => {
  // 简单判断是否登录（有Token�?
  const token = localStorage.getItem('access_token') || localStorage.getItem('token') || sessionStorage.getItem('token')
  
  // 如果没有token，或者是登录页面，不显示
  if (!token || route.path.includes('/login')) {
    visible.value = false
    return
  }

  // 如果当前已经在添加学期页面，则暂时隐藏弹窗（让用户操作）
  if (route.path === '/addterm') {
    visible.value = false
    return
  }

  try {
    const res = await checkTermStatusApi()
    if (res && res.success && res.data) {
      const { is_superuser, is_current } = res.data
      const has_current_term = !!is_current
      if (has_current_term) {
        visible.value = false
        localStorage.removeItem('skip_term_reminder')
      } else if (is_superuser && !has_current_term) {
        const skipReminder = localStorage.getItem('skip_term_reminder')
        if (skipReminder === 'true') {
          visible.value = false
        } else {
          visible.value = true
        }
      } else {
        visible.value = false
      }
    }
  } catch (error) { }}

const goToSetTerm = () => {
  visible.value = false
  router.push('/addterm')
}

const handleSkip = () => {
  visible.value = false
  localStorage.setItem('skip_term_reminder', 'true')
}

const handleLogout = async () => {
  const confirmed = await showConfirm(
    '确定要退出登录吗？',
    '退出确认',
    { confirmButtonText: '确定退出', cancelButtonText: '取消', type: 'warning' }
  )
  if (confirmed) {
    visible.value = false
    await logout()
  }
}

onMounted(() => {
  checkTermStatus()
})

watch(() => appStore.refreshTermTrigger, () => {
  checkTermStatus()
})

watch(
  () => route.path,
  () => {
    checkTermStatus()
  }
)
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: center;
  gap: 16px;
}
.action-btn {
  width: 140px;
}
</style>
