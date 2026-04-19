<!-- 学期列表 -->
<template>
  <CrudList
    :title="listHeader || '学期管理'"
    :icon="Calendar"
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
    :options="opt"
    @option-click="handleOptionClick"
    @action-click="handleActionClick"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
  >
  </CrudList>
</template>

<script setup>
import { useTermList } from '@/core/hooks'
import CrudList from '@/views/pc/components/CrudList.vue'
import { Calendar } from '@element-plus/icons-vue'

const {
    listHeader, columns, tableData, opt, error,
    showCheckbox, isPaginated, currentPage, totalCount, pageSize,
    loading,
    handleOptionClick,
    handleActionClick,
    handleSizeChange,
    handleCurrentChange
} = useTermList()
</script>
