<!-- 工单管理中心 -->
<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="work-order-center">
        <div class="woc-header">
          <div class="woc-title">
            <el-icon :size="28">
              <Tickets />
            </el-icon>
            <h2>工单中心</h2>
          </div>
          <div class="woc-actions">
            <el-button 
              v-if="canReportFault" 
              type="primary" 
              :icon="Plus" 
              @click="goToReport"
            >
              故障上报
            </el-button>
            <el-button
              :icon="ArrowLeft"
              @click="smartBack"
            >
              返回
            </el-button>
            <el-button
              :icon="HomeFilled"
              @click="goHome"
            >
              首页
            </el-button>
          </div>
        </div>

        <div class="woc-stats">
          <div 
            class="woc-stat" 
            :class="{ active: activeTab === 'pending' }" 
            @click="switchTab('pending')"
          >
            <div class="stat-icon pending">
              <el-icon :size="24">
                <Clock />
              </el-icon>
            </div>
            <div class="stat-body">
              <span class="stat-num">{{ pendingCount }}</span>
              <span class="stat-txt">待处理</span>
            </div>
          </div>
          <div 
            class="woc-stat" 
            :class="{ active: activeTab === 'processing' }" 
            @click="switchTab('processing')"
          >
            <div class="stat-icon processing">
              <el-icon :size="24">
                <Tools />
              </el-icon>
            </div>
            <div class="stat-body">
              <span class="stat-num">{{ processingCount }}</span>
              <span class="stat-txt">处理中</span>
            </div>
          </div>
          <div 
            class="woc-stat" 
            :class="{ active: activeTab === 'completed' }" 
            @click="switchTab('completed')"
          >
            <div class="stat-icon completed">
              <el-icon :size="24">
                <CircleCheck />
              </el-icon>
            </div>
            <div class="stat-body">
              <span class="stat-num">{{ completedCount }}</span>
              <span class="stat-txt">已完成</span>
            </div>
          </div>
          <div 
            class="woc-stat" 
            :class="{ active: activeTab === 'closed' }" 
            @click="switchTab('closed')"
          >
            <div class="stat-icon closed">
              <el-icon :size="24">
                <Finished />
              </el-icon>
            </div>
            <div class="stat-body">
              <span class="stat-num">{{ closedCount }}</span>
              <span class="stat-txt">已关闭</span>
            </div>
          </div>
        </div>

        <div class="woc-main">
          <div class="woc-toolbar">
            <div class="woc-tabs">
              <el-radio-group
                v-model="activeTab"
                size="default"
                @change="onTabChange"
              >
                <el-radio-button value="all">
                  全部工单
                </el-radio-button>
                <el-radio-button value="pending">
                  待处理
                  <el-badge
                    v-if="pendingCount > 0"
                    :value="pendingCount"
                    class="tab-badge"
                  />
                </el-radio-button>
                <el-radio-button value="processing">
                  处理中
                </el-radio-button>
                <el-radio-button value="completed">
                  已完成
                </el-radio-button>
                <el-radio-button value="closed">
                  已关闭
                </el-radio-button>
              </el-radio-group>
            </div>
            <div class="woc-search">
              <el-input 
                v-model="filters.search" 
                placeholder="搜索实训室、故障内容"
                clearable
                :prefix-icon="Search"
                @keyup.enter="handleSearch"
                @clear="handleSearch"
              />
            </div>
          </div>

          <div
            v-loading="loading"
            class="woc-list"
          >
            <template v-if="workOrders.length > 0">
              <el-card 
                v-for="item in workOrders" 
                :key="item.id" 
                class="woc-card"
                :class="getStatusClass(item.status)"
                shadow="hover"
                @click="viewDetail(item)"
              >
                <div class="card-header">
                  <div class="card-status">
                    <el-tag
                      :type="getTagType(item.status)"
                      size="default"
                    >
                      {{ getStatusLabel(item.status) }}
                    </el-tag>
                  </div>
                  <div class="card-time">
                    <el-icon><Clock /></el-icon>
                    {{ item.reported_at }}
                  </div>
                </div>
                <div class="card-body">
                  <div class="card-location">
                    <el-icon><Location /></el-icon>
                    <span class="sxs-name">{{ item.laboratory_name }}</span>
                    <el-tag
                      size="small"
                      type="info"
                    >
                      {{ item.laboratory_code || '' }}
                    </el-tag>
                  </div>
                  <div class="card-content">
                    {{ item.title }}
                  </div>
                </div>
                <div class="card-footer">
                  <div class="card-reporter">
                    <el-avatar
                      :size="24"
                      :style="{ background: getAvatarColor(item.reporter_name) }"
                    >
                      {{ getInitial(item.reporter_name) }}
                    </el-avatar>
                    <span>{{ item.reporter_name || '未知' }}</span>
                  </div>
                  <div
                    class="card-actions"
                    @click.stop
                  >
                    <template v-if="item.status === 'pending' && canHandle(item)">
                      <el-button
                        type="primary"
                        size="small"
                        :icon="Tools"
                        @click="startProcess(item)"
                      >
                        接单处理
                      </el-button>
                    </template>
                    <template v-else-if="item.status === 'processing' && canHandle(item)">
                      <el-button
                        type="success"
                        size="small"
                        :icon="CircleCheck"
                        @click="completeOrder(item)"
                      >
                        完成修复
                      </el-button>
                    </template>
                    <template v-else-if="item.status === 'completed' && canConfirm(item)">
                      <el-button
                        type="success"
                        size="small"
                        plain
                        :icon="Finished"
                        @click="confirmOrder(item)"
                      >
                        确认关闭
                      </el-button>
                    </template>
                    <el-button
                      size="small"
                      :icon="View"
                      @click="viewDetail(item)"
                    >
                      详情
                    </el-button>
                    <el-button
                      type="danger"
                      size="small"
                      plain
                      :icon="Delete"
                      @click="hideOrder(item)"
                    >
                      删除
                    </el-button>
                  </div>
                </div>
              </el-card>
            </template>
            <template v-else>
              <div class="woc-empty">
                <el-empty description="暂无工单">
                  <el-button
                    v-if="canReportFault"
                    type="primary"
                    :icon="Plus"
                    @click="goToReport"
                  >
                    上报故障
                  </el-button>
                </el-empty>
              </div>
            </template>
          </div>

          <div class="woc-pagination">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="totalOrders"
              :page-sizes="[6, 3, 9, 12]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>

        <el-dialog
          v-model="showCompleteDialog"
          title="完成修复"
          width="500px"
          destroy-on-close
        >
          <el-form
            :model="completeForm"
            label-width="80px"
          >
            <el-form-item label="处理备注">
              <el-input 
                v-model="completeForm.memo" 
                type="textarea" 
                :rows="4"
                placeholder="请填写处理情?.."
              />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="showCompleteDialog = false">
              取消
            </el-button>
            <el-button
              type="primary"
              @click="submitComplete"
            >
              确认完成
            </el-button>
          </template>
        </el-dialog>
      </div>
    </template>
  </Index>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi, useAuth } from '@/core/hooks'
