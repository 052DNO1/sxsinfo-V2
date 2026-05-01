<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="cache-page">
        <div class="page-header">
          <div class="header-left">
            <h1 class="page-title">
              <el-icon><Monitor /></el-icon> 缓存管理中心
            </h1>
            <span class="page-desc">后端缓存配置管理</span>
          </div>
          <div class="header-right">
            <el-button
              plain
              @click="smartBack"
            >
              返回
            </el-button>
            <el-button
              type="success"
              plain
              :loading="toggleLoading"
              @click="handleToggleAll(true)"
            >
              <el-icon><CircleCheck /></el-icon> 一键开启
            </el-button>
            <el-button
              type="warning"
              plain
              :loading="toggleLoading"
              @click="handleToggleAll(false)"
            >
              <el-icon><CircleClose /></el-icon> 一键关闭
            </el-button>
            <el-button
              type="danger"
              plain
              @click="handleClearAllCache"
            >
              清除所有缓存
            </el-button>
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

        <div class="main-content">
          <div class="section-panel">
            <div class="panel-header">
              <h3><el-icon><Setting /></el-icon> 缓存配置列表</h3>
              <div class="filter-group">
                <el-select
                  v-model="selectedCategory"
                  placeholder="按功能筛选"
                  clearable
                  style="width: 160px;"
                >
                  <el-option
                    label="全部分类"
                    value=""
                  />
                  <el-option
                    v-for="cat in categoryOptions"
                    :key="cat.value"
                    :label="cat.label"
                    :value="cat.value"
                  />
                </el-select>
                <el-input
                  v-model="configSearch"
                  placeholder="搜索API路径..."
                  prefix-icon="Search"
                  clearable
                  style="width: 200px;"
                />
              </div>
            </div>
            
            <div
              v-if="!selectedCategory"
              class="category-groups"
            >
              <div
                v-for="group in groupedConfigs"
                :key="group.category"
                class="category-group"
              >
                <div
                  class="category-header"
                  @click="toggleCategory(group.category)"
                >
                  <div class="category-info">
                    <el-icon
                      class="expand-icon"
                      :class="{ expanded: expandedCategories.includes(group.category) }"
                    >
                      <ArrowRight />
                    </el-icon>
                    <span class="category-name">{{ getCategoryLabel(group.category) }}</span>
                    <el-tag
                      size="small"
                      type="info"
                    >
                      {{ group.items.length }} 条
                    </el-tag>
                  </div>
                  <div class="category-stats">
                    <span class="enabled-count">{{ group.enabledCount }} 启用</span>
                    <span class="disabled-count">{{ group.items.length - group.enabledCount }} 禁用</span>
                  </div>
                </div>
                <div
                  v-show="expandedCategories.includes(group.category)"
                  class="category-content"
                >
                  <div
                    v-for="item in group.items"
                    :key="item.id"
                    class="config-item"
                  >
                    <div class="config-info">
                      <code class="api-path">{{ item.api_path }}</code>
                      <span
                        v-if="item.description"
                        class="config-desc"
                      >{{ item.description }}</span>
                    </div>
                    <div class="config-actions">
                      <div class="ttl-edit">
                        <span>TTL:</span>
                        <el-input-number 
                          v-model="item.backend_ttl" 
                          :min="0" 
                          :max="86400" 
                          :step="60"
                          size="small" 
                          controls-position="right"
                          @change="handleTtlChange(item)"
                        />
                        <span>秒</span>
                      </div>
                      <el-switch
                        v-model="item.enabled"
                        size="small"
                        @change="toggleConfigStatus(item)"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div
              v-else
              class="flat-list"
            >
              <div
                v-for="item in filteredConfigList"
                :key="item.id"
                class="config-item"
              >
                <div class="config-info">
                  <code class="api-path">{{ item.api_path }}</code>
                  <span
                    v-if="item.description"
                    class="config-desc"
                  >{{ item.description }}</span>
                </div>
                <div class="config-actions">
                  <div class="ttl-edit">
                    <span>TTL:</span>
                    <el-input-number 
                      v-model="item.backend_ttl" 
                      :min="0" 
                      :max="86400" 
                      :step="60"
                      size="small" 
                      controls-position="right"
                      @change="handleTtlChange(item)"
                    />
                    <span>秒</span>
                  </div>
                  <el-switch
                    v-model="item.enabled"
                    size="small"
                    @change="toggleConfigStatus(item)"
                  />
                </div>
              </div>
              <el-empty
                v-if="!filteredConfigList.length && !configLoading"
                description="暂无缓存配置"
                :image-size="80"
              />
            </div>

            <div
              v-if="configLoading"
              class="loading-container"
            >
              <el-icon class="is-loading">
                <Loading />
              </el-icon>
              <span>加载中...</span>
            </div>
          </div>
        </div>

        <el-dialog
          v-model="clearCacheDialogVisible"
          title="清除缓存确认"
          width="400px"
          destroy-on-close
        >
          <el-alert
            title="清除后用户需重新获取数据"
            type="warning"
            show-icon
            :closable="false"
            style="margin-bottom: 12px;"
          />
          <el-form
            ref="clearCacheFormRef"
            :model="clearCacheForm"
            label-position="top"
          >
            <el-form-item
              label="操作原因"
              prop="reason"
            >
              <el-input
                v-model="clearCacheForm.reason"
                type="textarea"
                :rows="2"
                placeholder="请输入原因"
              />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="clearCacheDialogVisible = false">
              取消
            </el-button>
            <el-button
              type="danger"
              :loading="clearLoading"
              @click="confirmClearCache"
            >
              确认清除
            </el-button>
          </template>
        </el-dialog>
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
import { Monitor, Setting, ArrowRight, Loading, CircleCheck, CircleClose } from '@element-plus/icons-vue'

