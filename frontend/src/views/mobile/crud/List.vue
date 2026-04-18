<template>
  <!-- 移动端列表页面 - 使用与PC端相同的业务逻辑 -->
  <div class="mobile-list-page mobile-layout">
    <van-nav-bar
      :title="listHeader"
      left-arrow
      @click-left="goBack"
      class="mobile-nav-bar"
    >
      <template #right>
        <van-icon name="search" size="18" @click="showFilter = !showFilter" />
      </template>
    </van-nav-bar>

    <!-- 操作按钮区域 -->
    <div v-if="opt && opt.length > 0" class="mobile-action-bar">
      <van-button
        v-for="(option, index) in opt"
        :key="index"
        size="small"
        :type="getButtonType(option)"
        plain
        @click="handleOptionClick(option)"
        class="action-btn"
      >
        {{ option.text }}
      </van-button>
    </div>

    <!-- 筛选区域 -->
    <van-collapse v-model="activeFilterNames" v-if="select || showFilter">
      <van-collapse-item name="filter" title="筛选条件">
        <van-form @submit="handleFilter">
          <van-field
            v-if="select"
            v-model="filterValue"
            :name="select.name || 'filter'"
            label="筛选"
            placeholder="请选择"
            is-link
            readonly
            @click="showSelectPicker = true"
          />
          <van-popup v-model:show="showSelectPicker" position="bottom">
            <van-picker
              :columns="selectOptions"
              @confirm="onSelectConfirm"
              @cancel="showSelectPicker = false"
            />
          </van-popup>
          <div style="padding: 12px;">
            <van-button type="primary" block native-type="submit">查询</van-button>
          </div>
        </van-form>
      </van-collapse-item>
    </van-collapse>

    <!-- 列表内容 -->
    <div class="mobile-list-content">
      <!-- 加载状态 -->
      <div v-if="loading" style="padding: 40px 16px; text-align: center;">
        <van-loading size="24px" vertical>加载中...</van-loading>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="custom-empty-state">
        <div class="empty-icon">⚠️</div>
        <div class="empty-text">{{ error }}</div>
        <van-button type="primary" size="small" @click="refreshData">重试</van-button>
      </div>
      
      <!-- 空状态 -->
      <div v-else-if="tableData.length === 0" class="custom-empty-state">
        <div class="empty-icon">📋</div>
        <div class="empty-text">暂无数据</div>
      </div>
      
      <!-- 列表数据 -->
      <div v-else class="custom-list-container">
        <div
          v-for="(row, rowIndex) in tableData"
          :key="rowIndex"
          class="custom-list-item"
          @click="handleRowClick(row)"
        >
          <!-- 主标题行 -->
          <div class="list-item-header">
            <span class="list-item-title">{{ getRowTitle(row) }}</span>
            <van-tag 
              v-if="getStatusInfo(row)" 
              :type="getStatusInfo(row).type" 
              size="small"
            >
              {{ getStatusInfo(row).text }}
            </van-tag>
          </div>
          
          <!-- 详情信息 -->
          <div class="list-item-details">
            <div 
              v-for="(col, colIndex) in getDisplayColumns(row)" 
              :key="colIndex"
              class="detail-row"
            >
              <span class="detail-label">{{ col.label }}:</span>
              <span class="detail-value">{{ formatCellValue(row[col.prop], col) }}</span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div v-if="row.actions && row.actions.length > 0" class="list-item-actions">
            <van-button
              v-for="(action, actionIndex) in row.actions"
              :key="actionIndex"
              size="mini"
              :type="getActionType(action)"
              plain
              @click.stop="handleAction(action)"
            >
              {{ action.text }}
            </van-button>
          </div>

          <van-icon name="arrow" class="list-item-arrow" />
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="isPaginated && tableData.length > 0 && totalCount > pageSize" class="custom-pagination">
        <button
          class="pagination-btn"
          :disabled="currentPage === 1"
          @click="handlePageChange(currentPage - 1)"
        >
          上一页
        </button>
        <span class="pagination-info">{{ currentPage }} / {{ totalPages }}</span>
        <button
          class="pagination-btn"
          :disabled="currentPage >= totalPages"
          @click="handlePageChange(currentPage + 1)"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  useUserList, 
  useSxsList, 
  useDeptList, 
  useClassList, 
  useTermList,
  useRecordList,
  useMaintainList,
  useMessageList as useMessageListHook
} from '@/core/hooks'
import { useAuth } from '@/core/hooks'
import { useNavigation } from '@/core/utils/routeDecision'
import { useMobile } from '@/composables/useMobile'
import { showSuccessToast, showFailToast, showConfirmDialog } from '@/utils/mobileDialog'

