<!-- 
  通用数据表格组件 
  用于统一项目中的列表展现，减少重复代?-->
<template>
  <div class="data-table-container">
    <!-- 头部操作卡片 -->
    <el-card class="header-card" shadow="hover" v-if="showHeader">
      <div class="listheader">
        <div class="header-title">
          <el-icon v-if="icon" class="header-icon">
            <component :is="icon" />
          </el-icon>
          <span>{{ title }}</span>
        </div>
        
        <div class="listheader-actions">
          <!-- 操作按钮区域 -->
          <div class="action-buttons">
            <slot name="actions">
              <!-- 默认批量删除按钮 -->
              <el-button
                v-if="showBatchDelete"
                type="danger"
                plain
                :icon="Delete"
                @click="$emit('batch-delete')"
                :disabled="selectedCount === 0">
                批量删除
              </el-button>

              <!-- 动态操作按�?-->
              <template v-if="options && options.length">
                <el-button
                  v-for="(o, index) in options"
                  :key="index"
                  :type="getButtonType(o)"
                  :icon="getButtonIcon(o)"
                  plain
                  @click="$emit('option-click', o)">
                  {{ o.text }}
                </el-button>
              </template>
            </slot>
            
            <el-button v-if="shouldShowBackButton" plain :icon="Back" @click="$emit('back')">返回</el-button>
            <el-button v-if="showHome" plain :icon="HomeFilled" @click="$emit('home')">首页</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 表格内容卡片 -->
    <el-card class="table-card" shadow="hover">
      <div v-if="error" class="error-state">
        <el-empty :description="error" />
      </div>
      
      <el-table
        v-else
        :data="data"
        v-loading="loading"
        border
        stripe
        highlight-current-row
        @selection-change="val => $emit('selection-change', val)">
        
        <!-- 多选列 -->
        <el-table-column
          v-if="showCheckbox"
          type="selection"
          width="55"
          align="center"
        />

        <!-- 动态数据列 -->
        <el-table-column
          v-for="(col, index) in columns"
          :key="index"
          :label="col.label"
          :prop="col.prop"
          :min-width="col.minWidth || 120"
          show-overflow-tooltip>
          <template #default="scope">
            <!-- 操作单元�?-->
            <div v-if="col.isAction" class="action-cell">
              <slot name="row-actions" :row="scope.row" :column="col">
                <template v-for="(op, opIndex) in scope.row[col.prop]" :key="opIndex">
                  <el-button
                    v-if="!shouldHideAction(op)"
                    :type="getButtonType(op)"
                    size="small"
                    link
                    :icon="getButtonIcon(op)"
                    @click="$emit('action-click', op, scope.row)">
                    {{ op.text }}
                  </el-button>
                </template>
              </slot>
            </div>
            
            <!-- 状态单元格 -->
            <el-tag 
              v-else-if="col.isStatus" 
              :type="scope.row[col.prop]?.type || 'info'"
              size="small">
              {{ scope.row[col.prop]?.text || scope.row[col.prop] }}
            </el-tag>

            <!-- 普通单元格 -->
            <span v-else>{{ formatValue(scope.row[col.prop]) }}</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页组件 -->
      <div class="pagination-wrapper" v-if="showPagination && (total > 0 || isPaginated)">
        <el-pagination
          v-model:current-page="currentPageModel"
          v-model:page-size="pageSizeModel"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="val => $emit('size-change', val)"
          @current-change="val => $emit('current-change', val)"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Delete, Back, HomeFilled } from '@element-plus/icons-vue'
import { getButtonType, getButtonIcon } from '@/core/utils/tableHelpers'
import { useUserStore } from '@/core/store/user'

const userStore = useUserStore()

const props = defineProps({
  title: String,
  icon: [String, Object],
  columns: { type: Array, default: () => [] },
  data: { type: Array, default: () => [] },
  loading: Boolean,
  error: String,
  showHeader: { type: Boolean, default: true },
  showPagination: { type: Boolean, default: true },
  showCheckbox: Boolean,
  showBatchDelete: Boolean,
  showBack: { type: Boolean, default: true },
  showHome: { type: Boolean, default: true },
  total: { type: Number, default: 0 },
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 10 },
  isPaginated: Boolean,
  options: Array,
  selectedCount: { type: Number, default: 0 },
  excludeActionPatterns: { type: Array, default: () => [] }
})

const emit = defineEmits([
  'batch-delete', 
  'option-click', 
  'action-click',
  'selection-change',
  'size-change',
  'current-change',
  'back',
  'home',
  'update:currentPage',
  'update:pageSize'
])

const currentPageModel = computed({
  get: () => props.currentPage,
  set: (val) => emit('update:currentPage', val)
})

const pageSizeModel = computed({
  get: () => props.pageSize,
  set: (val) => emit('update:pageSize', val)
})

const shouldShowBackButton = computed(() => {
  const user = userStore.user
  if (user?.is_super_admin && !user?.is_superuser) {
    return false
  }
  return props.showBack
})

const formatValue = (val) => {
  if (val === null || val === undefined) return '-'
  if (val === '') return ''
  return val
}

const shouldHideAction = (op) => {
  if (!op || !op.text) return true
  return props.excludeActionPatterns.some(p => op.text.includes(p))
}
</script>

<style scoped>
.header-card {
  margin-bottom: 20px;
  border-radius: 12px;
  border: none;
}

.listheader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.header-title {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  white-space: nowrap;
}

.header-icon {
  margin-right: 10px;
  color: #1890ff;
  font-size: 24px;
}

.listheader-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  justify-content: flex-end;
}

.filter-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-select {
  width: 200px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.table-card {
  border-radius: 12px;
  border: none;
  min-height: 400px;
}

.action-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.error-state {
  padding: 40px;
}
</style>
