<template>
  <div class="mobile-page">
    <van-nav-bar title="课程管理" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="search" size="20" color="#4F6EF7" @click="showSearch = true" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <!-- 统计概览 -->
      <div class="stats-overview" v-if="totalCount > 0 || tableData.length > 0">
        <div class="stat-card">
          <div class="stat-icon stat-icon--teal">
            <van-icon name="calendar-o" size="22" />
          </div>
          <div class="stat-info">
            <span class="stat-number">{{ totalCount || tableData.length }}</span>
            <span class="stat-text">门课程</span>
          </div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-card">
          <div class="stat-icon stat-icon--purple">
            <van-icon name="friends-o" size="22" />
          </div>
          <div class="stat-info">
            <span class="stat-number">{{ totalStudents }}</span>
            <span class="stat-text">总人数</span>
          </div>
        </div>
      </div>

      <!-- 日期选择器 -->
      <div class="date-selector" v-if="tableData.length > 0">
        <van-button 
          v-for="(day, index) in weekDays" 
          :key="index"
          :class="{ active: selectedDay === index }"
          @click="selectedDay = index"
          size="small"
          round
        >
          {{ day.label }}
        </van-button>
      </div>

      <van-pull-refresh v-model:refreshing="refreshing" @refresh="handleRefresh">

        <van-empty v-if="error" :description="error" image="error">
          <van-button size="small" type="primary" round @click="loadData()">重试</van-button>
        </van-empty>

        <div v-else-if="!loading && tableData.length === 0" class="empty-state">
          <div class="empty-icon">📚</div>
          <h3>暂无课程</h3>
          <p>点击右下角按钮添加新课程</p>
        </div>

        <div v-else class="class-list animate-fade-in-up">
          <div 
            v-for="(item, index) in tableData" 
            :key="item.id"
            class="class-card"
            :style="{ animationDelay: `${index * 0.05}s` }"
            @click="router.push(`/edit-class/${item.id}`)"
          >
            <!-- 左侧时间徽章（静版设计 - 单一青绿色系） -->
            <div class="time-badge badge-teal">
              <span class="time-text">{{ getTimeText(item.time_slot || item.time) }}</span>
              <span class="day-label">{{ getDayLabel(item.day_of_week || item.weekday) }}</span>
            </div>

            <!-- 中间内容 -->
            <div class="class-content">
              <div class="class-header">
                <h3 class="class-name">{{ item.name || item.course_name }}</h3>
                <span 
                  class="type-tag"
                  :class="'tag-' + (item.type || 'required')"
                >
                  {{ getTypeText(item.type) }}
                </span>
              </div>

              <!-- 教师和班级信息 -->
              <div class="info-row">
                <template v-if="item.teacher_name || item.instructor">
                  <span class="info-item">
                    <van-icon name="user-o" size="12" />
                    {{ item.teacher_name || item.instructor }}
                  </span>
                </template>
                <template v-if="item.class_name || item.classroom">
                  <span class="info-item info-item--highlight">
                    <van-icon name="home-o" size="12" />
                    {{ item.class_name || item.classroom }}
                  </span>
                </template>
              </div>

              <!-- 学生人数 -->
              <div class="student-count" v-if="item.student_count !== undefined || item.students?.length">
                <van-icon name="friends-o" size="12" />
                <span>{{ item.student_count || item.students?.length || 0 }}人</span>
              </div>
            </div>

            <!-- 右侧箭头 -->
            <van-icon name="arrow" color="#C0C4CC" size="16" class="card-arrow" />
          </div>
        </div>

        <Pagination 
          v-if="totalCount > pageSize"
          :show="true"
          :current-page="currentPage"
          :page-size="pageSize"
          :total-count="totalCount"
          @current-change="(p) => loadData({ page: p })"
        />
      </van-pull-refresh>
    </div>

    <div class="floating-action-btn" @click="router.push('/add-class')">
      <van-icon name="plus" size="24" />
    </div>

    <van-popup v-model:show="showSearch" position="top" :style="{ height: 'auto' }">
      <van-search
        v-model="searchKeyword"
        placeholder="搜索课程名称、教师..."
        show-action
        @search="handleSearch"
        @cancel="showSearch = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useClassList } from '@/core/hooks'
