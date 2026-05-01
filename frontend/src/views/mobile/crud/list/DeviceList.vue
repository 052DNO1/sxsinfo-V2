<template>
  <div class="mobile-page">
    <van-nav-bar
      title="设备列表"
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
      <div class="filter-bar">
        <van-dropdown-menu>
          <van-dropdown-item
            v-model="selectedLab"
            :options="labOptions"
            @change="handleLabChange"
          />
        </van-dropdown-menu>
      </div>

      <div
        v-if="totalCount > 0 || tableData.length > 0"
        class="page-header"
      >
        <h2>设备列表</h2>
        <p>共 {{ totalCount || tableData.length }} 台设备</p>
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
          <div class="empty-state-icon">
            💻
          </div>
          <h3>暂无设备</h3>
          <p>点击右下角按钮添加第一台设备</p>
        </div>

        <div
          v-else
          class="list-container animate-fade-in-up"
        >
          <div
            v-for="(item, index) in tableData"
            :key="item.id"
            class="list-card"
            :style="{ animationDelay: `${index * 0.05}s` }"
            @click="router.push(`/edit-device/${item.id}`)"
          >
            <div
              class="list-card-avatar"
              :style="{ background: getAvatarBg(item.category) }"
            >
              <van-icon
                name="desktop-o"
                size="22"
              />
            </div>
            <div class="list-card-content">
              <div class="list-card-header">
                <span class="list-card-title">{{ item.name }}</span>
                <span
                  class="status-badge"
                  :class="getStatusClass(item.status)"
                >
                  {{ getStatusText(item.status) }}
                </span>
              </div>
              <div class="list-card-subtitle">
                <template v-if="item.code">
                  <van-icon
                    name="label-o"
                    size="12"
                  /> {{ item.code }}
                </template>
                <template v-if="item.category">
                  · <van-icon
                    name="apps-o"
                    size="12"
                  /> {{ item.category }}
                </template>
                <template v-if="item.brand || item.model">
                  · {{ [item.brand, item.model].filter(Boolean).join('/') }}
                </template>
              </div>
              <div
                v-if="item.laboratory_name"
                class="list-card-location"
              >
                <van-icon
                  name="location-o"
                  size="11"
                /> {{ item.laboratory_name }}
              </div>
            </div>
            <van-icon
              name="arrow"
              color="#C5C9D0"
            />
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
      @click="router.push('/add-device')"
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
        placeholder="搜索设备名称、编号..."
        show-action
        @search="handleSearch"
        @cancel="showSearch = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { equipmentService, labService } from '@/core/services/BaseService'
import { useNavigation } from '@/core/utils/routeDecision'
import Pagination from '@/views/mobile/components/Pagination.vue'

const router = useRouter()
const { goBack } = useNavigation()

const tableData = ref([])
const loading = ref(false)
const error = ref('')
const totalCount = ref(0)
const pageSize = ref(20)
const currentPage = ref(1)
const refreshing = ref(false)
const showSearch = ref(false)
const searchKeyword = ref('')

const labList = ref([])
const selectedLab = ref('')

const labOptions = computed(() => {
  const options = [{ text: '全部实训室', value: '' }]
  labList.value.forEach(lab => {
    options.push({ text: `${lab.code || ''} ${lab.name || ''}`.trim(), value: lab.id })
  })
  return options
})

const loadLabList = async () => {
  try {
    const res = await labService.list({ nopage: true })
    labList.value = res?.list || res?.data?.list || []
  } catch (err) {
    console.error('Failed to load lab list:', err)
  }
}

const loadData = async (params = {}) => {
  loading.value = true
  error.value = ''
  try {
    const query = { page: currentPage.value, page_size: pageSize.value, ...params }
    if (searchKeyword.value) {
      query.search = searchKeyword.value
    }
    if (selectedLab.value) {
      query.laboratory_id = selectedLab.value
    }
    const res = await equipmentService.list(query)
    tableData.value = res?.list || res?.data?.list || []
    totalCount.value = res?.total || res?.data?.total || 0
  } catch (err) {
    error.value = err.message || '加载失败'
  } finally {
    loading.value = false
  }
}

const handleLabChange = () => {
  currentPage.value = 1
  loadData()
}

const getStatusText = (status) => {
  const map = { 'NORMAL': '正常', 'MAINTENANCE': '维护中', 'DAMAGED': '损坏' }
  return map[status] || status || '未知'
}

const getStatusClass = (status) => {
  const map = { 'NORMAL': 'success', 'MAINTENANCE': 'warning', 'DAMAGED': 'danger' }
  return map[status] || 'default'
}

const getAvatarBg = (category) => {
  return '#EBF7FD'
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
  loadLabList()
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
.status-badge.danger { background: #FFEBE9; color: #FF3B30; }
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
