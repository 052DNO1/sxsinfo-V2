
// Chart option generators
// This file centralizes ECharts configuration logic to avoid duplication in components.

/**
 * Common chart style configuration
 */
export const commonChartStyle = {
  backgroundColor: 'transparent',
  textStyle: { color: '#666' },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '10%',
    top: '15%',
    containLabel: true
  }
}

/**
 * Get common chart colors
 */
export const getChartColors = () => [
  '#1890ff', '#52c41a', '#fa8c16', '#f5222d', 
  '#722ed1', '#13c2c2', '#eb2f96', '#faad14',
  '#2f54eb', '#a0d911', '#f759ab', '#37cdc4'
]

/**
 * Generate a basic pie chart option
 * @param {Array} data - Array of { name, value, itemStyle? }
 * @param {Object} options - Custom options { name, radius, center, colors }
 */
export const getPieChartOption = (data, options = {}) => {
  if (!data || !data.length) return {}
  
  const { 
    name = '分布统计', 
    radius = ['45%', '65%'], 
    center = ['75%', '50%'],
    formatter = '{b}: {c}'
  } = options

  const colors = options.colors || getChartColors()

  return {
    ...commonChartStyle,
    tooltip: { 
      trigger: 'item', 
      formatter: options.tooltipFormatter || formatter 
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'center',
      textStyle: commonChartStyle.textStyle
    },
    series: [
      {
        name,
        type: 'pie',
        radius,
        center,
        avoidLabelOverlap: false,
        itemStyle: { borderColor: '#fff', borderWidth: 2 },
        label: {
          show: true,
          position: 'outside',
          formatter: '{b}\n{c}',
          color: '#666',
          lineHeight: 18
        },
        labelLine: {
          show: true,
          length: 15,
          length2: 20
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        },
        data: data.map((item, index) => ({
          ...item,
          value: Number(item.value),
          itemStyle: item.itemStyle || { color: colors[index % colors.length] }
        }))
      }
    ]
  }
}

/**
 * Generate a basic bar/line chart option
 * @param {Array} labels - X-axis labels
 * @param {Array} data - Series data
 * @param {Object} options - Custom options { type, name, color, yAxisName }
 */
export const getAxisChartOption = (labels, data, options = {}) => {
  if (!labels || !labels.length) return {}
  
  const {
    type = 'bar',
    name = '数量',
    color = '#1890ff',
    yAxisName = '',
    barWidth = '40%'
  } = options

  const colors = options.colors || getChartColors()

  return {
    ...commonChartStyle,
    tooltip: { trigger: 'axis' },
    grid: { ...commonChartStyle.grid, top: '10%' },
    xAxis: {
      type: 'category',
      data: labels,
      axisLine: { lineStyle: { color: '#d9d9d9' } },
      axisLabel: { color: '#666', rotate: options.rotateX || 0 }
    },
    yAxis: {
      type: 'value',
      name: yAxisName,
      splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
      axisLine: { show: false },
      axisLabel: { color: '#999' }
    },
    series: [
      {
        name,
        type,
        data,
        barWidth: type === 'bar' ? barWidth : undefined,
        smooth: type === 'line',
        symbol: type === 'line' ? 'circle' : undefined,
        symbolSize: type === 'line' ? 6 : undefined,
        lineStyle: type === 'line' ? { width: 3, color } : undefined,
        itemStyle: {
          color: (params) => {
             if (options.colorByItem) {
                 return colors[params.dataIndex % colors.length]
             }
             return color
          },
          borderRadius: type === 'bar' ? [4, 4, 0, 0] : 0
        },
        label: options.showLabel ? { show: true, position: 'top', color: '#333' } : undefined
      }
    ]
  }
}
