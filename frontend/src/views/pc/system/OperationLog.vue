<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="operation-log-page">
        <!-- 页面头部 -->
        <div class="page-header">
          <div class="header-left">
            <h1 class="page-title"><el-icon><Document /></el-icon> 系统操作日志</h1>
            <span class="page-desc">查看和管理系统核心操作的审计记录，支持多维度筛选和导出</span>
          </div>
          <div class="header-right">
            <el-button plain @click="smartBack">返回</el-button>
            <el-button type="success" plain :loading="exportLoading" @click="handleExport">
              <el-icon><Download /></el-icon> 导出日志
            </el-button>
            <el-popconfirm
              title="确定要清理历史日志吗？此操作不可恢复！"
              @confirm="handleCleanup"
              confirm-button-text="确定"
              cancel-button-text="取消"
            >
              <template #reference>
                <el-button type="danger" plain>清理历史日志</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>

        <!-- 统计概览 -->
        <div class="stats-overview">
          <div class="stat-card">
            <span class="stat-number">{{ stats.total_count || 0 }}</span>
            <span class="stat-label">总操作数</span>
          </div>
          <div class="stat-card">
            <span class="stat-number highlight">{{ stats.today_count || 0 }}</span>
            <span class="stat-label">今日操作</span>
          </div>
          <div class="stat-card">
            <span class="stat-number success">{{ stats.week_count || 0 }}</span>
            <span class="stat-label">近7天操作</span>
          </div>
        </div>

        <!-- 筛选区域 -->
        <div class="section-panel filter-panel">
          <div class="panel-header">
            <h3><el-icon><Search /></el-icon> 筛选条件</h3>
            <el-button link size="small" @click="resetFilters">重置筛选</el-button>
          </div>
          <el-form :inline="true" :model="filters" class="filter-form">
            <el-form-item label="模块">
              <el-select v-model="filters.module" placeholder="全部模块" clearable style="width: 140px;" @change="handleFilterChange">
                <el-option v-for="item in moduleOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="操作类型">
              <el-select v-model="filters.operation_type" placeholder="全部类型" clearable style="width: 160px;" @change="handleFilterChange">
                <el-option v-for="item in filteredOperationTypes" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="时间范围">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 240px;"
                @change="handleDateChange"
              />
            </el-form-item>
            <el-form-item label="关键词">
              <el-input
                v-model="filters.search"
                placeholder="搜索描述/目标/操作人"
                clearable
                style="width: 200px;"
                prefix-icon="Search"
                @clear="handleFilterChange"
                @keyup.enter="handleFilterChange"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleFilterChange"><el-icon><Search /></el-icon> 查询</el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 日志列表 -->
        <div class="section-panel">
          <div class="panel-header">
            <h3><el-icon><List /></el-icon> 操作日志列表</h3>
            <span class="list-info">共 {{ pagination.total }} 条记录</span>
          </div>
          
          <el-table 
            :data="logList" 
            v-loading="tableLoading" 
            stripe 
            size="default"
            :row-class-name="getRowClassName"
            @row-click="handleRowClick"
          >
            <el-table-column prop="created_at" label="操作时间" width="165" sortable>
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
            
            <el-table-column prop="operator_username" label="操作人" width="100">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ row.operator_username || '系统' }}</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="module_display" label="模块" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="getModuleTagType(row.module)">{{ row.module_display }}</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="operation_type_display" label="操作类型" width="120">
              <template #default="{ row }">
                <el-tag size="small" :type="getOperationTypeTagType(row.operation_type)">
                  {{ row.operation_type_display }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="target_name" label="目标对象" min-width="150" show-overflow-tooltip>
              <template #default="{ row }">
                <span v-if="row.target_name">{{ row.target_name }}</span>
                <span v-else class="text-muted">-</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="description" label="操作描述" min-width="250" show-overflow-tooltip>
              <template #default="{ row }">
                <span>{{ row.description || '-' }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="ip_address" label="IP地址" width="130">
              <template #default="{ row }">
                <span v-if="row.ip_address">{{ row.ip_address }}</span>
                <span v-else class="text-muted">-</span>
              </template>
            </el-table-column>
            
            <el-table-column label="详情" width="80" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click.stop="showDetail(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div class="table-pagination" v-if="pagination.total > 0">
            <el-pagination
              v-model:current-page="pagination.page"
              :page-size="pagination.pageSize"
              :total="pagination.total"
              layout="total, sizes, prev, pager, next, jumper"
              :page-sizes="[20, 50, 100, 200]"
              @size-change="handleSizeChange"
              @current-change="loadLogList"
              background
            />
          </div>

          <!-- 空状态 -->
          <div v-if="!logList.length && !tableLoading" class="empty-box">
            <el-empty description="暂无操作日志记录" :image-size="80" />
          </div>
        </div>

        <!-- 详情对话框 -->
        <el-dialog v-model="detailVisible" title="操作日志详情" width="600px" destroy-on-close>
          <el-descriptions :column="2" border v-if="currentLog">
            <el-descriptions-item label="操作时间">{{ formatDateTime(currentLog.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="操作人">{{ currentLog.operator_username || '系统' }}</el-descriptions-item>
            <el-descriptions-item label="模块">{{ currentLog.module_display }}</el-descriptions-item>
            <el-descriptions-item label="操作类型">
              <el-tag :type="getOperationTypeTagType(currentLog.operation_type)" size="small">
                {{ currentLog.operation_type_display }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="目标对象">{{ currentLog.target_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="目标ID">{{ currentLog.target_id || '-' }}</el-descriptions-item>
            <el-descriptions-item label="IP地址" :span="2">{{ currentLog.ip_address || '-' }}</el-descriptions-item>
            <el-descriptions-item label="操作描述" :span="2">{{ currentLog.description || '-' }}</el-descriptions-item>
          </el-descriptions>

          <div v-if="currentLog?.detail" class="detail-section">
            <el-divider content-position="left">详细信息 (修改前后对比)</el-divider>
            <div class="detail-json">
              <pre>{{ JSON.stringify(currentLog.detail, null, 2) }}</pre>
            </div>
          </div>

          <template #footer>
            <el-button @click="detailVisible = false">关闭</el-button>
          </template>
        </el-dialog>

        <!-- 清理确认对话框 -->
        <el-dialog v-model="cleanupVisible" title="清理历史日志" width="400px" destroy-on-close>
          <el-alert title="警告：此操作将永久删除历史日志！" type="warning" show-icon :closable="false" style="margin-bottom: 16px;" />
          <el-form :model="cleanupForm" label-position="top">
            <el-form-item label="保留最近多少天的日志？">
              <el-input-number v-model="cleanupForm.days" :min="30" :max="365" :step="30" controls-position-right style="width: 100%;" />
              <div class="form-tip">建议保留至少 90 天的日志用于审计</div>
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="cleanupVisible = false">取消</el-button>
            <el-button type="danger" :loading="cleanupLoading" @click="confirmCleanup">确认清理</el-button>
          </template>
        </el-dialog>
      </div>
    </template>
  </Index>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import Index from '@/views/pc/dashboard/Index.vue'
import { useNavigation } from '@/core/utils/routeDecision'
import { useApi } from '@/core/hooks'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document, Search, List, Download,
  View, Delete
} from '@element-plus/icons-vue'

export default {
  name: 'OperationLog',
  components: {
    Index,
    Document, Search, List, Download,
    View, Delete
  },
  setup() {
    const { goHome, smartBack } = useNavigation()
    const { get, del } = useApi()

    // 统计数据
    const stats = ref({
      total_count: 0,
      today_count: 0,
      week_count: 0
    })

    // 筛选条件
    const filters = reactive({
      module: '',
      operation_type: '',
      search: ''
    })
    
    const dateRange = ref(null)

    // 分页
    const pagination = reactive({
      page: 1,
      pageSize: 20,
      total: 0
    })

    // 数据状态
    const logList = ref([])
    const tableLoading = ref(false)
    const exportLoading = ref(false)
    const cleanupLoading = ref(false)
    
    // 对话框
    const detailVisible = ref(false)
    const cleanupVisible = ref(false)
    const currentLog = ref(null)
    
    const cleanupForm = reactive({ days: 90 })

    // 模块选项
    const moduleOptions = [
      { value: 'user', label: '用户管理' },
      { value: 'equipment', label: '设备管理' },
      { value: 'schedule', label: '课表管理' },
      { value: 'cache_config', label: '缓存配置' },
      { value: 'department', label: '部门管理' },
      { value: 'laboratory', label: '实训室管理' },
      { value: 'backup', label: '备份管理' },
      { value: 'system', label: '系统设置' }
    ]

    // 操作类型选项
    const operationTypeOptions = [
      // 用户管理
      { value: 'user_create', label: '创建用户', module: 'user' },
      { value: 'user_delete', label: '删除用户', module: 'user' },
      { value: 'user_update', label: '更新用户', module: 'user' },
      { value: 'user_role_update', label: '更新用户权限', module: 'user' },
      { value: 'user_batch_delete', label: '批量删除用户', module: 'user' },
      { value: 'user_import', label: '导入用户', module: 'user' },
      { value: 'user_activate', label: '启用/禁用用户', module: 'user' },
      // 设备管理
      { value: 'equipment_create', label: '添加设备', module: 'equipment' },
      { value: 'equipment_delete', label: '删除设备', module: 'equipment' },
      { value: 'equipment_update', label: '更新设备', module: 'equipment' },
      { value: 'equipment_batch_delete', label: '批量删除设备', module: 'equipment' },
      // 课表管理
      { value: 'schedule_create', label: '添加课表', module: 'schedule' },
      { value: 'schedule_delete', label: '删除课表', module: 'schedule' },
      { value: 'schedule_update', label: '更新课表', module: 'schedule' },
      // 缓存配置
      { value: 'cache_config_create', label: '创建缓存配置', module: 'cache_config' },
      { value: 'cache_config_delete', label: '删除缓存配置', module: 'cache_config' },
      { value: 'cache_config_update', label: '更新缓存配置', module: 'cache_config' },
      { value: 'cache_clear', label: '清除缓存', module: 'cache_config' },
      // 部门管理
      { value: 'department_create', label: '创建部门', module: 'department' },
      { value: 'department_update', label: '更新部门', module: 'department' },
      { value: 'department_delete', label: '删除部门', module: 'department' },
      // 实训室管理
      { value: 'laboratory_create', label: '创建实训室', module: 'laboratory' },
      { value: 'laboratory_update', label: '更新实训室', module: 'laboratory' },
      { value: 'laboratory_delete', label: '删除实训室', module: 'laboratory' },
      // 备份管理
      { value: 'backup_create', label: '创建备份', module: 'backup' },
      { value: 'backup_delete', label: '删除备份', module: 'backup' },
      { value: 'backup_restore', label: '恢复备份', module: 'backup' },
      // 系统设置
      { value: 'system_setting_update', label: '更新系统设置', module: 'system' }
    ]

    // 根据选择的模块过滤操作类型
    const filteredOperationTypes = computed(() => {
      if (!filters.module) return operationTypeOptions
      return operationTypeOptions.filter(opt => opt.module === filters.module)
    })

    // 加载统计数据
    const loadStats = async () => {
      try {
        const res = await get({}, { url: '/operation-logs/stats/' })
        if (res?.data) {
          stats.value = res.data
        }
      } catch (e) {
        console.error('加载统计失败:', e)
      }
    }

    // 加载日志列表
    const loadLogList = async () => {
      tableLoading.value = true
      try {
        const params = {
          page: pagination.page,
          page_size: pagination.pageSize
        }

        if (filters.module) params.module = filters.module
        if (filters.operation_type) params.operation_type = filters.operation_type
        if (filters.search) params.search = filters.search
        
        if (dateRange.value && dateRange.value.length === 2) {
          params.start_date = dateRange.value[0]
          params.end_date = dateRange.value[1]
        }

        const res = await get({}, { url: '/operation-logs/', params })
        
        if (res?.data) {
          logList.value = res.data.list || []
          pagination.total = res.data.pagination?.total || 0
        }
      } catch (e) {
        console.error('加载日志失败:', e)
        ElMessage.error('加载日志失败')
      } finally {
        tableLoading.value = false
      }
    }

    // 筛选变化处理
    const handleFilterChange = () => {
      pagination.page = 1
      loadLogList()
    }

    // 日期范围变化
    const handleDateChange = () => {
      handleFilterChange()
    }

    // 重置筛选
    const resetFilters = () => {
      Object.assign(filters, {
        module: '',
        operation_type: '',
        search: ''
      })
      dateRange.value = null
      pagination.page = 1
      loadLogList()
    }

    // 分页大小变化
    const handleSizeChange = (val) => {
      pagination.pageSize = val
      pagination.page = 1
      loadLogList()
    }

    // 显示详情
    const showDetail = async (row) => {
      try {
        const res = await get({}, { url: `/operation-logs/${row.id}/` })
        if (res?.data) {
          currentLog.value = res.data
          detailVisible.value = true
        }
      } catch (e) {
        ElMessage.error('获取详情失败')
      }
    }

    // 行点击
    const handleRowClick = (row) => {
      showDetail(row)
    }

    // 导出日志
    const handleExport = async () => {
      exportLoading.value = true
      try {
        const params = {}
        if (filters.module) params.module = filters.module
        if (filters.operation_type) params.operation_type = filters.operation_type
        if (pagination.pageSize) params.limit = Math.min(pagination.pageSize * pagination.page, 10000)
        
        const response = await fetch(`/api/v1/operation-logs/export/?${new URLSearchParams(params).toString()}`, {
          headers: {
            'Authorization': `Bearer ${sessionStorage.getItem('access_token')}`
          }
        })
        
        if (response.ok) {
          const blob = await response.blob()
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `操作日志_${new Date().toISOString().split('T')[0]}.csv`
          document.body.appendChild(a)
          a.click()
          window.URL.revokeObjectURL(url)
          document.body.removeChild(a)
          ElMessage.success('导出成功')
        } else {
          throw new Error('导出失败')
        }
      } catch (e) {
        ElMessage.error(e.message || '导出失败')
      } finally {
        exportLoading.value = false
      }
    }

    // 清理历史日志
    const handleCleanup = () => {
      cleanupForm.days = 90
      cleanupVisible.value = true
    }

    const confirmCleanup = async () => {
      cleanupLoading.value = true
      try {
        await del({ days: cleanupForm.days }, { url: '/operation-logs/cleanup/' })
        ElMessage.success(`已清理 ${cleanupForm.days} 天前的历史日志`)
        cleanupVisible.value = false
        loadStats()
        loadLogList()
      } catch (e) {
        ElMessage.error(e.message || '清理失败')
      } finally {
        cleanupLoading.value = false
      }
    }

    // 格式化日期时间
    const formatDateTime = (datetime) => {
      if (!datetime) return '-'
      const date = new Date(datetime)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }

    // 获取模块标签类型
    const getModuleTagType = (module) => {
      const typeMap = {
        'user': 'primary',
        'equipment': 'success',
        'schedule': 'warning',
        'cache_config': 'info',
        'department': '',
        'laboratory': 'success',
        'backup': 'info',
        'system': 'danger'
      }
      return typeMap[module] || 'info'
    }

    // 获取操作类型标签类型
    const getOperationTypeTagType = (operationType) => {
      if (operationType.includes('delete')) return 'danger'
      if (operationType.includes('create')) return 'success'
      if (operationType.includes('update')) return 'warning'
      if (operationType.includes('clear')) return 'danger'
      return 'info'
    }

    // 行样式
    const getRowClassName = ({ row }) => {
      if (row.operation_type.includes('delete')) return 'danger-row'
      return ''
    }

    // 初始化
    onMounted(() => {
      loadStats()
      loadLogList()
    })

    return {
      goHome, smartBack, Search,
      stats, filters, dateRange, pagination,
      logList, tableLoading, exportLoading, cleanupLoading,
      detailVisible, cleanupVisible, currentLog, cleanupForm,
      moduleOptions, operationTypeOptions, filteredOperationTypes,
      loadStats, loadLogList, handleFilterChange, handleDateChange,
      resetFilters, handleSizeChange, showDetail, handleRowClick,
      handleExport, handleCleanup, confirmCleanup,
      formatDateTime, getModuleTagType, getOperationTypeTagType,
      getRowClassName
    }
  }
}
</script>

<style scoped>
.operation-log-page {
  padding: 20px 24px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 18px 22px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  width: 100%;
  box-sizing: border-box;
}

.header-left .page-title {
  margin: 0 0 4px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-desc {
  font-size: 13px;
  color: #909399;
  margin-left: 26px;
}

.header-right { 
  display: flex; 
  gap: 10px; 
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  margin-bottom: 20px;
  width: 100%;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px 18px;
  border: 1px solid #e4e7ed;
  text-align: center;
}

.stat-card .stat-number {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.3;
}

.stat-card .stat-number.highlight { 
  color: #409eff; 
}
.stat-card .stat-number.success { 
  color: #67c23a; 
}

.stat-card .stat-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.section-panel {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
  margin-bottom: 20px;
  max-width: 100%;
  min-width: 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  border-bottom: 1px solid #ebeef5;
  background: #fafafa;
}

.panel-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 6px;
}

.list-info {
  font-size: 13px;
  color: #909399;
}

.filter-panel .filter-form {
  padding: 16px 18px;
}

.filter-panel :deep(.el-form-item) {
  margin-bottom: 12px;
}

.section-panel :deep(.el-table) {
  width: 100% !important;
  table-layout: fixed !important;
}

.table-pagination {
  display: flex;
  justify-content: center;
  padding: 14px 18px;
  border-top: 1px solid #ebeef5;
}

.empty-box { 
  text-align: center; 
  padding: 30px 0; 
}

.text-muted {
  color: #c0c4cc;
}

.detail-section {
  margin-top: 16px;
}

.detail-json {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.detail-json pre {
  margin: 0;
  font-family: Monaco, Menlo, monospace;
  font-size: 12px;
  line-height: 1.5;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-all;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

:deep(.danger-row) {
  background-color: #fef0f0 !important;
}

:deep(.el-table__body tr:hover > td.el-table__cell) {
  background-color: #ecf5ff !important;
}

@media (max-width: 1200px) {
  .stats-overview { 
    grid-template-columns: repeat(2, 1fr); 
  }
  .filter-form { 
    flex-wrap: wrap; 
  }
}

@media (max-width: 800px) {
  .stats-overview { 
    grid-template-columns: 1fr; 
  }
  .page-header { 
    flex-direction: column; 
    gap: 12px; 
    align-items: flex-start; 
  }
  .header-right { 
    width: 100%; 
    flex-wrap: wrap; 
  }
}
</style>
