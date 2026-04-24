<template>
  <div class="mobile-page">
    <van-nav-bar :title="pageTitle" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="search" size="20" color="#4F6EF7" @click="showSearch = true" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <div class="filter-bar">
        <van-dropdown-menu>
          <van-dropdown-item v-model="currentFilter" :options="statusOptions" @change="handleFilterChange" />
        </van-dropdown-menu>
      </div>

      <div class="page-header" v-if="totalCount > 0 || tableData.length > 0">
        <h2>{{ pageTitle }}</h2>
        <p>共 {{ totalCount || tableData.length }} 条记录</p>
      </div>

      <van-pull-refresh v-model:refreshing="refreshing" @refresh="handleRefresh">

        <van-empty v-if="error" :description="error" image="error">
          <van-button size="small" type="primary" round @click="loadData()">重试</van-button>
        </van-empty>

        <div v-else-if="!loading && tableData.length === 0" class="empty-state">
          <div class="empty-state-icon">🔧</div>
          <h3>暂无{{ pageTitle }}</h3>
          <p v-if="!isFault">点击右下角按钮上报故障</p>
        </div>

        <div v-else class="list-container animate-fade-in-up">
          <div
            v-for="(item, index) in tableData"
            :key="item.id"
            class="list-card"
            :style="{ animationDelay: `${index * 0.05}s` }"
            @click="router.push(`/workorder/${item.id}`)"
          >
            <div class="list-card-avatar" :style="{ background: getAvatarBg(item.status) }">
              <van-icon :name="isFault ? 'warning-o' : 'setting-o'" size="22" />
            </div>
            <div class="list-card-content">
              <div class="list-card-header">
                <span class="list-card-title">{{ item.title || (isFault ? '故障报修' : '维护工单') }}</span>
                <span class="status-badge" :class="getStatusClass(item.status)">
                  {{ getStatusText(item.status) }}
                </span>
              </div>
              <div class="list-card-subtitle">
                <template v-if="item.laboratory_name">
                  <van-icon name="home-o" size="12" /> {{ item.laboratory_name }}
                </template>
                <template v-if="item.reporter_name">
                  · <van-icon name="user-o" size="12" /> {{ item.reporter_name }}
                </template>
                <template v-if="item.order_number">
                  · #{{ item.order_number }}
                </template>
              </div>
              <div class="list-card-location" v-if="item.description">
                <van-icon name="description-o" size="11" /> {{ item.description.substring(0, 50) }}{{ item.description.length > 50 ? '...' : '' }}
              </div>
            </div>
            <van-icon name="arrow" color="#C5C9D0" />
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

    <div class="floating-action-btn" v-if="!isFault" @click="router.push('/report-maintenance')">
      <van-icon name="plus" size="24" />
    </div>

    <van-popup v-model:show="showSearch" position="top" :style="{ height: 'auto' }">
      <van-search
        v-model="searchKeyword"
        placeholder="搜索工单..."
        show-action
        @search="handleSearch"
        @cancel="showSearch = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { workOrderService } from '@/core/services/BaseService'
import { useNavigation } from '@/core/utils/routeDecision'
import Pagination from '@/views/mobile/components/Pagination.vue'

const router = useRouter()
const route = useRoute()
const { goBack } = useNavigation()

const isFault = computed(() => route.query.type === 'fault')

const pageTitle = computed(() => isFault.value ? '故障记录' : '维护记录')

const tableData = ref([])
const loading = ref(false)
const error = ref('')
const totalCount = ref(0)
const pageSize = ref(20)
const currentPage = ref(1)
const refreshing = ref(false)
const showSearch = ref(false)
const searchKeyword = ref('')
const currentFilter = ref('')

const statusOptions = [
  { text: '全部状态', value: '' },
  { text: '待处理', value: 'PENDING' },
  { text: '处理中', value: 'PROCESSING' },
  { text: '已完成', value: 'COMPLETED' },
  { text: '已关闭', value: 'CLOSED' }
]

const loadData = async (params = {}) => {
  loading.value = true
  error.value = ''
  try {
    const query = { page: currentPage.value, page_size: pageSize.value, ...params }
    if (searchKeyword.value) {
      query.search = searchKeyword.value
    }
    if (currentFilter.value) {
      query.status = currentFilter.value
    }
    if (isFault.value) {
      query.maintenance_type = 3
    }
    const res = await workOrderService.list(query)
    tableData.value = res?.list || res?.data?.list || []
    totalCount.value = res?.total || res?.data?.total || 0
  } catch (err) {
    error.value = err.message || '加载失败'
  } finally {
    loading.value = false
  }
}

const getStatusText = (status) => {
  const map = { PENDING: '待处理', PROCESSING: '处理中', COMPLETED: '已完成', CLOSED: '已关闭' }
  return map[status] || status || '未知'
}

const getStatusClass = (status) => {
  const map = { PENDING: 'warning', PROCESSING: 'primary', COMPLETED: 'success', CLOSED: 'default' }
  return map[status] || 'default'
}

const getAvatarBg = (status) => {
  return '#FFF5E6'
}

const handleFilterChange = (value) => {
  currentFilter.value = value
  currentPage.value = 1
  loadData()
}

const handleRefresh = async () => {
  refreshing.value = true
  await loadData()
  refreshing.value = false
}

const handleSearch = () => {
  showSearch.value = false
  currentPage.value = 1
  loadData({ search: searchKeyword.value })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.filter-bar {
  padding: 8px 16px;
  background: var(--mobile-bg);
}

.list-container { padding: 0 16px; }

.list-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: var(--mobile-card);
  border-radius: var(--mobile-radius-lg);
  margin-bottom: 10px;
  box-shadow: var(--mobile-shadow-sm);
  transition: all 0.25s ease;
  cursor: pointer;
}

.list-card:active { transform: scale(0.98); box-shadow: var(--mobile-shadow-md); }

.list-card-avatar {
  width: 46px;
  height: 46px;
  border-radius: var(--mobile-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.list-card-content { flex: 1; min-width: 0; }

.list-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 4px;
}

.list-card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-card-subtitle {
  font-size: 12px;
  color: var(--mobile-text-hint);
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.list-card-subtitle .van-icon { margin-right: 2px; }

.list-card-location {
  font-size: 11px;
  color: var(--mobile-text-hint);
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}

.status-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  flex-shrink: 0;
}

.status-badge.success { background: #E8F8EE; color: #07C160; }
.status-badge.warning { background: #FFF5E6; color: #FF9500; }
.status-badge.primary { background: #EEF2FF; color: #4F6EF7; }
.status-badge.default { background: #F5F5F5; color: #999; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-state-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: var(--mobile-text-primary);
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  color: var(--mobile-text-hint);
}

.floating-action-btn {
  position: fixed;
  right: 20px;
  bottom: 80px;
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: var(--mobile-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.4);
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 100;
}

.floating-action-btn:active {
  transform: scale(0.92);
  box-shadow: 0 2px 8px rgba(79, 110, 247, 0.3);
}

.page-header {
  padding: 16px;
  margin-bottom: 8px;
}

.page-header h2 {
  margin: 0 0 4px;
  font-size: 18px;
  font-weight: 600;
  color: var(--mobile-text-primary);
}

.page-header p {
  margin: 0;
  font-size: 13px;
  color: var(--mobile-text-hint);
}

.animate-fade-in-up {
  animation: fadeInUp 0.3s ease-out forwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
