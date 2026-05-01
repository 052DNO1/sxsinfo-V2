<!-- 数据备份管理 -->
<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="page-container">
        <div class="listheader custom-header">
          <span class="header-text"><el-icon><Download /></el-icon> 数据备份与恢复</span>
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

        <div class="unified-panel-layout">
          <div class="unified-panel">
            <div class="panel-side">
              <div class="side-header">
                <h3><el-icon><InfoFilled /></el-icon> 操作指南</h3>
                <p>数据备份与恢复功能说明</p>
              </div>

              <div class="side-content">
                <div class="side-block">
                  <div class="block-title">
                    备份步骤
                  </div>
                  <div class="guide-list">
                    <div class="guide-item">
                      <div class="guide-icon backup">
                        1
                      </div>
                      <div class="guide-text">
                        <h4>点击备份按钮</h4>
                        <p>系统将自动导出所有数据</p>
                      </div>
                    </div>
                    <div class="guide-item">
                      <div class="guide-icon backup">
                        2
                      </div>
                      <div class="guide-text">
                        <h4>下载备份文件</h4>
                        <p>Gzip压缩格式，体积更小</p>
                      </div>
                    </div>
                    <div class="guide-item">
                      <div class="guide-icon backup">
                        3
                      </div>
                      <div class="guide-text">
                        <h4>定期备份</h4>
                        <p>建议每周备份一次数据</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="side-block">
                  <div class="block-title">
                    恢复步骤
                  </div>
                  <div class="guide-list">
                    <div class="guide-item">
                      <div class="guide-icon restore">
                        1
                      </div>
                      <div class="guide-text">
                        <h4>上传备份文件</h4>
                        <p>支持 .json 或 .json.gz 格式</p>
                      </div>
                    </div>
                    <div class="guide-item">
                      <div class="guide-icon restore">
                        2
                      </div>
                      <div class="guide-text">
                        <h4>查看备份信息</h4>
                        <p>确认备份内容和时间</p>
                      </div>
                    </div>
                    <div class="guide-item">
                      <div class="guide-icon restore">
                        3
                      </div>
                      <div class="guide-text">
                        <h4>确认恢复</h4>
                        <p>选择是否清除现有数据</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="side-block tips-block">
                  <div class="block-title">
                    <el-icon><WarningFilled /></el-icon> 注意事项
                  </div>
                  <ul class="tips-list">
                    <li>备份文件包含所有数据（含已归档），请妥善保管</li>
                    <li>恢复前建议先备份当前数据</li>
                    <li>选择"清除现有数据"会删除所有数据</li>
                    <li>仅超级管理员可使用此功能</li>
                    <li>备份文件自动保存到服务器，最多保留10份</li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="panel-main">
              <div class="main-header">
                <h3><el-icon><Setting /></el-icon> 数据操作</h3>
                <el-button
                  type="primary"
                  plain
                  @click="showBackupList = !showBackupList"
                >
                  <el-icon><FolderOpened /></el-icon>
                  {{ showBackupList ? '返回操作' : '备份记录' }}
                </el-button>
              </div>

              <div
                class="main-content"
                :class="{ 'list-mode': showBackupList }"
              >
                <template v-if="!showBackupList">
                  <div class="operation-section">
                    <div class="section-title">
                      <el-icon class="title-icon backup-icon">
                        <Download />
                      </el-icon>
                      <span>数据备份</span>
                    </div>
                    <p class="section-desc">
                      导出系统所有数据（含已归档）为压缩文件，可用于数据迁移或灾难恢复
                    </p>
                    
                    <div class="backup-content-box">
                      <div
                        v-for="item in backupItems"
                        :key="item.key"
                        class="backup-item"
                      >
                        <el-icon class="item-icon">
                          <component :is="item.icon" />
                        </el-icon>
                        <span class="item-name">{{ item.name }}</span>
                        <span class="item-count">{{ item.count }} 条</span>
                        <span
                          v-if="item.archived > 0 && !item.fromArchive"
                          class="item-archived"
                        >{{ item.archived }} 已归档</span>
                        <span
                          v-if="item.fromArchive > 0"
                          class="item-from-archive"
                        >{{ item.fromArchive }} 来自学期归档</span>
                      </div>
                    </div>

                    <div class="backup-options">
                      <el-checkbox v-model="useCompression">
                        <span class="option-text">使用 Gzip 压缩</span>
                        <span class="option-tip">（推荐，文件体积减少约80%）</span>
                      </el-checkbox>
                    </div>

                    <el-button 
                      type="primary" 
                      size="large" 
                      class="action-btn"
                      :loading="backupLoading"
                      @click="handleBackup"
                    >
                      <el-icon><Download /></el-icon>
                      {{ backupLoading ? '正在备份...' : '立即备份' }}
                    </el-button>
                  </div>

                  <div class="section-divider">
                    <span>恢复操作</span>
                  </div>

                  <div class="operation-section">
                    <div class="section-title">
                      <el-icon class="title-icon restore-icon">
                        <Upload />
                      </el-icon>
                      <span>数据恢复</span>
                    </div>
                    <p class="section-desc">
                      从备份文件恢复数据，可选择是否清除现有数据
                    </p>

                    <el-upload
                      ref="uploadRef"
                      class="upload-area"
                      drag
                      :auto-upload="false"
                      :limit="1"
                      accept=".json,.json.gz,.gz"
                      :on-change="handleFileChange"
                      :on-exceed="handleExceed"
                      :show-file-list="false"
                    >
                      <div class="upload-content">
                        <el-icon class="upload-icon">
                          <UploadFilled />
                        </el-icon>
                        <div class="upload-text">
                          <span>拖拽文件到此处，或点击上传</span>
                          <em>点击上传</em>
                        </div>
                        <div class="upload-hint">
                          支持 .json 或 .json.gz 格式的备份文件
                        </div>
                      </div>
                    </el-upload>

                    <div
                      v-if="selectedFile"
                      class="file-info"
                    >
                      <div class="file-name">
                        <el-icon><Document /></el-icon>
                        <span>{{ selectedFile.name }}</span>
                        <el-tag
                          v-if="isCompressedFile"
                          type="success"
                          size="small"
                        >
                          已压缩
                        </el-tag>
                      </div>
                      <el-button
                        type="danger"
                        text
                        size="small"
                        @click="clearFile"
                      >
                        <el-icon><Close /></el-icon>
                        移除
                      </el-button>
                    </div>

                    <div
                      v-if="backupInfo"
                      class="backup-info-card"
                    >
                      <div class="info-header">
                        <el-icon><DocumentChecked /></el-icon>
                        <span>备份文件信息</span>
                      </div>
                      <div class="info-grid">
                        <div class="info-item">
                          <span class="label">版本</span>
                          <span class="value">{{ backupInfo.version }}</span>
                        </div>
                        <div class="info-item">
                          <span class="label">创建时间</span>
                          <span class="value">{{ formatDateTime(backupInfo.created_at) }}</span>
                        </div>
                        <div class="info-item">
                          <span class="label">创建人</span>
                          <span class="value">{{ backupInfo.created_by }}</span>
                        </div>
                        <div
                          v-if="backupInfo.checksum"
                          class="info-item"
                        >
                          <span class="label">校验码</span>
                          <span class="value checksum">{{ backupInfo.checksum }}</span>
                        </div>
                      </div>
                      <div
                        v-if="backupInfo.counts"
                        class="counts-section"
                      >
                        <div class="counts-title">
                          数据统计
                        </div>
                        <div class="counts-grid">
                          <div
                            v-for="(count, key) in backupInfo.counts"
                            :key="key"
                            class="count-item"
                          >
                            <span class="count-value">{{ count.total || count }}</span>
                            <span class="count-label">{{ getCountLabel(key) }}</span>
                            <span
                              v-if="count.archived > 0"
                              class="count-archived"
                            >{{ count.archived }} 已归档</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div class="restore-options">
                      <el-checkbox v-model="clearExisting">
                        <span class="option-text">恢复前清除现有数据</span>
                        <span class="option-warning">（谨慎操作！）</span>
                      </el-checkbox>
                    </div>

                    <el-button 
                      type="warning" 
                      size="large"
                      class="action-btn"
                      :disabled="!selectedFile"
                      :loading="restoreLoading"
                      @click="handleRestore"
                    >
                      <el-icon><Upload /></el-icon>
                      {{ restoreLoading ? '正在恢复...' : '恢复数据' }}
                    </el-button>
                  </div>
                </template>

                <template v-else>
                  <div class="operation-section list-section">
                    <div class="section-title">
                      <el-icon class="title-icon">
                        <FolderOpened />
                      </el-icon>
                      <span>备份记录</span>
                    </div>
                    
                    <div class="auto-backup-config">
                      <div class="config-header">
                        <h4><el-icon><Clock /></el-icon> 自动备份设置</h4>
                        <div class="config-switch">
                          <span>启用自动备份</span>
                          <el-switch
                            v-model="autoBackupEnabled"
                            @change="handleAutoBackupChange"
                          />
                        </div>
                      </div>
                      <div class="config-desc">
                        开启后系统将按照设定周期自动创建备份文件。自动备份会保留最近10份，超过数量会自动删除旧备份。
                      </div>
                      <div
                        v-if="autoBackupEnabled"
                        class="config-options"
                      >
                        <div style="display: flex; align-items: center; gap: 12px;">
                          <span>备份周期</span>
                          <el-select
                            v-model="autoBackupPeriod"
                            style="width: 150px"
                            @change="handlePeriodChange"
                          >
                            <el-option
                              label="每天"
                              value="daily"
                            />
                            <el-option
                              label="每周"
                              value="weekly"
                            />
                            <el-option
                              label="每月"
                              value="monthly"
                            />
                          </el-select>
                          <span style="font-size: 12px; color: #909399;">
                            （下次备份时间：{{ nextBackupTime || '计算中...' }}）
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div class="filter-bar">
                      <el-select
                        v-model="listFilter"
                        placeholder="筛选类型"
                        style="width: 120px"
                        @change="loadBackupList"
                      >
                        <el-option
                          label="全部"
                          value=""
                        />
                        <el-option
                          label="压缩文件"
                          value="compressed"
                        />
                        <el-option
                          label="JSON文件"
                          value="json"
                        />
                      </el-select>
                      <el-button
                        :icon="Refresh"
                        @click="loadBackupList"
                      >
                        刷新
                      </el-button>
                    </div>

                    <el-table
                      v-loading="listLoading"
                      :data="backupList"
                      stripe
                      class="backup-table"
                      style="width: 100%"
                    >
                      <el-table-column
                        prop="filename"
                        label="文件名"
                        min-width="220"
                        show-overflow-tooltip
                      />
                      <el-table-column
                        prop="file_type"
                        label="类型"
                        width="80"
                        align="center"
                      >
                        <template #default="{ row }">
                          <el-tag
                            :type="row.is_compressed ? 'success' : 'info'"
                            size="small"
                          >
                            {{ row.is_compressed ? 'Gzip' : 'JSON' }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column
                        prop="size_display"
                        label="大小"
                        width="100"
                        align="center"
                      />
                      <el-table-column
                        prop="created_at"
                        label="创建时间"
                        width="160"
                        align="center"
                      />
                      <el-table-column
                        label="操作"
                        width="180"
                        align="center"
                        fixed="right"
                      >
                        <template #default="{ row }">
                          <div class="action-buttons">
                            <el-button 
                              type="primary" 
                              size="small" 
                              text
                              :disabled="!row.can_download"
                              @click="handleDownloadBackup(row)"
                            >
                              <el-icon><Download /></el-icon>下载
                            </el-button>
                            <el-button 
                              type="danger" 
                              size="small" 
                              text
                              @click="handleDeleteBackup(row)"
                            >
                              <el-icon><Delete /></el-icon>删除
                            </el-button>
                          </div>
                        </template>
                      </el-table-column>
                      <template #empty>
                        <el-empty description="暂无备份记录" />
                      </template>
                    </el-table>

                    <div
                      v-if="listTotal > 0"
                      class="pagination-wrapper"
                    >
                      <el-pagination
                        v-model:current-page="listPage"
                        v-model:page-size="listPageSize"
                        :total="listTotal"
                        :page-sizes="[10, 20, 50]"
                        layout="total, sizes, prev, pager, next"
                        @size-change="loadBackupList"
                        @current-change="loadBackupList"
                      />
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Index>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import Index from '@/views/pc/dashboard/Index.vue'
import { useNavigation } from '@/core/utils/routeDecision'
import { useApi } from '@/core/hooks'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Download, Upload, UploadFilled, InfoFilled, WarningFilled, Setting,
  Document, Close, DocumentChecked, User, OfficeBuilding, Calendar,
  Reading, Tools, Monitor, FolderOpened, Refresh, Delete, Clock
} from '@element-plus/icons-vue'

