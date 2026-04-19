<template>
  <!-- 首页主页 -->
  <BaseLayout>
    <template #content>
      <div class="dashboard-container">
        <el-container class="main-container">
          <!-- 左侧侧边?-->
          <DashboardSidebar 
            :user="user" 
            :user-role="userRole"
            @navigate="navigateTo"
            @logout="handleLogout"
            @search="handleSearch"
          />

          <!-- 右侧内容区域 -->
          <el-main class="dashboard-main">
            <slot name="rightcontent">
              <!-- 新版欢迎区域 -->
              <div class="welcome-section">
                <div class="welcome-left">
                  <div class="welcome-greeting">
                    <span class="greeting-time">{{ greetingText }}</span>
                    <h1 class="greeting-name">{{ user?.nickname || '用户' }}</h1>
                    <p class="greeting-sub">{{ isTeacher ? '教书育人，辛苦了！' : '欢迎回来，祝您工作顺利！' }}</p>
                  </div>
                  <div class="welcome-meta">
                    <span class="meta-item">
                      <el-icon><Calendar /></el-icon>
                      {{ today }}
                    </span>
                    <span class="meta-divider">|</span>
                    <span class="meta-item">
                      <el-icon><Monitor /></el-icon>
                      {{ currentTerm?.name || '未设置学期' }}
                    </span>
                  </div>
                </div>
                <div class="welcome-right">
                  <div class="quick-stats-mini">
                  <div class="mini-stat">
                    <span class="mini-value">{{ stats?.records?.today || 0 }}</span>
                    <span class="mini-label">今日记录</span>
                  </div>
                  <div class="mini-stat">
                    <span class="mini-value">{{ stats?.laboratories?.total || 0 }}</span>
                    <span class="mini-label">实训室总数</span>
                  </div>
                </div>
                </div>
              </div>

              <!-- 数据统计区域 -->
              <div class="section-container">
                <div class="section-header">
                  <span class="section-title">{{ isTeacher ? '个人数据' : '数据统计' }}</span>
                  <span class="section-desc">{{ isTeacher ? '您的教学数据' : '系统核心数据' }}</span>
                </div>
                
                <div class="stats-grid">
                  <!-- 系统超级用户统计 -->
                  <template v-if="user?.is_superuser">
                    <div 
                      v-for="(stat, index) in systemSuperuserStats" 
                      :key="index"
                      class="stat-card-new"
                      :class="'stat-color-' + (index + 1)"
                    >
                      <div class="stat-icon-wrap">
                        <el-icon :size="24"><component :is="stat.icon" /></el-icon>
                      </div>
                      <div class="stat-content">
                        <span class="stat-number">{{ stat.value }}</span>
                        <span class="stat-name">{{ stat.label }}</span>
                      </div>
                      <div class="stat-trend up">
                        <el-icon><ArrowRight /></el-icon>
                      </div>
                    </div>
                  </template>
                  
                  <!-- 管理员-校长统计 -->
                  <template v-else-if="user?.is_super_admin && !user?.is_superuser">
                    <div 
                      v-for="(stat, index) in superuserStats" 
                      :key="index"
                      class="stat-card-new"
                      :class="'stat-color-' + (index + 1)"
                    >
                      <div class="stat-icon-wrap">
                        <el-icon :size="24"><component :is="stat.icon" /></el-icon>
                      </div>
                      <div class="stat-content">
                        <span class="stat-number">{{ stat.value }}</span>
                        <span class="stat-name">{{ stat.label }}</span>
                      </div>
                      <div class="stat-trend up">
                        <el-icon><ArrowRight /></el-icon>
                      </div>
                    </div>
                  </template>
                  
                  <template v-else>
                    <div 
                      v-for="(stat, index) in commonStats" 
                      :key="index"
                      class="stat-card-new"
                      :class="'stat-color-' + (index + 1)"
                    >
                      <div class="stat-icon-wrap">
                        <el-icon :size="24"><component :is="stat.icon" /></el-icon>
                      </div>
                      <div class="stat-content">
                        <span class="stat-number">{{ stat.value }}</span>
                        <span class="stat-name">{{ stat.label }}</span>
                      </div>
                      <div class="stat-trend up">
                        <el-icon><ArrowRight /></el-icon>
                      </div>
                    </div>
                  </template>
                </div>
              </div>

              <!-- 图表与活动区域 -->
              <div class="section-container two-column-section">
                <!-- 左侧：数据趋势图 -->
                <div v-if="canShowCharts" class="column-left">
                  <!-- 系统超级用户图表 -->
                  <template v-if="user?.is_superuser">
                    <div class="section-header">
                      <span class="section-title">系统状态监控</span>
                      <span class="section-desc">系统运行状态</span>
                    </div>
                    
                    <div class="superuser-charts-grid">
                      <div class="chart-card-new">
                        <div class="chart-header-new">
                          <div class="chart-header-left">
                            <div class="chart-icon-wrap user-icon">
                              <el-icon><UserFilled /></el-icon>
                            </div>
                            <div class="chart-header-text">
                              <span class="chart-main-title">登录活跃统计</span>
                              <span class="chart-sub-title">近30天登录情况</span>
                            </div>
                          </div>
                        </div>
                        <VChart v-if="chartReady && systemSuperuserLoginActivityData.length" class="chart-area-single" :option="systemSuperuserLoginActivityOption" autoresize />
                        <div v-else class="chart-empty-single">
                          <el-icon :size="48"><UserFilled /></el-icon>
                          <span>暂无数据</span>
                        </div>
                      </div>
                      
                      <div class="chart-card-new">
                        <div class="chart-header-new">
                          <div class="chart-header-left">
                            <div class="chart-icon-wrap user-icon">
                              <el-icon><UserFilled /></el-icon>
                            </div>
                            <div class="chart-header-text">
                              <span class="chart-main-title">账号状态统计</span>
                              <span class="chart-sub-title">启用与禁用用户</span>
                            </div>
                          </div>
                        </div>
                        <VChart v-if="chartReady && systemSuperuserAccountStatusData.length" class="chart-area-single" :option="systemSuperuserAccountStatusOption" autoresize />
                        <div v-else class="chart-empty-single">
                          <el-icon :size="48"><UserFilled /></el-icon>
                          <span>暂无数据</span>
                        </div>
                      </div>
                    </div>
                  </template>
                  
                  <!-- 管理员-校长图表 -->
                  <template v-else-if="user?.is_super_admin && !user?.is_superuser">
                    <div class="section-header">
                      <span class="section-title">数据概览</span>
                      <span class="section-desc">系统核心数据可视化</span>
                    </div>
                    
                    <div class="superuser-charts-grid">
                      <div class="chart-card-new">
                        <div class="chart-header-new">
                          <div class="chart-header-left">
                            <div class="chart-icon-wrap dept-icon">
                              <el-icon><OfficeBuilding /></el-icon>
                            </div>
                            <div class="chart-header-text">
                              <span class="chart-main-title">分院实训室分布</span>
                              <span class="chart-sub-title">各分院实训室数量统计</span>
                            </div>
                          </div>
                        </div>
                        <VChart v-if="chartReady && superuserDeptDistributionData.length" class="chart-area-bar" :option="superuserDeptDistributionOption" autoresize />
                        <div v-else class="chart-empty-bar">
                          <el-icon :size="48"><OfficeBuilding /></el-icon>
                          <span>暂无数据</span>
                        </div>
                      </div>
                      
                      <div class="chart-card-new">
                        <div class="chart-header-new">
                          <div class="chart-header-left">
                            <div class="chart-icon-wrap user-icon">
                              <el-icon><UserFilled /></el-icon>
                            </div>
                            <div class="chart-header-text">
                              <span class="chart-main-title">用户类型分布</span>
                              <span class="chart-sub-title">系统用户构成统计</span>
                            </div>
                          </div>
                        </div>
                        <VChart v-if="chartReady && superuserUserTypeData.length" class="chart-area-bar" :option="superuserUserTypeOption" autoresize />
                        <div v-else class="chart-empty-bar">
                          <el-icon :size="48"><UserFilled /></el-icon>
                          <span>暂无数据</span>
                        </div>
                      </div>
                    </div>
                  </template>
                  
                  <!-- 实训室管理员图表 -->
                  <template v-else-if="isSxsadmin">
                    <div class="section-header">
                      <span class="section-title">管理数据概览</span>
                      <span class="section-desc">您管理的实训室数据统计</span>
                    </div>
                    
                    <div class="superuser-charts-grid">
                      <div class="chart-card-new">
                        <div class="chart-header-new">
                          <div class="chart-header-left">
                            <div class="chart-icon-wrap equipment-icon">
                              <el-icon><DataAnalysis /></el-icon>
                            </div>
                            <div class="chart-header-text">
                              <span class="chart-main-title">设备分布</span>
                              <span class="chart-sub-title">各实训室设备数量统计</span>
                            </div>
                          </div>
                        </div>
                        <VChart v-if="chartReady && sxsadminEquipmentData.length" class="chart-area-bar" :option="sxsadminEquipmentOption" autoresize />
                        <div v-else class="chart-empty-bar">
                          <el-icon :size="48"><DataAnalysis /></el-icon>
                          <span>暂无数据</span>
                        </div>
                      </div>
                      
                      <div class="chart-card-new">
                        <div class="chart-header-new">
                          <div class="chart-header-left">
                            <div class="chart-icon-wrap usage-icon">
                              <el-icon><DataLine /></el-icon>
                            </div>
                            <div class="chart-header-text">
                              <span class="chart-main-title">使用记录趋势</span>
                              <span class="chart-sub-title">本学期使用记录月度统计</span>
                            </div>
                          </div>
                        </div>
                        <VChart v-if="chartReady && sxsadminRecordsByMonthData.length" class="chart-area-bar" :option="sxsadminRecordsTrendOption" autoresize />
                        <div v-else class="chart-empty-bar">
                          <el-icon :size="48"><DataLine /></el-icon>
                          <span>暂无数据</span>
                        </div>
                      </div>
                    </div>
                  </template>
                  
                  <!-- 教师图表 -->
                  <template v-else-if="user?.is_teacher">
                    <div class="section-header">
                      <span class="section-title">个人教学数据</span>
                      <span class="section-desc">您的实训室使用情况统计</span>
                    </div>
                    
                    <div class="superuser-charts-grid">
                      <div class="chart-card-new">
                        <div class="chart-header-new">
                          <div class="chart-header-left">
                            <div class="chart-icon-wrap teacher-icon">
                              <el-icon><Reading /></el-icon>
                            </div>
                            <div class="chart-header-text">
                              <span class="chart-main-title">使用记录趋势</span>
                              <span class="chart-sub-title">本学期个人使用记录统计</span>
                            </div>
                          </div>
                        </div>
                        <VChart v-if="chartReady && teacherRecordsByMonthData.length" class="chart-area-bar" :option="teacherRecordsTrendOption" autoresize />
                        <div v-else class="chart-empty-bar">
                          <el-icon :size="48"><Reading /></el-icon>
                          <span>暂无使用记录</span>
                        </div>
                      </div>
                      
                      <div class="chart-card-new">
                        <div class="chart-header-new">
                          <div class="chart-header-left">
                            <div class="chart-icon-wrap sxs-usage-icon">
                              <el-icon><OfficeBuilding /></el-icon>
                            </div>
                            <div class="chart-header-text">
                              <span class="chart-main-title">实训室使用分布</span>
                              <span class="chart-sub-title">各实训室使用次数统计</span>
                            </div>
                          </div>
                        </div>
                        <VChart v-if="chartReady && teacherRecordsBySxsData.length" class="chart-area-bar" :option="teacherSxsUsageOption" autoresize />
                        <div v-else class="chart-empty-bar">
                          <el-icon :size="48"><OfficeBuilding /></el-icon>
                          <span>暂无使用记录</span>
                        </div>
                      </div>
                    </div>
                  </template>
                  
                  <!-- 分院管理员图表 -->
                  <template v-else>
                    <div class="section-header">
                      <span class="section-title">数据趋势</span>
                      <el-button 
                        type="primary" 
                        link 
                        size="small"
                        @click="navigateTo('/comprehensive-stats')">
                        查看更多
                        <el-icon><ArrowRight /></el-icon>
                      </el-button>
                    </div>
                    
                    <div class="chart-container">
                      <div class="chart-card-new chart-equipment">
                        <div class="chart-header-new">
                          <div class="chart-header-left">
                            <div class="chart-icon-wrap equipment-icon">
                              <el-icon><DataAnalysis /></el-icon>
                            </div>
                            <div class="chart-header-text">
                              <span class="chart-main-title">设备分布</span>
                              <span class="chart-sub-title">各实训室设备数量统计</span>
                            </div>
                          </div>
                        </div>
                        <VChart v-if="chartReady && equipmentSxsData.length" class="chart-area-single" :option="equipmentSxsOption" autoresize />
                        <div v-else class="chart-empty-single">
                          <el-icon :size="48"><DataAnalysis /></el-icon>
                          <span>暂无数据</span>
                        </div>
                      </div>
                    </div>
                  </template>
                </div>

                <!-- 右侧：系统状态与通知 -->
                <div class="column-right">
                  <!-- 系统状态卡?-->
                  <div class="system-status-card">
                    <div class="status-header">
                      <span class="status-title">系统状态</span>
                      <el-tag :type="currentTerm?.islocked ? 'info' : 'success'" effect="dark" size="small">
                        {{ currentTerm?.islocked ? '已归档' : '运行中' }}
                      </el-tag>
                    </div>
                    <div class="status-list">
                      <div class="status-row-new">
                        <span class="status-label">当前学期</span>
                        <span class="status-value">{{ currentTerm?.name || '未设置' }} </span>
                      </div>
                      <div class="status-row-new">
                        <span class="status-label">学期状态</span>
                        <span class="status-value" :class="currentTerm?.islocked ? 'locked' : 'active'">
                          {{ currentTerm?.islocked ? '已归' : '进行中' }}
                        </span>
                      </div>
                      <div class="status-row-new">
                        <span class="status-label">系统时间</span>
                        <span class="status-value">{{ todayDate }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- 快捷入口 -->
                  <div class="quick-links-card">
                    <div class="quick-header">
                      <span class="quick-title">快捷入口</span>
                    </div>
                    <div class="quick-links-grid">
                      <!-- 系统超级用户快捷操作 -->
                      <template v-if="user?.is_superuser">
                        <div 
                          v-for="(action, index) in systemSuperuserActions" 
                          :key="index"
                          class="quick-link-item"
                          @click="navigateTo(action.path)"
                        >
                          <el-icon :size="20"><component :is="action.icon" /></el-icon>
                          <span>{{ action.label }}</span>
                        </div>
                      </template>
                      <!-- 管理员-校长快捷操作 -->
                      <template v-else-if="user?.is_super_admin && !user?.is_superuser">
                        <div 
                          v-for="(action, index) in superuserActions" 
                          :key="index"
                          class="quick-link-item"
                          @click="navigateTo(action.path)"
                        >
                          <el-icon :size="20"><component :is="action.icon" /></el-icon>
                          <span>{{ action.label }}</span>
                        </div>
                      </template>
                      <!-- 教师快捷操作 -->
                      <template v-else-if="user?.is_teacher && !user?.is_super_admin && !user?.is_departadmin && !user?.is_sxsadmin">
                        <div 
                          v-for="(action, index) in teacherActions" 
                          :key="index"
                          class="quick-link-item"
                          @click="navigateTo(action.path)"
                        >
                          <el-icon :size="20"><component :is="action.icon" /></el-icon>
                          <span>{{ action.label }}</span>
                        </div>
                      </template>
                      <!-- 其他用户快捷操作 -->
                      <template v-else>
                        <div 
                          v-for="(action, index) in commonActions" 
                          :key="index"
                          class="quick-link-item"
                          @click="navigateTo(action.path)"
                        >
                          <el-icon :size="20"><component :is="action.icon" /></el-icon>
                          <span>{{ action.label }}</span>
                        </div>
                      </template>
                      <div class="quick-link-item" @click="handleLogout">
                        <el-icon :size="20"><SwitchButton /></el-icon>
                        <span>退出登录</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

            </slot>
          </el-main>
        </el-container>
      </div>
    </template>
  </BaseLayout>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useApi, useAuth, useDashboardCharts } from '@/core/hooks'
