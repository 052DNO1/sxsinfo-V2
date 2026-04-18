<!-- 归档学期列表 -->
<template>
  <Index>
    <template #rightcontent>
      <div class="archive-page">
        <div class="page-header">
          <div class="header-content">
            <div class="header-icon">
              <el-icon :size="28"><FolderOpened /></el-icon>
            </div>
            <div class="header-text">
              <h1>归档记录列表</h1>
              <p class="header-desc">查看历史学期归档数据</p>
            </div>
          </div>
          <div class="header-actions">
            <el-button v-if="user?.is_superuser" type="warning" plain @click="openSettings">
              <el-icon><Setting /></el-icon>
              归档设置
            </el-button>
            <el-button v-if="user?.is_superuser" type="danger" plain @click="manualCleanup" :loading="cleanupLoading">
              {{ cleanupLoading ? '清理中...' : '立即清理' }}
            </el-button>
            <el-button v-if="showBackButton" plain :icon="Back" @click="smartBack">返回</el-button>
            <el-button plain :icon="HomeFilled" @click="goHome">首页</el-button>
          </div>
        </div>

        <el-dialog
          v-model="settingsVisible"
          title="归档自动清理设置"
          width="500px"
          destroy-on-close
        >
          <div class="settings-content">
            <el-alert
              title="自动清理说明"
              type="info"
              :closable="false"
              description="系统将根据设置的保留时间，自动清理过期的归档学期数据。设置为0表示永久保留。"
              show-icon
              style="margin-bottom: 20px;"
            />
            
            <el-form label-position="top">
              <el-form-item label="归档保留时间（月）">
                <el-input-number 
                  v-model="retentionMonths" 
                  :min="0" 
                  :max="120" 
                  style="width: 100%;"
                />
                <div class="form-tip">当前设置：{{ retentionText }}</div>
              </el-form-item>
            </el-form>
          </div>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="settingsVisible = false">取消</el-button>
              <el-button type="primary" @click="saveSettings" :loading="saving">
                保存设置
              </el-button>
            </span>
          </template>
        </el-dialog>

        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>
        
        <div v-else-if="archivedTerms && archivedTerms.length > 0" class="archive-content">
          <div class="terms-grid">
            <div
              v-for="(termData, index) in archivedTerms"
              :key="termData.id || index"
              class="term-card"
            >
              <div class="term-card-header">
                <div class="term-title-row">
                  <h3 class="term-name">{{ termData.name }}</h3>
                  <el-tag type="success" size="small">已归档</el-tag>
                </div>
                <div class="term-dates">
                  <div class="date-item">
                    <el-icon :size="14"><Calendar /></el-icon>
                    <span>{{ formatDate(termData.start_date) }} ~ {{ formatDate(termData.end_date) }}</span>
                  </div>
                </div>
              </div>

              <div class="term-stats">
                <div class="stat-item">
                  <div class="stat-icon">
                    <el-icon :size="18"><Document /></el-icon>
                  </div>
                  <div class="stat-info">
                    <span class="stat-value">{{ termData.stats?.record_count || 0 }}</span>
                    <span class="stat-label">使用记录</span>
                  </div>
                </div>
                <div class="stat-item">
                  <div class="stat-icon">
                    <el-icon :size="18"><Tools /></el-icon>
                  </div>
                  <div class="stat-info">
                    <span class="stat-value">{{ termData.stats?.maintain_count || 0 }}</span>
                    <span class="stat-label">维护记录</span>
                  </div>
                </div>
                <div class="stat-item">
                  <div class="stat-icon">
                    <el-icon :size="18"><Reading /></el-icon>
                  </div>
                  <div class="stat-info">
                    <span class="stat-value">{{ termData.stats?.class_count || 0 }}</span>
                    <span class="stat-label">课表记录</span>
                  </div>
                </div>
                <div class="stat-item">
                  <div class="stat-icon">
                    <el-icon :size="18"><Warning /></el-icon>
                  </div>
                  <div class="stat-info">
                    <span class="stat-value">{{ termData.stats?.equipment_maintenance_count || 0 }}</span>
                    <span class="stat-label">故障工单</span>
                  </div>
                </div>
              </div>

              <div class="term-actions">
                <el-button type="primary" @click="viewArchivedRecords(termData)">
                  <el-icon><View /></el-icon>
                  查看记录
                </el-button>
                <el-button type="success" plain @click="handleExport(termData.id, termData.name)">
                  <el-icon><Download /></el-icon>
                  导出Excel
                </el-button>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-state">
          <el-empty description="暂无归档记录" />
        </div>
      </div>
    </template>
  </Index>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi, useAuth } from '@/core/hooks'
import Index from '@/views/pc/dashboard/Index.vue'
import { useNavigation } from '@/core/utils/routeDecision'
import { formatDateChinese } from '@/core/utils/format'
import { showError, showSuccess, showConfirm } from '@/core/utils/errorHandler'
import { handleExportFromResponse } from '@/core/utils/io'
import { 
  Setting, Back, HomeFilled, FolderOpened, Calendar, Document, 
  Tools, Reading, Warning, View, Download
} from '@element-plus/icons-vue'