export default {
  name: 'BackupManage',
  components: {
    Index,
    Download, Upload, UploadFilled, InfoFilled, WarningFilled, Setting,
    Document, Close, DocumentChecked, User, OfficeBuilding, Calendar,
    Reading, Tools, Monitor, FolderOpened, Refresh, Delete, Clock
  },
  setup() {
    const { goHome } = useNavigation()
    const { get, post } = useApi()

    const showBackupList = ref(false)
    const autoBackupEnabled = ref(false)
    const autoBackupPeriod = ref('daily')
    const nextBackupTime = ref('')
    const backupLoading = ref(false)
    const restoreLoading = ref(false)
    const selectedFile = ref(null)
    const backupInfo = ref(null)
    const clearExisting = ref(false)
    const uploadRef = ref(null)
    const useCompression = ref(true)

    const isCompressedFile = computed(() => {
      if (!selectedFile.value) return false
      const name = selectedFile.value.name.toLowerCase()
      return name.endsWith('.gz') || name.endsWith('.json.gz')
    })

    const backupItems = ref([
      { key: 'users', name: '用户数据', icon: 'User', count: 0, archived: 0, fromArchive: 0 },
      { key: 'departments', name: '部门数据', icon: 'OfficeBuilding', count: 0, archived: 0, fromArchive: 0 },
      { key: 'semesters', name: '学期数据', icon: 'Calendar', count: 0, archived: 0, fromArchive: 0 },
      { key: 'term_archives', name: '学期归档', icon: 'FolderOpened', count: 0, archived: 0, fromArchive: 0 },
      { key: 'laboratories', name: '实训室数据', icon: 'Monitor', count: 0, archived: 0, fromArchive: 0 },
      { key: 'schedules', name: '课表数据', icon: 'Reading', count: 0, archived: 0, fromArchive: 0 },
      { key: 'records', name: '使用记录', icon: 'Document', count: 0, archived: 0, fromArchive: 0 },
      { key: 'work_orders', name: '工单数据', icon: 'Tools', count: 0, archived: 0, fromArchive: 0 },
      { key: 'equipment', name: '设备数据', icon: 'Monitor', count: 0, archived: 0, fromArchive: 0 },
      { key: 'system_settings', name: '系统设置', icon: 'Setting', count: 0, archived: 0, fromArchive: 0 },
    ])

    const countLabels = {
      'users': '用户',
      'departments': '部门',
      'semesters': '学期',
      'term_archives': '学期归档',
      'laboratories': '实训室',
      'records': '使用记录',
      'work_orders': '工单',
      'schedules': '课表',
      'equipment': '设备',
      'system_settings': '系统设置',
    }

    const backupList = ref([])
    const listLoading = ref(false)
    const listFilter = ref('')
    const listPage = ref(1)
    const listPageSize = ref(10)
    const listTotal = ref(0)

    const getCountLabel = (key) => {
      return countLabels[key] || key
    }

    const formatDateTime = (dateStr) => {
      if (!dateStr) return '未知'
      try {
        const date = new Date(dateStr)
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch {
        return dateStr
      }
    }

    const loadAutoBackupConfig = async () => {
      try {
        const response = await get({}, { url: '/backups/auto-config/' })
        const data = response?.data || response || {}
        if (Object.keys(data).length > 0) {
          autoBackupEnabled.value = data.enabled || false
          autoBackupPeriod.value = data.period || 'daily'
          calculateNextBackupTime()
        }
      } catch (error) {
      }
    }

    const calculateNextBackupTime = () => {
      if (!autoBackupEnabled.value) {
        nextBackupTime.value = ''
        return
      }

      const now = new Date()
      let nextDate = new Date(now)

      switch (autoBackupPeriod.value) {
        case 'daily':
          nextDate.setDate(now.getDate() + 1)
          nextDate.setHours(2, 0, 0, 0)
          break
        case 'weekly':
          const daysUntilSunday = (7 - now.getDay()) % 7 || 7
          nextDate.setDate(now.getDate() + daysUntilSunday)
          nextDate.setHours(2, 0, 0, 0)
          break
        case 'monthly':
          nextDate.setMonth(now.getMonth() + 1)
          nextDate.setDate(1)
          nextDate.setHours(2, 0, 0, 0)
          break
      }

      const options = { month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }
      nextBackupTime.value = nextDate.toLocaleDateString('zh-CN', options)
    }

    const handleAutoBackupChange = async (value) => {
      try {
        await post({ 
          enabled: value, 
          period: autoBackupPeriod.value 
        }, { url: '/backups/auto-config/' })
        
        ElMessage.success(value ? '已启用自动备份' : '已禁用自动备份')
        calculateNextBackupTime()
      } catch (error) {
        ElMessage.error('保存配置失败' + (error.message || '未知错误'))
        autoBackupEnabled.value = !value
      }
    }

    const handlePeriodChange = async (value) => {
      try {
        await post({ 
          enabled: autoBackupEnabled.value, 
          period: value 
        }, { url: '/backups/auto-config/' })
        
        ElMessage.success('备份周期已更新')
        calculateNextBackupTime()
      } catch (error) {
        ElMessage.error('保存配置失败' + (error.message || '未知错误'))
      }
    }

    const loadBackupStats = async () => {
      try {
        const response = await get({}, { url: '/backups/stats/' })
        const statsData = response?.data?.stats || response?.stats || {}
        if (Object.keys(statsData).length > 0) {
          const statsMap = {
            'users': 'users',
            'departments': 'departments',
            'semesters': 'semesters',
            'term_archives': 'term_archives',
            'laboratories': 'laboratories',
            'schedules': 'schedules',
            'records': 'records',
            'work_orders': 'work_orders',
            'equipment': 'equipment',
            'system_settings': 'system_settings',
          }
          backupItems.value = backupItems.value.map(item => {
            const stat = statsData[statsMap[item.key]] || {}
            return {
              ...item,
              count: stat.total || 0,
              archived: stat.archived || 0,
              fromArchive: stat.archived_from_term || 0
            }
          })
        }
      } catch (error) {
      }
    }

    const loadBackupList = async () => {
      listLoading.value = true
      try {
        const params = {
          page: listPage.value,
          page_size: listPageSize.value
        }
        if (listFilter.value) {
          params.type = listFilter.value
        }
        
        const response = await get(params, { url: '/backups/list/' })
        const data = response?.data || response || {}
        backupList.value = data.list || []
        listTotal.value = data.total || 0
      } catch (error) {
      } finally {
        listLoading.value = false
      }
    }

    const handleBackup = async () => {
      try {
        backupLoading.value = true
        const compressParam = useCompression.value ? 'true' : 'false'
        const response = await get({}, { 
          url: `/backups/export/?compress=${compressParam}`, 
          responseType: 'blob' 
        })
        
        let blobData = response
        if (response && response.data) {
          blobData = response.data
        }
        
        const contentType = blobData.type || 'application/octet-stream'
        const isGzip = contentType.includes('gzip') || useCompression.value
        
        if (!(blobData instanceof Blob)) {
          blobData = new Blob([blobData], { 
            type: isGzip ? 'application/gzip' : 'application/json' 
          })
        }
        
        const url = window.URL.createObjectURL(blobData)
        const link = document.createElement('a')
        link.href = url
        const ext = isGzip ? 'json.gz' : 'json'
        link.setAttribute('download', `lims_backup_${new Date().toISOString().slice(0,10)}.${ext}`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        ElMessage.success('备份成功')
        loadBackupStats()
      } catch (error) {
        ElMessage.error('备份失败' + (error.message || '未知错误')) 
      } finally {
        backupLoading.value = false
      }
    }

    const handleDownloadBackup = async (row) => {
      try {
        const response = await get({}, { 
          url: `/backups/download/${row.filename}/`, 
          responseType: 'blob' 
        })
        
        let blobData = response
        if (response && response.data) {
          blobData = response.data
        }
        
        const isGzip = row.is_compressed || row.filename.endsWith('.gz')
        
        if (!(blobData instanceof Blob)) {
          blobData = new Blob([blobData], { 
            type: isGzip ? 'application/gzip' : 'application/json' 
          })
        }
        
        const url = window.URL.createObjectURL(blobData)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', row.filename)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        ElMessage.success('下载成功')
      } catch (error) {
        ElMessage.error('下载失败' + (error.message || '未知错误')) 
      }
    }

    const handleDeleteBackup = async (row) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除备份「${row.filename}」吗？此操作不可恢复！`,      
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await post({}, { url: `/backups/delete/${row.filename}/` })
        ElMessage.success('删除成功')
        loadBackupList()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败' + (error.message || '未知错误'))
        }
      }
    }

    const handleFileChange = async (file) => {
      selectedFile.value = file.raw
      
      const formData = new FormData()
      formData.append('backup_file', file.raw)
      
      try {
        const response = await post(formData, { url: '/backups/info/' })
        const data = response?.data || response || {}
        if (Object.keys(data).length > 0) {
          backupInfo.value = data
        }
      } catch (error) {
        ElMessage.error('读取备份文件失败: ' + (error.message || '文件格式错误'))
        backupInfo.value = null
        selectedFile.value = null
      }
    }

    const handleExceed = () => {
      ElMessage.warning('只能上传一个文件')
    }

    const clearFile = () => {
      selectedFile.value = null
      backupInfo.value = null
      uploadRef.value?.clearFiles()
    }

    const handleRestore = async () => {
      if (!selectedFile.value) {
        ElMessage.warning('请先选择备份文件')
        return
      }

      try {
        await ElMessageBox.confirm(
          clearExisting.value 
            ? '确定要恢复数据吗？选择"清除现有数据"将删除所有当前数据，此操作不可撤销！' 
            : '确定要恢复数据吗？现有数据将与备份数据合并。',
          '确认恢复',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        restoreLoading.value = true
        const formData = new FormData()
        formData.append('backup_file', selectedFile.value)
        formData.append('clear_existing', clearExisting.value)

        const response = await post(formData, { url: '/backups/restore/' })
        
        if (response) {
          ElMessage.success('数据恢复成功')
          clearFile()
          loadBackupStats()
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('恢复失败: ' + (error.message || '未知错误'))
        }
      } finally {
        restoreLoading.value = false
      }
    }

    watch(showBackupList, (val) => {
      if (val) {
        loadBackupList()
      } else {
        loadBackupStats()
      }
    })

    onMounted(() => {
      loadBackupStats()
      loadAutoBackupConfig()
    })

    return {
      showBackupList,
      autoBackupEnabled,
      autoBackupPeriod,
      nextBackupTime,
      goHome,
      backupLoading,
      restoreLoading,
      selectedFile,
      backupInfo,
      clearExisting,
      uploadRef,
      useCompression,
      isCompressedFile,
      backupItems,
      backupList,
      listLoading,
      listFilter,
      listPage,
      listPageSize,
      listTotal,
      getCountLabel,
      formatDateTime,
      loadBackupList,
      handleBackup,
      handleDownloadBackup,
      handleDeleteBackup,
      handleFileChange,
      handleExceed,
      clearFile,
      handleRestore,
      handleAutoBackupChange,
      handlePeriodChange,
      Refresh,
      Delete,
      Clock
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
}

.guide-icon.backup {
  background: #e6f4ff;
  color: #1890ff;
}

.guide-icon.restore {
  background: #fff7e6;
  color: #fa8c16;
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

.main-content.list-mode {
  max-width: 100%;
  padding: 24px 32px;
}

.operation-section {
  margin-bottom: 24px;
}

.operation-section.list-section {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.title-icon {
  font-size: 20px;
}

.title-icon.backup-icon {
  color: #1890ff;
}

.title-icon.restore-icon {
  color: #fa8c16;
}

.section-desc {
  font-size: 13px;
  color: #909399;
  margin: 0 0 16px;
}

.backup-content-box {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.backup-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 12px;
  background: #f8f9fb;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.item-icon {
  font-size: 24px;
  color: #1890ff;
  margin-bottom: 8px;
}

.item-name {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
}

.item-count {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.item-archived {
  font-size: 10px;
  color: #909399;
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
}

.item-from-archive {
  font-size: 10px;
  color: #67c23a;
  background: #f0f9eb;
  padding: 2px 6px;
  border-radius: 4px;
}

.backup-options {
  padding: 12px 16px;
  background: #f0f7ff;
  border-radius: 8px;
  margin-bottom: 16px;
  border: 1px solid #d6e4ff;
}

.option-tip {
  font-size: 12px;
  color: #1890ff;
}

.section-divider {
  display: flex;
  align-items: center;
  margin: 24px 0;
}

.section-divider::before,
.section-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #ebeef5;
}

.section-divider span {
  padding: 0 16px;
  color: #909399;
  font-size: 13px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.backup-table {
  background: #fff;
  border-radius: 8px;
}

.backup-table :deep(.el-table__header th) {
  background: #f5f7fa !important;
  color: #303133;
  font-weight: 600;
}

.backup-table :deep(.el-table__row td) {
  color: #606266;
}

.backup-table :deep(.el-table__row:hover > td) {
  background: #f5f7fa !important;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}

.auto-backup-config {
  background: #f8f9fb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.config-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.config-switch {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-desc {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
  line-height: 1.5;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.upload-area {
  width: 100%;
  margin-bottom: 16px;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  border: 2px dashed #d9d9d9;
  border-radius: 12px;
  background: #fafafa;
  transition: all 0.3s;
}

.upload-area :deep(.el-upload-dragger:hover) {
  border-color: #1890ff;
  background: #f0f7ff;
}

.upload-content {
  padding: 32px 20px;
  text-align: center;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 12px;
}

.upload-text {
  font-size: 14px;
  color: #606266;
}

.upload-text em {
  color: #1890ff;
  font-style: normal;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.file-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f0f7ff;
  border-radius: 8px;
  margin-bottom: 16px;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1890ff;
  font-size: 14px;
}

.backup-info-card {
  background: #f8f9fb;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  font-size: 12px;
  color: #909399;
}

.info-item .value {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
}

.info-item .value.checksum {
  font-family: monospace;
  font-size: 12px;
  color: #67c23a;
}

.counts-section {
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.counts-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 10px;
}

.counts-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.count-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 14px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}

.count-value {
  font-size: 16px;
  font-weight: 600;
  color: #1890ff;
}

.count-label {
  font-size: 11px;
  color: #909399;
}

.count-archived {
  font-size: 9px;
  color: #e6a23c;
}

.restore-options {
  padding: 14px 16px;
  background: #fffbe6;
  border-radius: 8px;
  border: 1px solid #ffe58f;
  margin-bottom: 16px;
}

.option-text {
  font-size: 14px;
  color: #303133;
}

.option-warning {
  font-size: 12px;
  color: #fa8c16;
}

.action-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  border-radius: 22px;
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

  .backup-content-box {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .main-content {
    padding: 20px;
  }

  .main-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
}
</style>
