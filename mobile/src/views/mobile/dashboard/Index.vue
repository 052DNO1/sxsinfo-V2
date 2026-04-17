<template>
  <div class="alipay-app">
    <!-- 顶部导航 -->
    <div class="app-header">
      <div class="header-content">
        <div class="logo-section">
          <div class="logo">
            <van-icon name="cluster-o" size="24" color="#fff" />
          </div>
          <div class="app-name">实训室管理</div>
        </div>
        <div class="header-actions">
          <van-icon name="scan" size="20" color="#fff" />
          <van-icon name="search" size="20" color="#fff" />
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="main-content">
      <!-- 用户信息卡片 -->
      <div class="user-card">
        <div class="user-avatar">
          <van-image round width="60" height="60" :src="userAvatar" icon="user-o" />
        </div>
        <div class="user-info">
          <div class="greeting">{{ greetingText }}</div>
          <div class="name">{{ user?.nikename || '用户' }}</div>
          <div class="term-info" v-if="currentTerm">
            <van-tag :type="currentTerm?.islocked ? 'default' : 'success'" size="small">
              {{ currentTerm?.islocked ? '已归档' : '运行中' }}
            </van-tag>
            <span class="term-name">{{ currentTerm.termname }}</span>
          </div>
        </div>
      </div>

      <!-- 功能模块区 -->
      <div class="feature-modules">
        <div class="module-card">
          <div class="module-header">
            <div class="module-title">管理功能</div>
            <van-icon name="arrow" size="14" />
          </div>
          <div class="module-content">
            <div class="menu-grid">
              <div class="menu-item" v-for="(menu, index) in menuItems" :key="index" @click="navigateTo(menu.path)">
                <van-icon :name="menu.icon" size="20" color="#1989fa" />
                <span>{{ menu.title }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷操作卡片 -->
      <div class="service-cards">
        <!-- 超级管理员快捷操作 -->
        <template v-if="safeUser.is_superuser">
          <div class="service-card" @click="navigateTo('/term')">
            <div class="service-icon">
              <van-icon name="calendar-o" size="24" color="#667eea" />
            </div>
            <div class="service-info">
              <div class="service-title">学期管理</div>
              <div class="service-desc">查看和管理学期</div>
            </div>
            <van-icon name="arrow" size="16" color="#999" />
          </div>
          <div class="service-card" @click="navigateTo('/userlist/4')">
            <div class="service-icon">
              <van-icon name="manager-o" size="24" color="#ff9800" />
            </div>
            <div class="service-info">
              <div class="service-title">查看分院管理员</div>
              <div class="service-desc">管理分院管理员账号</div>
            </div>
            <van-icon name="arrow" size="16" color="#999" />
          </div>
        </template>

        <!-- 分院管理员快捷操作 -->
        <template v-else-if="safeUser.is_departadmin">
          <div class="service-card" @click="navigateTo('/adduser')">
            <div class="service-icon">
              <van-icon name="add-o" size="24" color="#667eea" />
            </div>
            <div class="service-info">
              <div class="service-title">添加用户</div>
              <div class="service-desc">快速添加新用户</div>
            </div>
            <van-icon name="arrow" size="16" color="#999" />
          </div>
          <div class="service-card" @click="navigateTo('/addsxs')">
            <div class="service-icon">
              <van-icon name="add-o" size="24" color="#ff9800" />
            </div>
            <div class="service-info">
              <div class="service-title">添加实训室</div>
              <div class="service-desc">快速添加实训室</div>
            </div>
            <van-icon name="arrow" size="16" color="#999" />
          </div>
        </template>

        <!-- 教师快捷操作（优先级最高，但超级管理员不显示） -->
        <template v-if="safeUser.is_teacher && !safeUser.is_superuser">
          <div class="service-card" @click="navigateTo('/add-record')">
            <div class="service-icon">
              <van-icon name="time-o" size="24" color="#1989fa" />
            </div>
            <div class="service-info">
              <div class="service-title">使用记录</div>
              <div class="service-desc">快速添加使用记录</div>
            </div>
            <van-icon name="arrow" size="16" color="#999" />
          </div>
          <div class="service-card" @click="navigateTo('/report-maintenance')">
            <div class="service-icon">
              <van-icon name="warning-o" size="24" color="#ff9800" />
            </div>
            <div class="service-info">
              <div class="service-title">设备故障</div>
              <div class="service-desc">发现故障，立即上报</div>
            </div>
            <van-icon name="arrow" size="16" color="#999" />
          </div>
        </template>

        <!-- 实训室管理员快捷操作 -->
        <template v-else-if="safeUser.is_sxsadmin">
          <div class="service-card" @click="navigateTo('/addmaintain')">
            <div class="service-icon">
              <van-icon name="add-o" size="24" color="#1989fa" />
            </div>
            <div class="service-info">
              <div class="service-title">添加维护记录</div>
              <div class="service-desc">快速添加维护记录</div>
            </div>
            <van-icon name="arrow" size="16" color="#999" />
          </div>
        </template>
      </div>
    </div>

    <!-- 底部导航栏 -->
    <div class="bottom-nav">
      <div class="nav-item active">
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
      <div class="nav-item" @click="navigateTo('/profile')">
        <van-icon name="user-o" size="20" />
        <span>我的</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'
import { useAuth } from '@/composables/useAuth'
import { showConfirm } from '@/utils/errorHandler'

const router = useRouter()

const { user, userRole, logout } = useAuth()
const { data: dashboardData, get: fetchDashboardData } = useApi('/', { immediate: false })

const currentTerm = ref(null)

const safeUser = computed(() => user.value || {})

const userAvatar = computed(() => safeUser.value.avatar || '')

const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  if (hour < 22) return '晚上好'
  return '夜深了'
})

