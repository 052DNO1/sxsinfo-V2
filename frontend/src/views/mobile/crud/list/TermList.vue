<template>
  <div class="mobile-page">
    <van-nav-bar
      title="学期管理"
      left-arrow
      @click-left="goBack"
    >
      <template #right>
        <van-icon
          name="search"
          size="20"
          color="#4F6EF7"
          @click="showSearch = true"
        />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <!-- 统计概览 -->
      <div
        v-if="totalCount > 0 || tableData.length > 0"
        class="stats-overview"
      >
        <div class="stat-card">
          <div class="stat-icon stat-icon--blue">
            <van-icon
              name="calendar-o"
              size="22"
            />
          </div>
          <div class="stat-info">
            <span class="stat-number">{{ totalCount || tableData.length }}</span>
            <span class="stat-text">个学期</span>
          </div>
        </div>
        <div class="stat-divider" />
        <div class="stat-card">
          <div class="stat-icon stat-icon--green">
            <van-icon
              name="checked"
              size="22"
            />
          </div>
          <div class="stat-info">
            <span class="stat-number">{{ currentTermCount }}</span>
            <span class="stat-text">当前学期</span>
          </div>
        </div>
      </div>

      <van-pull-refresh
        v-model:refreshing="refreshing"
        @refresh="handleRefresh"
      >
        <van-empty
          v-if="error"
          :description="error"
          image="error"
        >
          <van-button
            size="small"
            type="primary"
            round
            @click="loadData()"
          >
            重试
          </van-button>
        </van-empty>

        <div
          v-else-if="!loading && tableData.length === 0"
          class="empty-state"
        >
          <div class="empty-icon">
            📅
          </div>
          <h3>暂无学期</h3>
          <p>点击右下角按钮添加新学期</p>
        </div>

        <div
          v-else
          class="term-list animate-fade-in-up"
        >
          <div 
            v-for="(item, index) in tableData" 
            :key="item.id"
            class="term-card"
            :class="{ 'is-current': item.is_current }"
            :style="{ animationDelay: `${index * 0.05}s` }"
            @click="handleItemClick(item)"
          >
            <!-- 左侧指示条 -->
            <div
              class="card-indicator"
              :class="{ active: item.is_current }"
            />

            <!-- 图标区 -->
            <div
              class="icon-wrapper"
              :class="{ 'icon--current': item.is_current }"
            >
              <van-icon
                name="certificate"
                size="24"
              />
            </div>

            <!-- 内容区 -->
            <div class="term-content">
              <div class="term-header">
                <h3 class="term-name">
                  {{ item.name }}
                </h3>
                <span
                  v-if="item.is_current"
                  class="current-badge"
                >
                  <van-icon
                    name="fire-o"
                    size="12"
                  /> 当前
                </span>
              </div>

              <div class="term-date">
                <van-icon
                  name="clock-o"
                  size="13"
                />
                <span>{{ item.start_date }} ~ {{ item.end_date }}</span>
              </div>

              <div
                v-if="!item.is_current"
                class="term-status-row"
              >
                <span class="status-hint">点击设为当前学期</span>
              </div>
            </div>

            <!-- 右侧箭头/图标 -->
            <div class="term-action">
              <van-icon 
                :name="item.is_current ? 'checked' : 'arrow'" 
                :color="item.is_current ? '#07C160' : '#C0C4CC'"
                :size="item.is_current ? 22 : 16"
              />
            </div>
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

    <div
      class="floating-action-btn"
      @click="router.push('/addterm')"
    >
      <van-icon
        name="plus"
        size="24"
      />
    </div>

    <van-popup
      v-model:show="showSearch"
      position="top"
      :style="{ height: 'auto' }"
    >
      <van-search
        v-model="searchKeyword"
        placeholder="搜索学期名称..."
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
import { useTermList } from '@/core/hooks'
import { semesterService } from '@/core/services/BaseService'
import { useNavigation } from '@/core/utils/routeDecision'
import { showSuccess, showConfirm } from '@/core/utils/errorHandler'
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
} = useTermList({ immediate: true })

const refreshing = ref(false)
const showSearch = ref(false)
const searchKeyword = ref('')

const currentTermCount = computed(() => {
  return tableData.value.filter(item => item.is_current).length
})

const handleItemClick = async (item) => {
  if (item.is_current) return
  
  const confirmed = await showConfirm(`确定要将"${item.name}"设为当前学期吗？`)
  if (!confirmed) return
  
  try {
    const res = await semesterService.setCurrent(item.id)
    if (res?.success) {
      showSuccess('设置成功')
      await loadData()
    }
  } catch (e) {
    console.error(e)
  }
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
  background: #EEF2FF;
  border-radius: 16px;
  padding: 20px;
  margin: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-divider {
  width: 1px;
  height: 36px;
  background: rgba(79, 110, 247, 0.2);
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

.stat-icon--blue {
  background: rgba(79, 110, 247, 0.15);
  color: #4F6EF7;
}

.stat-icon--green {
  background: rgba(7, 193, 96, 0.15);
  color: #07C160;
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

.term-list {
  padding: 0 16px;
}

.term-card {
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

.term-card:active {
  transform: scale(0.98);
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
}

.term-card.is-current {
  background: #F0FFF4;
  border-color: #07C160;
}

.card-indicator {
  position: absolute;
  left: 0;
  top: 14px;
  bottom: 14px;
  width: 4px;
  border-radius: 0 4px 4px 0;
  background: #e0e0e0;
  transition: all 0.3s ease;
}

.card-indicator.active {
  background: linear-gradient(180deg, #07C160 0%, #06AD56 100%);
  box-shadow: 0 0 8px rgba(7, 193, 96, 0.3);
}

.icon-wrapper {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
  color: #4F6EF7;
  flex-shrink: 0;
  margin-left: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.icon-wrapper .van-icon {
  font-size: 26px !important;
  font-weight: 500;
}

.icon-wrapper.icon--current {
  background: linear-gradient(135deg, #E8F8EE 0%, #D1F2E0 100%);
  color: #07C160;
}

.term-content {
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
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.current-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  color: #07C160;
  background: linear-gradient(135deg, #E8F8EE 0%, #D1F2E0 100%);
  white-space: nowrap;
  flex-shrink: 0;
}

.term-date {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
  margin-bottom: 6px;
}

.term-date .van-icon {
  opacity: 0.7;
}

.term-status-row {
  margin-top: 4px;
}

.status-hint {
  font-size: 11px;
  color: #4F6EF7;
  font-weight: 500;
}

.term-action {
  flex-shrink: 0;
  padding-left: 8px;
}
</style>