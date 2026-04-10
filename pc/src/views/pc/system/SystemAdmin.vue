<!-- 系统管理员控制台 -->
<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="page-container">
        <div class="listheader custom-header">
          <span class="header-text"><el-icon><Monitor /></el-icon> 系统管理控制台</span>
          <div class="listheader-actions">
            <el-button class="nav-action-btn" plain @click="smartBack">返回</el-button>
            <el-button class="nav-action-btn" plain @click="goHome">首页</el-button>
          </div>
        </div>

        <div class="system-admin-layout">
          <!-- 系统概览卡片 -->
          <div class="overview-section">
            <h3 class="section-title"><el-icon><DataLine /></el-icon> 系统概览</h3>
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-icon users">
                  <el-icon><User /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.totalUsers }}</div>
                  <div class="stat-label">总用户数</div>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon departments">
                  <el-icon><OfficeBuilding /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.totalDepartments }}</div>
                  <div class="stat-label">部门数量</div>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon labs">
                  <el-icon><Monitor /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.totalLabs }}</div>
                  <div class="stat-label">实训室数量</div>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon records">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.totalRecords }}</div>
                  <div class="stat-label">使用记录</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 快捷功能 -->
          <div class="quick-actions-section">
            <h3 class="section-title"><el-icon><Grid /></el-icon> 管理工具</h3>
            <div class="actions-grid">
              <div class="action-card" @click="handleNavigate('/userlist')">
                <div class="action-icon user-mgmt">
                  <el-icon><UserFilled /></el-icon>
                </div>
                <div class="action-content">
                  <h4>用户管理</h4>
                  <p>管理系统用户账号</p>
                </div>
                <el-icon class="action-arrow"><ArrowRight /></el-icon>
              </div>

              <div class="action-card" @click="handleNavigate('/deptlist')">
                <div class="action-icon dept-mgmt">
                  <el-icon><OfficeBuilding /></el-icon>
                </div>
                <div class="action-content">
                  <h4>部门管理</h4>
                  <p>管理部门信息结构</p>
                </div>
                <el-icon class="action-arrow"><ArrowRight /></el-icon>
              </div>

              <div class="action-card" @click="handleNavigate('/term')">
                <div class="action-icon term-mgmt">
                  <el-icon><Calendar /></el-icon>
                </div>
                <div class="action-content">
                  <h4>学期管理</h4>
                  <p>管理学期和归档</p>
                </div>
                <el-icon class="action-arrow"><ArrowRight /></el-icon>
              </div>

              <div class="action-card" @click="handleNavigate('/backup-manage')">
                <div class="action-icon backup-mgmt">
                  <el-icon><Download /></el-icon>
                </div>
                <div class="action-content">
                  <h4>数据备份</h4>
                  <p>备份和恢复系统数据</p>
                </div>
                <el-icon class="action-arrow"><ArrowRight /></el-icon>
              </div>

              <div class="action-card" @click="handleNavigate('/assign-permission')">
                <div class="action-icon perm-mgmt">
                  <el-icon><Key /></el-icon>
                </div>
                <div class="action-content">
                  <h4>权限分配</h4>
                  <p>分配用户权限角色</p>
                </div>
                <el-icon class="action-arrow"><ArrowRight /></el-icon>
              </div>

              <div class="action-card" @click="handleNavigate('/comprehensive-stats')">
                <div class="action-icon stats-mgmt">
                  <el-icon><TrendCharts /></el-icon>
                </div>
                <div class="action-content">
                  <h4>数据中心</h4>
                  <p>查看统计分析报表</p>
                </div>
                <el-icon class="action-arrow"><ArrowRight /></el-icon>
              </div>
            </div>
          </div>

          <!-- 系统信息 -->
          <div class="system-info-section">
            <h3 class="section-title"><el-icon><InfoFilled /></el-icon> 系统信息</h3>
            <div class="info-cards">
              <div class="info-card">
                <div class="info-header">
                  <el-icon><Cpu /></el-icon>
                  <span>系统状态</span>
                </div>
                <div class="info-body">
                  <div class="info-item">
                    <span class="label">系统版本</span>
                    <span class="value">v2.0.0</span>
                  </div>
                  <div class="info-item">
                    <span class="label">运行状态</span>
                    <el-tag type="success" size="small">正常</el-tag>
                  </div>
                  <div class="info-item">
                    <span class="label">最后备份</span>
                    <span class="value">{{ lastBackupTime || '暂无' }}</span>
                  </div>
                </div>
              </div>

              <div class="info-card">
                <div class="info-header">
                  <el-icon><Warning /></el-icon>
                  <span>安全提醒</span>
                </div>
                <div class="info-body">
                  <div class="security-tips">
                    <div class="tip-item">
                      <el-icon class="tip-icon success"><CircleCheck /></el-icon>
                      <span>定期备份数据（建议每周）</span>
                    </div>
                    <div class="tip-item">
                      <el-icon class="tip-icon warning"><WarningFilled /></el-icon>
                      <span>检查用户权限分配</span>
                    </div>
                    <div class="tip-item">
                      <el-icon class="tip-icon info"><InfoFilled /></el-icon>
                      <span>监控系统运行状态</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Index>
