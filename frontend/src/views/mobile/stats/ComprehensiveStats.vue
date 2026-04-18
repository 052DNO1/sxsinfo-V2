<template>
  <div class="mobile-dashboard-page mobile-layout">
    <van-nav-bar
      :title="`数据中心 - ${currentTerm?.termname || ''}`"
      left-arrow
      @click-left="handleBack"
      class="mobile-nav-bar"
    />

    <div class="mobile-content-wrapper">
      <van-tabs v-model:active="activeTab" class="mobile-stats-tabs">
        <van-tab
          v-for="tab in tabs"
          :key="tab.id"
          :name="tab.id"
          :title="tab.label"
        >
          <template #title>
            <van-icon :name="tab.icon" size="16px" style="margin-right: 4px;" />
            {{ tab.label }}
          </template>
        </van-tab>
      </van-tabs>

      <div style="padding: 12px;">
        <van-button
          type="primary"
          block
          :loading="exporting"
          @click="exportReport"
        >
          <van-icon name="chart-trending-o" size="16px" style="margin-right: 4px;" />
          {{ exporting ? '导出中...' : '导出报表' }}
        </van-button>
      </div>

      <div v-show="activeTab === 'sxs'" class="mobile-stats-content">
        <van-cell-group inset style="margin-top: 12px;">
          <van-cell title="按分院分布" />
          <van-cell
            v-for="(data, dept) in stats?.sxs?.by_depart || {}"
            :key="dept"
            :title="dept"
            :value="`${data.count}间 (${data.capacity}人)`"
          />
          <van-cell v-if="!stats?.sxs?.by_depart || Object.keys(stats.sxs.by_depart).length === 0" title="无数据" />
        </van-cell-group>

        <van-cell-group inset style="margin-top: 12px;">
          <van-cell title="按教学楼分布" />
          <van-cell
            v-for="(data, building) in stats?.sxs?.by_building || {}"
            :key="building"
            :title="building"
            :value="`${data.count}间 (${data.capacity}人)`"
          />
          <van-cell v-if="!stats?.sxs?.by_building || Object.keys(stats.sxs.by_building).length === 0" title="无数据" />
        </van-cell-group>

        <van-cell-group inset style="margin-top: 12px;">
          <van-cell title="容量统计" />
          <van-cell title="总容量" :value="`${stats?.sxs?.capacity_stats?.total_capacity || 0}人`" />
          <van-cell title="平均容量" :value="`${formatNumber(stats?.sxs?.capacity_stats?.avg_capacity)}人`" />
          <van-cell title="最大容量" :value="`${stats?.sxs?.capacity_stats?.max_capacity || 0}人`" />
          <van-cell title="最小容量" :value="`${stats?.sxs?.capacity_stats?.min_capacity || 0}人`" />
        </van-cell-group>

        <van-cell-group inset style="margin-top: 12px;">
          <van-cell title="使用情况" />
          <van-cell title="总数量" :value="`${stats?.sxs?.total || 0}间`" />
          <van-cell title="已使用" :value="`${stats?.usage_rate?.used_sxs || 0}间`" />
          <van-cell title="课表使用率" :value="`${stats?.usage_rate?.classroom_rate || 0}%`" />
          <van-cell title="记录使用率" :value="`${stats?.usage_rate?.record_rate || 0}%`" />
        </van-cell-group>
      </div>

      <div v-show="activeTab === 'classes'" class="mobile-stats-content">
        <van-cell-group inset style="margin-top: 12px;">
          <van-cell title="按星期分布" />
          <van-cell
            v-for="(count, weekday) in stats?.classes?.by_weekday || {}"
            :key="weekday"
            :title="weekday"
            :value="`${count}门`"
          />
          <van-cell v-if="!stats?.classes?.by_weekday || Object.keys(stats.classes.by_weekday).length === 0" title="无数据" />
        </van-cell-group>
      </div>

      <div v-show="activeTab === 'records'" class="mobile-stats-content">
        <van-cell-group inset style="margin-top: 12px;">
          <van-cell title="按月份分布" />
          <van-cell
            v-for="(count, month) in stats?.records?.by_month || {}"
            :key="month"
            :title="month"
            :value="`${count}条`"
          />
          <van-cell v-if="!stats?.records?.by_month || Object.keys(stats.records.by_month).length === 0" title="无数据" />
        </van-cell-group>
      </div>

      <div v-show="activeTab === 'maintain'" class="mobile-stats-content">
        <van-cell-group inset style="margin-top: 12px;">
          <van-cell title="维护状态" />
          <van-cell
            v-for="(count, status) in stats?.maintain?.by_status || {}"
            :key="status"
            :title="status"
            :value="`${count}条`"
          />
          <van-cell v-if="!stats?.maintain?.by_status || Object.keys(stats.maintain.by_status).length === 0" title="无数据" />
        </van-cell-group>
      </div>

      <div v-show="activeTab === 'users'" class="mobile-stats-content">
        <van-cell-group inset style="margin-top: 12px;">
          <van-cell title="按角色分布" />
          <van-cell
            v-for="(count, role) in stats?.users?.by_role || {}"
            :key="role"
            :title="getRoleName(role)"
            :value="`${count}人`"
          />
          <van-cell v-if="!stats?.users?.by_role || Object.keys(stats.users.by_role).length === 0" title="无数据" />
        </van-cell-group>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/api'
