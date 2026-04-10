<!-- 班级列表 -->
<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="page-container">
        <el-card class="header-card" shadow="hover">
          <div class="listheader">
            <div class="header-title">
              <el-icon class="header-icon"><List /></el-icon>
              <span>{{ listHeader || '课表管理' }}</span>
            </div>
            
            <div class="listheader-actions">
              <div class="filter-area" v-if="select">
                <el-select
                  v-model="filterValue"
                  :placeholder="select.name === 'filter_sxs' ? '筛选: 选择实训室' : '筛选: 选择条件'"
                  clearable
                  filterable
                  class="filter-select"
                  @change="handleFilter">
                  <el-option
                    v-for="item in select.options"
                    :key="item.id"
                    :label="item.text"
                    :value="item.id">
                  </el-option>
                </el-select>
              </div>

              <div class="view-switch">
                <el-radio-group v-model="viewMode" size="small" :disabled="!hasSelectedSxs">
                  <el-radio-button value="grid" :disabled="!hasSelectedSxs">
                    <el-icon><Grid /></el-icon>
                    网格视图
                  </el-radio-button>
                  <el-radio-button value="list">
                    <el-icon><List /></el-icon>
                    列表视图
                  </el-radio-button>
                </el-radio-group>
                <el-tooltip v-if="!hasSelectedSxs" content="请先选择特定实训室以使用网格视图" placement="top">
                  <el-icon class="view-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </div>

              <div class="action-buttons">
                <el-button
                  v-if="viewMode === 'list'"
                  type="danger"
                  plain
                  icon="Delete"
                  :disabled="multipleSelection.length === 0"
                  @click="handleBatchDelete">
                  批量删除
                </el-button>
                
                <template v-if="opt">
                  <el-button
                    v-for="(o, index) in opt"
                    :key="index"
                    :type="getButtonType(o)"
                    :icon="getButtonIcon(o)"
                    plain
                    @click="handleOptionClick(o)">
                    {{ o.text }}
                  </el-button>
                </template>
                
                <el-button v-if="showBackButton" class="nav-action-btn" plain icon="Back" @click="smartBack">返回</el-button>
                <el-button class="nav-action-btn" plain icon="HomeFilled" @click="goHome">首页</el-button>
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="table-card" shadow="hover">
          <div v-if="error" class="friendly-empty-state">
            <el-empty :description="error" />
          </div>
          
          <ScheduleGrid
            v-else-if="viewMode === 'grid'"
            :courses="allClassData"
            :title="gridTitle"
            :loading="allDataLoading"
            :selected-sxs-name="selectedSxsName"
            @edit="handleGridEdit"
            @delete="handleGridDelete"
            @add="handleGridAdd"
          />
          
          <el-table
            v-else
            :data="tableData"
            style="width: 100%"
            border
            stripe
            highlight-current-row
            @selection-change="handleSelectionChange"
            v-loading="loading"
            class="modern-table"
          >
            <el-table-column
              v-if="showCheckbox && !skipCheckbox"
              type="selection"
              width="55"
              align="center"
            />

            <template v-for="(col, index) in columns" :key="index">
              <el-table-column
                :label="col.label"
                :prop="col.prop"
                :min-width="col.minWidth || 120"
                show-overflow-tooltip
              >
                <template #default="scope">
                  <div v-if="col.isAction" class="action-buttons-container">
                    <template v-for="(op, opIndex) in scope.row[col.prop]" :key="opIndex">
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
                  </div>
                  <span v-else>{{ scope.row[col.prop] }}</span>
                </template>
              </el-table-column>
            </template>

            <template #empty>
              <div class="empty-data">
                <el-empty description="暂无数据" />
              </div>
            </template>
          </el-table>
          
          <Pagination
            v-if="viewMode === 'list' && (isPaginated || totalCount > 0)"
            v-model:currentPage="currentPage"
            v-model:pageSize="pageSize"
            :total-count="totalCount"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </el-card>
      </div>
    </template>
  </Index>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Index from '@/views/pc/dashboard/Index.vue'
import Pagination from '@/views/pc/components/Pagination.vue'
import ScheduleGrid from '@/views/pc/components/ScheduleGrid.vue'
import { useAuth, useClassList } from '@/core/hooks'
import { useNavigation } from '@/core/utils/routeDecision'
import { getButtonType, getButtonIcon, getButtonBg, isActionDisabled } from '@/core/utils/tableHelpers'
import { List, Delete, Back, HomeFilled, Grid, QuestionFilled } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const { user } = useAuth()
const { goHome, smartBack } = useNavigation()

const viewMode = ref('list')