import { showSuccess, showError } from '@/core/utils/errorHandler'
import { useNavigation } from '@/core/utils/routeDecision'
import Index from '@/views/pc/dashboard/Index.vue'
import api from '@/core/api/client'
import { 
  Tickets, Plus, Clock, Tools, CircleCheck, Finished,
  Search, ArrowLeft, HomeFilled, Location, View, Delete
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()
const { user, isSxsAdmin, isDepartAdmin, isTeacher } = useAuth()

const { loading, get: fetchOrders, post: updateOrder } = useApi('/work-orders/center/', { immediate: false })

const activeTab = ref('all')
const pendingCount = ref(0)
const processingCount = ref(0)
const completedCount = ref(0)
const closedCount = ref(0)
const workOrders = ref([])
const hiddenOrderIds = ref(new Set())
const filters = ref({ search: '' })
const currentPage = ref(1)
const pageSize = ref(6)
const totalOrders = ref(0)

const showCompleteDialog = ref(false)
const currentOrder = ref(null)
const completeForm = ref({ memo: '' })

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  loadData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadData()
}

const switchTab = (tab) => {
  activeTab.value = tab
  currentPage.value = 1
}

const onTabChange = () => {
  currentPage.value = 1
  loadData()
}

const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

const loadData = async () => {
  const params = {
    search: filters.value.search,
    page: currentPage.value,
    page_size: pageSize.value,
    status: activeTab.value === 'all' ? '' : activeTab.value
  }

  try {
    const response = await fetchOrders(params)
    
    if (response && response.success && response.data) {
      const data = response.data
      const statusCounts = data.status_counts || {}
      pendingCount.value = statusCounts.pending || 0
      processingCount.value = statusCounts.processing || 0
      completedCount.value = statusCounts.completed || 0
      closedCount.value = statusCounts.closed || 0
      
      let allOrders = Array.isArray(data.orders) ? data.orders : []
      
      // 过滤掉已隐藏的工单
      workOrders.value = allOrders.filter(order => !hiddenOrderIds.value.has(order.id))
      
      if (data.page_obj) {
        totalOrders.value = data.page_obj.count || data.page_obj.total || 0
        if (data.page_obj.number) {
          currentPage.value = data.page_obj.number
        }
      } else if (data.total) {
        totalOrders.value = data.total
      } else if (data.count) {
        totalOrders.value = data.count
      } else {
        totalOrders.value = workOrders.value.length
      }
      
      // 减去隐藏的工单数量
      totalOrders.value = Math.max(0, totalOrders.value - hiddenOrderIds.value.size)
    }
  } catch (err) {
  }
}

