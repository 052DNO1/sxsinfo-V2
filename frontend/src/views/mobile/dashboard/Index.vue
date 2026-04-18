<template>
  <!-- 移动端布局 -->
  <div class="mobile-index-container">
    <!-- 顶部导航栏 - 根据 activeTab 显示不同标题 -->
    <van-nav-bar
      :title="getNavBarTitle()"
    >
      <template #right>
        <van-icon 
          v-if="activeTab === 0"
          name="search" 
          size="18" 
          @click="showSearch = !showSearch" 
          style="margin-right: 16px;" 
        />
        <van-icon 
          v-if="activeTab === 0"
          name="setting-o" 
          size="18" 
          @click="showUserMenu = !showUserMenu" 
        />
      </template>
    </van-nav-bar>

    <!-- 用户菜单弹出层 -->
    <van-popup
      v-model:show="showUserMenu"
      position="bottom"
      :style="{ padding: '16px' }"
    >
      <van-cell-group>
        <van-cell is-link @click="navigateTo('/change-password'); showUserMenu = false">
          <template #title>
            <div style="display: flex; align-items: center;">
              <van-icon name="lock" size="20px" color="#1989fa" style="margin-right: 12px;" />
              <span>修改密码</span>
            </div>
          </template>
        </van-cell>
        <van-cell is-link @click="navigateTo('/update-user'); showUserMenu = false">
          <template #title>
            <div style="display: flex; align-items: center;">
              <van-icon name="user-o" size="20px" color="#1989fa" style="margin-right: 12px;" />
              <span>修改用户信息</span>
            </div>
          </template>
        </van-cell>
        <van-cell is-link @click="handleLogoutMobile">
          <template #title>
            <div style="display: flex; align-items: center;">
              <van-icon name="logout" size="20px" color="#ee0a24" style="margin-right: 12px;" />
              <span>退出登录</span>
            </div>
          </template>
        </van-cell>
      </van-cell-group>
    </van-popup>

    <!-- 搜索框（可展开） -->
    <van-search
      v-model="searchQuery"
      placeholder="全局搜索..."
      show-action
      @search="handleSearch"
      v-show="showSearch"
    >
      <template #action>
        <div @click="handleSearch">搜索</div>
      </template>
    </van-search>

    <!-- 内容区域 - 根据 activeTab 显示不同内容 -->
    <div class="mobile-content">
      <!-- 首页内容 (activeTab === 0) -->
      <div v-if="activeTab === 0">
        <!-- 欢迎横幅 -->
        <div class="mobile-welcome-card">
          <div class="mobile-welcome-title">
            <van-icon name="smile-o" size="20px" style="margin-right: 4px;" />
            欢迎您：{{ user?.nikename || '用户' }}
          </div>
          <div class="mobile-welcome-date">
            {{ today }}
          </div>
        </div>

        <!-- 快速操作 -->
        <div class="mobile-quick-actions">
          <div class="mobile-quick-actions-title">
            <van-icon name="flash-o" size="18px" style="margin-right: 4px;" />
            快速操作
          </div>
          <div class="mobile-quick-actions-grid">
            <!-- 超级管理员快捷操作 -->
            <template v-if="user?.is_superuser">
              <a 
                href="#" 
                class="mobile-quick-action-item"
                @click.prevent="navigateTo('/term')"
              >
                <div class="mobile-quick-action-icon">
                  <van-icon name="calendar-o" size="32px" color="#1989fa" />
                </div>
                <div class="mobile-quick-action-text">学期管理</div>
              </a>
              <a 
                href="#" 
                class="mobile-quick-action-item"
                @click.prevent="navigateTo('/archive-term')"
              >
                <div class="mobile-quick-action-icon">
                  <van-icon name="box" size="32px" color="#1989fa" />
                </div>
                <div class="mobile-quick-action-text">归档学期</div>
              </a>
              <a 
                href="#" 
                class="mobile-quick-action-item"
                @click.prevent="navigateTo('/deptlist')"
              >
                <div class="mobile-quick-action-icon">
                  <van-icon name="shop-o" size="32px" color="#1989fa" />
                </div>
                <div class="mobile-quick-action-text">查看分院信息</div>
              </a>
              <a 
                href="#" 
                class="mobile-quick-action-item"
                @click.prevent="navigateTo('/userlist/4')"
              >
                <div class="mobile-quick-action-icon">
                  <van-icon name="friends-o" size="32px" color="#1989fa" />
                </div>
                <div class="mobile-quick-action-text">查看分院管理员</div>
              </a>
            </template>
            <!-- 教师用户快捷操作 -->
            <template v-else-if="user?.is_teacher && !user?.is_superuser && !user?.is_departadmin && !user?.is_sxsadmin">
              <a 
                href="#" 
                class="mobile-quick-action-item"
                @click.prevent="navigateTo('/ai-assistant')"
              >
                <div class="mobile-quick-action-icon">
                  <van-icon name="service-o" size="32px" color="#1989fa" />
                </div>
                <div class="mobile-quick-action-text">AI助手</div>
              </a>
              <a 
                href="#" 
                class="mobile-quick-action-item"
                @click.prevent="navigateTo('/message-list')"
              >
                <div class="mobile-quick-action-icon">
                  <van-icon name="chat-o" size="32px" color="#1989fa" />
                </div>
                <div class="mobile-quick-action-text">消息中心</div>
              </a>
              <a 
                href="#" 
                class="mobile-quick-action-item"
                @click.prevent="navigateTo('/personal-teaching')"
              >
                <div class="mobile-quick-action-icon">
                  <van-icon name="user-circle-o" size="32px" color="#1989fa" />
                </div>
                <div class="mobile-quick-action-text">个人教学中心</div>
              </a>
            </template>
            <!-- 其他用户快捷操作 -->
            <template v-else>
              <a 
                href="#" 
                class="mobile-quick-action-item"
                @click.prevent="navigateTo('/user-management')"
              >
                <div class="mobile-quick-action-icon">
                  <van-icon name="friends-o" size="32px" color="#1989fa" />
                </div>
                <div class="mobile-quick-action-text">用户管理</div>
              </a>
              <a 
                href="#" 
                class="mobile-quick-action-item"
                @click.prevent="navigateTo('/message-list')"
              >
                <div class="mobile-quick-action-icon">
                  <van-icon name="chat-o" size="32px" color="#1989fa" />
                </div>
                <div class="mobile-quick-action-text">消息中心</div>
              </a>
              <a 
                href="#" 
                class="mobile-quick-action-item"
                @click.prevent="navigateTo('/personal-teaching')"
              >
                <div class="mobile-quick-action-icon">
                  <van-icon name="user-circle-o" size="32px" color="#1989fa" />
                </div>
                <div class="mobile-quick-action-text">个人教学中心</div>
              </a>
            </template>
          </div>
        </div>

        <!-- 数据概览 -->
        <div class="mobile-stats-overview">
          <div class="mobile-stats-title">
            <van-icon name="chart-trending-o" size="18px" style="margin-right: 4px;" />
            数据概览
          </div>
          <div class="mobile-stats-grid">
            <!-- 超级管理员统计 -->
            <template v-if="user?.is_superuser">
              <div class="mobile-stat-item">
                <div class="mobile-stat-number">{{ stats?.total_terms || 0 }}</div>
                <van-icon name="calendar-o" size="24px" color="#1989fa" />
                <div class="mobile-stat-label">学期总数</div>
              </div>
              <div class="mobile-stat-item">
                <div class="mobile-stat-number">{{ stats?.total_departs || 0 }}</div>
                <van-icon name="shop-o" size="24px" color="#1989fa" />
                <div class="mobile-stat-label">分院总数</div>
              </div>
              <div class="mobile-stat-item">
                <div class="mobile-stat-number">{{ stats?.total_depart_admins || 0 }}</div>
                <van-icon name="user-o" size="24px" color="#1989fa" />
                <div class="mobile-stat-label">分院管理员</div>
              </div>
              <div class="mobile-stat-item">
                <div class="mobile-stat-number">{{ stats?.total_sxs || 0 }}</div>
                <van-icon name="shop-o" size="24px" color="#1989fa" />
                <div class="mobile-stat-label">实训室总数</div>
              </div>
            </template>
            <!-- 其他用户统计 -->
            <template v-else>
              <div class="mobile-stat-item">
                <div class="mobile-stat-number">{{ stats?.total_users || 0 }}</div>
                <van-icon name="user-o" size="24px" color="#1989fa" />
                <div class="mobile-stat-label">用户总数</div>
              </div>
              <div class="mobile-stat-item">
                <div class="mobile-stat-number">{{ stats?.today_records || 0 }}</div>
                <van-icon name="records" size="24px" color="#1989fa" />
                <div class="mobile-stat-label">今日使用记录</div>
              </div>
              <div class="mobile-stat-item">
                <div class="mobile-stat-number">{{ stats?.pending_maintenance || 0 }}</div>
                <van-icon name="setting-o" size="24px" color="#1989fa" />
                <div class="mobile-stat-label">待维护项目</div>
              </div>
              <div class="mobile-stat-item">
                <div class="mobile-stat-number">{{ stats?.total_sxs || 0 }}</div>
                <van-icon name="shop-o" size="24px" color="#1989fa" />
                <div class="mobile-stat-label">实训室总数</div>
              </div>
            </template>
          </div>
        </div>

        <!-- 系统状态 -->
        <div class="mobile-status-panel">
          <div class="mobile-status-title">
            <van-icon name="setting-o" size="18px" style="margin-right: 4px;" />
            系统状态
          </div>
          <div class="mobile-status-item">
            <span class="mobile-status-label">当前学期</span>
            <span class="mobile-status-value">{{ currentTerm?.termname || '未设置' }}</span>
          </div>
          <div class="mobile-status-item">
            <span class="mobile-status-label">学期状态</span>
            <span class="mobile-status-value">
              <van-tag :type="currentTerm?.islocked ? 'danger' : 'success'" size="small">
                {{ currentTerm?.islocked ? '已归档' : '进行中' }}
              </van-tag>
            </span>
          </div>
          <div class="mobile-status-item">
            <span class="mobile-status-label">系统时间</span>
            <span class="mobile-status-value">{{ todayDate }}</span>
          </div>
        </div>
      </div>

      <!-- 功能页面内容 (activeTab === 1) -->
      <div v-else-if="activeTab === 1" class="mobile-function-section">
        <!-- 主要工作标题 -->
        <div class="mobile-function-title">主要工作</div>
        
        <!-- 功能列表 -->
        <div class="mobile-function-list">
          <!-- 超级管理员功能 -->
          <template v-if="user?.is_superuser">
            <a href="#" class="mobile-function-item" @click.prevent="navigateTo('/term')">
              <div class="mobile-function-icon">
                <van-icon name="calendar-o" size="20" color="#1989fa" />
              </div>
              <span class="mobile-function-text">学期管理</span>
              <van-icon name="arrow" class="mobile-function-arrow" />
            </a>
            <a href="#" class="mobile-function-item" @click.prevent="navigateTo('/archive-term')">
              <div class="mobile-function-icon">
                <van-icon name="box" size="20" color="#1989fa" />
              </div>
              <span class="mobile-function-text">归档学期</span>
              <van-icon name="arrow" class="mobile-function-arrow" />
            </a>
            <a href="#" class="mobile-function-item" @click.prevent="navigateTo('/deptlist')">
              <div class="mobile-function-icon">
                <van-icon name="shop-o" size="20" color="#1989fa" />
              </div>
              <span class="mobile-function-text">查看分院信息</span>
              <van-icon name="arrow" class="mobile-function-arrow" />
            </a>
            <a href="#" class="mobile-function-item" @click.prevent="navigateTo('/userlist/4')">
              <div class="mobile-function-icon">
                <van-icon name="friends-o" size="20" color="#1989fa" />
              </div>
              <span class="mobile-function-text">查看分院管理员</span>
              <van-icon name="arrow" class="mobile-function-arrow" />
            </a>
          </template>
          
          <!-- 分院管理员特有功能 -->
          <template v-if="user?.is_departadmin && !user?.is_superuser">
            <a href="#" class="mobile-function-item" @click.prevent="navigateTo('/user-management')">
              <div class="mobile-function-icon">
                <van-icon name="friends-o" size="20" color="#7232dd" />
              </div>
              <span class="mobile-function-text">用户管理</span>
              <van-icon name="arrow" class="mobile-function-arrow" />
            </a>
            <a href="#" class="mobile-function-item" @click.prevent="navigateTo('/lab-resource-management')">
              <div class="mobile-function-icon">
                <van-icon name="shop-o" size="20" color="#ff976a" />
              </div>
              <span class="mobile-function-text">全部实训室</span>
              <van-icon name="arrow" class="mobile-function-arrow" />
            </a>
          </template>
          
          <!-- 实训室管理员特有功能（仅当不是分院管理员时显示） -->
          <template v-if="user?.is_sxsadmin && !user?.is_superuser && !user?.is_departadmin">
            <a href="#" class="mobile-function-item" @click.prevent="navigateTo('/lab-resource-management')">
              <div class="mobile-function-icon">
                <van-icon name="shop-o" size="20" color="#ff976a" />
              </div>
              <span class="mobile-function-text">实训室与资源管理</span>
              <van-icon name="arrow" class="mobile-function-arrow" />
            </a>
          </template>
          
          <!-- 教师特有功能 -->
          <template v-if="user?.is_teacher && !user?.is_superuser">
            <a href="#" class="mobile-function-item" @click.prevent="navigateTo('/personal-teaching')">
              <div class="mobile-function-icon">
                <van-icon name="user-circle-o" size="20" color="#ff976a" />
              </div>
              <span class="mobile-function-text">个人教学中心</span>
              <van-icon name="arrow" class="mobile-function-arrow" />
            </a>
          </template>
          
          <!-- 公共功能（所有非超级管理员用户） -->
          <template v-if="!user?.is_superuser && (user?.is_departadmin || user?.is_sxsadmin || user?.is_teacher)">
            <a href="#" class="mobile-function-item" @click.prevent="navigateTo('/comprehensive-stats')">
              <div class="mobile-function-icon">
                <van-icon name="bar-chart-o" size="20" color="#07c160" />
              </div>
              <span class="mobile-function-text">数据中心</span>
              <van-icon name="arrow" class="mobile-function-arrow" />
            </a>
            <a href="#" class="mobile-function-item" @click.prevent="navigateTo('/message-list')">
              <div class="mobile-function-icon">
                <van-icon name="chat-o" size="20" color="#1989fa" />
              </div>
              <span class="mobile-function-text">消息中心</span>
              <van-icon name="arrow" class="mobile-function-arrow" />
            </a>
            <a href="#" class="mobile-function-item" @click.prevent="navigateTo('/ai-assistant')">
              <div class="mobile-function-icon">
                <van-icon name="service-o" size="20" color="#7232dd" />
              </div>
              <span class="mobile-function-text">AI智能助手</span>
              <van-icon name="arrow" class="mobile-function-arrow" />
            </a>
          </template>
        </div>
      </div>


      <!-- 我的页面内容 (activeTab === 3) -->
      <div v-else-if="activeTab === 3">
        <!-- 用户信息卡片 -->
        <van-cell-group inset style="margin-top: 12px;">
          <van-cell>
            <template #title>
              <div style="display: flex; align-items: center; gap: 12px;">
                <van-icon name="user-circle-o" size="48" color="#1989fa" />
                <div>
                  <div style="font-size: 18px; font-weight: 600; color: #323233;">
                    {{ user?.nikename || '用户' }}
                  </div>
                  <div style="font-size: 12px; color: #969799; margin-top: 4px;">
                    {{ userRole }}
                  </div>
                </div>
              </div>
            </template>
          </van-cell>
        </van-cell-group>

        <!-- 功能菜单 -->
        <van-cell-group inset style="margin-top: 12px;">
          <van-cell is-link @click="navigateTo('/change-password')">
            <template #title>
              <div style="display: flex; align-items: center;">
                <van-icon name="lock" size="20px" color="#1989fa" style="margin-right: 12px;" />
                <span>修改密码</span>
              </div>
            </template>
          </van-cell>
          <van-cell is-link @click="navigateTo('/update-user')">
            <template #title>
              <div style="display: flex; align-items: center;">
                <van-icon name="user-o" size="20px" color="#1989fa" style="margin-right: 12px;" />
                <span>修改用户信息</span>
              </div>
            </template>
          </van-cell>
        </van-cell-group>

        <!-- 退出登录 -->
        <div style="padding: 16px; margin-top: 12px; margin-bottom: 12px;">
          <van-button
            round
            block
            type="danger"
            @click="handleLogoutMobile"
          >
            退出登录
          </van-button>
        </div>
      </div>
    </div>

    <!-- 底部导航栏 -->
    <van-tabbar v-model="activeTab" fixed>
      <van-tabbar-item icon="home-o">首页</van-tabbar-item>
      <van-tabbar-item icon="apps-o">功能</van-tabbar-item>
      <van-tabbar-item icon="chat-o">消息</van-tabbar-item>
      <van-tabbar-item icon="user-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/utils/api'
