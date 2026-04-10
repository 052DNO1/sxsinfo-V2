<!-- 维护记录列表 -->
<template>
  <CrudList
    :title="listHeader || '维护/设备列表'"
    icon="Tools"
    :columns="columns"
    :data="objectList"
    :loading="loading"
    :error="error"
    :total="totalCount"
    v-model:current-page="currentPage"
    v-model:page-size="pageSize"
    :is-paginated="isPaginated"
    :show-checkbox="showCheckbox"
    :show-batch-delete="isDeviceList"
    :selected-count="selectedCount"
    :options="filteredOpt"
    @batch-delete="handleBatchDelete"
    @option-click="handleOptionClick"
    @action-click="handleAction"
    @selection-change="handleSelectionChange"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
  >
    <template #actions>
      <el-button 
        v-if="isMaintainList" 
        type="success" 
        plain
        :icon="Download"
        @click="handleExportExcel">
        导出Excel
      </el-button>
      
      <el-button 
        v-if="!isDeviceList && user?.is_superuser"
        type="info" 
        plain
        :icon="Box"
        @click="goToArchive">
        查看归档记录
      </el-button>
    </template>

    <template #row-actions="{ row, column }">
      <div class="action-cell">
        <template v-if="column.isAction">
          <template v-for="(op, opIndex) in row[column.prop]" :key="opIndex">
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
        </template>
        <span v-else>{{ formatCellContent(row[column.prop]) }}</span>
      </div>
    </template>
  </CrudList>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import CrudList from '@/views/pc/components/CrudList.vue'
import { useAuth, useMaintainList } from '@/core/hooks'
import { getButtonType, getButtonIcon, isActionDisabled } from '@/core/utils/tableHelpers'
import { Download, Box, Tools } from '@element-plus/icons-vue'

const router = useRouter()
const { user } = useAuth()

const {
    listHeader, columns, tableData: objectList, opt, filteredOpt, error,
    showCheckbox, isPaginated, currentPage, totalCount, pageSize, loading,
    isDeviceList, isMaintainList,
    
    handleSizeChange,
    handleCurrentChange,
    handleBatchDelete: execBatchDelete,
    handleExportExcel,
    handleOptionClick,
    handleAction
} = useMaintainList()

const selectedRows = ref([])
const selectedCount = computed(() => selectedRows.value.length)

const formatCellContent = (content) => {
  if (content === null || content === undefined) return '-'
  return content
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const handleBatchDelete = async () => {
  await execBatchDelete(selectedRows.value)
  selectedRows.value = []
}

const goToArchive = () => {
  router.push({ path: '/archived-terms', query: { type: 'maintain' } })
}
</script>

<style scoped>
.action-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
