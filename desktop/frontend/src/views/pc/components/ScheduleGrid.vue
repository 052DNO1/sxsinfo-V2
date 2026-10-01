<!-- 课程表网格组件 -->
<template>
  <div class="schedule-grid-container">
    <div class="grid-header">
      <div class="header-left">
        <span class="grid-title">{{ title }}</span>
        <el-tag
          v-if="selectedSxsName"
          type="primary"
          size="small"
        >
          {{ selectedSxsName }}
        </el-tag>
      </div>
      <div class="header-right">
        <span class="week-selector-label">当前周次:</span>
        <el-select
          v-model="selectedWeek"
          placeholder="选择周次"
          size="small"
          class="week-select"
          @change="handleWeekChange"
        >
          <el-option
            v-for="w in 20"
            :key="w"
            :label="`第${w}周`"
            :value="w"
          />
        </el-select>
      </div>
    </div>

    <div
      v-loading="loading"
      class="schedule-table-wrapper"
    >
      <table class="schedule-table">
        <thead>
          <tr>
            <th class="time-header">
              节次/星期
            </th>
            <th
              v-for="day in weekdays"
              :key="day.value"
              class="day-header"
            >
              {{ day.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="period in periods"
            :key="period.value"
          >
            <td class="period-cell">
              <div class="period-name">
                {{ period.label }}
              </div>
              <div class="period-time">
                {{ period.time }}
              </div>
            </td>
            <td 
              v-for="day in weekdays" 
              :key="day.value" 
              class="schedule-cell"
              :class="getCellClass(day.value, period.value)"
              @click="handleCellClick(day.value, period.value)"
            >
              <div
                v-if="getCourse(day.value, period.value)"
                class="course-content"
              >
                <div class="course-name">
                  {{ getCourse(day.value, period.value).course_name }}
                </div>
                <div class="course-info">
                  <span
                    v-if="getCourse(day.value, period.value).class_name"
                    class="course-class"
                  >
                    {{ getCourse(day.value, period.value).class_name }}
                  </span>
                  <span
                    v-if="getCourse(day.value, period.value).teacher_name"
                    class="course-teacher"
                  >
                    {{ getCourse(day.value, period.value).teacher_name }}
                  </span>
                </div>
                <div class="course-actions">
                  <el-button
                    type="primary"
                    size="small"
                    text
                    @click.stop="handleEditCourse(getCourse(day.value, period.value))"
                  >
                    编辑
                  </el-button>
                  <el-button
                    type="danger"
                    size="small"
                    text
                    @click.stop="handleDeleteCourse(getCourse(day.value, period.value))"
                  >
                    删除
                  </el-button>
                </div>
              </div>
              <div
                v-else
                class="empty-cell"
                @click="handleAddCourse(day.value, period.value)"
              >
                <el-icon><Plus /></el-icon>
                <span>空闲</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="grid-footer">
      <div class="legend">
        <span class="legend-item">
          <span class="legend-color has-course" />
          <span>有课</span>
        </span>
        <span class="legend-item">
          <span class="legend-color empty" />
          <span>空闲</span>
        </span>
      </div>
      <div class="stats">
        共<strong>{{ courseCount }}</strong> 门课程，
        空闲 <strong>{{ emptyCount }}</strong> 个时段
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'

export default {
  name: 'ScheduleGrid',
  components: { Plus },
  props: {
    courses: {
      type: Array,
      default: () => []
    },
    title: {
      type: String,
      default: '课程时刻表'
    },
    loading: {
      type: Boolean,
      default: false
    },
    selectedSxsName: {
      type: String,
      default: ''
    }
  },
  emits: ['edit', 'delete', 'add', 'week-change'],
  setup(props, { emit }) {
    const selectedWeek = ref(1)

    const weekdays = [
      { value: 1, label: '周一' },
      { value: 2, label: '周二' },
      { value: 3, label: '周三' },
      { value: 4, label: '周四' },
      { value: 5, label: '周五' },
      { value: 6, label: '周六' },
      { value: 7, label: '周日' }
    ]

    const periods = [
      { value: '1-2', label: '1-2节', time: '08:00-09:40' },
      { value: '3-4', label: '3-4节', time: '10:00-11:40' },
      { value: '5-6', label: '5-6节', time: '13:00-14:40' },
      { value: '7-8', label: '7-8节', time: '15:00-16:40' },
      { value: '9-10', label: '9-10节', time: '18:00-19:40' }
    ]

    const parsePeriodRange = (periodStr) => {
      if (!periodStr) return []
      const periods = []
      const cleanStr = periodStr.replace('节', '').trim()
      const parts = cleanStr.split(',')
      for (const part of parts) {
        const trimmed = part.trim()
        if (trimmed.includes('-')) {
          const [start, end] = trimmed.split('-').map(n => parseInt(n.trim()))
          for (let i = start; i <= end; i++) {
            periods.push(i)
          }
        } else {
          periods.push(parseInt(trimmed))
        }
      }
      return periods
    }

    const parseWeekRange = (weekStr) => {
      if (!weekStr) return []
      const weeks = []
      const cleanStr = weekStr.replace('周', '').trim()
      const parts = cleanStr.split(',')
      for (const part of parts) {
        const trimmed = part.trim()
        if (trimmed.includes('-')) {
          const [start, end] = trimmed.split('-').map(n => parseInt(n.trim()))
          for (let i = start; i <= end; i++) {
            weeks.push(i)
          }
        } else {
          weeks.push(parseInt(trimmed))
        }
      }
      return weeks
    }

    const getPeriodKey = (periodNum) => {
      if (periodNum <= 2) return '1-2'
      if (periodNum <= 4) return '3-4'
      if (periodNum <= 6) return '5-6'
      if (periodNum <= 8) return '7-8'
      return '9-10'
    }

    const weekdayMap = {
      '周一': 1, '周二': 2, '周三': 3, '周四': 4, '周五': 5, '周六': 6, '周日': 7
    }

    const getCourseWeekday = (course) => {
      if (course.weekday) {
        return weekdayMap[course.weekday] || course.weekday || 0
      }
      return course.weekday || 0
    }

    const courseGrid = computed(() => {
      const grid = {}
      
      for (const course of props.courses) {
        const weekday = getCourseWeekday(course)
        if (!weekday) continue

        const courseWeeks = parseWeekRange(course.weeks)
        if (!courseWeeks.includes(selectedWeek.value)) continue

        const coursePeriods = parsePeriodRange(course.time_slot)
        const periodKeys = new Set(coursePeriods.map(p => getPeriodKey(p)))

        for (const periodKey of periodKeys) {
          const key = `${weekday}-${periodKey}`
          if (!grid[key]) {
            grid[key] = course
          }
        }
      }
      
      return grid
    })

    const getCourse = (weekday, period) => {
      return courseGrid.value[`${weekday}-${period}`]
    }

    const getCellClass = (weekday, period) => {
      const course = getCourse(weekday, period)
      return {
        'has-course': !!course,
        'empty': !course
      }
    }

    const handleCellClick = (weekday, period) => {
      const course = getCourse(weekday, period)
      if (course) {
        emit('edit', course)
      } else {
        emit('add', { weekday, period })
      }
    }

    const handleEditCourse = (course) => {
      emit('edit', course)
    }

    const handleDeleteCourse = (course) => {
      emit('delete', course)
    }

    const handleAddCourse = (weekday, period) => {
      emit('add', { weekday, period })
    }

    const handleWeekChange = (week) => {
      emit('week-change', week)
    }

    const courseCount = computed(() => {
      return Object.keys(courseGrid.value).length
    })

    const emptyCount = computed(() => {
      let total = weekdays.length * periods.length
      return total - courseCount.value
    })

    return {
      selectedWeek,
      weekdays,
      periods,
      getCourse,
      getCellClass,
      handleCellClick,
      handleEditCourse,
      handleDeleteCourse,
      handleAddCourse,
      handleWeekChange,
      courseCount,
      emptyCount
    }
  }
}
</script>

<style scoped>
.schedule-grid-container {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
}

.grid-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.grid-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.week-selector-label {
  font-size: 14px;
  color: #606266;
}

.week-select {
  width: 120px;
}

.schedule-table-wrapper {
  overflow-x: auto;
  margin-bottom: 20px;
}

.schedule-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.schedule-table th,
.schedule-table td {
  border: 1px solid #ebeef5;
  padding: 0;
  vertical-align: top;
}

.time-header {
  width: 100px;
  background: #f5f7fa;
  font-weight: 600;
  color: #606266;
  padding: 12px 8px;
}

.day-header {
  width: calc((100% - 100px) / 7);
  background: #f5f7fa;
  font-weight: 600;
  color: #606266;
  padding: 12px 8px;
  text-align: center;
}

.period-cell {
  background: #f5f7fa;
  padding: 12px 8px;
  text-align: center;
}

.period-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
  margin-bottom: 4px;
}

.period-time {
  font-size: 12px;
  color: #909399;
}

.schedule-cell {
  min-height: 100px;
  height: 120px;
  cursor: pointer;
  transition: all 0.3s;
}

.schedule-cell:hover {
  background: #f5f9fc;
}

.schedule-cell.has-course {
  background: #f0f7fc;
  border-left: 3px solid #91c2f5;
}

.schedule-cell.has-course:hover {
  background: #e6f1fa;
}

.schedule-cell.empty {
  background: #fdfdfd;
}

.schedule-cell.empty:hover {
  background: #f8f8f8;
}

.course-content {
  padding: 10px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.course-name {
  font-weight: 600;
  color: #5a9bd5;
  font-size: 14px;
  margin-bottom: 6px;
  word-break: break-all;
}

.course-info {
  flex: 1;
  font-size: 12px;
  color: #7a8b99;
  line-height: 1.5;
}

.course-class,
.course-teacher {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-actions {
  display: flex;
  gap: 4px;
  margin-top: 6px;
  opacity: 0;
  transition: opacity 0.3s;
}

.schedule-cell:hover .course-actions {
  opacity: 1;
}

.course-actions .el-button {
  padding: 2px 6px;
  font-size: 12px;
}

.empty-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #d0d5db;
  font-size: 14px;
  gap: 4px;
}

.empty-cell:hover {
  color: #91c2f5;
}

.empty-cell .el-icon {
  font-size: 20px;
}

.grid-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.legend {
  display: flex;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-color.has-course {
  background: #f0f7fc;
  border: 1px solid #91c2f5;
}

.legend-color.empty {
  background: #fdfdfd;
  border: 1px solid #e4e7ed;
}

.stats {
  font-size: 13px;
  color: #909399;
}

.stats strong {
  color: #5a9bd5;
}
</style>
