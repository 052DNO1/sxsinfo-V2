<template>
  <div class="alipay-page">
    <!-- 顶部状态栏 -->
    <div class="status-bar">
      <div class="time">{{ currentTime }}</div>
      <div class="status-icons">
        <van-icon name="signal" size="14" />
        <van-icon name="wifi" size="14" />
        <van-icon name="battery" size="14" />
      </div>
    </div>

    <!-- 顶部导航 -->
    <div class="page-header">
      <div class="header-content">
        <van-icon name="arrow-left" size="20" color="#333" @click="goBack" />
        <div class="header-title">个人中心</div>
        <div class="header-actions">
          <van-icon name="more-o" size="20" color="#333" />
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="page-content">
      <!-- 用户信息卡片 -->
      <div class="user-card">
        <div class="user-avatar">
          <van-image round width="80" height="80" :src="userAvatar" icon="user-o" />
        </div>
        <div class="user-info">
          <div class="user-name">{{ user?.nikename || user?.username || '用户' }}</div>
          <div class="user-role">{{ userRole }}</div>
          <div class="user-email" v-if="user?.email">{{ user.email }}</div>
        </div>
      </div>

      <!-- 功能列表 -->
      <div class="function-list">
        <div class="section-title">账户设置</div>
        <van-cell-group inset>
          <van-cell title="修改个人信息" icon="edit" is-link @click="navigateTo('/edit-profile')" />
          <van-cell title="修改密码" icon="lock" is-link @click="navigateTo('/change-password')" />
        </van-cell-group>

        <div class="section-title">其他</div>
        <van-cell-group inset>
          <van-cell title="关于我们" icon="info-o" is-link />
          <van-cell title="帮助中心" icon="help-o" is-link />
          <van-cell title="退出登录" icon="sign" is-link @click="handleLogout" />
        </van-cell-group>
      </div>
    </div>

    <!-- 底部导航栏 -->
    <div class="bottom-nav">
      <div class="nav-item" @click="navigateTo('/')">
        <van-icon name="home-o" size="20" />
        <span>首页</span>
      </div>
      <template v-if="!safeUser.is_teacher">
        <div class="nav-item" v-if="safeUser.is_superuser" @click="navigateTo('/deptlist')">
          <van-icon name="cluster-o" size="20" />
          <span>分院</span>
        </div>
        <div class="nav-item" v-else @click="navigateTo('/listsxs')">
          <van-icon name="cluster-o" size="20" />
          <span>实训室</span>
        </div>
        <div class="nav-item" @click="navigateTo(getUserNavPath())">
          <van-icon :name="getUserNavIcon()" size="20" />
          <span>{{ getUserNavText() }}</span>
        </div>
      </template>
      <div class="nav-item active">
        <van-icon name="user-o" size="20" />
        <span>我的</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { showConfirm } from '@/utils/errorHandler'

const router = useRouter()
const currentTime = ref('')
let timeInterval = null

const { user, userRole, logout } = useAuth()

const safeUser = computed(() => user.value || {})
const userAvatar = computed(() => user.value?.avatar || '')

const updateCurrentTime = () => {
  const now = new Date()
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  currentTime.value = `${hours}:${minutes}`
}

const navigateTo = (path) => {
  router.push(path).catch(() => {})
}

const getUserNavPath = () => {
  const u = safeUser.value
  if (u.is_superuser) {
    return '/userlist/4'
  }
  if (u.is_departadmin) {
    return '/userlist/1'
  }
  if (u.is_sxsadmin) {
    return '/message-list'
  }
  return '/update-user'
}

const getUserNavIcon = () => {
  const u = safeUser.value
  if (u.is_superuser) {
    return 'manager-o'
  }
  if (u.is_departadmin) {
    return 'friends-o'
  }
  if (u.is_sxsadmin) {
    return 'comment-o'
  }
  return 'user-o'
}

const getUserNavText = () => {
  const u = safeUser.value
  if (u.is_superuser) {
    return '管理员'
  }
  if (u.is_departadmin) {
    return '用户'
  }
  if (u.is_sxsadmin) {
    return '消息'
  }
  return '个人'
}

const handleLogout = async () => {
  const confirmed = await showConfirm('确定要退出登录吗？', '退出确认')
  if (confirmed) await logout()
}

const goBack = () => router.go(-1)

onMounted(() => {
  updateCurrentTime()
  timeInterval = setInterval(updateCurrentTime, 60000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.alipay-page {
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
}

/* 状态栏 */
.status-bar {
  height: 24px;
  background: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 12px;
  color: #333;
  font-size: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.status-icons {
  display: flex;
  gap: 8px;
}

/* 页面头部 */
.page-header {
  background: #fff;
  padding: 12px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

/* 主要内容 */
.page-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

/* 用户信息卡片 */
.user-card {
  background: linear-gradient(135deg, #1989fa 0%, #07c160 100%);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.user-avatar {
  margin-bottom: 8px;
}

.user-info {
  text-align: center;
  color: #fff;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.user-role {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 4px;
}

.user-email {
  font-size: 12px;
  opacity: 0.8;
}

/* 功能列表 */
.function-list {
  margin-bottom: 80px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #999;
  margin: 20px 0 12px 16px;
}

/* 底部导航栏 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 8px 0;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 20px;
  font-size: 12px;
  color: #999;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-item.active {
  color: #1989fa;
}

.nav-item:active {
  transform: scale(0.95);
}
</style>