import BaseLayout from '@/views/pc/components/BaseLayout.vue'
import DashboardSidebar from './DashboardSidebar.vue'
import { useAppStore } from '@/core/store/app'
import { 
  UserFilled, Setting, HomeFilled, Lock, User, SwitchButton, 
  Briefcase, Calendar, Box, Collection, OfficeBuilding, Reading, 
  DataLine, DataAnalysis, Monitor,
  ArrowRight, Download, Tickets
} from '@element-plus/icons-vue'

import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent
])

export default {
  name: 'Index',
  components: {
    BaseLayout,
    DashboardSidebar,
    UserFilled, Setting, HomeFilled, Lock, User, SwitchButton,
    Briefcase, Calendar, Box, Collection, OfficeBuilding, Reading,
    DataLine, DataAnalysis, Monitor,
    ArrowRight, Download, VChart, Tickets
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    const { user, userRole, logout } = useAuth()
    const appStore = useAppStore()
    const { data: dashboardData, loading: isLoadingData, get: fetchDashboardData } = useApi('/statistics/dashboard/', { immediate: false })
    const { get: fetchStatsData } = useApi('/statistics/comprehensive/', { immediate: false })
    const { get: fetchSuperuserStats } = useApi('/statistics/super-admin/', { immediate: false })
    const { get: fetchSxsadminStats } = useApi('/statistics/laboratory-admin/', { immediate: false })
    const { get: fetchTeacherStats } = useApi('/statistics/teacher/', { immediate: false })
    const { get: fetchSystemSuperuserStats } = useApi('/statistics/system-superuser/', { immediate: false })
    
    const stats = ref({})
    const chartStats = ref({})
    const superuserChartStats = ref({})
    const sxsadminChartStats = ref({})
    const teacherChartStats = ref({})
    const systemSuperuserChartStats = ref({})
    const currentTerm = ref(null)
    const chartReady = ref(false)

    const safeUser = computed(() => user.value || {})

    const {
      canShowCharts,
      isSxsadmin,
      isSystemSuperuser,
      systemSuperuserStats,
      superuserStats,
      commonStats,
      usageTrendData,
      equipmentSxsData,
      usageTrendOption,
      equipmentSxsOption,
      superuserDeptDistributionData,
      superuserUserTypeData,
      superuserDeptDistributionOption,
      superuserUserTypeOption,
      sxsadminEquipmentData,
      sxsadminRecordsByMonthData,
      sxsadminEquipmentOption,
      sxsadminRecordsTrendOption,
      teacherRecordsByMonthData,
      teacherRecordsBySxsData,
      teacherRecordsTrendOption,
      teacherSxsUsageOption,
      systemSuperuserLoginActivityData,
      systemSuperuserLoginActivityOption,
      systemSuperuserAccountStatusData,
      systemSuperuserAccountStatusOption
    } = useDashboardCharts(stats, chartStats, superuserChartStats, sxsadminChartStats, teacherChartStats, systemSuperuserChartStats, safeUser)

    const userAvatar = computed(() => {
      // 仅使用用户自定义头像，如果没有则返回空字符串以显示默认插槽内?
      return safeUser.value.avatar || ''
    })

    const today = computed(() => {
      const date = new Date()
      const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
      return `${date.getFullYear()} ${String(date.getMonth() + 1).padStart(2, '0')} ${String(date.getDate()).padStart(2, '0')} ${weekdays[date.getDay()]}`
    })

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

    const todayDate = computed(() => {
      const date = new Date()
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    })

    const isTeacher = computed(() => {
      const u = safeUser.value
      return !!u.is_teacher && !u.is_super_admin && !u.is_departadmin && !u.is_sxsadmin
    })

    const systemSuperuserActions = [
      { path: '/userlist', icon: 'UserFilled', label: '用户管理' },
      { path: '/cache-config', icon: 'Setting', label: '缓存管理' },
      { path: '/backup-manage', icon: 'Download', label: '数据备份' }
    ]

    const superuserActions = [
      { path: '/term', icon: 'Calendar', label: '学期管理' },
      { path: '/deptlist', icon: 'OfficeBuilding', label: '查看分院信息' },
      { path: '/userlist/4', icon: 'UserFilled', label: '查看分院管理用户' }
    ]

    const teacherActions = [
      { path: '/workorder-center', icon: 'Tickets', label: '工单中心' },
      { path: '/personal-teaching', icon: 'Reading', label: '个人教学中心' }
    ]

    const commonActions = [
      { path: '/lab-resource-management', icon: 'OfficeBuilding', label: '实训室管理' },
      { path: '/workorder-center', icon: 'Tickets', label: '工单中心' }
    ]

    const navigateTo = (path) => {
      router.push(path).catch(() => {})
    }

    const handleSearch = (query) => {
      router.push({ path: '/global-search', query: { q: query } })
    }

    const handleLogout = async () => {
      await logout()
    }

    const loadData = async () => {
      const currentPath = route.path
      if (currentPath !== '/' && currentPath !== '') return
      
      try {
        const response = await fetchDashboardData()
        
        if (response && (response.success || response.data)) {
          const dashboardData = response.data || response
          stats.value = dashboardData || {}
          currentTerm.value = dashboardData?.current_semester || null
        } else {
          stats.value = {}
          currentTerm.value = null
        }
      } catch (error) {
        stats.value = {}
        currentTerm.value = null
      }

      if (canShowCharts.value) {
        const u = safeUser.value
        if (u.is_superuser) {
          try {
            const systemSuperuserResponse = await fetchSystemSuperuserStats()
            if (systemSuperuserResponse) {
              const responseData = systemSuperuserResponse.data || systemSuperuserResponse
              systemSuperuserChartStats.value = responseData.stats || {}
            }
          } catch (error) { }
        } else if (u.is_super_admin && !u.is_superuser) {
          try {
            const superuserResponse = await fetchSuperuserStats()
            if (superuserResponse) {
              const responseData = superuserResponse.data || superuserResponse
              superuserChartStats.value = responseData.stats || {}
            }
          } catch (error) { }} else if (isSxsadmin.value) {
          try {
            const sxsadminResponse = await fetchSxsadminStats()
            if (sxsadminResponse) {
              const responseData = sxsadminResponse.data || sxsadminResponse
              sxsadminChartStats.value = responseData.stats || {}
            }
          } catch (error) { }} else if (u.is_teacher) {
          try {
            const teacherResponse = await fetchTeacherStats()
            if (teacherResponse) {
              const responseData = teacherResponse.data || teacherResponse
              teacherChartStats.value = responseData.stats || {}
            }
          } catch (error) { }} else {
          try {
            const statsResponse = await fetchStatsData()
            if (statsResponse) {
              const responseData = statsResponse.data || statsResponse
              chartStats.value = responseData.stats || {}
            }
          } catch (error) { }}
      }
      
      await nextTick()
      setTimeout(() => {
        chartReady.value = true
      }, 100)
    }

    onMounted(() => {
      setTimeout(loadData, 100)
    })

    watch(() => appStore.refreshTermTrigger, () => {
      loadData()
    })

    return {
      user,
      userRole,
      stats,
      currentTerm,
      userAvatar,
      today,
      todayDate,
      greetingText,
      isTeacher,
      isSxsadmin,
      isSystemSuperuser,
      systemSuperuserActions,
      superuserActions,
      teacherActions,
      commonActions,
      systemSuperuserStats,
      superuserStats,
      commonStats,
      navigateTo,
      handleSearch,
      handleLogout,
      canShowCharts,
      chartReady,
      usageTrendOption,
      equipmentSxsOption,
      usageTrendData,
      equipmentSxsData,
      superuserDeptDistributionOption,
      superuserUserTypeOption,
      superuserDeptDistributionData,
      superuserUserTypeData,
      sxsadminEquipmentData,
      sxsadminRecordsByMonthData,
      sxsadminEquipmentOption,
      sxsadminRecordsTrendOption,
      sxsadminChartStats,
      teacherRecordsByMonthData,
      teacherRecordsBySxsData,
      teacherRecordsTrendOption,
      teacherSxsUsageOption,
      teacherChartStats,
      systemSuperuserLoginActivityData,
      systemSuperuserLoginActivityOption,
      systemSuperuserAccountStatusData,
      systemSuperuserAccountStatusOption
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 0;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.main-container {
  max-width: 100%;
  margin: 0;
  min-height: 100vh;
}

.dashboard-main {
  padding: 24px 32px;
  overflow-x: hidden;
  overflow-y: auto;
  height: 100vh;
}

.dashboard-main::-webkit-scrollbar {
  width: 8px;
}
.dashboard-main::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 4px;
}
.dashboard-main::-webkit-scrollbar-track {
  background: transparent;
}

.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #d4e8f7;
  border-radius: 12px;
  padding: 16px 24px;
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(66, 165, 245, 0.15);
  border: 1px solid #b3d9f2;
}

.welcome-section::before {
  display: none;
}

.welcome-section::after {
  display: none;
}

.welcome-left {
  position: relative;
  z-index: 1;
}

.welcome-greeting {
  margin-bottom: 8px;
}

.greeting-time {
  display: inline-block;
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 10px;
  margin-bottom: 6px;
}

.greeting-name {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  letter-spacing: 0.5px;
}

.greeting-sub {
  margin: 4px 0 0;
  font-size: 13px;
  color: #909399;
}

.welcome-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #a0a0a0;
  font-size: 13px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-divider {
  opacity: 0.3;
}

.welcome-right {
  position: relative;
  z-index: 1;
}

.quick-stats-mini {
  display: flex;
  gap: 10px;
}

.mini-stat {
  text-align: center;
  background: #f5f7fa;
  padding: 10px 16px;
  border-radius: 10px;
  min-width: 80px;
  transition: all 0.3s ease;
}

.mini-stat:hover {
  background: #ecf5ff;
  transform: translateY(-2px);
}

.mini-value {
  display: block;
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
  line-height: 1.2;
}

.mini-label {
  display: block;
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
}

.section-container {
  margin-bottom: 28px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-left: 4px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.section-desc {
  font-size: 13px;
  color: #909399;
  margin-left: 12px;
}

/* 数据统计网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card-new {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card-new::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  opacity: 0.1;
  transform: translate(30%, -30%);
}

.stat-card-new:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}

.stat-color-1::after { background: #409eff; }
.stat-color-2::after { background: #67c23a; }
.stat-color-3::after { background: #e6a23c; }
.stat-color-4::after { background: #909399; }

.stat-icon-wrap {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  flex-shrink: 0;
}

.stat-color-1 .stat-icon-wrap { background: #ecf5ff; color: #409eff; }
.stat-color-2 .stat-icon-wrap { background: #f0f9eb; color: #67c23a; }
.stat-color-3 .stat-icon-wrap { background: #fdf6ec; color: #e6a23c; }
.stat-color-4 .stat-icon-wrap { background: #f4f4f5; color: #909399; }

.stat-content {
  flex: 1;
}

.stat-number {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.2;
}

.stat-name {
  display: block;
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.stat-trend {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #f0f9ff;
  color: #52c41a;
}

/* 两列布局 */
.two-column-section {
  display: flex;
  gap: 24px;
}

.column-left {
  flex: 1;
  min-width: 0;
}

.column-right {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 图表容器 */
.chart-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-card-new {
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #f0f0f0;
  overflow: hidden;
  transition: all 0.3s ease;
}

.chart-card-new:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
}

.chart-header-new {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

.chart-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-icon-wrap {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-size: 18px;
}

.usage-icon {
  background: #ecf5ff;
  color: #409eff;
}

.equipment-icon {
  background: #ecf5ff;
  color: #409eff;
}

.chart-header-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.chart-main-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.chart-sub-title {
  font-size: 12px;
  color: #909399;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 20px;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.chart-title .el-icon {
  color: #409eff;
}

.chart-area {
  height: 180px;
  padding: 12px;
}

.chart-area-single {
  height: 320px;
  padding: 16px;
}

.chart-area-bar {
  height: 240px;
  padding: 16px;
}

.chart-empty-new {
  height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #c0c4cc;
  background: #fafafa;
}

.chart-empty-bar {
  height: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #c0c4cc;
  background: #fafafa;
}

.chart-empty-single {
  height: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #c0c4cc;
  background: #fafafa;
}

/* Superuser charts grid */
.superuser-charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 1200px) {
  .superuser-charts-grid {
    grid-template-columns: 1fr;
  }
}

.chart-empty-new .el-icon {
  opacity: 0.4;
}

.chart-empty-new span {
  font-size: 14px;
}

/* 系统状态卡?*/
.system-status-card {
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #f0f0f0;
  padding: 20px;
  transition: all 0.3s ease;
}

.system-status-card.full-width {
  margin-top: 0;
}

.system-status-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
}

.status-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.status-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-list-horizontal {
  display: flex;
  gap: 24px;
}

.status-row-new {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
}

.status-label {
  font-size: 13px;
  color: #909399;
}

.status-value {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
}

.status-value.active {
  color: #52c41a;
}

.status-value.locked {
  color: #909399;
}

/* 快捷入口卡片 */
.quick-links-card {
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #f0f0f0;
  padding: 20px;
  transition: all 0.3s ease;
}

.quick-links-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
}

