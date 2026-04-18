<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="cache-page">
        <div class="page-header">
          <div class="header-left">
            <h1 class="page-title"><el-icon><Monitor /></el-icon> 缓存管理中心</h1>
            <span class="page-desc">实时监控API请求，动态调整缓存策略</span>
          </div>
          <div class="header-right">
            <el-button plain @click="smartBack">返回</el-button>
            <el-button type="success" plain :loading="autoDiscovering" @click="handleRefreshApis">
              <el-icon><Refresh /></el-icon> 刷新API列表
            </el-button>
            <el-button type="danger" plain @click="handleClearAllCache">清除所有缓存</el-button>
          </div>
        </div>

        <div class="stats-overview">
          <div class="stat-card">
            <span class="stat-number">{{ overview.today_stats?.total_requests || 0 }}</span>
            <span class="stat-label">今日总请求</span>
          </div>
          <div class="stat-card">
            <span class="stat-number highlight">{{ overview.today_stats?.cache_hit_rate || 0 }}%</span>
            <span class="stat-label">缓存命中率</span>
          </div>
          <div class="stat-card">
            <span class="stat-number">{{ overview.today_stats?.avg_response_time || 0 }}<small>ms</small></span>
            <span class="stat-label">平均响应时间</span>
          </div>
          <div class="stat-card">
            <span class="stat-number">{{ overview.config_stats?.enabled || 0 }}<small>/{{ overview.config_stats?.total || 0 }}</small></span>
            <span class="stat-label">启用配置</span>
          </div>
          <div class="stat-card error">
            <span class="stat-number">{{ overview.today_stats?.total_errors || 0 }}</span>
            <span class="stat-label">错误请求</span>
          </div>
        </div>

        <div class="sub-panels">
          <div class="section-panel sub-panel">
            <div class="panel-header">
              <h3><el-icon><TrendCharts /></el-icon> 热门 API TOP 5</h3>
            </div>
            <div class="top-list compact">
              <div v-for="(api, index) in (overview.top_apis || [])" :key="api.api_path" class="top-item">
                <span class="rank-badge" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
                <div class="top-info">
                  <span class="top-path">{{ truncatePath(api.api_path) }}</span>
                  <span class="top-meta">{{ api.request_count }} 次</span>
                </div>
              </div>
              <el-empty v-if="!overview.top_apis?.length" description="暂无数据" :image-size="40" />
            </div>
          </div>

          <div class="section-panel sub-panel">
            <div class="panel-header">
              <h3><el-icon><Document /></el-icon> 最近操作</h3>
              <el-button link size="small" @click="showAllLogs = true">全部</el-button>
            </div>
            <div class="log-list compact">
              <div v-for="log in (overview.recent_logs || []).slice(0, 5)" :key="log.id" class="log-item">
                <span class="log-type-tag" :class="getLogTypeClass(log.operation_type)">{{ log.operation_type_display }}</span>
                <div class="log-detail">
                  <span class="log-api" v-if="log.api_path">{{ truncatePath(log.api_path) }}</span>
                  <span class="log-time">{{ formatTime(log.created_at) }}</span>
                </div>
              </div>
              <el-empty v-if="!(overview.recent_logs || []).length" description="暂无记录" :image-size="40" />
            </div>
          </div>
        </div>

        <div class="main-content">
          <div class="section-panel">
            <div class="panel-header">
              <h3><el-icon><Setting /></el-icon> 缓存配置列表</h3>
              <el-input v-model="configSearch" placeholder="搜索API路径..." prefix-icon="Search" clearable size="small" style="width: 200px;" />
            </div>
            <el-table :data="filteredConfigList" v-loading="configLoading" stripe size="default" :row-class-name="tableRowClassName">
              <el-table-column prop="api_path" label="API路径" min-width="200">
                <template #default="{ row }">
                  <code>{{ row.api_path }}</code>
                </template>
              </el-table-column>
              <el-table-column prop="frontend_ttl" label="前端TTL" width="100" align="center">
                <template #default="{ row }">
                  <span class="ttl-text">{{ row.frontend_ttl }}s</span>
                </template>
              </el-table-column>
              <el-table-column prop="backend_ttl" label="后端TTL" width="100" align="center">
                <template #default="{ row }">
                  <span class="ttl-text green">{{ row.backend_ttl }}s</span>
                </template>
              </el-table-column>
              <el-table-column prop="enabled" label="状态" width="80" align="center">
                <template #default="{ row }">
                  <el-switch v-model="row.enabled" @change="toggleConfigStatus(row)" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="160" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" @click="handleEditConfig(row)">编辑</el-button>
                  <el-button link type="warning" @click="handleClearCache(row)">清除</el-button>
                  <el-popconfirm title="确定删除此配置？" @confirm="handleDeleteConfig(row)" confirm-button-text="确定" cancel-button-text="取消">
                    <template #reference>
                      <el-button link type="danger">删除</el-button>
                    </template>
                  </el-popconfirm>
                </template>
              </el-table-column>
            </el-table>
            <div class="table-pagination" v-if="configTotal > 0">
              <el-pagination
                v-model:current-page="configPage"
                :page-size="configPageSize"
                :total="configTotal"
                layout="total, sizes, prev, pager, next, jumper"
                :page-sizes="[20, 50, 100]"
                @size-change="handleConfigSizeChange"
                @current-change="loadConfigList"
                background
              />
            </div>
            <div v-if="!filteredConfigList.length && !configLoading" class="empty-box">
              <el-empty description="暂无缓存配置" :image-size="80" />
            </div>
          </div>

          <div class="section-panel">
            <div class="panel-header">
              <h3><el-icon><DataLine /></el-icon> API请求统计</h3>
              <el-date-picker
                v-model="statsDate"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                size="small"
                style="width: 140px;"
                @change="loadApiStats"
              />
            </div>
            <el-table :data="apiStatsList" v-loading="statsLoading" stripe size="default">
              <el-table-column prop="api_path" label="API路径" min-width="180">
                <template #default="{ row }">
                  <code>{{ row.api_path }}</code>
                </template>
              </el-table-column>
              <el-table-column prop="request_count" label="请求数" width="80" align="center" sortable />
              <el-table-column label="命中率" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="getHitRateTagType(calculateHitRate(row.cache_hit_count, row.request_count))" size="small">
                    {{ calculateHitRate(row.cache_hit_count, row.request_count) }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="avg_response_time" label="响应(ms)" width="90" align="center" sortable />
              <el-table-column prop="error_count" label="错误" width="60" align="center">
                <template #default="{ row }">
                  <span :class="{ 'has-error': row.error_count > 0 }">{{ row.error_count }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <el-dialog v-model="configDialogVisible" :title="configForm.id ? '编辑缓存配置' : '新增缓存配置'" width="480px" destroy-on-close>
          <el-form :model="configForm" :rules="configRules" ref="configFormRef" label-position="top">
            <el-form-item label="API 路径" prop="api_path">
              <el-input v-model="configForm.api_path" placeholder="/api/example/" :disabled="!!configForm.id" />
            </el-form-item>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="前端缓存时间(秒)" prop="frontend_ttl">
                  <el-input-number v-model="configForm.frontend_ttl" :min="0" :max="86400" controls-position="right" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="后端缓存时间(秒)" prop="backend_ttl">
                  <el-input-number v-model="configForm.backend_ttl" :min="0" :max="86400" controls-position="right" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="启用状态">
              <el-switch v-model="configForm.enabled" active-text="启用" inactive-text="禁用" />
            </el-form-item>
            <el-form-item label="说明">
              <el-input v-model="configForm.description" type="textarea" :rows="2" placeholder="可选" />
            </el-form-item>
            <el-divider content-position="left">操作信息</el-divider>
            <el-form-item label="操作原因" prop="reason">
              <el-input v-model="configForm.reason" type="textarea" :rows="2" placeholder="请填写操作原因" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="configDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleSaveConfig" :loading="saveLoading">保存</el-button>
          </template>
        </el-dialog>

        <el-dialog v-model="clearCacheDialogVisible" title="清除缓存确认" width="400px" destroy-on-close>
          <el-alert title="清除后用户需重新获取数据" type="warning" show-icon :closable="false" style="margin-bottom: 12px;" />
          <el-form :model="clearCacheForm" ref="clearCacheFormRef" label-position="top">
            <el-form-item label="目标 API">
              <el-input v-model="clearCacheForm.api_path" placeholder="留空则清除所有缓存" />
            </el-form-item>
            <el-form-item label="操作原因" prop="reason">
              <el-input v-model="clearCacheForm.reason" type="textarea" :rows="2" placeholder="请输入原因" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="clearCacheDialogVisible = false">取消</el-button>
            <el-button type="danger" @click="confirmClearCache" :loading="clearLoading">确认清除</el-button>
          </template>
        </el-dialog>

        <el-drawer v-model="showAllLogs" title="操作日志" direction="rtl" size="480px">
          <template #header>
            <div class="drawer-title-row">
              <span>操作日志</span>
              <el-select v-model="logFilter.operation_type" placeholder="筛选类型" clearable size="small" style="width: 130px;">
                <el-option label="全部" value="" />
                <el-option label="创建配置" value="config_create" />
                <el-option label="更新配置" value="config_update" />
                <el-option label="删除配置" value="config_delete" />
                <el-option label="清除缓存" value="cache_clear" />
                <el-option label="清除全部" value="cache_clear_all" />
              </el-select>
            </div>
          </template>
          <el-table :data="operationLogs" v-loading="logsLoading" size="small">
            <el-table-column prop="operator_name" label="操作人" width="75" />
            <el-table-column prop="operation_type_display" label="类型" width="85" />
            <el-table-column prop="api_path" label="API路径" min-width="130" show-overflow-tooltip />
            <el-table-column prop="reason" label="原因" min-width="110" show-overflow-tooltip />
            <el-table-column prop="ip_address" label="IP" width="100" />
            <el-table-column prop="created_at" label="时间" width="145" />
          </el-table>
        </el-drawer>
      </div>
    </template>
  </Index>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import Index from '@/views/pc/dashboard/Index.vue'
import { useNavigation } from '@/core/utils/routeDecision'
import { useApi } from '@/core/hooks'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Monitor, Setting, DataLine, TrendCharts, Document,
  Connection, CircleCheck, Timer, WarningFilled, Refresh
} from '@element-plus/icons-vue'

export default {
  name: 'CacheConfig',
  components: {
    Index,
    Monitor, Setting, DataLine, TrendCharts, Document,
    Connection, CircleCheck, Timer, WarningFilled, Refresh
  },
  setup() {
    const { goHome, smartBack } = useNavigation()
    const { get, post, put, del } = useApi()

    const configSearch = ref('')
    const statsDate = ref(new Date().toISOString().split('T')[0])
    const showAllLogs = ref(false)

    const configPage = ref(1)
    const configPageSize = ref(20)
    const configTotal = ref(0)

    const configLoading = ref(false)
    const statsLoading = ref(false)
    const logsLoading = ref(false)
    const saveLoading = ref(false)
    const clearLoading = ref(false)
    const autoDiscovering = ref(false)

    const overview = ref({ today_stats: {}, config_stats: {}, recent_logs: [], top_apis: [] })
    const configList = ref([])
    const apiStatsList = ref([])
    const operationLogs = ref([])

    const configDialogVisible = ref(false)
    const clearCacheDialogVisible = ref(false)
    const configFormRef = ref(null)
    const clearCacheFormRef = ref(null)

    const configForm = reactive({
      id: null, api_path: '', frontend_ttl: 60, backend_ttl: 300,
      enabled: true, description: '', reason: ''
    })

    const clearCacheForm = reactive({ api_path: '', reason: '' })
    const logFilter = reactive({ operation_type: '' })

    const configRules = {
      api_path: [{ required: true, message: '请输入API路径', trigger: 'blur' }],
      reason: [{ required: true, message: '请填写操作原因', trigger: 'blur' }]
    }

    const filteredConfigList = computed(() => {
      if (!configSearch.value) return configList.value
      return configList.value.filter(item => item.api_path.toLowerCase().includes(configSearch.value.toLowerCase()))
    })

    const loadOverview = async () => {
      try {
        const res = await get({}, { url: '/cache-config/overview/' })
        if (res?.data) overview.value = res.data
      } catch (e) {}
    }

    const loadConfigList = async () => {
      configLoading.value = true
      try {
        const res = await get({}, { 
          url: '/cache-config/configs/',
          params: { page: configPage.value, page_size: configPageSize.value }
        })
        if (res?.data) {
          configList.value = res.data.list || []
          configTotal.value = res.data.pagination?.total || 0
        } else {
          configList.value = res?.results || (Array.isArray(res) ? res : [])
          configTotal.value = res?.count || configList.value.length
        }
      } catch (e) {} finally { configLoading.value = false }
    }

    const handleConfigSizeChange = (val) => {
      configPageSize.value = val
      configPage.value = 1
      loadConfigList()
    }

    const loadApiStats = async () => {
      statsLoading.value = true
      try {
        const res = await get({}, { url: '/cache-config/stats/ranking/', params: { date: statsDate.value, limit: 20 } })
        apiStatsList.value = res?.data ? (Array.isArray(res.data) ? res.data : []) : []
      } catch (e) {} finally { statsLoading.value = false }
    }

    const loadOperationLogs = async () => {
      logsLoading.value = true
      try {
        const params = {}
        if (logFilter.operation_type) params.operation_type = logFilter.operation_type
        const res = await get({}, { url: '/cache-config/logs/', params })
        operationLogs.value = res?.data ? (res.data.results || (Array.isArray(res.data) ? res.data : [])) : []
      } catch (e) {} finally { logsLoading.value = false }
    }

    const handleAddConfig = () => {
      Object.assign(configForm, { id: null, api_path: '', frontend_ttl: 60, backend_ttl: 300, enabled: true, description: '', reason: '' })
      configDialogVisible.value = true
    }

    const handleEditConfig = (row) => {
      Object.assign(configForm, { id: row.id, api_path: row.api_path, frontend_ttl: row.frontend_ttl, backend_ttl: row.backend_ttl, enabled: row.enabled, description: row.description, reason: '' })
      configDialogVisible.value = true
    }

    const handleSaveConfig = async () => {
      if (!configFormRef.value) return
      await configFormRef.value.validate(async (valid) => {
        if (!valid) return
        saveLoading.value = true
        try {
          if (configForm.id) {
            await put(configForm, { url: `/cache-config/configs/${configForm.id}/` })
            ElMessage.success('配置更新成功')
          } else {
            await post(configForm, { url: '/cache-config/configs/' })
            ElMessage.success('配置创建成功')
          }
          configDialogVisible.value = false
          loadConfigList()
          loadOverview()
        } catch (e) { ElMessage.error(e.message || '操作失败') }
        finally { saveLoading.value = false }
      })
    }

    const toggleConfigStatus = async (row) => {
      try {
        await put({ enabled: row.enabled, reason: `切换${row.enabled ? '启用' : '禁用'}状态` }, { url: `/cache-config/configs/${row.id}/` })
        ElMessage.success(`已${row.enabled ? '启用' : '禁用'} ${row.api_path}`)
        loadOverview()
      } catch (e) { row.enabled = !row.enabled; ElMessage.error('操作失败') }
    }

    const handleDeleteConfig = async (row) => {
      try {
        const { value: reason } = await ElMessageBox.prompt('请输入删除原因', '操作原因', { inputPattern: /.+/, inputErrorMessage: '请输入原因' })
        await del({}, { url: `/cache-config/configs/${row.id}/`, data: { reason } })
        ElMessage.success('配置已删除')
        loadConfigList()
        loadOverview()
      } catch (e) {}
    }

    const handleClearCache = (row) => {
      Object.assign(clearCacheForm, { api_path: row.api_path, reason: '' })
      clearCacheDialogVisible.value = true
    }

    const handleClearAllCache = () => {
      Object.assign(clearCacheForm, { api_path: '', reason: '' })
      clearCacheDialogVisible.value = true
    }

    const confirmClearCache = async () => {
      clearLoading.value = true
      try {
        const res = await post(clearCacheForm, { url: '/cache-config/clear/' })
        ElMessage.success(res.message || '缓存清除成功')
        clearCacheDialogVisible.value = false
        loadOverview()
        loadOperationLogs()
      } catch (e) { ElMessage.error(e.message || '清除失败') }
      finally { clearLoading.value = false }
    }

    const calculateHitRate = (hit, total) => (!total ? 0 : ((hit / total) * 100).toFixed(1))
    const getHitRateTagType = (rate) => rate >= 80 ? 'success' : rate >= 50 ? 'warning' : 'danger'
    const tableRowClassName = ({ row }) => row.enabled ? '' : 'disabled-row'
    const getLogTypeClass = (type) => type.includes('delete') || type.includes('clear') ? 'danger' : type.includes('create') ? 'success' : 'primary'
    const formatTime = (time) => time ? new Date(time).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) : ''
    const truncatePath = (path) => path.length > 22 ? path.substring(0, 19) + '...' : path

    const autoDiscoverApis = async () => {
      try {
        await post({}, { url: '/cache-config/auto-discover/' })
      } catch (e) {}
    }

    const handleRefreshApis = async () => {
      autoDiscovering.value = true
      try {
        const res = await post({}, { url: '/cache-config/auto-discover/' })
        ElMessage.success(res.message || 'API列表已刷新')
        loadConfigList()
        loadOverview()
      } catch (e) {
        ElMessage.error(e.message || '刷新失败')
      } finally {
        autoDiscovering.value = false
      }
    }

    onMounted(async () => {
      await autoDiscoverApis()
      loadOverview()
      loadConfigList()
      loadApiStats()
      loadOperationLogs()
    })

    return {
      goHome, smartBack, configSearch, statsDate, showAllLogs,
      configPage, configPageSize, configTotal,
      configLoading, statsLoading, logsLoading, saveLoading, clearLoading, autoDiscovering,
      overview, configList, apiStatsList, operationLogs,
      configDialogVisible, clearCacheDialogVisible, configFormRef, clearCacheFormRef,
      configForm, clearCacheForm, logFilter, configRules, filteredConfigList,
      loadOverview, loadConfigList, loadApiStats, loadOperationLogs,
      handleAddConfig, handleEditConfig, handleSaveConfig, handleDeleteConfig,
      toggleConfigStatus, handleClearCache, handleClearAllCache, confirmClearCache, handleRefreshApis,
      calculateHitRate, getHitRateTagType, tableRowClassName, getLogTypeClass, formatTime, truncatePath,
      autoDiscoverApis, handleConfigSizeChange
    }
  }
}
</script>

