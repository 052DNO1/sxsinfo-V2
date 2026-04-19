<!-- 使用记录列表 -->
<template>
  <CrudList
    :title="listHeader"
    :icon="listIcon"
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
      <el-button
        v-if="isArchiveMode"
        type="primary"
        plain
        :icon="Back"
        @click="goBackToDashboard">
        返回
      </el-button>

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
import { useRoute, useRouter } from 'vue-router'
import CrudList from '@/views/pc/components/CrudList.vue'
import { useRecordList } from '@/core/hooks'
import { Download, View, Back, Document, Tools, Warning } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

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
  recordType,
  isFaultList,
  isMaintainList,
  handleSizeChange,
  handleCurrentChange,
  handleExportExcel,
  handleOptionClick,
  handleAction
} = useRecordList()

const listIcon = computed(() => {
  if (isFaultList.value) return Warning
  if (isMaintainList.value) return Tools
  return Document
})

const isArchiveMode = computed(() => route.path.includes('view-archived'))

const goBackToDashboard = () => {
  const query = { ...route.query }
  delete query.type
  router.push({ query })
}

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
