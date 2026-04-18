<!-- 统计项组�?-->
<template>
  <div class="stats-item">
    <h4>{{ title }}</h4>
    <div class="stats-list">
      <div v-if="hasData" class="stats-content">
        <div v-for="(item, index) in displayItems" :key="index" class="stats-row">
          <span class="stats-label">{{ item.label }}</span>
          <span class="stats-value">{{ item.value }}</span>
        </div>
      </div>
      <div v-else class="stats-row">
        <span class="stats-label" style="color: #999;">无数�?/span>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'StatsItem',
  props: {
    title: {
      type: String,
      required: true
    },
    data: {
      type: [Object, Array],
      default: () => ({})
    },
    formatter: {
      type: Function,
      default: null
    },
    valueFormatter: {
      type: Function,
      default: null
    }
  },
  setup(props) {
    const hasData = computed(() => {
      if (Array.isArray(props.data)) {
        return props.data.length> 0
      }
      return props.data && Object.keys(props.data).length> 0
    })

    const displayItems = computed(() => {
      if (!hasData.value) return []

      if (Array.isArray(props.data)) {
        return props.data.map((item, index) => {
          if (props.formatter) {
            return props.formatter(item, index)
          }
          return {
            label: item.label || item.name || `�?{index + 1}`,
            value: item.value || item.count || item
          }
        })
      }

      // 处理对象数据
      return Object.entries(props.data).map(([key, value]) => {
        let label = key
        let displayValue = value

        // 如果值是对象，尝试提�?count 或其他属�?
        if (typeof value === 'object' && value !== null) {
          if (value.count !== undefined) {
            displayValue = value.count
            if (value.capacity !== undefined) {
              displayValue = `${value.count}�?(${value.capacity}�?`
            }
          } else {
            displayValue = value
          }
        }

        // 使用自定义格式化函数
        if (props.formatter) {
          const formatted = props.formatter(key, value)
          return formatted
        }

        // 使用值格式化函数
        if (props.valueFormatter) {
          displayValue = props.valueFormatter(value)
        }

        return {
          label,
          value: displayValue
        }
      })
    })

    return {
      hasData,
      displayItems
    }
  }
}
</script>

<style scoped>
.stats-item {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.stats-item h4 {
  margin-bottom: 15px;
  color: #333;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stats-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stats-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.stats-label {
  color: #666;
}

.stats-value {
  font-weight: bold;
  color: #007bff;
}
</style>

