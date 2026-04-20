<template>
  <div class="mobile-page">
    <van-nav-bar title="分院管理" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="search" size="20" color="#4F6EF7" @click="showSearch = true" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <!-- 统计概览 -->
      <div class="stats-overview" v-if="totalCount > 0 || tableData.length > 0">
        <div class="stat-card">
          <div class="stat-icon stat-icon--blue">
            <van-icon name="hotel-o" size="22" />
          </div>
          <div class="stat-info">
            <span class="stat-number">{{ totalCount || tableData.length }}</span>
            <span class="stat-text">个分院</span>
          </div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-card">
          <div class="stat-icon stat-icon--green">
            <van-icon name="friends-o" size="22" />
          </div>
          <div class="stat-info">
            <span class="stat-number">{{ totalUsers }}</span>
            <span class="stat-text">总人数</span>
          </div>
        </div>
      </div>

      <van-pull-refresh v-model:refreshing="refreshing" @refresh="handleRefresh">

        <van-empty v-if="error" :description="error" image="error">
          <van-button size="small" type="primary" round @click="loadData()">重试</van-button>
        </van-empty>

        <div v-else-if="!loading && tableData.length === 0" class="empty-state">
          <div class="empty-icon">🏢</div>
          <h3>暂无分院</h3>
          <p>点击右下角按钮添加第一个分院</p>
        </div>

        <div v-else class="dept-list animate-fade-in-up">
          <div 
            v-for="(item, index) in tableData" 
            :key="item.id"
            class="dept-card"
            :style="{ animationDelay: `${index * 0.05}s` }"
            @click="router.push(`/edit-dept/${item.id}`)"
          >
            <!-- 左侧指示条 -->
            <div class="card-indicator" :style="{ background: getIndicatorColor(item) }"></div>

            <!-- 图标区（浅色系） -->
            <div class="icon-wrapper" :style="{ background: getIconBg(item), color: getIconColor(item) }">
              <van-icon name="hotel-o" size="24" />
            </div>

            <!-- 内容区 -->
            <div class="dept-content">
              <div class="dept-header">
                <h3 class="dept-name">{{ item.name }}</h3>
              </div>

              <div class="dept-meta">
                <template v-if="item.user_count !== undefined">
                  <span class="meta-tag">
                    <van-icon name="friends-o" size="12" />
                    {{ item.user_count }}人
                  </span>
                </template>
                <template v-if="item.manager_names">
                  <span class="meta-tag meta-tag--manager">
                    <van-icon name="manager-o" size="12" />
                    {{ item.manager_names }}
                  </span>
                </template>
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

    <div class="floating-action-btn" @click="router.push('/adddept')">
      <van-icon name="plus" size="24" />
    </div>

    <van-popup v-model:show="showSearch" position="top" :style="{ height: 'auto' }">
      <van-search
        v-model="searchKeyword"
        placeholder="搜索分院名称..."
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
import { useDeptList } from '@/core/hooks'
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
} = useDeptList({ immediate: true })

const refreshing = ref(false)
const showSearch = ref(false)
const searchKeyword = ref('')

const totalUsers = computed(() => {
  return tableData.value.reduce((sum, item) => sum + (item.user_count || 0), 0)
})

const getIconBg = (item) => {
  return '#EEF2FF'
}

const getIconColor = (item) => {
  return '#4F6EF7'
}

const getIndicatorColor = (item) => {
  return '#4F6EF7'
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
  background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
  border-radius: 16px;
  padding: 20px;
  margin: 16px;
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.1);
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

.dept-list {
  padding: 0 16px;
}

.dept-card {
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

.dept-card:active {
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
  transition: all 0.3s ease;
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

.dept-content {
  flex: 1;
  min-width: 0;
}

.dept-header {
  margin-bottom: 10px;
}

.dept-name {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dept-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.meta-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 10px;
  border-radius: 8px;
}

.meta-tag .van-icon {
  opacity: 0.7;
}

.meta-tag--manager {
  color: #FF9500;
  background: #FFF5E6;
}

.card-arrow {
  flex-shrink: 0;
  opacity: 0.6;
}
</style>