const menuItems = computed(() => {
  const u = safeUser.value
  const items = []
  
  if (u.is_superuser) {
    items.push(
      { title: '学期管理', icon: 'calendar-o', path: '/term' },
      { title: '分院信息', icon: 'cluster-o', path: '/deptlist' },
      { title: '分院管理员', icon: 'manager-o', path: '/userlist/4' },
    )
  }
  
  if (u.is_departadmin) {
    items.push(
      { title: '用户管理', icon: 'friends-o', path: '/userlist/' },
      { title: '实训室管理', icon: 'cluster-o', path: '/listsxs' },
      { title: '添加用户', icon: 'add-o', path: '/adduser' },
      { title: '添加实训室', icon: 'add-o', path: '/addsxs' },
    )
  }
  
  if (u.is_sxsadmin && !u.is_departadmin && !u.is_superuser) {
    items.push(
      { title: '实训室列表', icon: 'cluster-o', path: '/listsxs' },
      { title: '添加维护记录', icon: 'add-o', path: '/addmaintain' },
    )
  }
  
  if (u.is_teacher && !u.is_departadmin && !u.is_sxsadmin && !u.is_superuser) {
    items.push(
      { title: '添加使用记录', icon: 'add-o', path: '/add-record' },
      { title: '上报故障', icon: 'warning-o', path: '/report-maintenance' },
    )
  }
  
  return items
})

const navigateTo = (path) => {
  router.push(path).catch(() => {})
}

const handleLogout = async () => {
  const confirmed = await showConfirm('确定要退出登录吗？', '退出确认')
  if (confirmed) await logout()
}

const getUserNavPath = () => {
  const u = safeUser.value
  if (u.is_departadmin) {
    return '/userlist/1'
  }
  return '/edit-profile'
}

const getUserNavIcon = () => {
  const u = safeUser.value
  if (u.is_departadmin) {
    return 'friends-o'
  }
  return 'user-o'
}

const getUserNavText = () => {
  const u = safeUser.value
  if (u.is_departadmin) {
    return '用户'
  }
  return '个人'
}

const loadData = async () => {
  try {
    const response = await fetchDashboardData()
    if (response && response.success) {
      currentTerm.value = response.current_term || null
    }
  } catch (error) {
    console.error('Load data error:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.alipay-app {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

/* 应用头部 */
.app-header {
  background: linear-gradient(135deg, #1989fa 0%, #07c160 100%);
  padding: 16px 20px;
  padding-bottom: 40px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.app-name {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.header-actions {
  display: flex;
  gap: 20px;
}

/* 主要内容 */
.main-content {
  flex: 1;
  padding: 16px;
  padding-top: 0;
  margin-top: -24px;
  z-index: 1;
}

/* 用户信息卡片 */
.user-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-avatar {
  flex-shrink: 0;
}

.user-info {
  flex: 1;
}

.greeting {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.term-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.term-name {
  font-size: 12px;
  color: #999;
}

/* 功能模块区 */
.feature-modules {
  margin-bottom: 20px;
}

.module-card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.module-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.menu-item span {
  font-size: 12px;
  color: #666;
}

/* 服务卡片 */
.service-cards {
  display: flex;
  gap: 12px;
  margin-bottom: 100px;
}

.service-card {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 12px;
}

.service-icon {
  flex-shrink: 0;
}

.service-info {
  flex: 1;
}

.service-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.service-desc {
  font-size: 12px;
  color: #999;
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
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.05);
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

/* 响应式 */
@media (max-width: 375px) {
  .function-grid {
    gap: 16px;
  }
  
  .menu-grid {
    gap: 16px;
  }
  
  .service-cards {
    flex-direction: column;
  }
}
</style>
