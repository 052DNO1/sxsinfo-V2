<template>
  <div class="mobile-page">
    <van-nav-bar title="归档学期" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <!-- 统计概览 -->
      <div class="stats-overview" v-if="termList.length > 0">
        <div class="stat-card">
          <div class="stat-icon stat-icon--purple">
            <van-icon name="archive-o" size="22" />
          </div>
          <div class="stat-info">
            <span class="stat-number">{{ termList.length }}</span>
            <span class="stat-text">个归档学期</span>
          </div>
        </div>
      </div>

      <van-empty v-if="error" :description="error" image="error">
        <van-button size="small" type="primary" round @click="loadData()">重试</van-button>
      </van-empty>

      <div v-else-if="!loading && termList.length === 0" class="empty-state">
        <div class="empty-icon">📦</div>
        <h3>暂无归档学期</h3>
        <p>已归档的学期将显示在这里</p>
      </div>

      <div v-else class="archived-list animate-fade-in-up">
        <div 
          v-for="(item, index) in termList" 
          :key="item.id"
          class="archived-card"
          :style="{ animationDelay: `${index * 0.05}s` }"
          @click="handleItemClick(item)"
        >
          <!-- 左侧指示条（归档专用颜色） -->
          <div class="card-indicator"></div>

          <!-- 图标区 -->
          <div class="icon-wrapper icon--archived">
            <van-icon name="certificate" size="24" />
          </div>

          <!-- 内容区 -->
          <div class="archived-content">
            <div class="term-header">
              <h3 class="term-name">{{ item.name || item.termname }}</h3>
              <span class="archived-badge">
                <van-icon name="lock" size="12" /> 已归档
              </span>
            </div>

            <div class="term-date-range">
              <van-icon name="calendar-o" size="13" />
              <span>{{ formatDateRange(item) }}</span>
            </div>

            <div class="term-footer">
              <span class="view-hint">点击查看详情</span>
            </div>
          </div>

          <!-- 右侧箭头 -->
          <van-icon name="arrow" color="#C0C4CC" size="16" class="card-arrow" />
        </div>
      </div>

      <Pagination 
        v-if="isPaginated"
        :show="isPaginated"
        :current-page="currentPage"
        :page-size="pageSize"
        :total-count="totalCount"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { semesterService } from '@/core/services/BaseService'
import { useNavigation } from '@/core/utils/routeDecision'
import Pagination from '@/views/mobile/components/Pagination.vue'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()

const loading = ref(false)
const termList = ref([])
const error = ref('')
const isPaginated = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)

const loadData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      archived: true
    }
    
    const response = await semesterService.list(params)
    
    if (response && response.success !== false) {
      termList.value = response.list || response.data?.list || []
      
      if (response.pagination || response.total !== undefined) {
        isPaginated.value = true
        totalCount.value = response.pagination?.total || response.total || 0
      }
    } else {
      termList.value = []
      error.value = response?.message || '加载失败'
    }
  } catch (err) {
    error.value = '加载失败'
    termList.value = []
    console.error('Load archived terms error:', err)
  } finally {
    loading.value = false
  }
}

const handleCurrentChange = async (page) => {
  currentPage.value = page
  await loadData()
}

const handleItemClick = (item) => {
  router.push({
    path: `/archived-records/${item.id}`,
    query: { type: route.query.type }
  })
}

const formatDateRange = (item) => {
  if (item.start_date && item.end_date) {
    return `${item.start_date} ~ ${item.end_date}`
  }
  return '日期信息未知'
}

const goBack = () => router.go(-1)

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.stats-overview {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: linear-gradient(135deg, #F9F0FF 0%, #E8D5F7 100%);
  border-radius: 16px;
  padding: 20px;
  margin: 16px;
  box-shadow: 0 4px 12px rgba(155, 89, 182, 0.1);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
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

.archived-list {
  padding: 0 16px;
}

.archived-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  background: white;
  border-radius: 16px;
  margin-bottom: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
}

.archived-card:active {
  transform: scale(0.98);
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
}

.card-indicator {
  position: absolute;
  left: 0;
  top: 14px;
  bottom: 14px;
  width: 4px;
  border-radius: 0 4px 4px 0;
  background: linear-gradient(180deg, #909399 0%, #7A7D83 100%);
}

.icon-wrapper {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-left: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.icon-wrapper .van-icon {
  font-size: 26px !important;
  font-weight: 500;
}

.icon-wrapper.icon--archived {
  background: linear-gradient(135deg, #F5F5F5 0%, #E8E8E8 100%);
  color: #909399;
}

.archived-content {
  flex: 1;
  min-width: 0;
}

.term-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.term-name {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.archived-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  color: #909399;
  background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
  white-space: nowrap;
  flex-shrink: 0;
}

.term-date-range {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #999;
  margin-bottom: 6px;
}

.term-date-range .van-icon {
  opacity: 0.6;
}

.term-footer {
  margin-top: 4px;
}

.view-hint {
  font-size: 11px;
  color: #9B59B6;
  font-weight: 500;
}

.card-arrow {
  flex-shrink: 0;
  opacity: 0.6;
}
</style>