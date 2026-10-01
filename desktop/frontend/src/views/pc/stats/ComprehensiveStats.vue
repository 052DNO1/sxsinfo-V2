<template>
  <!-- PC端使用Index组件 -->
  <Index class="pc-layout">
    <template #rightcontent>
      <!-- 简洁头部 -->
      <div class="listheader">
        <div class="header-left">
          <div class="header-title">
            <div class="title-icon">
              <el-icon :size="24">
                <DataAnalysis />
              </el-icon>
            </div>
            <span>数据分析</span>
          </div>
          <div class="header-subtitle">
            {{ currentTerm?.name || '' }}
          </div>
        </div>
        <div class="listheader-actions">
          <el-button 
            type="primary" 
            round
            :loading="exporting"
            @click="exportReport"
          >
            {{ exporting ? '导出中...' : '导出报表' }}
          </el-button>
          <el-button
            v-if="shouldShowBackButton"
            class="nav-action-btn"
            plain
            @click="smartBack"
          >
            返回
          </el-button>
          <el-button
            class="nav-action-btn"
            plain
            @click="goHome"
          >
            首页
          </el-button>
        </div>
      </div>
      <div class="data-center-wrapper">
        <!-- 顶部统计卡片 - 重新设计 -->
        <div class="stats-summary-cards">
          <div
            v-for="card in summaryCards"
            :key="card.title"
            class="summary-card"
            :style="{ '--theme-color': card.color }"
          >
            <div class="card-main-content">
              <div class="card-title">
                {{ card.title }}
              </div>
              <div class="card-data-row">
                <span class="card-value">{{ card.value }}</span>
                <span class="card-unit">{{ card.unit }}</span>
              </div>
              <div class="card-desc">
                {{ card.desc }}
              </div>
            </div>
            <div class="card-icon-container">
              <div
                class="card-icon-bg"
                :style="{ color: card.color }"
              >
                <el-icon :size="28">
                  <component :is="card.iconComponent" />
                </el-icon>
              </div>
            </div>
          </div>
        </div>

        <!-- 标签导航 -->
        <el-tabs
          v-model="activeTab"
          class="modern-tabs-nav"
        >
          <!-- 实训室统计 -->
          <el-tab-pane
            v-if="showSxsTab"
            name="sxs"
          >
            <template #label>
              <span class="tab-icon"><el-icon><OfficeBuilding /></el-icon></span>
              <span class="tab-label">实训室统计</span>
            </template>
            <div class="modern-tab-content">
              <div class="section-header">
                <h2>
                  <el-icon class="section-icon">
                    <OfficeBuilding />
                  </el-icon> 实训室统计分析
                </h2>
                <div class="section-tools">
                  <el-select
                    v-model="sxsChartType"
                    size="small"
                    style="width: 120px;"
                  >
                    <el-option
                      label="柱状图"
                      value="bar"
                    />
                    <el-option
                      label="折线图"
                      value="line"
                    />
                  </el-select>
                </div>
              </div>

              <div class="charts-grid">
                <div class="chart-container card full-width">
                  <div class="chart-header">
                    <h3>教室容量分布统计</h3>
                    <div class="chart-subtitle">
                      {{ sxsChartType === 'line' ? '折线图' : '柱状图' }}展示
                    </div>
                  </div>
                  <VChart
                    v-if="chartReady && capacityMetrics.length"
                    class="chart-content"
                    :option="capacityOption"
                    autoresize
                  />
                  <div
                    v-else
                    class="chart-empty"
                  >
                    <el-icon class="empty-icon">
                      <TrendCharts />
                    </el-icon>
                    <p>暂无数据</p>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 课表统计 -->
          <el-tab-pane name="classes">
            <template #label>
              <span class="tab-icon"><el-icon><Reading /></el-icon></span>
              <span class="tab-label">课表统计</span>
            </template>
            <div class="modern-tab-content">
              <div class="section-header">
                <h2>
                  <el-icon class="section-icon">
                    <Reading />
                  </el-icon> 课表统计分析
                </h2>
                <div class="section-tools">
                  <el-select
                    v-model="classesChartType"
                    size="small"
                    style="width: 120px;"
                  >
                    <el-option
                      label="柱状图"
                      value="bar"
                    />
                    <el-option
                      label="折线图"
                      value="line"
                    />
                  </el-select>
                </div>
              </div>
              
              <div class="charts-grid single-chart">
                <div class="chart-container card full-width">
                  <div class="chart-header">
                    <h3>课程星期分布</h3>
                    <div class="chart-subtitle">
                      {{ classesChartType === 'line' ? '折线图' : '柱状图' }}展示
                    </div>
                  </div>
                  <VChart
                    v-if="chartReady && weekdayChartData.length"
                    class="chart-content"
                    :option="weekdayOption"
                    autoresize
                  />
                  <div
                    v-else
                    class="chart-empty"
                  >
                    <el-icon class="empty-icon">
                      <DataAnalysis />
                    </el-icon>
                    <p>暂无课程数据</p>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 设备统计 -->
          <el-tab-pane name="equipment">
            <template #label>
              <span class="tab-icon"><el-icon><Setting /></el-icon></span>
              <span class="tab-label">设备统计</span>
            </template>
            <div class="modern-tab-content">
              <div class="section-header">
                <h2>
                  <el-icon class="section-icon">
                    <Setting />
                  </el-icon> 设备统计
                </h2>
                <div class="section-tools">
                  <el-select
                    v-model="equipmentChartType"
                    size="small"
                    style="width: 150px;"
                  >
                    <el-option
                      label="设备实训室分布"
                      value="sxs"
                    />
                    <el-option
                      label="设备类型分布"
                      value="type"
                    />
                  </el-select>
                  <el-select
                    v-model="equipmentChartStyle"
                    size="small"
                    style="width: 100px; margin-left: 8px;"
                  >
                    <el-option
                      label="柱状图"
                      value="bar"
                    />
                    <el-option
                      label="折线图"
                      value="line"
                    />
                  </el-select>
                </div>
              </div>
              <div class="charts-grid single-chart">
                <div class="chart-container card full-width">
                  <div class="chart-header">
                    <h3>{{ equipmentChartType === 'sxs' ? '设备实训室分布' : '设备类型分布' }}</h3>
                    <div class="chart-subtitle">
                      {{ equipmentChartStyle === 'line' ? '折线图' : '柱状图' }}展示
                    </div>
                  </div>
                  <VChart
                    v-if="chartReady && (equipmentChartType === 'sxs' ? equipmentSxsSeries.length : equipmentTypeSeries.length)"
                    class="chart-content"
                    :option="equipmentChartType === 'sxs' ? equipmentSxsOption : equipmentTypeOption"
                    autoresize
                  />
                  <div
                    v-else
                    class="chart-empty"
                  >
                    <el-icon class="empty-icon">
                      <Setting />
                    </el-icon>
                    <p>暂无数据</p>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 维护记录 -->
          <el-tab-pane name="maintain">
            <template #label>
              <span class="tab-icon"><el-icon><Tools /></el-icon></span>
              <span class="tab-label">维护记录</span>
            </template>
            <div class="modern-tab-content">
              <div class="section-header">
                <h2>
                  <el-icon class="section-icon">
                    <Tools />
                  </el-icon> 维护记录分析
                </h2>
                <div class="section-tools">
                  <el-select
                    v-model="maintainChartType"
                    size="small"
                    style="width: 150px;"
                  >
                    <el-option
                      label="维护分布统计"
                      value="sxs"
                    />
                    <el-option
                      label="维护趋势分析"
                      value="trend"
                    />
                  </el-select>
                  <el-select
                    v-model="maintainChartStyle"
                    size="small"
                    style="width: 100px; margin-left: 8px;"
                  >
                    <el-option
                      label="柱状图"
                      value="bar"
                    />
                    <el-option
                      label="折线图"
                      value="line"
                    />
                  </el-select>
                </div>
              </div>
              <div class="charts-grid single-chart">
                <div class="chart-container card full-width">
                  <div class="chart-header">
                    <h3>{{ maintainChartType === 'sxs' ? '维护分布统计' : '维护趋势分析' }}</h3>
                    <div class="chart-subtitle">
                      {{ maintainChartStyle === 'line' ? '折线图' : '柱状图' }}展示
                    </div>
                  </div>
                  <VChart
                    v-if="chartReady && (maintainChartType === 'sxs' ? maintainSxsSeries.length : maintainMonthlySeries.length)"
                    class="chart-content"
                    :option="maintainChartType === 'sxs' ? maintainSxsOption : maintainMonthlyOption"
                    autoresize
                  />
                  <div
                    v-else
                    class="chart-empty"
                  >
                    <el-icon class="empty-icon">
                      <Tools />
                    </el-icon>
                    <p>暂无数据</p>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 使用记录 -->
          <el-tab-pane name="records">
            <template #label>
              <span class="tab-icon"><el-icon><Document /></el-icon></span>
              <span class="tab-label">使用记录</span>
            </template>
            <div class="modern-tab-content">
              <div class="section-header">
                <h2>
                  <el-icon class="section-icon">
                    <Document />
                  </el-icon> 使用记录分析
                </h2>
                <div class="section-tools">
                  <el-select
                    v-model="usageChartType"
                    size="small"
                    style="width: 150px;"
                  >
                    <el-option
                      label="使用分布统计"
                      value="sxs"
                    />
                    <el-option
                      label="使用趋势分析"
                      value="trend"
                    />
                  </el-select>
                  <el-select
                    v-model="usageChartStyle"
                    size="small"
                    style="width: 100px; margin-left: 8px;"
                  >
                    <el-option
                      label="柱状图"
                      value="bar"
                    />
                    <el-option
                      label="折线图"
                      value="line"
                    />
                  </el-select>
                </div>
              </div>
              <div class="charts-grid single-chart">
                <div class="chart-container card full-width">
                  <div class="chart-header">
                    <h3>{{ usageChartType === 'sxs' ? '使用分布统计' : '使用趋势分析' }}</h3>
                    <div class="chart-subtitle">
                      {{ usageChartStyle === 'line' ? '折线图' : '柱状图' }}展示
                    </div>
                  </div>
                  <VChart
                    v-if="chartReady && (usageChartType === 'sxs' ? usageSxsSeries.length : usageSeries.length)"
                    class="chart-content"
                    :option="usageChartType === 'sxs' ? usageSxsOption : usageOption"
                    autoresize
                  />
                  <div
                    v-else
                    class="chart-empty"
                  >
                    <el-icon class="empty-icon">
                      <Document />
                    </el-icon>
                    <p>暂无数据</p>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </template>
  </Index>
