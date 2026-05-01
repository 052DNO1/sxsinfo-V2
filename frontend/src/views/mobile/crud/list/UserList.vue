<template>
  <div class="mobile-page">
    <van-nav-bar
      title="用户管理"
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
      <!-- 统计信息头部 -->
      <div
        v-if="totalCount > 0 || tableData.length > 0"
        class="stats-header"
      >
        <div class="stat-item">
          <span class="stat-number">{{ totalCount || tableData.length }}</span>
          <span class="stat-label">位用户</span>
        </div>
        <div class="stat-divider" />
        <div class="stat-item">
          <span class="stat-number">{{ activeCount }}</span>
          <span class="stat-label">已激活</span>
        </div>
        <div class="stat-divider" />
        <div class="stat-item">
          <span class="stat-number">{{ inactiveCount }}</span>
          <span class="stat-label">未激活</span>
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
            👥
          </div>
          <h3>暂无用户</h3>
          <p>点击右下角按钮添加第一位用户</p>
        </div>

        <div
          v-else
          class="user-list animate-fade-in-up"
        >
          <div
            v-for="(item, index) in tableData"
            :key="item.id"
            class="user-card"
            :class="{ 'is-inactive': !item.is_active }"
            :style="{ animationDelay: `${index * 0.05}s` }"
            @click="router.push(`/edit-user/${item.id}`)"
          >
            <!-- 左侧边框指示器 -->
            <div
              class="card-indicator"
              :class="{ active: item.is_active }"
            />

            <!-- 用户信息区 -->
            <div class="user-main">
              <!-- 头像 -->
              <div
                class="avatar-wrapper"
                :style="{ background: getAvatarColor(item), color: getAvatarTextColor(item) }"
              >
                <span>{{ (item.nickname || item.username).charAt(0).toUpperCase() }}</span>
              </div>

              <!-- 信息内容 -->
              <div class="user-info">
                <div class="user-name-row">
                  <h3 class="user-name">
                    {{ item.nickname || item.username }}
                  </h3>
                  <span
                    class="role-tag"
                    :style="{ background: getRoleColor(item), color: getRoleTextColor(item) }"
                  >
                    {{ getRoleText(item) }}
                  </span>
                </div>
                <div class="user-meta">
                  <span class="meta-item">
                    <van-icon
                      name="user-o"
                      size="12"
                    />
                    {{ item.username }}
                  </span>
                  <span class="meta-dot">·</span>
                  <span
                    v-if="item.department_name"
                    class="meta-item"
                  >
                    <van-icon
                      name="location-o"
                      size="12"
                    />
                    {{ item.department_name }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 右侧操作区 -->
            <div
              class="user-actions"
              @click.stop
            >
              <van-switch
                :model-value="item.is_active"
                size="22px"
                :loading="togglingId === item.id"
                active-color="#07c160"
                inactive-color="#dcdee0"
                @click.stop="handleToggleStatus(item)"
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
      @click="router.push('/adduser')"
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
        placeholder="搜索用户名、昵称..."
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
import { showDialog } from 'vant'
import { useUserList } from '@/core/hooks'
import { useNavigation } from '@/core/utils/routeDecision'
import { userService } from '@/core/services/BaseService'
import { showSuccess, showError } from '@/core/utils/errorHandler'
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
  loadData,
  handleDelete,
  handleBatchDelete
} = useUserList({ immediate: true })

const refreshing = ref(false)
const showSearch = ref(false)
const searchKeyword = ref('')
const togglingId = ref(null)

const activeCount = computed(() => {
  return tableData.value.filter(item => item.is_active).length
})

const inactiveCount = computed(() => {
  return tableData.value.filter(item => !item.is_active).length
})

const getAvatarColor = (item) => {
  return '#EEF2FF'
}

const getAvatarTextColor = (item) => {
  return '#4F6EF7'
}

const ROLE_MAP = {
  1: '教师',
  2: '实训室管理',
  4: '分院管理',
  16: '超级管理员',
  32: '系统管理员'
}

const formatRoleDisplay = (role) => {
  if (!role && role !== 0) return '普通用户'
  const roles = []
  for (const [value, name] of Object.entries(ROLE_MAP)) {
    if (role & parseInt(value)) {
      roles.push(name)
    }
  }
  if (role & 8) roles.push('实训室管理')
  return roles.length > 0 ? roles.join('+') : '普通用户'
}

const getRoleText = (item) => {
  if (item.is_superuser) return '系统管理员'
  if (item.is_super_admin) return '超级管理员'
  if (item.role) return formatRoleDisplay(item.role)
  const roles = []
  if (item.is_departadmin) roles.push('分院管理')
  if (item.is_sxsadmin) roles.push('实训室管理')
  if (item.is_teacher) roles.push('教师')
  if (roles.length > 0) return roles.join('+')
  return '普通用户'
}

const getRoleColor = (item) => {
  return '#F5F5F5'
}

const getRoleTextColor = (item) => {
  return '#666'
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

const handleToggleStatus = async (item) => {
  const action = item.is_active ? '禁用' : '激活'
  
  try {
    await showDialog({
      title: '确认操作',
      message: `确定要${action}该用户吗？`,
      showCancelButton: true,
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      confirmButtonColor: action === '禁用' ? '#FF3B30' : '#07c160'
    })
  } catch {
    return
  }
  
  togglingId.value = item.id
  try {
    const isActive = !item.is_active
    const response = await userService.activate(item.id, { is_active: isActive })
    if (response?.success !== false) {
      showSuccess(`${action}成功`)
      await loadData()
    } else {
      showError(response?.message || `${action}失败`)
    }
  } catch (e) {
    showError(`${action}失败`)
  } finally {
    togglingId.value = null
  }
}
</script>

<style scoped>
.stats-header {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
  border-radius: 16px;
  padding: 20px;
  margin: 16px;
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.1);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: #4F6EF7;
}

.stat-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: rgba(79, 110, 247, 0.2);
}

.user-list {
  padding: 0 16px;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: white;
  border-radius: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
}

.user-card:active {
  transform: scale(0.98);
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
}

.user-card.is-inactive {
  opacity: 0.65;
  background: #fafafa;
}

.card-indicator {
  position: absolute;
  left: 0;
  top: 12px;
  bottom: 12px;
  width: 4px;
  border-radius: 0 4px 4px 0;
  background: #dcdee0;
  transition: all 0.3s ease;
}

.card-indicator.active {
  background: linear-gradient(180deg, #07c160 0%, #06ad56 100%);
  box-shadow: 0 0 8px rgba(7, 193, 96, 0.3);
}

.user-main {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 0;
  margin-left: 8px;
}

.avatar-wrapper {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.role-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  flex-shrink: 0;
  white-space: nowrap;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
  overflow: hidden;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-item .van-icon {
  opacity: 0.7;
}

.meta-dot {
  opacity: 0.4;
}

.user-actions {
  flex-shrink: 0;
  padding-left: 8px;
}
</style>