const {
    listHeader, columns, tableData, select, opt, error, filterValue,
    hideBack, backUrl, showCheckbox, skipCheckbox, isPaginated,
    currentPage, totalCount, pageSize, loading,
    allClassData, allDataLoading,
    
    loadData,
    loadAllData,
    handleFilter,
    handleSizeChange,
    handleCurrentChange,
    execBatchDelete,
    execDelete,
    getActionRoute
} = useClassList()

const multipleSelection = ref([])

const showBackButton = computed(() => {
  if (user.value?.is_superuser) return false
  if (hideBack.value) return false
  return true
})

const selectedSxsName = computed(() => {
  if (filterValue.value && select.value?.options) {
    const option = select.value.options.find(o => o.id === filterValue.value)
    return option?.text || ''
  }
  return ''
})

const gridTitle = computed(() => {
  return selectedSxsName.value || '全部实训室课程时刻表'
})

const hasSelectedSxs = computed(() => {
  return !!filterValue.value
})

watch(filterValue, (newVal) => {
  if (newVal) {
    viewMode.value = 'grid'
  } else {
    viewMode.value = 'list'
  }
}, { immediate: true })

const handleSelectionChange = (val) => {
  multipleSelection.value = val
}

const handleOptionClick = async (option) => {
  if ((option.onclick && option.onclick.includes('batchDeleteClass')) || (option.text && option.text.includes('批量删除'))) {
    await execBatchDelete(multipleSelection.value)
    return
  }
  
  const navUrl = getActionRoute(option)
  if (navUrl) {
    try {
      await router.push(navUrl)
    } catch (err) {
      window.location.href = navUrl
    }
  }
}

const handleBatchDelete = async () => {
  if (multipleSelection.value.length === 0) {
    return
  }
  await execBatchDelete(multipleSelection.value)
}

const handleAction = async (action) => {
  if (!action) return
  
  if (action.action_type === 'delete') {
    await execDelete(action)
    return
  }
  
  const navUrl = getActionRoute(action)
  if (navUrl) {
    try {
      await router.push(navUrl)
    } catch (err) {
      window.location.href = navUrl
    }
  }
}

const handleGridEdit = (course) => {
  router.push(`/edit-class/${course.id}`)
}

const handleGridDelete = async (course) => {
  await execDelete({
    action_type: 'delete',
    resource_type: 'class',
    resource_id: course.id
  })
}

const handleGridAdd = ({ weekday, period }) => {
  const sxsid = filterValue.value || route.params.id || ''
  const query = {
    weekday,
    period,
    filter_sxs: filterValue.value || sxsid
  }
  if (sxsid) {
    router.push({ path: `/addclass/${sxsid}`, query })
  } else {
    router.push({ path: '/addclass', query })
  }
}
</script>

<style scoped>
.page-container {
  padding: 0;
  max-width: 100%;
}

.header-card {
  margin-bottom: 20px;
  border-radius: 12px;
  border: none;
}

.header-card :deep(.el-card__body) {
  overflow-x: auto;
}

.listheader {
  display: flex !important;
  justify-content: space-between;
  align-items: center !important;
  flex-wrap: nowrap !important;
  gap: 12px;
  max-width: 100%;
  min-width: 0;
}

.header-title {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  flex-shrink: 0;
  white-space: nowrap;
}

.header-icon {
  margin-right: 10px;
  color: #1890ff;
  font-size: 24px;
}

.listheader-actions {
  display: flex !important;
  align-items: center !important;
  gap: 16px;
  flex-wrap: nowrap !important;
  max-width: 100%;
  min-width: 0;
  flex: 1 1 auto;
  justify-content: flex-end;
}

.filter-area {
  display: flex;
  align-items: center;
  min-width: 0;
}

.filter-select {
  width: clamp(140px, 16vw, 200px);
}

.view-switch {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.view-switch :deep(.el-radio-button__inner) {
  display: flex;
  align-items: center;
  gap: 4px;
}

.view-tip {
  color: #909399;
  font-size: 16px;
  cursor: help;
}

.action-buttons {
  display: flex !important;
  gap: 10px;
  flex-wrap: nowrap !important;
  align-items: center !important;
  white-space: nowrap !important;
  overflow-x: auto;
  overflow-y: hidden;
  max-width: 100%;
  min-width: 0;
}

.action-buttons :deep(.el-button + .el-button) {
  margin-left: 0;
}

.action-buttons :deep(.el-button) {
  padding: 6px 12px;
  font-size: 13px;
}

.table-card {
  border-radius: 12px;
  border: none;
  min-height: 500px;
}

.modern-table {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th.el-table__cell) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 600;
  height: 50px;
}

.action-buttons-container {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.empty-data {
  padding: 40px;
  text-align: center;
}
</style>