const getStatusLabel = (status) => {
    const labels = {
    'PENDING': '待处理',
    'PROCESSING': '处理中',
    'COMPLETED': '已完成',
    'CLOSED': '已关闭'
  }
  return labels[status] || status
}

const getStatusClass = (status) => {
  return `card-${status.toLowerCase()}`
}

const getTagType = (status) => {
  const types = {
    'PENDING': 'warning',
    'PROCESSING': 'primary',
    'COMPLETED': 'success',
    'CLOSED': 'info'
  }
  return types[status] || 'info'
}

const getAvatarColor = (name) => {
  if (!name) return '#909399'
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#00d4aa']
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const getInitial = (name) => {
  return name ? name.charAt(0).toUpperCase() : '?'
}

const canHandle = (item) => {
  if (!user.value) return false
  return isSxsAdmin.value || isDepartAdmin.value
}

const canConfirm = (item) => {
  if (!user.value) return false
  return item.maintainrequester === user.value.id
}

const canReportFault = computed(() => {
  if (!user.value) return false
  return isTeacher.value
})

const goToReport = () => {
  router.push('/report-maintenance')
}

const viewDetail = (item) => {
  router.push(`/workorder/${item.id}`)
}

const startProcess = async (item) => {
  try {
    const response = await updateOrder({ status: 'processing' }, { url: `/work-orders/center/${item.id}/` })
    if (response && response.success) {
      showSuccess('已接单，请尽快处理')
      loadData()
    }
  } catch (err) {
    showError('操作失败')
  }
}

const completeOrder = (item) => {
  currentOrder.value = item
  completeForm.value.memo = ''
  showCompleteDialog.value = true
}

const submitComplete = async () => {
  if (!currentOrder.value) return
  
  try {
    const response = await updateOrder({ 
      status: 'completed',
      memo: completeForm.value.memo 
    }, { url: `/work-orders/center/${currentOrder.value.id}/` })
    
    if (response && response.success) {
      showSuccess('已标记为完成，等待上报人确认')
      showCompleteDialog.value = false
      loadData()
    }
  } catch (err) {
    showError('操作失败')
  }
}

const confirmOrder = async (item) => {
  try {
    const response = await updateOrder({ status: 'closed' }, { url: `/work-orders/center/${item.id}/` })
    if (response && response.success) {
      showSuccess('工单已关闭')
      loadData()
    }
  } catch (err) {
    showError('操作失败')
  }
}

const hideOrder = async (item) => {
  try {
    const response = await api.post(`/work-orders/center/${item.id}/hide/`, {})
    
    if (response && response.success) {
      showSuccess('已从工单中心移除')
      
      // 添加到隐藏列表
      hiddenOrderIds.value.add(item.id)
      
      // 立即从列表中移除该项
      const index = workOrders.value.findIndex(o => o.id === item.id)
      if (index !== -1) {
        workOrders.value.splice(index, 1)
      }
      
      // 更新总数
      totalOrders.value = Math.max(0, totalOrders.value - 1)
      
      // 重新加载数据以更新统计
      loadData()
    } else {
      showError('隐藏失败：' + (response?.message || '未知错误'))
    }
  } catch (err) {
    showError('操作失败')
  }
}

onMounted(() => {
  if (route.query.tab) {
    activeTab.value = route.query.tab
  }
  loadData()
})
</script>

<style scoped>
.work-order-center {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
}

.woc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 32px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.woc-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.woc-title .el-icon {
  color: #e6a23c;
}

.woc-title h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.woc-actions {
  display: flex;
  gap: 12px;
}

.woc-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 24px 32px;
}