export default {
  name: 'CacheConfig',
  components: {
    Index,
    Monitor, Setting, ArrowRight, Loading, CircleCheck, CircleClose
  },
  setup() {
    const { smartBack } = useNavigation()
    const { get, post, put } = useApi()

    const configSearch = ref('')
    const selectedCategory = ref('')
    const expandedCategories = ref([])

    const configLoading = ref(false)
    const clearLoading = ref(false)
    const toggleLoading = ref(false)

    const overview = ref({ today_stats: {}, config_stats: {}, category_stats: [], recent_logs: [], top_apis: [] })
    const configList = ref([])

    const clearCacheDialogVisible = ref(false)
    const clearCacheFormRef = ref(null)
    const clearCacheForm = reactive({ api_path: '', reason: '' })

    const categoryOptions = [
      { value: 'schedules', label: '日程管理' },
      { value: 'laboratories', label: '实训室管理' },
      { value: 'equipments', label: '设备管理' },
      { value: 'records', label: '使用记录' },
      { value: 'work_orders', label: '工单管理' },
      { value: 'users', label: '用户管理' },
      { value: 'departments', label: '部门管理' },
      { value: 'semesters', label: '学期管理' },
      { value: 'notifications', label: '通知管理' },
      { value: 'ai', label: 'AI助手' },
      { value: 'backups', label: '数据备份' },
      { value: 'statistics', label: '统计分析' },
      { value: 'common', label: '公共功能' },
      { value: 'other', label: '其他' },
    ]

    const getCategoryLabel = (category) => {
      const found = categoryOptions.find(c => c.value === category)
      return found ? found.label : category
    }

    const filteredConfigList = computed(() => {
      let list = configList.value || []
      if (selectedCategory.value) {
        list = list.filter(item => (item.category || 'other') === selectedCategory.value)
      }
      if (configSearch.value) {
        const search = configSearch.value.toLowerCase()
        list = list.filter(item => 
          item.api_path?.toLowerCase().includes(search) ||
          (item.description && item.description.toLowerCase().includes(search))
        )
      }
      return list
    })

    const groupedConfigs = computed(() => {
      const groups = {}
      ;(configList.value || []).forEach(item => {
        const cat = item.category || 'other'
        if (!groups[cat]) {
          groups[cat] = {
            category: cat,
            items: [],
            enabledCount: 0
          }
        }
        groups[cat].items.push(item)
        if (item.enabled) {
          groups[cat].enabledCount++
        }
      })
      
      const sortedGroups = Object.values(groups).sort((a, b) => {
        const orderA = categoryOptions.findIndex(c => c.value === a.category)
        const orderB = categoryOptions.findIndex(c => c.value === b.category)
        return orderA - orderB
      })
      
      return sortedGroups
    })

    const toggleCategory = (category) => {
      const idx = expandedCategories.value.indexOf(category)
      if (idx === -1) {
        expandedCategories.value.push(category)
      } else {
        expandedCategories.value.splice(idx, 1)
      }
    }

    const loadOverview = async () => {
      try {
        const res = await get({}, { url: '/cache-config/overview/' })
        if (res?.data) overview.value = res.data
      } catch (e) {}
    }

    const loadConfigList = async () => {
      configLoading.value = true
      try {
        const res = await get({}, { url: '/cache-config/configs/' })
        if (res?.data) {
          configList.value = Array.isArray(res.data) ? res.data : (res.data.results || res.data.list || [])
        } else {
          configList.value = Array.isArray(res) ? res : (res?.results || res?.list || [])
        }
      } catch (e) {} finally { configLoading.value = false }
    }

    const toggleConfigStatus = async (row) => {
      try {
        await put({ enabled: row.enabled }, { url: `/cache-config/configs/${row.id}/` })
        ElMessage.success(`已${row.enabled ? '启用' : '禁用'}缓存`)
        loadOverview()
      } catch (e) { 
        row.enabled = !row.enabled
        ElMessage.error('操作失败') 
      }
    }

    const handleTtlChange = async (row) => {
      try {
        await put({ backend_ttl: row.backend_ttl }, { url: `/cache-config/configs/${row.id}/` })
        ElMessage.success('TTL已更新')
      } catch (e) { 
        ElMessage.error('更新失败') 
      }
    }

    const handleToggleAll = async (enabled) => {
      const action = enabled ? '开启' : '关闭'
      try {
        await ElMessageBox.confirm(
          `确定要${action}所有缓存配置吗？`,
          '确认操作',
          { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
        )
        
        toggleLoading.value = true
        const res = await post({ enabled }, { url: '/cache-config/batch-toggle/' })
        ElMessage.success(res.message || `已${action}所有缓存`)
        await loadConfigList()
        loadOverview()
      } catch (e) {
        if (e !== 'cancel') {
          ElMessage.error(e.message || '操作失败')
        }
      } finally {
        toggleLoading.value = false
      }
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
      } catch (e) { ElMessage.error(e.message || '清除失败') }
      finally { clearLoading.value = false }
    }

    onMounted(async () => {
      loadOverview()
      await loadConfigList()
      expandedCategories.value = groupedConfigs.value.slice(0, 3).map(g => g.category)
    })

    return {
      smartBack, configSearch, selectedCategory, expandedCategories,
      configLoading, clearLoading, toggleLoading,
      overview, configList,
      clearCacheDialogVisible, clearCacheFormRef, clearCacheForm,
      categoryOptions, filteredConfigList, groupedConfigs,
      loadOverview, loadConfigList,
      toggleConfigStatus, handleTtlChange, handleToggleAll, handleClearAllCache, confirmClearCache,
      getCategoryLabel, toggleCategory
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

.filter-group {
  display: flex;
  gap: 12px;
  align-items: center;
}

.category-groups {
  padding: 12px 0;
}

.category-group {
  border-bottom: 1px solid #f0f0f0;
}

.category-group:last-child {
  border-bottom: none;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  cursor: pointer;
  transition: background 0.2s;
}

.category-header:hover {
  background: #f5f7fa;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.expand-icon {
  transition: transform 0.2s;
  color: #909399;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.category-name {
  font-weight: 500;
  color: #303133;
}

.category-stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
}

.enabled-count {
  color: #67c23a;
}

.disabled-count {
  color: #909399;
}

.category-content {
  background: #fafafa;
  border-top: 1px solid #f0f0f0;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 18px 10px 36px;
  border-bottom: 1px solid #f5f5f5;
  transition: background 0.2s;
}

.config-item:hover {
  background: #fff;
}

.config-item:last-child {
  border-bottom: none;
}

.config-info {
  flex: 1;
  min-width: 0;
}

.api-path {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  color: #409eff;
  font-family: 'Monaco', 'Menlo', monospace;
}

.config-desc {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.config-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.ttl-edit {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #606266;
}

.ttl-edit :deep(.el-input-number) {
  width: 100px;
}

.ttl-edit :deep(.el-input-number .el-input__inner) {
  text-align: center;
}

.flat-list {
  padding: 12px 0;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: #909399;
}

@media (max-width: 1200px) {
  .stats-overview { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 800px) {
  .stats-overview { grid-template-columns: repeat(2, 1fr); }
  .page-header { flex-direction: column; gap: 12px; align-items: flex-start; }
  .header-right { width: 100%; flex-wrap: wrap; }
  .filter-group { flex-direction: column; width: 100%; }
}
</style>
