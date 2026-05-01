<!-- 学期归档页面 -->
<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="page-container">
        <div class="listheader custom-header">
          <span class="header-text"><el-icon><Box /></el-icon> 归档学期</span>
          <div class="listheader-actions">
            <el-button
              class="nav-action-btn"
              plain
              @click="goHome"
            >
              首页
            </el-button>
          </div>
        </div>

        <div
          v-if="currentTerm"
          class="unified-panel-layout"
        >
          <div class="unified-panel">
            <div class="panel-side">
              <div class="side-header">
                <h3><el-icon><InfoFilled /></el-icon> 操作指南</h3>
                <p>学期数据归档功能说明</p>
              </div>

              <div class="side-content">
                <div class="side-block">
                  <div class="block-title">
                    归档步骤
                  </div>
                  <div class="guide-list">
                    <div class="guide-item">
                      <div class="guide-icon">
                        1
                      </div>
                      <div class="guide-text">
                        <h4>查看学期信息</h4>
                        <p>确认当前学期和数据状态</p>
                      </div>
                    </div>
                    <div class="guide-item">
                      <div class="guide-icon">
                        2
                      </div>
                      <div class="guide-text">
                        <h4>选择数据类型</h4>
                        <p>勾选需要归档的数据类型</p>
                      </div>
                    </div>
                    <div class="guide-item">
                      <div class="guide-icon">
                        3
                      </div>
                      <div class="guide-text">
                        <h4>确认归档</h4>
                        <p>点击按钮执行归档操作</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="side-block">
                  <div class="block-title">
                    数据类型说明
                  </div>
                  <div class="type-list">
                    <div class="type-item">
                      <el-icon class="type-icon">
                        <OfficeBuilding />
                      </el-icon>
                      <div class="type-text">
                        <span class="type-name">实训室信息</span>
                        <span class="type-desc">包含实训室、设备、使用记录、课表、工单</span>
                      </div>
                    </div>
                    <div class="type-item">
                      <el-icon class="type-icon">
                        <Monitor />
                      </el-icon>
                      <div class="type-text">
                        <span class="type-name">设备信息</span>
                        <span class="type-desc">单独归档设备信息（物理删除）</span>
                      </div>
                    </div>
                    <div class="type-item">
                      <el-icon class="type-icon">
                        <User />
                      </el-icon>
                      <div class="type-text">
                        <span class="type-name">用户信息</span>
                        <span class="type-desc">仅复制用户信息（不删除用户）</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="side-block tips-block">
                  <div class="block-title">
                    <el-icon><WarningFilled /></el-icon> 重要提示
                  </div>
                  <ul class="tips-list">
                    <li>实训室归档会同时归档设备、使用记录、课表、工单</li>
                    <li>归档后数据会从业务表物理删除，仅保留在归档表</li>
                    <li>用户信息归档仅复制数据，不删除用户</li>
                    <li>归档操作不可逆，请谨慎操作</li>
                    <li>建议归档前先进行数据备份</li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="panel-main">
              <div class="main-header">
                <h3><el-icon><Calendar /></el-icon> 当前学期信息</h3>
                <el-tag
                  :type="currentTerm.is_archived ? 'danger' : 'success'"
                  size="large"
                >
                  {{ currentTerm.is_archived ? '已归档' : '未归档' }}
                </el-tag>
              </div>

              <div class="main-content">
                <div class="term-info-section">
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">学期名称</span>
                      <span class="info-value">{{ currentTerm.name }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">开始日期</span>
                      <span class="info-value">{{ currentTerm.start_date }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">结束日期</span>
                      <span class="info-value">{{ currentTerm.end_date }}</span>
                    </div>
                  </div>
                </div>

                <div
                  v-if="currentTermStats"
                  class="stats-section"
                >
                  <div class="section-title">
                    <div class="title-left">
                      <el-icon><DataAnalysis /></el-icon>
                      <span>学期数据统计</span>
                    </div>
                    <el-select 
                      v-model="selectedDepartmentId" 
                      placeholder="选择部门筛选" 
                      clearable
                      size="small"
                      style="width: 180px"
                      @change="handleDepartmentChange"
                    >
                      <el-option
                        label="全部部门"
                        :value="null"
                      />
                      <el-option 
                        v-for="dept in departments" 
                        :key="dept.id" 
                        :label="dept.name" 
                        :value="dept.id" 
                      />
                    </el-select>
                  </div>
                  <div class="stats-grid">
                    <div class="stat-card">
                      <el-icon class="stat-icon">
                        <OfficeBuilding />
                      </el-icon>
                      <div class="stat-info">
                        <span class="stat-value">{{ currentTermStats.lab_count || 0 }}</span>
                        <span class="stat-label">实训室</span>
                      </div>
                    </div>
                    <div class="stat-card">
                      <el-icon class="stat-icon">
                        <Monitor />
                      </el-icon>
                      <div class="stat-info">
                        <span class="stat-value">{{ currentTermStats.device_count || 0 }}</span>
                        <span class="stat-label">设备</span>
                      </div>
                    </div>
                    <div class="stat-card">
                      <el-icon class="stat-icon">
                        <User />
                      </el-icon>
                      <div class="stat-info">
                        <span class="stat-value">{{ currentTermStats.user_count || 0 }}</span>
                        <span class="stat-label">用户</span>
                      </div>
                    </div>
                    <div class="stat-card">
                      <el-icon class="stat-icon">
                        <Document />
                      </el-icon>
                      <div class="stat-info">
                        <span class="stat-value">{{ currentTermStats.record_count || 0 }}</span>
                        <span class="stat-label">使用记录</span>
                      </div>
                    </div>
                    <div class="stat-card">
                      <el-icon class="stat-icon">
                        <Reading />
                      </el-icon>
                      <div class="stat-info">
                        <span class="stat-value">{{ currentTermStats.class_count || 0 }}</span>
                        <span class="stat-label">课表记录</span>
                      </div>
                    </div>
                    <div class="stat-card">
                      <el-icon class="stat-icon">
                        <Tools />
                      </el-icon>
                      <div class="stat-info">
                        <span class="stat-value">{{ currentTermStats.maintain_count || 0 }}</span>
                        <span class="stat-label">维护记录</span>
                      </div>
                    </div>
                    <div class="stat-card">
                      <el-icon class="stat-icon">
                        <Warning />
                      </el-icon>
                      <div class="stat-info">
                        <span class="stat-value">{{ currentTermStats.equipment_maintenance_count || 0 }}</span>
                        <span class="stat-label">故障记录</span>
                      </div>
                    </div>
                  </div>
                </div>

                <template v-if="!currentTerm.is_archived">
                  <div class="section-divider" />

                  <div class="archive-section">
                    <div class="section-title">
                      <el-icon><Setting /></el-icon>
                      <span>选择要归档的数据类型</span>
                    </div>
                    <p class="section-desc">
                      实训室归档会同时归档设备、使用记录、课表、工单，归档后数据会从业务表物理删除
                    </p>

                    <div class="options-grid">
                      <label
                        class="option-card"
                        :class="{ selected: archiveTypes.lab_info }"
                      >
                        <el-checkbox
                          v-model="archiveTypes.lab_info"
                          size="large"
                        />
                        <div class="option-icon">
                          <el-icon :size="22"><OfficeBuilding /></el-icon>
                        </div>
                        <div class="option-info">
                          <span class="option-title">实训室信息</span>
                          <span class="option-count">实训室{{ currentTermStats?.lab_count || 0 }} / 设备{{ currentTermStats?.device_count || 0 }}</span>
                          <span class="option-count">使用记录{{ currentTermStats?.record_count || 0 }} / 课表{{ currentTermStats?.class_count || 0 }}</span>
                          <span class="option-count">维护{{ currentTermStats?.maintain_count || 0 }} / 故障{{ currentTermStats?.equipment_maintenance_count || 0 }}</span>
                        </div>
                      </label>

                      <label
                        class="option-card"
                        :class="{ selected: archiveTypes.device_info }"
                      >
                        <el-checkbox
                          v-model="archiveTypes.device_info"
                          size="large"
                        />
                        <div class="option-icon">
                          <el-icon :size="22"><Monitor /></el-icon>
                        </div>
                        <div class="option-info">
                          <span class="option-title">设备信息</span>
                          <span class="option-count">{{ currentTermStats?.device_count || 0 }}台设备</span>
                        </div>
                      </label>

                      <label
                        class="option-card"
                        :class="{ selected: archiveTypes.user_info }"
                      >
                        <el-checkbox
                          v-model="archiveTypes.user_info"
                          size="large"
                        />
                        <div class="option-icon">
                          <el-icon :size="22"><User /></el-icon>
                        </div>
                        <div class="option-info">
                          <span class="option-title">用户信息</span>
                          <span class="option-count">{{ currentTermStats?.user_count || 0 }}个用户（仅复制）</span>
                        </div>
                      </label>
                    </div>

                    <div class="archive-action">
                      <el-button 
                        type="danger"
                        size="large"
                        :disabled="!hasSelectedTypes || loading"
                        :loading="loading"
                        @click="handleArchive"
                      >
                        <el-icon :size="18">
                          <Box />
                        </el-icon>
                        {{ loading ? '归档中...' : '确认归档当前学期' }}
                      </el-button>
                    </div>
                  </div>
                </template>

                <div
                  v-else
                  class="archived-notice"
                >
                  <el-icon :size="48">
                    <Lock />
                  </el-icon>
                  <h4>当前学期已归档</h4>
                  <p>归档后的数据只能查看，不能修改。如需修改请联系超级管理员。</p>
                  <el-button
                    type="primary"
                    @click="goArchivedTerms"
                  >
                    查看归档记录
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div
          v-else
          class="empty-state"
        >
          <el-empty description="未设置当前学期（归档后需要由超级管理员手动创建并设为当前学期）">
            <div class="empty-actions">
              <el-button
                type="primary"
                @click="goAddTerm"
              >
                创建学期
              </el-button>
              <el-button @click="goTermList">
                学期管理
              </el-button>
              <el-button
                type="info"
                @click="goArchivedTerms"
              >
                查看归档记录
              </el-button>
            </div>
          </el-empty>
        </div>
      </div>
    </template>
  </Index>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi, useAuth } from '@/core/hooks'
import api from '@/core/api/client'
import Index from '@/views/pc/dashboard/Index.vue'
import { showWarning, safeConfirm, showSuccess, showError } from '@/core/utils/errorHandler'
import { useNavigation } from '@/core/utils/routeDecision'
import { useAppStore } from '@/core/store/app'
import { 
  Box, Calendar, Document, Tools, Reading, Warning, Monitor, 
  OfficeBuilding, User, Setting, WarningFilled, InfoFilled,
  DataAnalysis, Lock
} from '@element-plus/icons-vue'

export default {
  name: 'ArchiveTerm',
  components: {
    Index,
    Box, Calendar, Document, Tools, Reading, Warning, Monitor, 
    OfficeBuilding, User, Setting, WarningFilled, InfoFilled,
    DataAnalysis, Lock
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const appStore = useAppStore()
    
    const { user } = useAuth()
    const { smartBack, goHome } = useNavigation()
    const { get: fetchArchiveDataApi, post: submitArchiveApi } = useApi('/semesters/archive_overview/', { immediate: false })
    
    const currentTerm = ref(null)
    const currentTermStats = ref(null)
    const archivedTerms = ref([])
    const backUrl = ref('/')
    const departments = ref([])
    const selectedDepartmentId = ref(null)
    const archiveTypes = ref({
      lab_info: true,
      device_info: false,
      user_info: false
    })
    const loading = ref(false)
    
    const showBackButton = computed(() => {
      if (user.value?.is_superuser) return false
      return true
    })

    const hasSelectedTypes = computed(() => {
      return Object.values(archiveTypes.value).some(v => v)
    })

    const handleArchive = async () => {
      if (!hasSelectedTypes.value) {
        await showWarning('请至少选择一种要归档的数据类型')
        return
      }

      const confirmed = await safeConfirm('确定要归档选中的数据类型吗？此操作不可逆！')
      if (!confirmed) return

      loading.value = true
      
      try {
        const selectedTypes = Object.keys(archiveTypes.value).filter(k => archiveTypes.value[k])
        const payload = { archive_types: selectedTypes }
        if (selectedDepartmentId.value) {
          payload.department_id = selectedDepartmentId.value
        }
        const response = await api.post('/schedules/archive-current/', payload)
        
        if (response && response.success) {
          await showSuccess('归档成功')
          await router.push('/archived-terms')
        } else {
          await showError(response?.message || '归档失败，请重试')
        }
      } catch (err) {
        await showError(err)
      } finally {
        loading.value = false
      }
    }

    const loadData = async () => {
      try {
        const params = {}
        if (selectedDepartmentId.value) {
          params.department_id = selectedDepartmentId.value
        }
        const response = await fetchArchiveDataApi(params)
        
        if (response && response.success) {
          const data = response.data || response
          currentTerm.value = data.current_semester
          if (data.current_semester && data.current_semester.stats) {
            currentTermStats.value = data.current_semester.stats
          } else {
            currentTermStats.value = null
          }
          archivedTerms.value = data.archived_semesters || []
          backUrl.value = data.back_url || '/'
          departments.value = data.departments || []
        }
      } catch (err) {
        currentTerm.value = null
        currentTermStats.value = null
      }
    }

    const handleDepartmentChange = () => {
      loadData()
    }

    const goAddTerm = () => router.push('/addterm')
    const goTermList = () => router.push('/term')
    const goArchivedTerms = () => router.push('/archived-terms')

    onMounted(() => {
      loadData()
    })

    watch(() => appStore.refreshTermTrigger, () => {
      loadData()
    })
    
    return {
      currentTerm,
      currentTermStats,
      archivedTerms,
      backUrl,
      departments,
      selectedDepartmentId,
      archiveTypes,
      loading,
      hasSelectedTypes,
      handleArchive,
      handleDepartmentChange,
      showBackButton,
      user,
      smartBack,
      goHome,
      goAddTerm,
      goTermList,
      goArchivedTerms
    }
  }
}
</script>

<style scoped>
.page-container {
  padding: 20px;
  max-width: 100%;
}

.custom-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0;
}

