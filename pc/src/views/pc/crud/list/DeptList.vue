<!-- 分院列表 -->
<template>
  <CrudList
    :title="listHeader || '部门管理'"
    icon="OfficeBuilding"
    :columns="columns"
    :data="objectList"
    :loading="loading"
    :error="error"
    :total="totalCount"
    v-model:current-page="currentPage"
    v-model:page-size="pageSize"
    :is-paginated="isPaginated"
    :show-checkbox="showCheckbox"
    :show-batch-delete="showCheckbox"
    :selected-count="selectedRows?.length || 0"
    :options="opt"
    @batch-delete="handleBatchDeleteDept"
    @option-click="handleOptionClick"
    @action-click="handleAction"
    @selection-change="handleSelectionChange"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
  >
    <template #row-actions="{ row, column }">
      <div class="action-cell">
        <template v-for="(op, opIndex) in row[column.prop]" :key="opIndex">
          <el-button
            :type="getButtonType(op)"
            size="small"
            text
            :bg="getButtonBg(op)"
            :icon="getButtonIcon(op)"
            :disabled="isActionDisabled(op)"
            @click="handleAction(op)"
          >
            {{ op.text }}
          </el-button>
        </template>
      </div>
    </template>
  </CrudList>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import CrudList from '@/views/pc/components/CrudList.vue'
import { useDeptList } from '@/core/hooks'
import { getButtonType, getButtonIcon, getButtonBg, isActionDisabled } from '@/core/utils/tableHelpers'

const router = useRouter()

const {
    listHeader, columns, tableData: objectList, opt, error,
    showCheckbox, isPaginated,
    currentPage, totalCount, pageSize, loading,
    handleOptionClick,
    handleSizeChange,
    handleCurrentChange,
    execBatchDelete,
    execDelete
} = useDeptList()

const selectedRows = ref([])

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const handleBatchDeleteDept = async () => {
  await execBatchDelete(selectedRows.value)
}

const handleAction = async (action) => {
  if (!action) return
  if (isActionDisabled(action)) return
  
  if (action.action_type === 'delete') {
     await execDelete(action)
     return
  }
  
  if (action.action_type === 'edit' && action.resource_id) {
    router.push(`/edit-dept/${action.resource_id}`)
  }
}
</script>

<style scoped>
.action-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
