<!-- 使用记录列表 -->
<template>
  <CrudList
    :title="listHeader"
    icon="Document"
    :columns="columns"
    :data="objectList"
    :loading="loading"
    :error="error"
    :total="totalCount"
    v-model:current-page="currentPage"
    v-model:page-size="pageSize"
    :is-paginated="isPaginated"
    :show-checkbox="showCheckbox"
    :show-batch-delete="false"
    :selected-count="multipleSelection.length"
    :options="opt"
    @option-click="handleOptionClick"
    @selection-change="handleSelectionChange"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
  >
    <template #actions>
      <template v-if="showCheckbox && !showExport">
        <el-button
          type="success"
          plain
          :icon="Download"
          @click="handleExportExcel">
          导出Excel
        </el-button>
      </template>

      <template v-if="showExport && exportUrls">
        <el-link :href="exportUrls.excel" type="success" target="_blank" :underline="false">
          <el-button type="success" plain :icon="Download">导出Excel</el-button>
        </el-link>
      </template>
    </template>

    <template #row-actions="{ row, column }">
      <div class="action-buttons-container">
        <template v-for="(op, opIndex) in row[column.prop]" :key="opIndex">
          <el-button
            type="primary"
            size="small"
            link
            :icon="View"
            @click="handleAction(op)">
            {{ op.text }}
          </el-button>
        </template>
      </div>
    </template>
  </CrudList>
</template>

<script setup>
import { ref, computed } from 'vue'
import CrudList from '@/views/pc/components/CrudList.vue'
import { useRecordList } from '@/core/hooks'
import { Download, View } from '@element-plus/icons-vue'

const {
  listHeader,
  columns,
  tableData,
  opt,
  error,
  showCheckbox,
  isPaginated,
  currentPage,
  totalCount,
  pageSize,
  loading,
  exportUrls,
  handleSizeChange,
  handleCurrentChange,
  handleExportExcel,
  handleOptionClick,
  handleAction
} = useRecordList()

const objectList = computed(() => tableData.value || tableData || [])
const showExport = computed(() => {
  const header = listHeader.value || listHeader || ''
  return header.includes('归档记录')
})

const multipleSelection = ref([])

const handleSelectionChange = (val) => {
  multipleSelection.value = val
}
</script>

<style scoped>
.action-buttons-container {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
