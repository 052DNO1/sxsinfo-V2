<template>
  <CrudList
    :title="listHeader || '实训室列表'"
    :icon="Monitor"
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
    :selected-count="selectedCount"
    :options="opt"
    @batch-delete="handleBatchDeleteLab"
    @option-click="handleOptionClick"
    @action-click="handleAction"
    @selection-change="handleSelectionChange"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
  >
    <template #actions>
      <el-button
        v-if="showCheckbox"
        type="danger"
        plain
        :icon="Delete"
        @click="handleBatchDeleteLab"
        :disabled="selectedCount === 0">
        批量删除
      </el-button>
      <el-button type="primary" plain size="default" :icon="Document" @click="handleViewRecords('usage')">
        查看使用记录
      </el-button>
      <el-button type="primary" plain size="default" :icon="Tools" @click="handleViewRecords('maintain')">
        查看维护记录
      </el-button>
      <el-button type="primary" plain size="default" :icon="Warning" @click="handleViewRecords('fault')">
        查看故障工单
      </el-button>
      <el-button type="primary" plain size="default" :icon="Calendar" @click="handleViewClassSchedule">
        查看课程表
      </el-button>
      <el-button type="primary" plain size="default" :icon="Monitor" @click="handleViewDevices">
        查看全部设备
      </el-button>
    </template>

    <template #row-actions="{ row, column }">
      <div class="action-buttons-container">
        <template v-for="(op, opIndex) in (column.prop ? row[column.prop] : [])" :key="opIndex">
          <el-button
            :type="getButtonType(op)"
            size="small"
            link
            :icon="getButtonIcon(op)"
            :disabled="isActionDisabled(op)"
            @click="handleAction(op)">
            {{ op.text }}
          </el-button>
        </template>
      </div>
    </template>
  </CrudList>
</template>

<script setup>
import CrudList from '@/views/pc/components/CrudList.vue'
import { useSxsList } from '@/core/hooks'
import { getButtonType, getButtonIcon, isActionDisabled } from '@/core/utils/tableHelpers'
import { Document, Tools, Warning, Monitor, Calendar, Delete } from '@element-plus/icons-vue'

const {
  listHeader, columns, tableData, opt, error,
  showCheckbox, isPaginated, currentPage, totalCount, pageSize,
  loading, selectedCount,
  
  handleSelectionChange,
  handleSizeChange,
  handleCurrentChange,
  handleOptionClick,
  handleAction,
  handleBatchDeleteLab,
  handleViewRecords,
  handleViewDevices,
  handleViewClassSchedule
} = useSxsList()
</script>

<style scoped>
.action-buttons-container {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