.quick-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.quick-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
}

.quick-links-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-link-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #606266;
}

.quick-link-item:hover {
  background: #ecf5ff;
  color: #409eff;
  transform: translateX(4px);
}

.quick-link-item span {
  font-size: 14px;
}

/* 响应式布局 */
@media (max-width: 1400px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .two-column-section {
    flex-direction: column;
  }
  
  .column-right {
    width: 100%;
    flex-direction: row;
  }
  
  .system-status-card,
  .quick-links-card {
    flex: 1;
  }
}

@media (max-width: 1200px) {
  .dashboard-sidebar:not(.is-collapsed) {
    width: 240px !important;
  }
}

@media (max-width: 992px) {
  .welcome-section {
    flex-direction: column;
    text-align: center;
    padding: 24px;
  }
  
  .welcome-left {
    margin-bottom: 20px;
  }
  
  .welcome-meta {
    justify-content: center;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .column-right {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .greeting-name {
    font-size: 24px;
  }
  
  .quick-stats-mini {
    gap: 16px;
  }
  
  .mini-stat {
    padding: 12px 16px;
    min-width: 80px;
  }
  
  .mini-value {
    font-size: 22px;
  }
}

.superuser-charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart-area-bar {
  height: 280px;
  padding: 16px;
}

.chart-empty-bar {
  height: 280px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #c0c4cc;
  background: #fafafa;
}

.dept-icon {
  background: #ecf5ff;
  color: #409eff;
}

.user-icon {
  background: #f0f9eb;
  color: #67c23a;
}

.teacher-icon {
  background: #f9f0ff;
  color: #722ed1;
}

.sxs-usage-icon {
  background: #fff7e6;
  color: #fa8c16;
}

@media (max-width: 992px) {
  .superuser-charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