</template>

<script>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { useApi, useAuth } from '@/core/hooks'
import Index from '@/views/pc/dashboard/Index.vue'
import { useNavigation } from '@/core/utils/routeDecision'
import { getPieChartOption, getAxisChartOption, getChartColors } from '@/core/utils/chartUtils'
import { 
  OfficeBuilding, UserFilled, DataLine, Reading, Setting, 
  Document, Tools, DataAnalysis, TrendCharts, List,
  Histogram, Aim, Star, Trophy
} from '@element-plus/icons-vue'

// 导入 vue-echarts
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent,
  GraphicComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

// 注册必要的组?
use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent,
  GraphicComponent
])



import { showSuccess, showError } from '@/core/utils/errorHandler'
import { formatNumber, formatRoleName, formatDate } from '@/core/utils/format'
import { downloadFile, generateReportFileName, handleExportFromResponse } from '@/core/utils/io'
import { useUserStore } from '@/core/store/user'

export default {
  name: 'ComprehensiveStats',
  components: {
    Index,
    VChart,
    OfficeBuilding, UserFilled, DataLine, Reading, Setting, 
    Document, Tools, DataAnalysis, TrendCharts, List,
    Histogram, Aim, Star, Trophy
  },
  setup() {
    const { smartBack, navigateTo, goHome } = useNavigation()
    const { isSxsAdmin } = useAuth()
    const userStore = useUserStore()
    
    const shouldShowBackButton = computed(() => {
      const user = userStore.user
      if (user?.is_super_admin && !user?.is_superuser) {
        return false
      }
      return true
    })
    
    const msgSuccess = showSuccess
    const msgError = showError
    
    const { get: fetchStatsApi } = useApi('/statistics/comprehensive/', { immediate: false })
    const { post: exportStatsApi } = useApi('/statistics/comprehensive/export/', { immediate: false })
    
    const currentTerm = ref(null)
    const stats = ref({})
    const activeTab = ref('sxs')
    const exporting = ref(false)
    const chartReady = ref(false)
    const sxsChartType = ref('bar')
    const classesChartType = ref('bar')
    const equipmentChartType = ref('sxs')
    const equipmentChartStyle = ref('line')
    const usageChartType = ref('sxs')
    const usageChartStyle = ref('line')
    const maintainChartType = ref('sxs')
    const maintainChartStyle = ref('line')
    
    const showSxsTab = computed(() => {
      if (isSxsAdmin.value && stats.value?.laboratories) {
        const labCount = stats.value.laboratories.total || 0
        return labCount > 1
      }
      return true
    })
    
    onMounted(() => {
      loadData()
    })

    watch(activeTab, async () => {
      await nextTick()
      requestAnimationFrame(() => {
        window.dispatchEvent(new Event('resize'))
      })
    })

    // 简化颜色方?- 使用纯色
    const chartColors = getChartColors()

    // 顶部统计卡片数据
    const summaryCards = computed(() => {
      const labStats = stats.value?.laboratories || {}
      const usageRate = stats.value?.usage_rate || {}
      
      return [
        {
          title: '实训室总数',
          value: labStats.total || 0,
          unit: '间',
          iconComponent: 'OfficeBuilding',
          color: '#1890ff',
          desc: '当前管理的实训室总量'
        },
        {
          title: '总容量',
          value: labStats.capacity_stats?.total_capacity || 0,
          unit: '人',
          iconComponent: 'UserFilled',
          color: '#52c41a',
          desc: '可容纳学生总人数'
        },
        {
          title: '使用率',
          value: usageRate.schedule_rate || 0,
          unit: '%',
          iconComponent: 'DataLine',
          color: '#fa8c16',
          desc: '本学期平均使用率'
        },
        {
          title: '课程数量',
          value: stats.value?.schedules?.total || 0,
          unit: '门',
          iconComponent: 'Reading',
          color: '#722ed1',
          desc: '本学期开设课程总数'
        }
      ]
    })

    // ============== 计算属性：数据准备 ==============
    const departChartData = computed(() => {
      const src = stats.value?.laboratories?.by_department || {}
      return Object.entries(src).map(([label, v]) => ({ 
        label, 
        count: v.count || 0, 
        capacity: v.capacity || 0 
      }))
    })

    const capacityMetrics = computed(() => {
      const rooms = stats.value?.laboratories?.room_list
      if (!rooms || !rooms.length) {
        const cs = stats.value?.laboratories?.capacity_stats
        if (!cs) return []
        return [
          { name: '总容量', value: cs.total_capacity || 0 },
          { name: '平均容量', value: Number(formatNumber(cs.avg_capacity)) || 0 },
          { name: '最大容量', value: cs.max_capacity || 0 },
          { name: '最小容量', value: cs.min_capacity || 0 }
        ]
      }
      
      return rooms.map(room => ({
        name: room.name,
        value: room.capacity
      }))
    })

    const usageSxsSeries = computed(() => {
      const byLab = stats.value?.records?.by_laboratory
      if (byLab && Object.keys(byLab).length) {
        return Object.entries(byLab).map(([label, count]) => ({ label, count }))
      }
      return []
    })

    const usageSeries = computed(() => {
      const byMonth = stats.value?.records?.by_month
      if (byMonth && Object.keys(byMonth).length) {
        return Object.entries(byMonth)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([label, count]) => ({ label, count }))
      }
      return []
    })

    const equipmentTypeSeries = computed(() => {
      const byType = stats.value?.equipment?.by_type
      if (byType && Object.keys(byType).length) {
        return Object.entries(byType).map(([label, count]) => ({ label, count }))
      }
      return []
    })

    const equipmentSxsSeries = computed(() => {
      const byLab = stats.value?.equipment?.by_laboratory
      if (byLab && Object.keys(byLab).length) {
        return Object.entries(byLab).map(([label, count]) => ({ label, count }))
      }
      return []
    })

    const equipmentStatusSeries = computed(() => {
      const byStatus = stats.value?.equipment?.by_status
      if (byStatus && Object.keys(byStatus).length) {
        return Object.entries(byStatus).map(([label, count]) => ({ label, count }))
      }
      return []
    })

    const maintainSxsSeries = computed(() => {
      const byLab = stats.value?.work_orders?.by_laboratory
      if (byLab && Object.keys(byLab).length) {
        return Object.entries(byLab).map(([label, count]) => ({ label, count }))
      }
      return []
    })

    const maintainTypeSeries = computed(() => {
      const byType = stats.value?.work_orders?.by_type
      if (byType && Object.keys(byType).length) {
        return Object.entries(byType).map(([label, count]) => ({ label, count }))
      }
      return []
    })

    const maintainMonthlySeries = computed(() => {
      const byMonth = stats.value?.work_orders?.by_month
      if (byMonth && Object.keys(byMonth).length) {
        return Object.entries(byMonth)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([label, count]) => ({ label, count }))
      }
      return []
    })

    const weekdayChartData = computed(() => {
      const src = stats.value?.schedules?.by_weekday || {}
      const orderZhou = ['周一','周二','周三','周四','周五','周六','周日']
      const orderXq = ['星期一','星期二','星期三','星期四','星期五','星期六','星期日']
      const hasZhou = orderZhou.some(k => src[k] !== undefined)
      const order = hasZhou ? orderZhou : orderXq
      return order.map(d => ({
        label: d.replace('星期', '周'),
        count: src[d] ?? 0
      }))
    })

    // ============== ECharts 配置（简化版） ==============

    // 1. 分院分布图表 - 简化版
    const departOption = computed(() => {
      if (!departChartData.value.length) return {}
      
      const labels = departChartData.value.map(d => d.label)
      const countData = departChartData.value.map(d => d.count)
      const capacityData = departChartData.value.map(d => d.capacity)
      
      return {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['数量', '容量'],
          textStyle: {
            color: '#666'
          },
          top: 10
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: labels,
          boundaryGap: sxsChartType.value !== 'line',
          axisLine: {
            lineStyle: {
              color: '#d9d9d9'
            }
          },
          axisLabel: {
            color: '#666',
            interval: 0,
            rotate: 45
          }
        },
        yAxis: [
          {
            type: 'value',
            name: '数量',
            nameTextStyle: {
              color: '#666'
            },
            splitLine: {
              lineStyle: {
                type: 'dashed',
                color: '#f0f0f0'
              }
            },
            axisLine: {
              show: false
            },
            axisLabel: {
              color: '#999'
            }
          },
          {
            type: 'value',
            name: '容量',
            nameTextStyle: {
              color: '#666'
            },
            splitLine: {
              show: false
            },
            axisLine: {
              show: false
            },
            axisLabel: {
              color: '#999'
            }
          }
        ],
        series: [
          {
            name: '数量',
            type: sxsChartType.value,
            data: countData,
            smooth: sxsChartType.value === 'line',
            symbol: sxsChartType.value === 'line' ? 'circle' : undefined,
            symbolSize: sxsChartType.value === 'line' ? 6 : undefined,
            lineStyle: sxsChartType.value === 'line' ? { width: 3, color: '#1890ff' } : undefined,
            itemStyle: {
              color: '#1890ff',
              borderRadius: sxsChartType.value === 'bar' ? [4, 4, 0, 0] : undefined
            },
            barWidth: '40%'
          },
          {
            name: '容量',
            type: sxsChartType.value,
            data: capacityData,
            yAxisIndex: 1,
            smooth: sxsChartType.value === 'line',
            symbol: sxsChartType.value === 'line' ? 'circle' : undefined,
            symbolSize: sxsChartType.value === 'line' ? 6 : undefined,
            lineStyle: sxsChartType.value === 'line' ? { width: 3, color: '#52c41a' } : undefined,
            itemStyle: {
              color: '#52c41a',
              borderRadius: sxsChartType.value === 'bar' ? [4, 4, 0, 0] : undefined
            },
            barWidth: '40%'
          }
        ]
      }
    })

    const equipmentSxsOption = computed(() => {
      if (!equipmentSxsSeries.value.length) return {}
      const labels = equipmentSxsSeries.value.map(d => d.label)
      const data = equipmentSxsSeries.value.map(d => d.count)
      const isLine = equipmentChartStyle.value === 'line'
      return {
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis', formatter: '{b}: {c}台' },
        grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
        xAxis: {
          type: 'category',
          data: labels,
          boundaryGap: !isLine,
          axisLine: { lineStyle: { color: '#d9d9d9' } },
          axisLabel: { color: '#666', interval: 0, rotate: 30 }
        },
        yAxis: {
          type: 'value',
          name: '数量(台)',
          nameTextStyle: { color: '#666' },
          splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
          axisLine: { show: false },
          axisLabel: { color: '#999' }
        },
        series: [
          {
            name: '设备数量',
            type: equipmentChartStyle.value,
            smooth: isLine,
            symbol: isLine ? 'circle' : undefined,
            symbolSize: isLine ? 8 : undefined,
            lineStyle: isLine ? { width: 3, color: '#1890ff' } : undefined,
            itemStyle: {
              color: '#1890ff',
              borderRadius: isLine ? undefined : [4, 4, 0, 0]
            },
            areaStyle: isLine ? {
              color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
                { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
                { offset: 1, color: 'rgba(24, 144, 255, 0.05)' }
              ]}
            } : undefined,
            barWidth: isLine ? undefined : '40%',
            data
          }
        ]
      }
    })

    const equipmentTypeOption = computed(() => {
      if (!equipmentTypeSeries.value.length) return {}
      const labels = equipmentTypeSeries.value.map(d => d.label)
      const data = equipmentTypeSeries.value.map(d => d.count)
      const isLine = equipmentChartStyle.value === 'line'
      return {
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis', formatter: '{b}: {c}台' },
        grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
        xAxis: {
          type: 'category',
          data: labels,
          boundaryGap: !isLine,
          axisLine: { lineStyle: { color: '#d9d9d9' } },
          axisLabel: { color: '#666', interval: 0, rotate: 30 }
        },
        yAxis: {
          type: 'value',
          name: '数量(台)',
          nameTextStyle: { color: '#666' },
          splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
          axisLine: { show: false },
          axisLabel: { color: '#999' }
        },
        series: [
          {
            name: '设备数量',
            type: equipmentChartStyle.value,
            smooth: isLine,
            symbol: isLine ? 'circle' : undefined,
            symbolSize: isLine ? 8 : undefined,
            lineStyle: isLine ? { width: 3, color: '#52c41a' } : undefined,
            itemStyle: {
              color: '#52c41a',
              borderRadius: isLine ? undefined : [4, 4, 0, 0]
            },
            areaStyle: isLine ? {
              color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
                { offset: 0, color: 'rgba(82, 196, 26, 0.3)' },
                { offset: 1, color: 'rgba(82, 196, 26, 0.05)' }
              ]}
            } : undefined,
            barWidth: isLine ? undefined : '40%',
            data
          }
        ]
      }
    })

    const equipmentStatusOption = computed(() => {
      if (!equipmentStatusSeries.value.length) return {}
      const labels = equipmentStatusSeries.value.map(d => d.label)
      const data = equipmentStatusSeries.value.map(d => d.count)
      return {
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '10%', top: '10%', containLabel: true },
        xAxis: {
          type: 'category',
          data: labels,
          axisLine: { lineStyle: { color: '#d9d9d9' } },
          axisLabel: { color: '#666' }
        },
        yAxis: {
          type: 'value',
          splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
          axisLine: { show: false },
          axisLabel: { color: '#999' }
        },
        series: [
          {
            name: '设备数量',
            type: 'bar',
            data,
            itemStyle: { color: '#1890ff' },
            barWidth: '40%'
          }
        ]
      }
    })

    // 3. 容量统计折线图
    const capacityOption = computed(() => {
      if (!capacityMetrics.value.length) return {}
      
      const labels = capacityMetrics.value.map(d => d.name)
      const data = capacityMetrics.value.map(d => d.value)
      const isLine = sxsChartType.value === 'line'
      
      return {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c}人'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: labels,
          boundaryGap: !isLine,
          axisLine: {
            lineStyle: {
              color: '#d9d9d9'
            }
          },
          axisLabel: {
            color: '#666',
            interval: 0,
            rotate: 30
          }
        },
        yAxis: {
          type: 'value',
          name: '容量(人)',
          nameTextStyle: {
            color: '#666'
          },
          splitLine: {
            lineStyle: {
              type: 'dashed',
              color: '#f0f0f0'
            }
          },
          axisLine: {
            show: false
          },
          axisLabel: {
            color: '#999'
          }
        },
        series: [
          {
            name: '容量',
            type: sxsChartType.value,
            smooth: isLine,
            symbol: isLine ? 'circle' : undefined,
            symbolSize: isLine ? 8 : undefined,
            lineStyle: isLine ? { width: 3, color: '#1890ff' } : undefined,
            itemStyle: {
              color: '#1890ff',
              borderRadius: isLine ? undefined : [4, 4, 0, 0]
            },
            areaStyle: isLine ? {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
                  { offset: 1, color: 'rgba(24, 144, 255, 0.05)' }
                ]
              }
            } : undefined,
            barWidth: isLine ? undefined : '40%',
            data: data
          }
        ]
      }
    })

    // 4. 使用趋势图表 - 简化版
    const usageOption = computed(() => {
      if (!usageSeries.value.length) return {}
      
      const labels = usageSeries.value.map(d => d.label)
      const data = usageSeries.value.map(d => d.count)
      const isLine = usageChartStyle.value === 'line'
      
      return {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: labels,
          boundaryGap: !isLine,
          axisLine: {
            lineStyle: {
              color: '#d9d9d9'
            }
          },
          axisLabel: {
            color: '#666'
          }
        },
        yAxis: {
          type: 'value',
          name: '次数',
          nameTextStyle: { color: '#666' },
          splitLine: {
            lineStyle: {
              type: 'dashed',
              color: '#f0f0f0'
            }
          },
          axisLine: {
            show: false
          },
          axisLabel: {
            color: '#999'
          }
        },
        series: [
          {
            name: '使用记录',
            type: usageChartStyle.value,
            smooth: isLine,
            symbol: isLine ? 'circle' : undefined,
            symbolSize: isLine ? 8 : undefined,
            lineStyle: isLine ? { width: 3, color: '#fa8c16' } : undefined,
            itemStyle: {
              color: '#fa8c16',
              borderRadius: isLine ? undefined : [4, 4, 0, 0]
            },
            areaStyle: isLine ? {
              color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
                { offset: 0, color: 'rgba(250, 140, 22, 0.3)' },
                { offset: 1, color: 'rgba(250, 140, 22, 0.05)' }
              ]}
            } : undefined,
            barWidth: isLine ? undefined : '40%',
            data: data
          }
        ]
      }
    })

    const maintainTypeOption = computed(() => {
      if (!maintainTypeSeries.value.length) return {}
      const labels = maintainTypeSeries.value.map(d => d.label)
      const data = maintainTypeSeries.value.map(d => d.count)
      return {
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis', formatter: '{b}: {c}条' },
        grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
        xAxis: {
          type: 'category',
          data: labels,
          boundaryGap: false,
          axisLine: { lineStyle: { color: '#d9d9d9' } },
          axisLabel: { color: '#666', interval: 0, rotate: 30 }
        },
        yAxis: {
          type: 'value',
          name: '数量(条)',
          nameTextStyle: { color: '#666' },
          splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
          axisLine: { show: false },
          axisLabel: { color: '#999' }
        },
        series: [
          {
            name: '维护数量',
            type: 'line',
            smooth: true,
            symbol: 'circle',
            symbolSize: 8,
            lineStyle: { width: 3, color: '#722ed1' },
            itemStyle: { color: '#722ed1' },
            areaStyle: {
              color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
                { offset: 0, color: 'rgba(114, 46, 209, 0.3)' },
                { offset: 1, color: 'rgba(114, 46, 209, 0.05)' }
              ]}
            },
            data
          }
        ]
      }
    })

    const maintainMonthlyOption = computed(() => {
      if (!maintainMonthlySeries.value.length) return {}
      const labels = maintainMonthlySeries.value.map(d => d.label)
      const data = maintainMonthlySeries.value.map(d => d.count)
      const isLine = maintainChartStyle.value === 'line'
      return {
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '10%', top: '10%', containLabel: true },
        xAxis: {
          type: 'category',
          data: labels,
          boundaryGap: !isLine,
          axisLine: { lineStyle: { color: '#d9d9d9' } },
          axisLabel: { color: '#666' }
        },
        yAxis: {
          type: 'value',
          name: '数量(条)',
          nameTextStyle: { color: '#666' },
          splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
          axisLine: { show: false },
          axisLabel: { color: '#999' }
        },
        series: [
          {
            name: '维护记录',
            type: maintainChartStyle.value,
            smooth: isLine,
            symbol: isLine ? 'circle' : undefined,
            symbolSize: isLine ? 8 : undefined,
            lineStyle: isLine ? { width: 3, color: '#13c2c2' } : undefined,
            itemStyle: {
              color: '#13c2c2',
              borderRadius: isLine ? undefined : [4, 4, 0, 0]
            },
            areaStyle: isLine ? {
              color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
                { offset: 0, color: 'rgba(19, 194, 194, 0.3)' },
                { offset: 1, color: 'rgba(19, 194, 194, 0.05)' }
              ]}
            } : undefined,
            barWidth: isLine ? undefined : '40%',
            data
          }
        ]
      }
    })

    // 5. 星期分布图表 - 简化版
    // 6. 维护分布图表 - 新增按实训室统计
    const maintainSxsOption = computed(() => {
      if (!maintainSxsSeries.value.length) return {}
      const labels = maintainSxsSeries.value.map(d => d.label)
      const data = maintainSxsSeries.value.map(d => d.count)
      const isLine = maintainChartStyle.value === 'line'
      return {
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis', formatter: '{b}: {c}条' },
        grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
        xAxis: {
          type: 'category',
          data: labels,
          boundaryGap: !isLine,
          axisLine: { lineStyle: { color: '#d9d9d9' } },
          axisLabel: { color: '#666', interval: 0, rotate: 30 }
        },
        yAxis: {
          type: 'value',
          name: '数量(条)',
          nameTextStyle: { color: '#666' },
          splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
          axisLine: { show: false },
          axisLabel: { color: '#999' }
        },
        series: [
          {
            name: '维护数量',
            type: maintainChartStyle.value,
            smooth: isLine,
            symbol: isLine ? 'circle' : undefined,
            symbolSize: isLine ? 8 : undefined,
            lineStyle: isLine ? { width: 3, color: '#13c2c2' } : undefined,
            itemStyle: {
              color: '#13c2c2',
              borderRadius: isLine ? undefined : [4, 4, 0, 0]
            },
            areaStyle: isLine ? {
              color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
                { offset: 0, color: 'rgba(19, 194, 194, 0.3)' },
                { offset: 1, color: 'rgba(19, 194, 194, 0.05)' }
              ]}
            } : undefined,
            barWidth: isLine ? undefined : '40%',
            data
          }
        ]
      }
    })

    // 7. 使用分布图表 - 新增按实训室统计
    const usageSxsOption = computed(() => {
      if (!usageSxsSeries.value.length) return {}
      const labels = usageSxsSeries.value.map(d => d.label)
      const data = usageSxsSeries.value.map(d => d.count)
      const isLine = usageChartStyle.value === 'line'
      return {
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis', formatter: '{b}: {c}次' },
        grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
        xAxis: {
          type: 'category',
          data: labels,
          boundaryGap: !isLine,
          axisLine: { lineStyle: { color: '#d9d9d9' } },
          axisLabel: { color: '#666', interval: 0, rotate: 30 }
        },
        yAxis: {
          type: 'value',
          name: '次数',
          nameTextStyle: { color: '#666' },
          splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
          axisLine: { show: false },
          axisLabel: { color: '#999' }
        },
        series: [
          {
            name: '使用次数',
            type: usageChartStyle.value,
            smooth: isLine,
            symbol: isLine ? 'circle' : undefined,
            symbolSize: isLine ? 8 : undefined,
            lineStyle: isLine ? { width: 3, color: '#fa8c16' } : undefined,
            itemStyle: {
              color: '#fa8c16',
              borderRadius: isLine ? undefined : [4, 4, 0, 0]
            },
            areaStyle: isLine ? {
              color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
                { offset: 0, color: 'rgba(250, 140, 22, 0.3)' },
                { offset: 1, color: 'rgba(250, 140, 22, 0.05)' }
              ]}
            } : undefined,
            barWidth: isLine ? undefined : '40%',
            data
          }
        ]
      }
    })

    const weekdayOption = computed(() => {
      if (!weekdayChartData.value.length) return {}
      
      const labels = weekdayChartData.value.map(d => d.label)
      const data = weekdayChartData.value.map(d => d.count)
      const isLine = classesChartType.value === 'line'
      
      return {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: labels,
          boundaryGap: !isLine,
          axisLine: {
            lineStyle: {
              color: '#d9d9d9'
            }
          },
          axisLabel: {
            color: '#666'
          }
        },
        yAxis: {
          type: 'value',
          name: '课程数量',
          splitLine: {
            lineStyle: {
              type: 'dashed',
              color: '#f0f0f0'
            }
          },
          axisLine: {
            show: false
          },
          axisLabel: {
            color: '#999'
          }
        },
        series: [
          {
            name: '课程数',
            type: classesChartType.value,
            smooth: isLine,
            symbol: isLine ? 'circle' : undefined,
            symbolSize: isLine ? 8 : undefined,
            lineStyle: isLine ? { width: 3, color: '#1890ff' } : undefined,
            itemStyle: {
              color: '#1890ff',
              borderRadius: isLine ? undefined : [4, 4, 0, 0]
            },
            areaStyle: isLine ? {
              color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
                { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
                { offset: 1, color: 'rgba(24, 144, 255, 0.05)' }
              ]}
            } : undefined,
            barWidth: isLine ? undefined : '50%',
            data: data
          }
        ]
      }
    })

    // ============== 工具函数 ==============
    const getTabIcon = (tabId) => {
      const icons = {
        'sxs': 'OfficeBuilding',
        'classes': 'Reading',
        'equipment': 'Setting',
        'records': 'Document',
        'maintain': 'Tools'
      }
      return icons[tabId] || 'DataAnalysis'
    }

    const getTabLabel = (tabId) => {
      const labels = {
        'sxs': '实训室统计',
        'classes': '课表统计',
        'equipment': '设备统计',
        'records': '使用记录',
        'maintain': '维护记录'
      }
      return labels[tabId] || '统计'
    }

    const getCurrentData = () => {
      const data = []
      switch (activeTab.value) {
        case 'records':
          if (stats.value?.records?.by_month) {
            Object.entries(stats.value.records.by_month).forEach(([month, count]) => {
              data.push({ label: month, value: `${count}条` })
            })
          }
          break
        case 'maintain':
          if (stats.value?.work_orders?.by_status) {
            Object.entries(stats.value.work_orders.by_status).forEach(([status, count]) => {
              data.push({ label: status, value: `${count}条` })
            })
          }
          break
        case 'equipment':
          if (stats.value?.equipment?.by_status) {
            Object.entries(stats.value.equipment.by_status).forEach(([status, count]) => {
              data.push({ label: status, value: `${count}台` })
            })
          }
          break
      }
      return data
    }

    // ============== 业务逻辑 ==============
    const loadData = async () => {
      try {
        const response = await fetchStatsApi()
        
        if (response) {
          const data = response.data || response
          
          currentTerm.value = data.current_semester || data.current_term || null
          stats.value = data.stats || {}
          
          if (!showSxsTab.value && activeTab.value === 'sxs') {
            activeTab.value = 'classes'
          }
          
          await nextTick()
          
          requestAnimationFrame(() => {
            setTimeout(() => {
              chartReady.value = true
            }, 200)
          })
        }
      } catch (err) {
        msgError('加载数据失败：' + (err.message || '未知错误'))
      }
    }

    const exportReport = async () => {
      if (exporting.value) return
      
      exporting.value = true
      try {
        const exportData = {
          term: currentTerm.value?.name || '当前学期',
          export_time: formatDate(),
          stats: stats.value,
          active_tab: activeTab.value,
          tab_label: getTabLabel(activeTab.value)
        }

        const response = await exportStatsApi(exportData, { responseType: 'blob' })

        const filename = generateReportFileName('综合统计', currentTerm.value?.name)
        await handleExportFromResponse(response, filename)
        await msgSuccess('报表导出成功！')
      } catch (err) {
        await msgError('导出失败：' + (err.message || '未知错误'))
      } finally {
        exporting.value = false
      }
    }

    return {
      currentTerm,
      stats,
      activeTab,
      showSxsTab,
      chartReady,
      sxsChartType,
      classesChartType,
      equipmentChartType,
      equipmentChartStyle,
      usageChartType,
      usageChartStyle,
      maintainChartType,
      maintainChartStyle,
      exporting,
      summaryCards,
      shouldShowBackButton,
      // 导航
      smartBack,
      goHome,
      navigateTo,
      // 导出
      exportReport,
      // 工具函数
      getTabIcon,
      getTabLabel,
      getCurrentData,
      // ECharts options
      departOption,
      capacityOption,
      usageOption,
      usageSxsOption,
      weekdayOption,
      equipmentTypeOption,
      equipmentSxsOption,
      equipmentStatusOption,
      maintainTypeOption,
      maintainMonthlyOption,
      maintainSxsOption,
      // 数据源
      departChartData,
      capacityMetrics,
      usageSeries,
      usageSxsSeries,
      weekdayChartData,
      equipmentTypeSeries,
      equipmentSxsSeries,
      equipmentStatusSeries,
      maintainTypeSeries,
      maintainMonthlySeries,
      maintainSxsSeries,
      // 样式
      chartColors
    }
  }
}
</script>