import { useNavigation } from '@/core/utils/routeDecision'
import Pagination from '@/views/mobile/components/Pagination.vue'

const router = useRouter()
const { goBack, goHome } = useNavigation()

const {
  tableData,
  loading,
  error,
  totalCount,
  pageSize,
  currentPage,
  loadData
} = useClassList({ immediate: true })

const refreshing = ref(false)
const showSearch = ref(false)
const searchKeyword = ref('')
const selectedDay = ref(0)

const weekDays = [
  { label: '周一', value: 1 },
  { label: '周二', value: 2 },
  { label: '周三', value: 3 },
  { label: '周四', value: 4 },
  { label: '周五', value: 5 },
  { label: '周六', value: 6 },
  { label: '周日', value: 0 }
]

const totalStudents = computed(() => {
  return tableData.value.reduce((sum, item) => sum + (item.student_count || item.students?.length || 0), 0)
})

const getTimeText = (timeSlot) => {
  if (!timeSlot) return '--:--'
  return timeSlot.split('-')[0] || timeSlot
}

const getDayLabel = (dayOfWeek) => {
  const days = ['日', '一', '二', '三', '四', '五', '六']
  const dayNum = typeof dayOfWeek === 'string' ? parseInt(dayOfWeek) : dayOfWeek
  return `周${days[dayNum] || '?'}`
}

const getTypeText = (type) => {
  const map = { 'REQUIRED': '必修', 'ELECTIVE': '选修', 'PRACTICE': '实践', '必修': '必修', '选修': '选修' }
  return map[type] || type || '其他'
}

const handleRefresh = async () => {
  refreshing.value = true
  await loadData()
  refreshing.value = false
}

const handleSearch = () => {
  showSearch.value = false
  loadData({ search: searchKeyword.value })
}
</script>

<style scoped>
.stats-overview {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: linear-gradient(135deg, #E8FAF0 0%, #D1F2E0 100%);
  border-radius: 16px;
  padding: 20px;
  margin: 16px;
  box-shadow: 0 4px 12px rgba(26, 188, 156, 0.1);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-divider {
  width: 1px;
  height: 36px;
  background: rgba(26, 188, 156, 0.2);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon--teal {
  background: rgba(26, 188, 156, 0.15);
  color: #1ABC9C;
}

.stat-icon--purple {
  background: rgba(155, 89, 182, 0.15);
  color: #9B59B6;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-number {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
}

.stat-text {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.date-selector {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  overflow-x: auto;
  margin-bottom: 8px;
}

.date-selector::-webkit-scrollbar {
  display: none;
}

.date-selector .van-button {
  flex-shrink: 0;
  min-width: 60px;
  font-size: 13px;
  background: #f5f7fa;
  color: #666;
  border: none;
}

.date-selector .van-button.active {
  background: linear-gradient(135deg, #1ABC9C 0%, #16A085 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(26, 188, 156, 0.3);
}

.class-list {
  padding: 0 16px;
}

.class-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  background: white;
  border-radius: 16px;
  margin-bottom: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
}

.class-card:active {
  transform: scale(0.98);
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
}

/* 时间徽章 - 静版设计（单一青绿色系） */
.time-badge {
  width: 52px;
  height: 64px;
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.badge-teal {
  background: linear-gradient(135deg, #E8FAF0 0%, #D1F2E8 100%);
}

.badge-teal .time-text {
  color: #1ABC9C;
  font-size: 18px;
  font-weight: 700;
  line-height: 1;
}

.badge-teal .day-label {
  color: #1ABC9C;
  font-size: 11px;
  font-weight: 600;
  line-height: 1;
  opacity: 0.7;
}

.class-content {
  flex: 1;
  min-width: 0;
}

.class-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.class-name {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.type-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 10px;
  flex-shrink: 0;
  white-space: nowrap;
  background: #f5f7fa;
  color: #666;
}

.info-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.info-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.info-item .van-icon {
  opacity: 0.7;
}

.card-arrow {
  flex-shrink: 0;
  opacity: 0.6;
}
</style>