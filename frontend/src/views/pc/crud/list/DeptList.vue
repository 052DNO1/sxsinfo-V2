<!-- 分院列表 -->
<template>
  <CrudList
    :title="listHeader || '部门管理'"
    :icon="OfficeBuilding"
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
import { OfficeBuilding } from '@element-plus/icons-vue'
import { safeConfirm, safeConfirmWithInput, showSuccess, showError } from '@/core/utils/errorHandler'
import { deptService } from '@/core/services/BaseService'

const router = useRouter()

const {
    listHeader, columns, tableData: objectList, opt, error,
    showCheckbox, isPaginated,
    currentPage, totalCount, pageSize, loading,
    handleOptionClick,
    handleSizeChange,
    handleCurrentChange,
    loadData
} = useDeptList()

const selectedRows = ref([])

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const handleBatchDeleteDept = async () => {
  if (!selectedRows.value || selectedRows.value.length === 0) return
  
  const totalUsers = selectedRows.value.reduce((sum, dept) => sum + (dept.user_count || 0), 0)
  const deptsWithUsers = selectedRows.value.filter(dept => (dept.user_count || 0) > 0)
  
  if (totalUsers > 0) {
    const deptNames = deptsWithUsers.map(d => d.name).join('、')
    const message = `选中的部门中共有 ${totalUsers} 个用户，删除部门将同时删除这些用户的所有数据！\n涉及部门：${deptNames}\n此操作不可恢复，请谨慎操作。`
    const confirmed = await safeConfirmWithInput(message, '危险操作警告')
    if (!confirmed) return
    
    try {
      let successCount = 0
      let failCount = 0
      for (const dept of selectedRows.value) {
        try {
          const response = await deptService.delete(dept.id, true)
          if (response.success) successCount++
          else failCount++
        } catch (err) {
          failCount++
        }
      }
      if (successCount > 0) {
        showSuccess(`成功删除 ${successCount} 个部门${failCount > 0 ? `，${failCount} 个失败` : ''}`)
        loadData()
      } else {
        showError('删除失败')
      }
    } catch (err) {
      showError(err.message || '删除失败')
    }
  } else {
    const confirmed = await safeConfirm(`确定要删除选中的 ${selectedRows.value.length} 个部门吗？此操作不可恢复！`)
    if (!confirmed) return
    
    try {
      let successCount = 0
      let failCount = 0
      for (const dept of selectedRows.value) {
        try {
          const response = await deptService.delete(dept.id)
          if (response.success) successCount++
          else failCount++
        } catch (err) {
          failCount++
        }
      }
      if (successCount > 0) {
        showSuccess(`成功删除 ${successCount} 个部门${failCount > 0 ? `，${failCount} 个失败` : ''}`)
        loadData()
      } else {
        showError('删除失败')
      }
    } catch (err) {
      showError(err.message || '删除失败')
    }
  }
}

const handleAction = async (action) => {
  if (!action) return
  if (isActionDisabled(action)) return
  
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
