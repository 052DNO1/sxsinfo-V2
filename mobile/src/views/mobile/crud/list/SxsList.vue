<template>
  <div class="mobile-page">
    <van-nav-bar :title="listHeader || '实训室列表'" left-arrow @click-left="goBack">
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
        <van-checkbox-group v-model="selectedIds" class="sxs-list">
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
                  class="sxs-checkbox"
                />
              </template>
              <template #title>
                <div class="sxs-title">
                  {{ item.sxsname }}
                  <van-tag v-if="item.sxsstatus === '正常'" type="success" size="small">正常</van-tag>
                  <van-tag v-else type="danger" size="small">{{ item.sxsstatus }}</van-tag>
                </div>
              </template>
              <template #label>
                <div class="sxs-info">
                  <span v-if="item.sxslocation">{{ item.sxslocation }}</span>
                  <span v-if="item.sxsno"> · 编号：{{ item.sxsno }}</span>
                  <span v-if="item.admin_name"> · 管理员：{{ item.admin_name }}</span>
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
        text="查看记录" 
        @click="handleViewRecords" 
      />
      <van-action-bar-button type="primary" text="添加实训室" @click="handleAdd" />
    </van-action-bar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSxsList } from '@/composables/useSxsList'
import { useDelete } from '@/composables/useDelete'
import { showWarning } from '@/utils/errorHandler'
import { useNavigation } from '@/utils/routeDecision'
import Pagination from '@/views/mobile/components/Pagination.vue'

const router = useRouter()
const { goHome } = useNavigation()

const {
  listHeader, tableData, select, error, filterValue,
  loading, refreshing, isPaginated, currentPage, totalCount, pageSize,
  loadData, handleFilter, handleCurrentChange
} = useSxsList()

const selectedIds = ref([])

const { handleBatchDelete: execBatchDelete } = useDelete({
  apiPath: '/sxs/batch_dellab/',
  paramName: 'lab_ids',
  refresh: () => {
    selectedIds.value = []
    return loadData()
  },
  confirmMessageBuilder: (selection) => {
    if (!selection || selection.length === 0) {
      return '请先选择要删除的实训室'
    }
    return `确定要删除选中的 ${selection.length} 个实训室吗？此操作不可恢复！`
  }
})

const filterOptions = computed(() => {
  if (!select.value?.options) return []
  return select.value.options.map(item => ({
    text: item.text,
    value: item.id
  }))
})

const handleItemClick = (item) => {
  router.push(`/edit-sxs/${item.id}`)
}

const handleBatchDelete = async () => {
  if (selectedIds.value.length === 0) {
    await showWarning('请先选择要删除的实训室')
    return
  }
  const selectedItems = tableData.value.filter(item => selectedIds.value.includes(item.id))
  await execBatchDelete(selectedItems)
}

const handleViewRecords = () => {
  router.push('/listsxsinfo')
}

const handleAdd = () => {
  router.push('/addsxs')
}

const goBack = () => router.go(-1)

onMounted(() => loadData())
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

.sxs-list {
  width: 100%;
}

.sxs-checkbox {
  margin-right: 12px;
}

.sxs-title {
  font-size: 15px;
  font-weight: 500;
  color: #323233;
  display: flex;
  align-items: center;
  gap: 6px;
}

.sxs-info {
  font-size: 12px;
  color: #969799;
  margin-top: 4px;
}

:deep(.pagination-wrapper) {
  margin-bottom: 60px;
}
</style>
