<template>
  <div class="mobile-page">
    <van-nav-bar title="实训室管理" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="search" size="20" color="#4F6EF7" @click="showSearch = true" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <!-- 统计概览 -->
      <div class="stats-overview" v-if="totalCount > 0 || tableData.length > 0">
        <div class="stat-card">
          <div class="stat-icon stat-icon--green">
            <van-icon name="home-o" size="22" />
          </div>
          <div class="stat-info">
            <span class="stat-number">{{ totalCount || tableData.length }}</span>
            <span class="stat-text">个实训室</span>
          </div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-card">
          <div class="stat-icon stat-icon--blue">
            <van-icon name="desktop-o" size="22" />
          </div>
          <div class="stat-info">
            <span class="stat-number">{{ totalEquipment }}</span>
            <span class="stat-text">设备总数</span>
          </div>
        </div>
      </div>

      <van-pull-refresh v-model:refreshing="refreshing" @refresh="handleRefresh">

        <van-empty v-if="error" :description="error" image="error">
          <van-button size="small" type="primary" round @click="loadData()">重试</van-button>
        </van-empty>

        <div v-else-if="!loading && tableData.length === 0" class="empty-state">
          <div class="empty-icon">🏫</div>
          <h3>暂无实训室</h3>
          <p>点击右下角按钮添加第一个实训室</p>
        </div>

        <div v-else class="sxs-list animate-fade-in-up">
          <div 
            v-for="(item, index) in tableData" 
            :key="item.id"
            class="sxs-card"
            :style="{ animationDelay: `${index * 0.05}s` }"
            @click="router.push(`/edit-sxs/${item.id}`)"
          >
            <!-- 左侧徽章 -->
            <div class="card-badge badge-green">
              <span class="badge-text">{{ (item.name || item.laboratory_name).charAt(0) }}</span>
            </div>

            <!-- 中间内容 -->
            <div class="sxs-content">
              <div class="sxs-header">
                <h3 class="sxs-name">{{ item.name || item.laboratory_name }}</h3>
                <span 
                  class="status-tag"
                  :class="{ 'tag-success': item.status === 'NORMAL' || item.status === '正常', 'tag-warning': item.status !== 'NORMAL' && item.status !== '正常' }"
                >
                  {{ getStatusText(item.status) }}
                </span>
              </div>

              <!-- 信息标签 -->
              <div class="info-tags-row">
                <template v-if="item.code">
                  <span class="info-chip">
                    <van-icon name="label-o" size="11" />
                    {{ item.code }}
                  </span>
                </template>
                <template v-if="item.equipment_count !== undefined">
                  <span class="info-chip info-chip--blue">
                    <van-icon name="desktop-o" size="11" />
                    {{ item.equipment_count }}台
                  </span>
                </template>
                <template v-if="item.admin_name">
                  <span class="info-chip info-chip--orange">
                    <van-icon name="manager-o" size="11" />
                    {{ item.admin_name }}
                  </span>
                </template>
                <template v-if="item.schedule_count !== undefined">
                  <span class="info-chip info-chip--purple">
                    <van-icon name="calendar-o" size="11" />
                    {{ item.schedule_count }}课
                  </span>
                </template>
              </div>

              <!-- 位置信息 -->
              <div class="location-hint" v-if="item.location || item.sxslocation">
                <van-icon name="location-o" size="12" />
                {{ item.location || item.sxslocation }}
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

    <div class="floating-action-btn" @click="router.push('/addsxs')">
      <van-icon name="plus" size="24" />
    </div>

    <van-popup v-model:show="showSearch" position="top" :style="{ height: 'auto' }">
      <van-search
        v-model="searchKeyword"
        placeholder="搜索实训室名称、编号..."
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
import { useSxsList } from '@/core/hooks'
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
} = useSxsList({ immediate: true })

const refreshing = ref(false)
const showSearch = ref(false)
const searchKeyword = ref('')

const totalEquipment = computed(() => {
  return tableData.value.reduce((sum, item) => sum + (item.equipment_count || 0), 0)
})

const getStatusText = (status) => {
  const map = { 'NORMAL': '正常', 'MAINTENANCE': '维护中', 'DAMAGED': '损坏', '正常': '正常', '维护中': '维护中' }
  return map[status] || status || '未知'
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
  background: linear-gradient(135deg, #E8F8EE 0%, #D1F2E0 100%);
  border-radius: 16px;
  padding: 20px;
  margin: 16px;
  box-shadow: 0 4px 12px rgba(7, 193, 96, 0.1);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-divider {
  width: 1px;
  height: 36px;
  background: rgba(7, 193, 96, 0.2);
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

.stat-icon--green {
  background: rgba(7, 193, 96, 0.15);
  color: #07C160;
}

.stat-icon--blue {
  background: rgba(79, 110, 247, 0.15);
  color: #4F6EF7;
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

.sxs-list {
  padding: 0 16px;
}

.sxs-card {
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

.sxs-card:active {
  transform: scale(0.98);
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
}

/* 左侧徽章（静版设计 - 单一绿色系） */
.card-badge {
  width: 52px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.badge-green {
  background: linear-gradient(135deg, #E8F8EE 0%, #D1F2E0 100%);
}

.badge-green .badge-text {
  color: #07C160;
  font-size: 22px;
  font-weight: 700;
}

.sxs-content {
  flex: 1;
  min-width: 0;
}

.sxs-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.sxs-name {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.status-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 10px;
  flex-shrink: 0;
  white-space: nowrap;
}

.tag-success {
  background: linear-gradient(135deg, #E8F8EE 0%, #D1F2E0 100%);
  color: #07C160;
}

.tag-warning {
  background: linear-gradient(135deg, #FFF5E6 0%, #FFE8CC 100%);
  color: #FF9500;
}

.info-tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.info-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 10px;
  border-radius: 8px;
}

.info-chip .van-icon {
  opacity: 0.7;
}

.location-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #999;
}

.location-hint .van-icon {
  opacity: 0.7;
}

.card-arrow {
  flex-shrink: 0;
  opacity: 0.6;
}
</style>