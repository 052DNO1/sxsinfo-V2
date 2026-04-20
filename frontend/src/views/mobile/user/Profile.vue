<template>
  <MobileLayout>
    <div class="mobile-page">
      <van-nav-bar title="个人中心" left-arrow @click-left="goBack" />

    <div class="page-content">
      <template v-if="userInfo">
        <!-- 用户信息卡片 -->
        <div class="welcome-card animate-fade-in-up">
          <div class="user-avatar">
            <span>{{ (userInfo.nickname || userInfo.username || 'U').charAt(0).toUpperCase() }}</span>
          </div>
          <h1 class="user-name">{{ userInfo.nickname || userInfo.username || '用户' }}</h1>
          <p class="user-role">{{ userRoleText }}</p>
        </div>

        <!-- 功能菜单列表 -->
        <div class="menu-section animate-fade-in-up animate-delay-1">
          <div class="menu-card">
            <div class="menu-item" @click="router.push('/edit-profile')">
              <div class="menu-item-left">
                <div class="menu-icon menu-icon--primary">
                  <van-icon name="edit" size="18" />
                </div>
                <span class="menu-text">修改个人信息</span>
              </div>
              <van-icon name="arrow" size="16" color="#C0C4CC" />
            </div>

            <div class="menu-divider"></div>

            <div class="menu-item" @click="router.push('/change-password')">
              <div class="menu-item-left">
                <div class="menu-icon menu-icon--warning">
                  <van-icon name="lock" size="18" />
                </div>
                <span class="menu-text">修改密码</span>
              </div>
              <van-icon name="arrow" size="16" color="#C0C4CC" />
            </div>

            <div class="menu-divider"></div>

            <div class="menu-item menu-item--danger" @click="handleLogout">
              <div class="menu-item-left">
                <div class="menu-icon menu-icon--danger">
                  <van-icon name="revoke" size="18" />
                </div>
                <span class="menu-text">退出登录</span>
              </div>
              <van-icon name="arrow" size="16" color="#C0C4CC" />
            </div>
          </div>
        </div>

        <!-- 版本信息 -->
        <div class="version-info animate-fade-in-up animate-delay-2">
          <span>智慧实训室平台 V2</span>
          <span>© 2026</span>
        </div>
      </template>

      <van-skeleton v-else :row="5" animated />
    </div>
    </div>
  </MobileLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/core/hooks'
import { useNavigation } from '@/core/utils/routeDecision'
import { showDialog } from 'vant'
import MobileLayout from '@/views/mobile/components/MobileLayout.vue'

const router = useRouter()
const { goBack } = useNavigation()
const { user: authUser, logout } = useAuth()

const userInfo = ref(null)

const userRoleText = computed(() => {
  const u = userInfo.value
  if (!u) return '未登录'
  if (u.is_superuser) return '系统管理员'
  if (u.is_super_admin) return '超级管理员'
  if (u.is_departadmin) return '分院管理员'
  if (u.is_sxsadmin) return '实训室管理员'
  if (u.is_teacher) return '教师'
  return '普通用户'
})

const handleLogout = async () => {
  showDialog({
    title: '提示',
    message: '确定要退出登录吗？',
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    confirmButtonColor: '#FF3B30'
  }).then(async () => {
    await logout()
    router.push('/login')
  }).catch(() => {})
}

onMounted(() => {
  if (authUser.value) {
    userInfo.value = authUser.value
  }
})
</script>

<style scoped>
.welcome-card {
  background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
  border-radius: 16px;
  padding: 32px 20px;
  margin: 16px;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.1);
}

.welcome-card::before {
  display: none;
}

.welcome-card::after {
  display: none;
}

.user-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(79, 110, 247, 0.15);
  border: 3px solid rgba(79, 110, 247, 0.3);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
  position: relative;
  z-index: 1;
}

.user-avatar span {
  font-size: 28px;
  font-weight: 700;
  color: #4F6EF7;
}

.user-name {
  margin: 0 0 6px;
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
  letter-spacing: -0.02em;
  position: relative;
  z-index: 1;
}

.user-role {
  margin: 0;
  font-size: 13px;
  color: #4F6EF7;
  background: rgba(255, 255, 255, 0.9);
  display: inline-block;
  padding: 4px 16px;
  border-radius: 20px;
  font-weight: 600;
  position: relative;
  z-index: 1;
}

.menu-section {
  padding: 0 16px;
  margin-top: 24px;
}

.menu-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.menu-item:active {
  background: #f5f7fa;
}

.menu-item--danger .menu-text {
  color: #FF3B30 !important;
}

.menu-item-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.menu-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.menu-icon--primary {
  background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
  color: #4F6EF7;
}

.menu-icon--warning {
  background: linear-gradient(135deg, #FFF5E6 0%, #FFE8CC 100%);
  color: #FF9500;
}

.menu-icon--danger {
  background: linear-gradient(135deg, #FFEBE9 0%, #FFD6D1 100%);
  color: #FF3B30;
}

.menu-text {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

.menu-divider {
  height: 1px;
  background: #f0f0f0;
  margin: 0 20px;
}

.version-info {
  text-align: center;
  padding: 32px 16px;
  color: #c0c4cc;
  font-size: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
</style>