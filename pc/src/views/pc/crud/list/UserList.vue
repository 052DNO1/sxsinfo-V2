
<!-- 用户列表 -->
<template>
  <CrudList
    :title="listHeader || '用户列表管理'"
    icon="List"
    :columns="columns"
    :data="tableData"
    :loading="loading"
    :error="error"
    :total="totalCount"
    v-model:current-page="currentPage"
    v-model:page-size="pageSize"
    :is-paginated="isPaginated"
    :show-checkbox="showCheckbox"
    :show-batch-delete="false"
    :selected-count="selectedRows?.length || 0"
    :options="filteredOptions"
    @option-click="handleOptionClick"
    @action-click="handleAction"
    @selection-change="handleSelectionChange"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
  >
    <template #row-actions="{ row, column }">
      <div class="action-buttons-container">
        <template v-for="(op, opIndex) in row[column.prop]" :key="opIndex">
          <template v-if="!(op.text === '重置密码' || op.text === '删除')">
            <el-button
              :type="getButtonType(op)"
              size="small"
              :disabled="isActionDisabled(op)"
              text
              :bg="getButtonBg(op)"
              @click="handleAction(op)">
              {{ op.text }}
            </el-button>
          </template>
        </template>
      </div>
    </template>
  </CrudList>
</template>

<script setup>
import { computed } from 'vue'
import { useUserList } from '@/core/hooks'
import { useUserStore } from '@/core/store/user'
import CrudList from '@/views/pc/components/CrudList.vue'
import { getButtonType, getButtonBg, isActionDisabled } from '@/core/utils/tableHelpers'

const userStore = useUserStore()
const user = computed(() => userStore.user)

const {
  listHeader, columns, tableData, opt, error,
  showCheckbox, isPaginated, currentPage, totalCount, pageSize,
  loading, selectedRows,
  handleBatchResetPassword,
  handleOptionClick,
  handleAction,
  handleSizeChange,
  handleCurrentChange,
  handleSelectionChange
} = useUserList()

const filteredOptions = computed(() => {
  const isSuperAdmin = user.value?.is_super_admin || user.value?.is_superuser
  return opt.value.filter(btn => {
    if (btn.onclick === 'add' && !isSuperAdmin) {
      return false
    }
    return true
  })
})
</script>

<style scoped>
.action-buttons-container {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