.woc-stat {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: #fff;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.woc-stat:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.woc-stat.active {
  border-color: var(--el-color-primary);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.2);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-icon.pending {
  background: linear-gradient(135deg, #e6a23c 0%, #f5c471 100%);
}

.stat-icon.processing {
  background: linear-gradient(135deg, #409eff 0%, #79bbff 100%);
}

.stat-icon.completed {
  background: linear-gradient(135deg, #67c23a 0%, #95d475 100%);
}

.stat-icon.closed {
  background: linear-gradient(135deg, #909399 0%, #b4b6ba 100%);
}

.stat-body {
  display: flex;
  flex-direction: column;
}

.stat-num {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
}

.stat-txt {
  font-size: 14px;
  color: #909399;
  margin-top: 6px;
}

.woc-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  margin: 0 32px 32px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.woc-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
  background: #fafbfc;
}

.woc-tabs {
  flex-shrink: 0;
}

.tab-badge {
  margin-left: 6px;
}

.woc-search {
  width: 280px;
}

.woc-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  align-content: start;
}

.woc-card {
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.woc-card:hover {
  transform: translateX(4px);
}

.woc-card.card-pending {
  border-left-color: #e6a23c;
}

.woc-card.card-processing {
  border-left-color: #409eff;
}

.woc-card.card-completed {
  border-left-color: #67c23a;
}

.woc-card.card-closed {
  border-left-color: #909399;
  opacity: 0.75;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
}

.card-body {
  margin-bottom: 16px;
}

.card-location {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  color: #606266;
}

.card-location .el-icon {
  color: #409eff;
}

.sxs-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.card-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.card-reporter {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #909399;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.woc-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.woc-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
  border-top: 1px solid #ebeef5;
  background: linear-gradient(180deg, #fafbfc 0%, #fff 100%);
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.04);
  position: sticky;
  bottom: 0;
  z-index: 10;
}

.woc-pagination :deep(.el-pagination) {
  display: flex;
  align-items: center;
  gap: 8px;
}

.woc-pagination :deep(.el-pagination .btn-prev),
.woc-pagination :deep(.el-pagination .btn-next) {
  border-radius: 8px;
  height: 38px;
  min-width: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.woc-pagination :deep(.el-pager li) {
  border-radius: 8px;
  margin: 0 4px;
  height: 38px;
  min-width: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
}

.woc-pagination :deep(.el-pager li.is-active) {
  background: linear-gradient(135deg, #409eff 0%, #5cadff 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.woc-pagination :deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
}

.woc-pagination :deep(.el-pagination__total),
.woc-pagination :deep(.el-pagination__jump) {
  font-weight: 500;
  color: #606266;
}

@media (max-width: 1200px) {
  .woc-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .woc-header {
    flex-direction: column;
    gap: 16px;
    padding: 16px;
  }
  
  .woc-stats {
    grid-template-columns: repeat(2, 1fr);
    padding: 16px;
    gap: 12px;
  }
  
  .woc-stat {
    padding: 14px 16px;
  }
  
  .woc-main {
    margin: 0 16px 16px;
  }
  
  .woc-toolbar {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .woc-tabs {
    overflow-x: auto;
  }
  
  .woc-search {
    width: 100%;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .card-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
