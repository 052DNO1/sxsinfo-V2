
/*首页图表展示逻辑*/
import { computed } from 'vue'

export function useDashboardCharts(stats, chartStats, superuserChartStats, sxsadminChartStats, teacherChartStats, systemSuperuserChartStats, safeUser) {
  const canShowCharts = computed(() => {
    const u = safeUser.value
    return u.is_superuser || (u.is_super_admin && !u.is_superuser) || u.is_departadmin || u.is_sxsadmin || u.is_teacher
  })

  const isSxsadmin = computed(() => {
    const u = safeUser.value
    return u.is_sxsadmin && !u.is_super_admin && !u.is_departadmin
  })

  const isSystemSuperuser = computed(() => {
    const u = safeUser.value
    return u.is_superuser
  })

  const systemSuperuserStats = computed(() => [
    { icon: 'UserFilled', value: systemSuperuserChartStats.value?.total_users || 0, label: '用户总数' },
    { icon: 'Monitor', value: systemSuperuserChartStats.value?.active_sessions || 0, label: '活跃会话' }
  ])

  const superuserStats = computed(() => [
    { icon: 'Calendar', value: stats.value?.users?.total || 0, label: '用户总数' },
    { icon: 'OfficeBuilding', value: stats.value?.laboratories?.total || 0, label: '实训室总数' },
    { icon: 'DataAnalysis', value: stats.value?.equipment?.total || 0, label: '设备总数' },
    { icon: 'Setting', value: stats.value?.work_orders?.pending || 0, label: '待处理工单' }
  ])

  const commonStats = computed(() => {
    const list = []
    const u = safeUser.value
    
    if (u.is_sxsadmin && !u.is_super_admin && !u.is_departadmin) {
      list.push(
        { icon: 'OfficeBuilding', value: sxsadminChartStats.value?.managed_laboratories || 0, label: '管理实训室数' },
        { icon: 'DataAnalysis', value: sxsadminChartStats.value?.equipment?.total || 0, label: '设备总数' },
        { icon: 'DataLine', value: sxsadminChartStats.value?.records?.total || 0, label: '本学期使用次数' },
        { icon: 'Setting', value: sxsadminChartStats.value?.work_orders?.pending || 0, label: '待维护项总数' }
      )
      return list
    } else if (u.is_teacher && !u.is_super_admin && !u.is_departadmin && !u.is_sxsadmin) {
      list.push(
        { icon: 'DataLine', value: teacherChartStats.value?.total_records || 0, label: '本学期使用次数' },
        { icon: 'OfficeBuilding', value: teacherChartStats.value?.used_laboratories || 0, label: '使用实训室数' },
        { icon: 'UserFilled', value: teacherChartStats.value?.total_students || 0, label: '累计服务学生数' },
        { icon: 'Calendar', value: teacherChartStats.value?.month_records || 0, label: '本月使用次数' }
      )
      return list
    } else {
      list.push({ icon: 'UserFilled', value: stats.value?.users?.total || 0, label: '用户总数' })
    }
    
    list.push(
      { icon: 'DataLine', value: stats.value?.records?.today || 0, label: '今日使用记录' },
      { icon: 'Setting', value: stats.value?.work_orders?.pending || 0, label: '待维护项总数' },
      { icon: 'Box', value: stats.value?.laboratories?.total || 0, label: '实训室总数' }
    )
    return list
  })

  const usageTrendData = computed(() => {
    const byMonth = chartStats.value?.records?.by_month || {}
    return Object.entries(byMonth)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([label, count]) => ({ label, count }))
  })

  const equipmentSxsData = computed(() => {
    const byLab = chartStats.value?.equipment?.by_laboratory || {}
    return Object.entries(byLab).map(([label, count]) => ({ label, count }))
  })

  const usageTrendOption = computed(() => {
    if (!usageTrendData.value.length) return {}
    const labels = usageTrendData.value.map(d => d.label)
    const data = usageTrendData.value.map(d => d.count)
    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: labels,
        boundaryGap: false,
        axisLine: { lineStyle: { color: '#d9d9d9' } },
        axisLabel: { 
          color: '#666',
          interval: 0,
          rotate: labels.length > 6 ? 30 : 0,
          fontSize: 12
        }
      },
      yAxis: {
        type: 'value',
        name: '次数',
        nameTextStyle: { color: '#666', fontSize: 12 },
        splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
        axisLine: { show: false },
        axisLabel: { color: '#999', fontSize: 12 }
      },
      series: [{
        name: '使用记录',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 3, color: '#1890ff' },
        itemStyle: { color: '#1890ff' },
        areaStyle: {
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
            { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
            { offset: 1, color: 'rgba(24, 144, 255, 0.05)' }
          ]}
        },
        data
      }]
    }
  })

  const equipmentSxsOption = computed(() => {
    if (!equipmentSxsData.value.length) return {}
    const labels = equipmentSxsData.value.map(d => d.label)
    const data = equipmentSxsData.value.map(d => d.count)
    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis', formatter: '{b}: {c}个设备' },
      grid: { left: '3%', right: '4%', bottom: '18%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: labels,
        axisLine: { lineStyle: { color: '#d9d9d9' } },
        axisLabel: { 
          color: '#666', 
          interval: 0, 
          rotate: labels.length > 4 ? 30 : 0,
          fontSize: 12
        }
      },
      yAxis: {
        type: 'value',
        name: '数量(个)',
        nameTextStyle: { color: '#666', fontSize: 12 },
        splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
        axisLine: { show: false },
        axisLabel: { color: '#999', fontSize: 12 }
      },
      series: [{
        name: '设备数量',
        type: 'bar',
        itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] },
        barWidth: '40%',
        data
      }]
    }
  })

  const superuserDeptDistributionData = computed(() => {
    const byDept = superuserChartStats.value?.dept_distribution || []
    return byDept.map(item => ({
      label: item.name,
      count: item.count
    }))
  })

  const superuserUserTypeData = computed(() => {
    const byType = superuserChartStats.value?.user_type_distribution || []
    return byType.map(item => ({
      label: item.name,
      count: item.count
    }))
  })

  const superuserDeptDistributionOption = computed(() => {
    if (!superuserDeptDistributionData.value.length) return {}
    const labels = superuserDeptDistributionData.value.map(d => d.label)
    const data = superuserDeptDistributionData.value.map(d => d.count)
    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis', formatter: '{b}: {c}个实训室' },
      grid: { left: '3%', right: '4%', bottom: '18%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: labels,
        axisLine: { lineStyle: { color: '#d9d9d9' } },
        axisLabel: { 
          color: '#666', 
          interval: 0, 
          rotate: labels.length > 4 ? 30 : 0,
          fontSize: 12
        }
      },
      yAxis: {
        type: 'value',
        name: '数量',
        nameTextStyle: { color: '#666', fontSize: 12 },
        splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
        axisLine: { show: false },
        axisLabel: { color: '#999', fontSize: 12 }
      },
      series: [{
        name: '实训室数量',
        type: 'bar',
        itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] },
        barWidth: '50%',
        data
      }]
    }
  })

  const superuserUserTypeOption = computed(() => {
    if (!superuserUserTypeData.value.length) return {}
    const labels = superuserUserTypeData.value.map(d => d.label)
    const data = superuserUserTypeData.value.map(d => d.count)
    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis', formatter: '{b}: {c}人' },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: labels,
        axisLine: { lineStyle: { color: '#d9d9d9' } },
        axisLabel: { 
          color: '#666', 
          interval: 0,
          fontSize: 12
        }
      },
      yAxis: {
        type: 'value',
        name: '人数',
        nameTextStyle: { color: '#666', fontSize: 12 },
        splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
        axisLine: { show: false },
        axisLabel: { color: '#999', fontSize: 12 }
      },
      series: [{
        name: '用户数量',
        type: 'bar',
        itemStyle: { color: '#67c23a', borderRadius: [4, 4, 0, 0] },
        barWidth: '40%',
        data
      }]
    }
  })

  const sxsadminEquipmentData = computed(() => {
    const byLab = sxsadminChartStats.value?.equipment?.by_laboratory || {}
    return Object.entries(byLab).map(([label, count]) => ({ label, count }))
  })

  const sxsadminRecordsByMonthData = computed(() => {
    const byMonth = sxsadminChartStats.value?.records?.by_month || {}
    return Object.entries(byMonth)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([label, count]) => ({ label, count }))
  })

  const sxsadminEquipmentOption = computed(() => {
    if (!sxsadminEquipmentData.value.length) return {}
    const labels = sxsadminEquipmentData.value.map(d => d.label)
    const data = sxsadminEquipmentData.value.map(d => d.count)
    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis', formatter: '{b}: {c}个设备' },
      grid: { left: '3%', right: '4%', bottom: '18%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: labels,
        axisLine: { lineStyle: { color: '#d9d9d9' } },
        axisLabel: { 
          color: '#666', 
          interval: 0, 
          rotate: labels.length > 4 ? 30 : 0,
          fontSize: 12
        }
      },
      yAxis: {
        type: 'value',
        name: '数量(个)',
        nameTextStyle: { color: '#666', fontSize: 12 },
        splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
        axisLine: { show: false },
        axisLabel: { color: '#999', fontSize: 12 }
      },
      series: [{
        name: '设备数量',
        type: 'bar',
        itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] },
        barWidth: '40%',
        data
      }]
    }
  })

  const sxsadminRecordsTrendOption = computed(() => {
    if (!sxsadminRecordsByMonthData.value.length) return {}
    const labels = sxsadminRecordsByMonthData.value.map(d => d.label)
    const data = sxsadminRecordsByMonthData.value.map(d => d.count)
    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: labels,
        boundaryGap: false,
        axisLine: { lineStyle: { color: '#d9d9d9' } },
        axisLabel: { 
          color: '#666',
          interval: 0,
          rotate: labels.length > 6 ? 30 : 0,
          fontSize: 12
        }
      },
      yAxis: {
        type: 'value',
        name: '次数',
        nameTextStyle: { color: '#666', fontSize: 12 },
        splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
        axisLine: { show: false },
        axisLabel: { color: '#999', fontSize: 12 }
      },
      series: [{
        name: '使用记录',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 3, color: '#52c41a' },
        itemStyle: { color: '#52c41a' },
        areaStyle: {
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
            { offset: 0, color: 'rgba(82, 196, 26, 0.3)' },
            { offset: 1, color: 'rgba(82, 196, 26, 0.05)' }
          ]}
        },
        data
      }]
    }
  })

  const teacherRecordsByMonthData = computed(() => {
    const byMonth = teacherChartStats.value?.records?.by_month || {}
    return Object.entries(byMonth)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([label, count]) => ({ label, count }))
  })

  const teacherRecordsBySxsData = computed(() => {
    const bySxs = teacherChartStats.value?.records_by_sxs || {}
    return Object.entries(bySxs).map(([label, count]) => ({ label, count }))
  })

  const teacherRecordsTrendOption = computed(() => {
    if (!teacherRecordsByMonthData.value.length) return {}
    const labels = teacherRecordsByMonthData.value.map(d => d.label)
    const data = teacherRecordsByMonthData.value.map(d => d.count)
    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: labels,
        boundaryGap: false,
        axisLine: { lineStyle: { color: '#d9d9d9' } },
        axisLabel: { 
          color: '#666',
          interval: 0,
          rotate: labels.length > 6 ? 30 : 0,
          fontSize: 12
        }
      },
      yAxis: {
        type: 'value',
        name: '次数',
        nameTextStyle: { color: '#666', fontSize: 12 },
        splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
        axisLine: { show: false },
        axisLabel: { color: '#999', fontSize: 12 }
      },
      series: [{
        name: '使用记录',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 3, color: '#722ed1' },
        itemStyle: { color: '#722ed1' },
        areaStyle: {
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
            { offset: 0, color: 'rgba(114, 46, 209, 0.3)' },
            { offset: 1, color: 'rgba(114, 46, 209, 0.05)' }
          ]}
        },
        data
      }]
    }
  })

  const teacherSxsUsageOption = computed(() => {
    if (!teacherRecordsBySxsData.value.length) return {}
    const labels = teacherRecordsBySxsData.value.map(d => d.label)
    const data = teacherRecordsBySxsData.value.map(d => d.count)
    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis', formatter: '{b}: {c}次' },
      grid: { left: '3%', right: '4%', bottom: '18%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: labels,
        axisLine: { lineStyle: { color: '#d9d9d9' } },
        axisLabel: { 
          color: '#666', 
          interval: 0, 
          rotate: labels.length > 4 ? 30 : 0,
          fontSize: 12
        }
      },
      yAxis: {
        type: 'value',
        name: '使用次数',
        nameTextStyle: { color: '#666', fontSize: 12 },
        splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
        axisLine: { show: false },
        axisLabel: { color: '#999', fontSize: 12 }
      },
      series: [{
        name: '使用次数',
        type: 'bar',
        itemStyle: { color: '#722ed1', borderRadius: [4, 4, 0, 0] },
        barWidth: '40%',
        data
      }]
    }
  })

  const systemSuperuserLoginActivityData = computed(() => {
    const stats = systemSuperuserChartStats.value || {}
    return [
      { label: '近30天登录', count: stats.recently_active_users || 0 },
      { label: '超30天未登录', count: stats.inactive_users || 0 },
    ]
  })

  const systemSuperuserLoginActivityOption = computed(() => {
    if (!systemSuperuserLoginActivityData.value.length) return {}
    const labels = systemSuperuserLoginActivityData.value.map(d => d.label)
    const data = systemSuperuserLoginActivityData.value.map(d => d.count)
    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis', formatter: '{b}: {c}人' },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: labels,
        axisLine: { lineStyle: { color: '#d9d9d9' } },
        axisLabel: { 
          color: '#666', 
          interval: 0,
          fontSize: 12
        }
      },
      yAxis: {
        type: 'value',
        name: '人数',
        nameTextStyle: { color: '#666', fontSize: 12 },
        splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
        axisLine: { show: false },
        axisLabel: { color: '#999', fontSize: 12 }
      },
      series: [{
        name: '用户数量',
        type: 'bar',
        itemStyle: { color: '#52c41a', borderRadius: [4, 4, 0, 0] },
        barWidth: '50%',
        data
      }]
    }
  })

  const systemSuperuserAccountStatusData = computed(() => {
    const stats = systemSuperuserChartStats.value || {}
    return [
      { label: '已启用', count: stats.enabled_users || 0 },
      { label: '已禁用', count: stats.disabled_users || 0 },
    ]
  })

  const systemSuperuserAccountStatusOption = computed(() => {
    if (!systemSuperuserAccountStatusData.value.length) return {}
    const labels = systemSuperuserAccountStatusData.value.map(d => d.label)
    const data = systemSuperuserAccountStatusData.value.map(d => d.count)
    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis', formatter: '{b}: {c}人' },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: labels,
        axisLine: { lineStyle: { color: '#d9d9d9' } },
        axisLabel: { 
          color: '#666', 
          interval: 0,
          fontSize: 12
        }
      },
      yAxis: {
        type: 'value',
        name: '人数',
        nameTextStyle: { color: '#666', fontSize: 12 },
        splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
        axisLine: { show: false },
        axisLabel: { color: '#999', fontSize: 12 }
      },
      series: [{
        name: '用户数量',
        type: 'bar',
        itemStyle: { color: '#1890ff', borderRadius: [4, 4, 0, 0] },
        barWidth: '50%',
        data
      }]
    }
  })

  return {
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
  }
}