.header-text {
  font-weight: bold;
  font-size: 18px;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 8px;
}

.listheader-actions {
  display: flex;
  gap: 12px;
}

.unified-panel-layout {
  display: flex;
  justify-content: center;
  padding: 0;
  min-height: auto;
}

.unified-panel {
  width: 100%;
  max-width: 1600px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
  border: 1px solid #ebeef5;
  display: flex;
  overflow: hidden;
  height: calc(100vh - 140px);
  max-height: 750px;
  min-height: 550px;
  margin-top: 10px;
}

.panel-side {
  flex: 0 0 380px;
  background-color: #f8f9fb;
  border-right: 1px solid #eef0f5;
  display: flex;
  flex-direction: column;
}

.side-header {
  padding: 24px 24px 16px;
  border-bottom: 1px solid #eef0f5;
}

.side-header h3 {
  margin: 0 0 6px;
  font-size: 18px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.side-header p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.side-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.side-block {
  display: flex;
  flex-direction: column;
}

.block-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.guide-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.guide-item {
  display: flex;
  gap: 14px;
}

.guide-icon {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 13px;
  flex-shrink: 0;
  background: #e6f4ff;
  color: #1890ff;
}

.guide-text h4 {
  margin: 0 0 3px 0;
  font-size: 14px;
  color: #303133;
  font-weight: 600;
}

.guide-text p {
  margin: 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.type-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.type-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.type-icon {
  font-size: 18px;
  color: #1890ff;
}

.type-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.type-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

.type-desc {
  font-size: 11px;
  color: #909399;
}

.tips-block {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
}

.tips-list {
  margin: 0;
  padding-left: 18px;
  font-size: 12px;
  color: #606266;
}

.tips-list li {
  margin-bottom: 6px;
  line-height: 1.5;
}

.panel-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  overflow-y: auto;
}

.main-header {
  padding: 24px 32px;
  border-bottom: 1px solid #f5f7fa;
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.main-header h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-content {
  flex: 1;
  padding: 32px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

.term-info-section {
  margin-bottom: 24px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px;
  background: #f8f9fb;
  border-radius: 10px;
}

.info-label {
  font-size: 12px;
  color: #909399;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.stats-section {
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.title-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title .el-icon {
  color: #1890ff;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f8f9fb;
  border-radius: 10px;
  border: 1px solid #ebeef5;
}

.stat-icon {
  font-size: 28px;
  color: #1890ff;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.section-divider {
  height: 1px;
  background: #ebeef5;
  margin: 24px 0;
}

.archive-section {
  margin-bottom: 24px;
}

.section-desc {
  font-size: 13px;
  color: #909399;
  margin: 0 0 16px;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.option-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: #f8f9fb;
  border: 2px solid #ebeef5;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.option-card:hover {
  border-color: #1890ff;
  background: #f0f7ff;
}

.option-card.selected {
  border-color: #1890ff;
  background: #e6f4ff;
}

.option-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1890ff;
  color: white;
  flex-shrink: 0;
}

.option-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.option-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.option-count {
  font-size: 12px;
  color: #909399;
}

.archive-action {
  display: flex;
  justify-content: center;
  padding-top: 16px;
}

.archive-action .el-button {
  min-width: 220px;
  height: 44px;
  font-size: 15px;
  border-radius: 22px;
}

.archived-notice {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
  background: #f8f9fb;
  border-radius: 12px;
  border: 1px solid #ebeef5;
}

.archived-notice .el-icon {
  color: #909399;
  margin-bottom: 16px;
}

.archived-notice h4 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #303133;
}

.archived-notice p {
  margin: 0 0 20px;
  font-size: 14px;
  color: #909399;
  max-width: 300px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  margin-top: 10px;
}

.empty-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

@media (max-width: 992px) {
  .unified-panel {
    flex-direction: column;
    height: auto;
    max-height: none;
  }
  
  .panel-side {
    flex: none;
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #eef0f5;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .options-grid {
    grid-template-columns: 1fr;
  }
  
  .main-content {
    padding: 20px;
  }
}
</style>