export default {
  name: 'MobileList',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const { user } = useAuth()
    const { smartBack, goHome } = useNavigation()
    
    // 移动端初始化
    const { init: initMobile, loadVantComponents } = useMobile()
    
    // UI 状态
    const showFilter = ref(false)
    const activeFilterNames = ref([])
    const showSelectPicker = ref(false)
    const filterValue = ref('')

    // 根据路由选择对应的 domain hook
    const getListHook = () => {
      const path = route.path
      
      // 用户列表
      if (path.startsWith('/userlist')) {
        return useUserList()
      }
      
      // 实训室列表
      if (path.startsWith('/listsxs')) {
        return useSxsList()
      }
      
      // 部门列表
      if (path.startsWith('/listdept') || path.startsWith('/deptlist')) {
        return useDeptList()
      }
      
      // 班级/课表列表
      if (path.startsWith('/listsxsclass') || path.startsWith('/class')) {
        return useClassList()
      }
      
      // 学期列表
      if (path.startsWith('/term')) {
        return useTermList()
      }
      
      // 使用记录列表
      if (path.startsWith('/listuserrecord') || path.startsWith('/listsxsrecord')) {
        return useRecordList()
      }
      
      // 维护记录列表
      if (path.startsWith('/listsxsmaintain')) {
        return useMaintainList()
      }
      
      // 消息列表
      if (path.includes('message')) {
        return useMessageListHook()
      }
      
      // 默认返回用户列表
      return useUserList()
    }

    const listHook = getListHook()
    
    // 从 hook 解构所需的数据和方法
    const {
      listHeader,
      columns,
      tableData,
      loading,
      error,
      showCheckbox,
      isPaginated,
      currentPage,
      totalCount,
      pageSize,
      opt,
      select,
      handleAction,
      handleOptionClick,
      handleSizeChange,
      handleCurrentChange,
      refreshData
    } = listHook

    // 计算总页数
    const totalPages = computed(() => {
      return Math.ceil(totalCount.value / pageSize.value)
    })

    // 移动端辅助函数
    const selectOptions = computed(() => {
      if (!select.value || !select.value.options) return []
      return select.value.options.map(item => ({
        text: item.text,
        value: item.id
      }))
    })

    const onSelectConfirm = ({ selectedOptions }) => {
      filterValue.value = selectedOptions[0]?.value || ''
      showSelectPicker.value = false
    }

    // 获取行的主标题
    const getRowTitle = (row) => {
      if (!row) return '无标题'
      
      // 根据不同类型的数据源获取标题
      if (row.username) return row.username
      if (row.sxsname) return row.sxsname
      if (row.classname) return row.classname
      if (row.termname) return row.termname
      if (row.deptname) return row.deptname
      if (row.subject) return row.subject
      
      // 尝试从第一列获取
      if (columns.value && columns.value.length > 0) {
        const firstCol = columns.value.find(c => c.prop !== 'actions')
        if (firstCol && row[firstCol.prop]) {
          return String(row[firstCol.prop]).substring(0, 30)
        }
      }
      
      return '列表项'
    }

    // 获取要显示的详情列（排除标题列和操作列）
    const getDisplayColumns = (row) => {
      if (!columns.value) return []
      
      // 排除操作列和已用于标题的列
      const excludeProps = ['actions']
      
      // 根据数据类型排除标题字段
      if (row.username) excludeProps.push('username')
      if (row.sxsname) excludeProps.push('sxsname')
      if (row.classname) excludeProps.push('classname')
      if (row.termname) excludeProps.push('termname')
      if (row.deptname) excludeProps.push('deptname')
      
      return columns.value.filter(col => 
        !excludeProps.includes(col.prop) && 
        row[col.prop] !== undefined && 
        row[col.prop] !== null &&
        col.show !== false
      ).slice(0, 4) // 最多显示4个详情
    }

    // 格式化单元格值
    const formatCellValue = (value, col) => {
      if (value === undefined || value === null) return '-'
      
      // 处理对象类型的值（如status_display）
      if (typeof value === 'object' && value.text) {
        return value.text
      }
      
      // 处理数组
      if (Array.isArray(value)) {
        return value.join(', ')
      }
      
      // 截断过长的字符串
      const str = String(value)
      return str.length > 20 ? str.substring(0, 20) + '...' : str
    }

    // 获取状态信息
    const getStatusInfo = (row) => {
      if (row.is_active !== undefined) {
        return row.is_active 
          ? { text: '正常', type: 'success' }
          : { text: '禁用', type: 'danger' }
      }
      
      if (row.status_display) {
        return row.status_display
      }
      
      return null
    }

    // 获取按钮类型
    const getButtonType = (option) => {
      if (!option) return 'default'
      
      if (option.type) {
        const typeMap = {
          primary: 'primary',
          success: 'success',
          warning: 'warning',
          danger: 'danger',
          info: 'info'
        }
        return typeMap[option.type] || 'default'
      }
      
      const text = option.text || ''
      if (text.includes('删除') || text.includes('批量')) return 'danger'
      if (text.includes('添加') || text.includes('新增')) return 'success'
      if (text.includes('重置') || text.includes('修改')) return 'warning'
      
      return 'primary'
    }

    const getActionType = (action) => {
      if (!action) return 'default'
      
      const text = action.text || ''
      if (text.includes('删除')) return 'danger'
      if (text.includes('禁用')) return 'warning'
      if (text.includes('激活') || text.includes('编辑')) return 'primary'
      
      return 'default'
    }

    // 行点击处理
    const handleRowClick = (row) => {
      // 如果有编辑操作，默认执行编辑
      if (row.actions && row.actions.length > 0) {
        const editAction = row.actions.find(a => 
          a.action_type === 'edit' || a.text?.includes('编辑')
        )
        if (editAction) {
          handleAction(editAction)
          return
        }
        
        // 否则执行第一个操作
        handleAction(row.actions[0])
      }
    }

    // 筛选处理
    const handleFilter = () => {
      // 触发 hook 的筛选方法（如果存在）
      if (listHook.loadDataWithFilter) {
        listHook.loadDataWithFilter({ [select.value?.name || 'q']: filterValue.value })
      }
    }

    // 分页处理
    const handlePageChange = (page) => {
      if (handleCurrentChange) {
        handleCurrentChange(page)
      }
    }

    const goBack = () => {
      smartBack()
    }

    // 初始化
    onMounted(() => {
      const cleanupMobile = initMobile()
      onUnmounted(() => {
        if (cleanupMobile) cleanupMobile()
      })
      
      setTimeout(() => {
        loadVantComponents()
      }, 200)
    })

    return {
      // 数据状态
      listHeader,
      columns,
      tableData,
      loading,
      error,
      showCheckbox,
      isPaginated,
      currentPage,
      totalCount,
      pageSize,
      totalPages,
      opt,
      select,
      
      // UI 状态
      showFilter,
      activeFilterNames,
      showSelectPicker,
      filterValue,
      selectOptions,
      
      // 方法
      handleAction,
      handleOptionClick,
      handleRowClick,
      handleFilter,
      handlePageChange,
      onSelectConfirm,
      goBack,
      refreshData,
      
      // 辅助方法
      getRowTitle,
      getDisplayColumns,
      formatCellValue,
      getStatusInfo,
      getButtonType,
      getActionType,
      
      // 用户信息
      user
    }
  }
}
</script>

