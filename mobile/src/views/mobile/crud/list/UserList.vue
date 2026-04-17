<template>
  <div class="mobile-page">
    <van-nav-bar :title="listHeader || '用户管理'" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-dropdown-menu v-if="select">
        <van-dropdown-item v-model="filterValue" :options="filterOptions" @change="handleFilter" />
      </van-dropdown-menu>

      <van-empty v-if="error" :description="error" />

      <div v-else class="list-container">
        <van-checkbox-group v-model="selectedIds" class="user-list">
          <van-cell-group inset>
            <van-cell
              v-for="item in tableData"
              :key="item.id"
              is-link
              clickable
              @click="handleItemClick(item)"
            >
              <template #icon>
                <van-checkbox 
                  :name="item.id" 
                  shape="square"
                  checked-color="#ee0a24"
                  @click.stop
                  class="user-checkbox"
                />
              </template>
              <template #title>
                <div class="user-title">
                  {{ item.nikename || item.username }}
                </div>
              </template>
              <template #label>
                <div class="user-info">
                  <span>{{ item.username }}</span>
                  <span v-if="item.is_superuser" class="role-text">超管</span>
                  <span v-if="item.is_departadmin" class="role-text">分院管理员</span>
                  <span v-if="item.is_sxsadmin" class="role-text">实训室管理员</span>
                  <span v-if="item.is_teacher" class="role-text">教师</span>
                </div>
              </template>
            </van-cell>
          </van-cell-group>
        </van-checkbox-group>
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

    <van-action-bar>
      <van-action-bar-button 
        type="default" 
        :text="selectedIds.length > 0 ? `删除(${selectedIds.length})` : '批量删除'" 
        @click="handleBatchDelete" 
      />
      <van-action-bar-button 
        type="default" 
        :text="selectedIds.length > 0 ? `重置(${selectedIds.length})` : '重置密码'" 
        @click="handleBatchReset" 
      />
      <van-action-bar-button type="primary" text="添加用户" @click="handleAdd" />
    </van-action-bar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/utils/routeDecision'
import { useUserList } from '@/composables/useUserList'
import { useDelete } from '@/composables/useDelete'
import { showWarning, showConfirm, showSuccess, showError } from '@/utils/errorHandler'
import { useApi } from '@/composables/useApi'
import Pagination from '@/views/mobile/components/Pagination.vue'

const route = useRoute()
const router = useRouter()
const { goHome } = useNavigation()

const {
  listHeader, tableData, select, error, filterValue,
  loading, refreshing, isPaginated, currentPage, totalCount, pageSize,
  loadData, handleFilter, handleBatchResetPassword, handleCurrentChange
} = useUserList()

const selectedIds = ref([])
const apiComposable = useApi('', { immediate: false })

const { handleBatchDelete: execBatchDelete } = useDelete({
  apiPath: '/userinfo/batch_deluser/',
  paramName: 'user_ids',
  refresh: () => {
    selectedIds.value = []
    return loadData()
  },
  confirmMessageBuilder: (selection) => {
    if (!selection || selection.length === 0) {
      return '请先选择要删除的用户'
    }
    return `确定要删除选中的 ${selection.length} 个用户吗？此操作不可恢复！`
  }
})

const filterOptions = computed(() => {
  if (!select.value?.options) return []
  return select.value.options.map(item => ({
    text: item.text,
    value: item.id
  }))
})

const onRefresh = async () => {
  refreshing.value = true
  selectedIds.value = []
  await loadData()
  refreshing.value = false
}

const handleLoadMore = async () => {
  // 空函数，避免错误
}

const handleItemClick = (item) => {
  const tid = route.params.id || route.query.typeid || '1'
  router.push(`/edit-user/${item.id}?tid=${tid}`)
}

const handleBatchDelete = async () => {
  if (selectedIds.value.length === 0) {
    await showWarning('请先选择要删除的用户')
    return
  }
  const selectedItems = tableData.value.filter(item => selectedIds.value.includes(item.id))
  await execBatchDelete(selectedItems)
}

const handleBatchReset = async () => {
  if (selectedIds.value.length === 0) {
    await showWarning('请先选择要重置密码的用户')
    return
  }
  
  const confirmed = await showConfirm(`确定要重置选中的 ${selectedIds.value.length} 个用户的密码吗？`)
  if (!confirmed) return
  
  try {
    // 循环调用单个重置密码的 API
    let successCount = 0
    for (const userId of selectedIds.value) {
      const response = await apiComposable.post(
        {},
        { url: `/userinfo/resetpassword/${userId}/` }
      )
      if (response && response.success) {
        successCount++
      }
    }
    
    if (successCount > 0) {
      showSuccess(`成功重置 ${successCount} 个用户的密码`)
      selectedIds.value = []
    } else {
      showError('重置失败')
    }
  } catch (err) {
    showError('重置失败')
  }
}

const handleAdd = () => {
  const typeid = route.params.id || route.query.typeid || '1'
  router.push(`/adduser/${typeid}`)
}

const goBack = () => router.go(-1)

onMounted(() => loadData())

// 只在组件初始化和手动操作时加载数据，避免无限循环
// 移除会导致无限循环的 watch 监听器
// 数据加载通过 onMounted 和手动操作触发
</script>

<style scoped>
.mobile-page {
  min-height: 100vh;
  background: #f7f8fa;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  padding-bottom: 100px;
}

.list-container {
  min-height: 300px;
}

.user-list {
  width: 100%;
}

.user-checkbox {
  margin-right: 12px;
}

.user-title {
  font-size: 15px;
  font-weight: 500;
  color: #323233;
  display: flex;
  align-items: center;
  gap: 6px;
}

.role-text {
  font-size: 12px;
  font-weight: normal;
  color: #969799;
}

.user-info {
  font-size: 12px;
  color: #969799;
  margin-top: 4px;
}

:deep(.pagination-wrapper) {
  margin-bottom: 60px;
}
</style>