import axios from 'axios'
import { useMobile } from '@/composables/useMobile'
import { formatNumber } from '@/utils/formatUtils'
import { getCookie } from '@/utils/exportUtils'

export default {
  name: 'ComprehensiveStats',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const currentTerm = ref(null)
    const stats = ref({})
    const activeTab = ref('sxs')
    const exporting = ref(false)
    
    const { init: initMobile, loadVantComponents } = useMobile()
    
    let cleanup = null
    onMounted(async () => {
      cleanup = initMobile()
      loadVantComponents()
      loadData()
    })
    
    onUnmounted(() => {
      if (cleanup) cleanup()
    })

    const tabs = [
      { id: 'sxs', label: '实训室统计', icon: 'shop-o' },
      { id: 'classes', label: '课表统计', icon: 'orders-o' },
      { id: 'records', label: '使用记录统计', icon: 'records' },
      { id: 'maintain', label: '维护记录统计', icon: 'setting-o' },
      { id: 'users', label: '用户统计', icon: 'user-o' }
    ]

    const getRoleName = (role) => {
      const roleMap = {
        'superuser': '超级管理员',
        'departadmin': '分院管理员',
        'sxsadmin': '实训室管理员',
        'teacher': '教师'
      }
      return roleMap[role] || role
    }

    const exportReport = async () => {
      exporting.value = true
      try {
        const csrftoken = getCookie('csrftoken')
        const response = await axios.get('/api/stats/comprehensive/', {
          params: {
            format: 'excel',
            ...route.query
          },
          responseType: 'blob',
          headers: {
            'X-CSRFToken': csrftoken
          }
        })
        
        const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `综合统计报表_${new Date().toISOString().split('T')[0]}.xlsx`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        const { showSuccessToast } = await import('@/utils/mobileDialog')
        showSuccessToast('导出成功')
      } catch (err) {
        console.error('导出失败:', err)
        const { showFailToast } = await import('@/utils/mobileDialog')
        showFailToast('导出失败：' + (err.message || '未知错误'))
      } finally {
        exporting.value = false
      }
    }

    const loadData = async () => {
      try {
        const response = await api.get('/stats/comprehensive/', { params: route.query })
        currentTerm.value = response.current_term
        stats.value = response.stats || {}
      } catch (err) {
        console.error('Load data error:', err)
        const { showFailToast } = await import('@/utils/mobileDialog')
        showFailToast('加载数据失败：' + (err.message || '未知错误'))
      }
    }

    const handleBack = () => {
      router.go(-1)
    }

    return {
      currentTerm,
      stats,
      activeTab,
      exporting,
      tabs,
      formatNumber,
      getRoleName,
      exportReport,
      handleBack
    }
  }
}
</script>