</template>

<script>
import { ref, onMounted } from 'vue'
import Index from '@/views/pc/dashboard/Index.vue'
import { useNavigation } from '@/core/utils/routeDecision'
import { useApi } from '@/core/hooks'
import {
  Monitor, DataLine, User, OfficeBuilding, Document, Grid,
  UserFilled, Calendar, Download, Key, TrendCharts, ArrowRight,
  InfoFilled, Cpu, Warning, CircleCheck, WarningFilled
} from '@element-plus/icons-vue'

export default {
  name: 'SystemAdmin',
  components: {
    Index,
    Monitor, DataLine, User, OfficeBuilding, Document, Grid,
    UserFilled, Calendar, Download, Key, TrendCharts, ArrowRight,
    InfoFilled, Cpu, Warning, CircleCheck, WarningFilled
  },
  setup() {
    const { goHome, smartBack } = useNavigation()
    const { get } = useApi()

    const stats = ref({
      totalUsers: 0,
      totalDepartments: 0,
      totalLabs: 0,
      totalRecords: 0
    })

    const lastBackupTime = ref('')

    const loadSystemStats = async () => {
      try {
        const response = await get({}, { url: '/backups/stats/' })
        if (response && response.stats) {
          stats.value = {
            totalUsers: response.stats.users || 0,
            totalDepartments: response.stats.departments || 0,
            totalLabs: response.stats.labs || 0,
            totalRecords: response.stats.lab_records || 0
          }
        }
      } catch (error) {
      }
    }

    const handleNavigate = (path) => {
      window.location.hash = path
    }

    onMounted(() => {
      loadSystemStats()
    })

    return {
      goHome,
      smartBack,
      stats,
      lastBackupTime,
      handleNavigate
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

.system-admin-layout {
  max-width: 1400px;
  margin: 0 auto;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.overview-section {
  margin-bottom: 32px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.stat-icon.users {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.stat-icon.departments {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: #fff;
}

.stat-icon.labs {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: #fff;
}

.stat-icon.records {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.quick-actions-section {
  margin-bottom: 32px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.action-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.action-icon.user-mgmt {
  background: #e6f7ff;
  color: #1890ff;
}

.action-icon.dept-mgmt {
  background: #fff7e6;
  color: #fa8c16;
}

.action-icon.term-mgmt {
  background: #f6ffed;
  color: #52c41a;
}

.action-icon.backup-mgmt {
  background: #e6f4ff;
  color: #1890ff;
}

.action-icon.perm-mgmt {
  background: #fff0f6;
  color: #eb2f96;
}

.action-icon.stats-mgmt {
  background: #f9f0ff;
  color: #722ed1;
}

.action-content {
  flex: 1;
}

.action-content h4 {
  margin: 0 0 4px;
  font-size: 15px;
  color: #303133;
  font-weight: 600;
}

.action-content p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.action-arrow {
  color: #c0c4cc;
  font-size: 18px;
  transition: all 0.3s ease;
}

.action-card:hover .action-arrow {
  color: #409eff;
  transform: translateX(4px);
}

.system-info-section {
  margin-bottom: 32px;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.info-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #ebeef5;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.info-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-item .label {
  font-size: 14px;
  color: #606266;
}

.info-item .value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.security-tips {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.tip-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.tip-icon.success {
  color: #67c23a;
}

.tip-icon.warning {
  color: #e6a23c;
}

.tip-icon.info {
  color: #909399;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }

  .info-cards {
    grid-template-columns: 1fr;
  }
}
</style>