<style scoped>
@import '@/assets/css/mobile.css';

.mobile-list-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.mobile-action-bar {
  padding: 12px 16px;
  background: white;
  display: flex;
  gap: 8px;
  overflow-x: auto;
  border-bottom: 1px solid #ebedf0;
}

.action-btn {
  flex-shrink: 0;
}

.mobile-list-content {
  padding: 12px 0;
}

.custom-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-text {
  font-size: 14px;
  color: #999;
  margin: 0 0 20px 0;
}

.custom-list-container {
  padding: 0 12px;
}

.custom-list-item {
  background: white;
  border-radius: 10px;
  padding: 14px 16px;
  margin-bottom: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  position: relative;
  transition: all 0.2s;
}

.custom-list-item:active {
  transform: scale(0.98);
  background: #f5f5f5;
}

.list-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.list-item-title {
  font-size: 15px;
  font-weight: 600;
  color: #323233;
  flex: 1;
  margin-right: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-item-details {
  margin-bottom: 10px;
}

.detail-row {
  display: flex;
  align-items: baseline;
  margin-bottom: 6px;
  font-size: 13px;
}

.detail-label {
  color: #969799;
  min-width: 70px;
  flex-shrink: 0;
}

.detail-value {
  color: #323233;
  flex: 1;
  word-break: break-all;
}

.list-item-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding-top: 8px;
  border-top: 1px solid #f5f5f5;
  margin-top: 8px;
}

.list-item-arrow {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #c8c9cc;
  font-size: 14px;
}

.custom-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 20px 16px;
}

.pagination-btn {
  padding: 8px 16px;
  border: 1px solid #dcdee0;
  background: white;
  border-radius: 6px;
  font-size: 13px;
  color: #323233;
  transition: all 0.2s;
}

.pagination-btn:active:not(:disabled) {
  background: #f5f5f5;
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 13px;
  color: #969799;
  min-width: 60px;
  text-align: center;
}
</style>
