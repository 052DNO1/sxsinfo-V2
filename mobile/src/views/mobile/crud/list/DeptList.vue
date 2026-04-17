<template>
  <div class="mobile-page">
    <van-nav-bar title="分院管理" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-empty v-if="error" :description="error" />

      <div v-else class="list-container">
        <van-checkbox-group v-model="selectedIds" class="dept-list">
          <van-cell-group inset>
            <van-cell
              v-for="item in objectList"
              :key="item.id"
              is-link
              clickable
              @click="handleItemClick(item)"
            >
              <template #title>
                <div class="dept-title">{{ item.departname }}</div>
              </template>
              <template #label>
                <div class="dept-info">用户数: {{ item.user_count || 0 }}</div>
              </template>
              <template #icon>
                <van-checkbox 
                  :name="item.id" 
                  shape="square"
                  checked-color="#ee0a24"
                  @click.stop
                  class="dept-checkbox"
                />
              </template>
            </van-cell>
          </van-cell-group>
        </van-checkbox-group>
      </div>
    </div>

    <van-action-bar>
      <van-action-bar-button 
        type="default" 
        :text="selectedIds.length > 0 ? `删除(${selectedIds.length})` : '批量删除'" 
        @click="handleBatchDelete" 
      />
      <van-action-bar-button type="primary" text="添加分院" @click="handleAdd" />
    </van-action-bar>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNavigation } from '@/utils/routeDecision'
import { useDeptList } from '@/composables/useDeptList'
import { useDelete } from '@/composables/useDelete'

const router = useRouter()
const { goHome } = useNavigation()

const {
    tableData: objectList, error,
    loadData,
} = useDeptList()

const selectedIds = ref([])

const { handleBatchDelete: execBatchDelete } = useDelete({
  apiPath: '/userinfo/batch_deldept/',
  paramName: 'dept_ids',
  refresh: () => {
    selectedIds.value = []
    return loadData()
  },
  confirmMessageBuilder: (selection) => {
    if (!selection || selection.length === 0) {
      return '请先选择要删除的分院'
    }
    return `确定要删除选中的 ${selection.length} 个分院吗？此操作不可恢复！`
  }
})

const handleItemClick = (item) => {
  router.push(`/edit-dept/${item.id}`)
}

const handleBatchDelete = async () => {
  if (selectedIds.value.length === 0) {
    const { showWarning } = await import('@/utils/errorHandler')
    await showWarning('请先选择要删除的分院')
    return
  }
  const selectedItems = objectList.value.filter(item => selectedIds.value.includes(item.id))
  await execBatchDelete(selectedItems)
}

const handleAdd = () => {
  router.push('/adddept')
}

const goBack = () => {
  router.go(-1)
}

onMounted(() => {
  loadData()
})
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

.dept-list {
  width: 100%;
}

.dept-checkbox {
  margin-right: 12px;
}

.dept-title {
  font-size: 15px;
  font-weight: 500;
  color: #323233;
}

.dept-info {
  font-size: 12px;
  color: #969799;
  margin-top: 4px;
}
</style>