export default {
  name: 'ArchivedTermList',
  components: {
    Index,
    Setting, Back, HomeFilled, FolderOpened, Calendar, Document, 
    Tools, Reading, Warning, View, Download
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const { user } = useAuth()
    const { smartBack, goHome } = useNavigation()
    
    const { get: fetchArchiveDataApi } = useApi('/semesters/', { immediate: false })
    const { get: fetchSettingsApi, post: saveSettingsApi } = useApi('/schedules/archive-settings/', { immediate: false })
    const { post: manualCleanupApi } = useApi('/schedules/manual-cleanup/', { immediate: false })
    const { get: exportArchiveApi } = useApi('', { immediate: false })
    
    const formatDate = formatDateChinese
    
    const archivedTerms = ref([])
    const loading = ref(false)
    
    const settingsVisible = ref(false)
    const retentionMonths = ref(0)
    const saving = ref(false)
    
    const retentionText = computed(() => {
      if (retentionMonths.value === 0) return '永久保留（不自动清理）'
      return `保留最多 ${retentionMonths.value} 个月的数据`
    })

    const openSettings = async () => {
      settingsVisible.value = true
      try {
        const res = await fetchSettingsApi()
        if (res.success) {
          retentionMonths.value = res.retention_months || 0
        }
      } catch (err) {
      }
    }

    const saveSettings = async () => {
      saving.value = true
      try {
        const res = await saveSettingsApi({ retention_months: retentionMonths.value })
        if (res.success) {
          showSuccess(res.message || '设置保存成功')
          settingsVisible.value = false
          loadData()
        } else {
          showError(res.message || '设置保存失败')
        }
      } catch (err) {
        showError('设置保存失败' + (err.message || '未知错误'))
      } finally {
        saving.value = false
      }
    }
    
    const cleanupLoading = ref(false)
    
    const manualCleanup = async () => {
      const confirmed = await showConfirm(
        '确定要立即执行归档数据清理吗？此操作将删除超过保留时间的归档学期数据，不可恢复！',
        '清理确认',
        { confirmButtonText: '确定清理', type: 'warning' }
      )
      
      if (!confirmed) return
      
      cleanupLoading.value = true
      try {
        const res = await manualCleanupApi()
        if (res.success) {
          showSuccess(res.message || '清理完成')
          loadData()
        } else {
          showError(res.message || '清理失败')
        }
      } catch (err) {
        showError('清理失败' + (err.message || '未知错误'))
      } finally {
        cleanupLoading.value = false
      }
    }
    
    const showBackButton = computed(() => {
      if (user.value?.is_superuser) return false
      if (user.value?.is_super_admin && !user.value?.is_superuser) return false
      return true
    })

    const handleExport = async (termId, termName) => {
      try {
        const response = await exportArchiveApi({}, { url: `/schedules/archived/${termId}/?format=excel`, responseType: 'blob' })
        
        const filename = `学期${termName}归档记录.xlsx`
        await handleExportFromResponse(response, filename)
        
        showSuccess('导出成功')
      } catch (err) {
        showError('导出失败' + (err.message || '未知错误'))
      }
    }

    const loadData = async () => {
      loading.value = true
      try {
        const response = await fetchArchiveDataApi()
        
        if (response.success) {
          const data = response.data || response
          archivedTerms.value = data.archived_terms || []
        }
      } catch (err) {
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadData()
    })

    const viewArchivedRecords = (termData) => {
      const query = {}
      if (route.query?.type) query.type = route.query.type
      router.push({ name: 'ViewArchivedRecords', params: { id: termData.id }, query })
    }

    return {
      archivedTerms,
      loading,
      showBackButton,
      user,
      formatDate,
      smartBack,
      goHome,
      handleExport,
      viewArchivedRecords,
      settingsVisible,
      retentionMonths,
      saving,
      retentionText,
      openSettings,
      saveSettings,
      cleanupLoading,
      manualCleanup,
      HomeFilled,
      Back
    }
  }
}
</script>

<style scoped>
.archive-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-text h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-desc {
  margin: 4px 0 0;
  font-size: 14px;
  color: #909399;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.archive-content {
  margin-top: 0;
}

.terms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}

.term-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.term-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.term-card-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f2f5;
}

.term-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.term-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.term-dates {
  display: flex;
  gap: 16px;
}

.date-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
}

.date-item .el-icon {
  color: #409eff;
}

.term-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #409eff;
  color: white;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.term-actions {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #f0f2f5;
}

.term-actions .el-button {
  flex: 1;
}

.loading-container {
  padding: 40px;
  background: white;
  border-radius: 12px;
}

.settings-content {
  padding: 10px;
}

.form-tip {
  font-size: 13px;
  color: #909399;
  margin-top: 8px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

@media (max-width: 768px) {
  .archive-page {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .terms-grid {
    grid-template-columns: 1fr;
  }
  
  .term-stats {
    grid-template-columns: 1fr;
  }
}
</style>
