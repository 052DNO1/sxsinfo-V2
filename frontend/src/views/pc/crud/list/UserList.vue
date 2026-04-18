
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
    <template #actions>
      <el-select
        v-if="user?.is_superuser && select?.showDepartmentFilter"
        v-model="selectedRoleId"
        placeholder="按角色筛选"
        clearable
        size="default"
        class="role-select"
      >
        <el-option
          v-for="role in select.options"
          :key="role.id"
          :label="role.text"
          :value="role.id"
        />
      </el-select>
      <el-select
        v-if="user?.is_superuser && select?.showDepartmentFilter"
        v-model="selectedDepartmentId"
        placeholder="按部门筛选"
        clearable
        size="default"
        class="dept-select"
      >
        <el-option
          v-for="dept in select.departmentOptions"
          :key="dept.id"
          :label="dept.text"
          :value="dept.id"
        />
      </el-select>
      <el-button
        v-for="(o, index) in filteredOptions"
        :key="index"
        :type="getButtonType(o)"
        :icon="getButtonIcon(o)"
        plain
        @click="handleOptionClick(o)">
        {{ o.text }}
      </el-button>
    </template>
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
import { getButtonType, getButtonBg, getButtonIcon, isActionDisabled } from '@/core/utils/tableHelpers'

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
  handleSelectionChange,
  selectedDepartmentId,
  selectedRoleId,
  select
} = useUserList()

const filteredOptions = computed(() => {
  const isSuperAdmin = user.value?.is_super_admin
  const isSystemAdmin = user.value?.is_superuser
  return opt.value.filter(btn => {
    if (btn.onclick === 'add' && !isSuperAdmin && !isSystemAdmin) {
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

.role-select {
  width: 130px;
  margin-right: 8px;
}

.dept-select {
  width: 140px;
  margin-right: 8px;
}
</style>