<style scoped>
.cache-page {
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

.header-right { display: flex; gap: 10px; }

.stats-overview {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
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
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1.3;
}

.stat-card .stat-number small {
  font-size: 13px;
  font-weight: 400;
  color: #909399;
  margin-left: 2px;
}

.stat-card .stat-number.highlight { color: #409eff; }
.stat-card.error .stat-number { color: #f56c6c; }

.stat-card .stat-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.main-content {
  display: block;
  width: 100%;
}

.sub-panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
  width: 100%;
}

.sub-panel .top-list,
.sub-panel .log-list { padding: 10px 14px; }

.top-list.compact .top-item { padding: 8px 6px; }
.log-list.compact .log-item { padding: 7px 0; }

.left-section {
  display: flex;
  flex-direction: column;
  width: 100%;
  min-width: 0;
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

.section-panel :deep(.el-table) {
  width: 100% !important;
  table-layout: fixed !important;
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

.left-section .section-panel:last-child { margin-bottom: 0; }

.empty-box { text-align: center; padding: 30px 0; }

.table-pagination {
  display: flex;
  justify-content: center;
  padding: 14px 18px;
  border-top: 1px solid #ebeef5;
}

.ttl-text { font-family: 'SF Mono', Monaco, monospace; font-weight: 500; }
.ttl-text.green { color: #67c23a; }

.has-error { color: #f56c6c; font-weight: 500; }

.top-list { padding: 12px 14px; }

.top-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 8px;
  border-radius: 6px;
  transition: background 0.2s;
}

.top-item:hover { background: #f5f7fa; }

.rank-badge {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.rank-1 { background: #e6a23c; }
.rank-2 { background: #909399; }
.rank-3 { background: #ba9b85; }
.rank-4, .rank-5 { background: #dcdfe6; color: #606266; }

.top-info { flex: 1; min-width: 0; }
.top-path { display: block; font-size: 12px; color: #606266; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.top-meta { display: block; font-size: 11px; color: #c0c4cc; margin-top: 2px; }

.log-list { padding: 10px 14px; }

.log-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.log-item:last-child { border-bottom: none; }

.log-type-tag {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 3px;
  flex-shrink: 0;
  white-space: nowrap;
  line-height: 1.6;
}

.log-type-tag.primary { background: #ecf5ff; color: #409eff; }
.log-type-tag.success { background: #f0f9eb; color: #67c23a; }
.log-type-tag.danger { background: #fef0f0; color: #f56c6c; }

.log-detail { flex: 1; min-width: 0; }
.log-api { display: block; font-size: 12px; color: #606266; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.log-time { display: block; font-size: 11px; color: #c0c4cc; margin-top: 2px; }

.drawer-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

:deep(.disabled-row) { opacity: 0.55; }
:deep(.section-panel code) { background: #f5f7fa; padding: 2px 6px; border-radius: 3px; font-size: 12px; color: #409eff; font-family: 'Monaco', 'Menlo', monospace; }

@media (max-width: 1200px) {
  .stats-overview { grid-template-columns: repeat(3, 1fr); }
  .sub-panels { grid-template-columns: 1fr; }
}

@media (max-width: 800px) {
  .stats-overview { grid-template-columns: repeat(2, 1fr); }
  .page-header { flex-direction: column; gap: 12px; align-items: flex-start; }
  .header-right { width: 100%; flex-wrap: wrap; }
}
</style>