import { useMobile } from '@/composables/useMobile'

export default {
  name: 'MobileIndex',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const user = ref(JSON.parse(sessionStorage.getItem('user') || '{}'))
    const stats = ref({})
    const currentTerm = ref(null)
    const searchQuery = ref('')
    
    // 移动端检测
    const { loadVantComponents, init: initMobile } = useMobile()
    
    // 移动端状态
    const showSearch = ref(false)
    const showUserMenu = ref(false)
    const activeTab = ref(0)
    

    const userRole = computed(() => {
      if (user.value?.is_superuser) return '超级管理员'
      if (user.value?.is_departadmin) return '分院管理员'
      if (user.value?.is_sxsadmin) return '实训室管理员'
      if (user.value?.is_teacher) return '教师'
      return '普通用户'
    })
    
    // 获取导航栏标题（移动端）
    const getNavBarTitle = () => {
      if (activeTab.value === 0) return user.value?.nikename || '首页'
      if (activeTab.value === 1) return '功能'
      if (activeTab.value === 3) return '我的'
      return '首页'
    }

    const today = computed(() => {
      const date = new Date()
      const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
      return `${date.getFullYear()}年${String(date.getMonth() + 1).padStart(2, '0')}月${String(date.getDate()).padStart(2, '0')}日 ${weekdays[date.getDay()]}`
    })

    const todayDate = computed(() => {
      const date = new Date()
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    })

    // 手动导航函数
    const navigateTo = (path) => {
      router.push(path).then(() => {
      }).catch((err) => {
        console.error('导航失败:', err)
      })
    }

    const handleSearch = () => {
      router.push({ path: '/global-search', query: { q: searchQuery.value } })
    }

    const handleLogout = async () => {
      try {
        await api.post('/logout/')
        sessionStorage.removeItem('user')
        router.push('/login')
      } catch (error) {
        console.error('Logout error:', error)
        sessionStorage.removeItem('user')
        router.push('/login')
      }
    }
    
    // 移动端退出登录（使用自定义确认对话框）
    const handleLogoutMobile = async () => {
      try {
        const { showConfirmDialog } = await import('@/utils/mobileDialog')
        try {
          await showConfirmDialog({ title: '确认退出', message: '确定要退出登录吗？' })
          await handleLogout()
        } catch {
          // 用户取消
        }
      } catch (error) {
        console.error('Logout error:', error)
        await handleLogout()
      }
    }
    

    const loadData = async () => {
      const currentPath = route.path
      if (currentPath !== '/' && currentPath !== '') {
        return
      }
      
      try {
        const response = await api.get('/')
        
        if (response && response.success) {
          stats.value = response.stats || {}
          currentTerm.value = response.current_term || null
        } else {
          console.error('Load data error:', response?.message || '未知错误')
          stats.value = {}
          currentTerm.value = null
        }
      } catch (error) {
        console.error('Load data error:', error)
        stats.value = {}
        currentTerm.value = null
      }
    }

    onMounted(() => {
      // 初始化移动端检测
      const cleanupMobile = initMobile()
      onUnmounted(() => {
        if (cleanupMobile) cleanupMobile()
      })
      
      // 检查是否有从其他页面传递过来的 activeTab
      const savedTab = sessionStorage.getItem('activeTab')
      if (savedTab !== null) {
        activeTab.value = parseInt(savedTab, 10)
        sessionStorage.removeItem('activeTab') // 使用后清除
      }
      
      // 预加载 Vant 组件
      setTimeout(() => {
        loadVantComponents()
      }, 200)
      
      // 延迟加载数据，确保路由已经稳定
      setTimeout(() => {
        loadData()
      }, 100)
    })
    
    // 监听 activeTab 变化，切换到消息页面时跳转到独立的消息页面
    watch(activeTab, (newTab) => {
      if (newTab === 2) {
        navigateTo('/message-list')
        // 重置 activeTab，避免显示空内容
        setTimeout(() => {
          activeTab.value = 0
        }, 100)
      }
    })

    return {
      user,
      stats,
      currentTerm,
      searchQuery,
      userRole,
      today,
      todayDate,
      navigateTo,
      handleSearch,
      handleLogoutMobile,
      showSearch,
      showUserMenu,
      activeTab,
      getNavBarTitle
    }
  }
}
</script>