<style scoped>
/* 全局布局优化 */
.pc-layout {
  background-color: #f5f7fa;
}

/* 头部样式优化 */
.listheader {
  background: #ffffff;
  padding: 20px 32px;
  border-radius: 16px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  border: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.listheader:hover {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 12px;
  letter-spacing: -0.5px;
}

.title-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e6f7ff 0%, #ffffff 100%);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.1);
  color: #1890ff;
}

.header-subtitle {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
  margin-left: 44px;
  min-height: 20px;
}

.listheader-actions {
  display: flex;
  gap: 12px;
}

/* 统计卡片优化 */
.stats-summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
  min-height: 140px;
}

.summary-card {
  background: white;
  border-radius: 20px;
  padding: 24px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  border: 1px solid #f0f2f5;
  cursor: default;
}

.summary-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--theme-color), transparent 80%);
  opacity: 0.06;
}

.summary-card:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
  border-color: transparent;
}

.summary-card:hover::before {
  opacity: 0.12;
}

.card-main-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 15px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 500;
}

.card-data-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 4px;
}

.card-value {
  font-size: 36px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.1;
  font-family: 'DIN Alternate', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  letter-spacing: -1px;
}

.card-unit {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
}

.card-desc {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.card-icon-container {
  position: relative;
  z-index: 2;
}

.card-icon-bg {
  width: 60px;
  height: 60px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
}

.summary-card:hover .card-icon-bg {
  background: white;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

/* 标签导航优化 */
.modern-tabs-nav {
  background: transparent;
  padding: 0;
  margin-bottom: 24px;
  border: none;
}

.modern-tabs-nav :deep(.el-tabs__content) {
  overflow: visible;
}

.modern-tabs-nav :deep(.el-tab-pane) {
  transition: none !important;
}

.tabs-container {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.modern-tab-btn {
  padding: 10px 24px;
  border: none;
  background: white;
  border-radius: 50px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #606266;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.modern-tab-btn:hover {
  color: #1890ff;
  background: #e6f7ff;
  transform: translateY(-2px);
}

.modern-tab-btn.active {
  background: #1890ff;
  color: white;
  box-shadow: 0 6px 16px rgba(24, 144, 255, 0.35);
  transform: translateY(-2px);
}

.tab-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-icon .el-icon {
  font-size: 18px;
}

/* 内容区域优化 */
.modern-tab-content {
  background: white;
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 32px;
  border: none;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f2f5;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-icon {
  background: #f0f2f5;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #1890ff;
}

/* 图表网格优化 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 24px;
}

.single-chart .charts-grid {
  grid-template-columns: 1fr;
}

.chart-container {
  background: white;
  border-radius: 16px;
  border: 1px solid #f0f2f5;
  overflow: hidden;
}

.chart-container:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.06);
  border-color: transparent;
}

.chart-container.card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.02);
}

.chart-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f2f5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fafafa;
}

.chart-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  border-left: 4px solid #1890ff;
  padding-left: 12px;
}

.chart-subtitle {
  font-size: 12px;
  color: #909399;
  padding: 4px 10px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
}

.chart-content {
  height: 320px;
  padding: 24px;
}

.chart-empty {
  height: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  gap: 16px;
  background: #fafafa;
}

.empty-icon {
  font-size: 64px;
  color: #c0c4cc;
}

/* 数据卡片优化 */
.data-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.data-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #f0f2f5;
  position: relative;
  overflow: hidden;
}

.data-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #1890ff, #36cfc9);
  opacity: 0;
}

.data-card:hover {
  border-color: transparent;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  transform: translateY(-4px);
}

.data-card:hover::before {
  opacity: 1;
}

.data-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.data-card-icon {
  font-size: 28px;
  background: #f0f7ff;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.data-card-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #606266;
  flex: 1;
}

.data-card-value {
  font-size: 36px;
  font-weight: 700;
  color: #303133;
  text-align: right;
  font-family: 'DIN Alternate', sans-serif;
  letter-spacing: 1px;
}

/* 响应式设?*/
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .listheader {
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
    padding: 20px;
  }
  
  .header-subtitle {
    margin-left: 0;
    margin-top: 8px;
  }
  
  .listheader-actions {
    justify-content: flex-end;
  }
  
  .stats-summary-cards {
    grid-template-columns: 1fr;
  }
  
  .tabs-container {
    overflow-x: auto;
    padding-bottom: 8px;
    -webkit-overflow-scrolling: touch;
  }
  
  .modern-tab-btn {
    flex-shrink: 0;
  }
  
  .modern-tab-content {
    padding: 20px;
  }
}
/* 16. 综合统计页面样式 */
.stats-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.overview-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.stats-overview .stat-icon {
    font-size: 40px;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--panel-bg, #f8f9fa);
    border-radius: 50%;
}

.stat-content h3 {
    margin: 0 0 5px 0;
    color: var(--primary-color);
    font-size: 30px;
    font-weight: 700;
}

.stat-content p {
    margin: 0;
    color: var(--text-secondary, #666);
    font-size: var(--font-size-sm);
}

.detailed-stats {
    display: grid;
    gap: 25px;
}

.stats-section {
    background: var(--card-bg, white);
    border-radius: 8px;
    padding: 25px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid #e1e8ed;
}

.stats-section h3 {
    margin: 0 0 20px 0;
    color: var(--text-primary, #333);
    font-size: 25px;
    border-bottom: 2px solid #1c6cd4;
    padding-bottom: 10px;
}

.detailed-stats .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
}

.stats-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.stats-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
}

.stats-label {
    color: var(--text-secondary, #666);
    font-size: var(--font-size-sm);
}

.stats-value {
    color: var(--text-primary, #333);
    font-weight: 600;
    font-size: var(--font-size-sm);
}

/* 23. 数据中心页面样式 */
.data-center-wrapper {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

.quick-reports-section {
    margin-bottom: 30px;
}

.quick-reports-section .section-title {
    margin: 0 0 20px 0;
    font-size: 22.5px;
    font-weight: 600;
    color: #2c3e50;
}

.quick-reports-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}

.section-divider {
    margin: 30px 0;
    border: none;
    border-top: 2px solid #e1e8ed;
}

.stats-tabs-nav {
    display: flex;
    gap: 8px;
    margin-bottom: 25px;
    border-bottom: 2px solid #e1e8ed;
    padding-bottom: 0;
    flex-wrap: wrap;
}

.data-center-wrapper .main-stats-section {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    border: 1px solid #e1e8ed;
}

.data-center-wrapper .main-stats-section h3 {
    color: #2c3e50;
    margin: 0 0 20px 0;
    font-size: 25px;
    font-weight: 600;
    border-bottom: 2px solid #f0f0f0;
    padding-bottom: 12px;
}

.data-center-wrapper .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
}

.data-center-wrapper .stats-item {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 18px;
    border: 1px solid #e1e8ed;
}

.data-center-wrapper .stats-item:hover {
    background: #ffffff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    transform: translateY(-2px);
}

.data-center-wrapper .stats-item h4 {
    font-size: 20px;
    font-weight: 600;
    color: #2c3e50;
    margin: 0 0 14px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #e1e8ed;
}

.data-center-wrapper .stats-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.data-center-wrapper .stats-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
}

.data-center-wrapper .stats-label {
    font-size: 17.5px;
    color: #7f8c8d;
    font-weight: 500;
}

.data-center-wrapper .stats-value {
    font-size: 17.5px;
    color: #2c3e50;
    font-weight: 600;
}
</style>
