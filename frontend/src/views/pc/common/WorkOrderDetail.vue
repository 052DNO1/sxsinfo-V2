<!-- 工单详情页面 -->
<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="work-order-detail" v-loading="loading">
        <div class="wod-header">
          <div class="wod-title">
            <el-icon :size="28"><Tickets /></el-icon>
            <h2>{{ order && order.maintenance_type === 3 ? '工单详情' : '维护详情' }}</h2>
          </div>
          <div class="wod-actions">
            <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
            <el-button :icon="HomeFilled" @click="goHome">首页</el-button>
          </div>
        </div>

        <div class="wod-content" v-if="order">
          <!-- 基本信息卡片 -->
          <el-card class="wod-card info-card">
            <template #header>
              <div class="card-header-content">
                <span class="card-title">基本信息</span>
                <el-tag :type="getTagType(order.status)" size="large">
                  {{ getStatusLabel(order.status) }}
                </el-tag>
              </div>
            </template>
            
            <el-descriptions :column="2" border>
              <el-descriptions-item label="工单编号">
                <span class="order-number">{{ order.order_number || order.id }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="上报时间">
                <span>{{ order.reported_at }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="实训室名称">
                <span>{{ order.laboratory_name }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="实训室编码">
                <span>{{ order.laboratory_code || '-' }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="上报人">
                <div class="user-info">
                  <el-avatar :size="24" :style="{ background: getAvatarColor(order.reporter_name) }">
                    {{ getInitial(order.reporter_name) }}
                  </el-avatar>
                  <span>{{ order.reporter_name || '未知' }}</span>
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="工单标题">
                <span>{{ order.title }}</span>
              </el-descriptions-item>
            </el-descriptions>
            
            <div class="description-section">
              <div class="section-label">{{ order.maintenance_type === 3 ? '故障描述' : '维护描述' }}</div>
              <div class="description-box">{{ order.description }}</div>
            </div>
          </el-card>

          <!-- 处理信息卡片 -->
          <el-card class="wod-card" v-if="order.status !== 'PENDING'">
            <template #header>
              <span class="card-title">{{ order.maintenance_type === 3 ? '处理信息' : '维护信息' }}</span>
            </template>
            
            <el-descriptions :column="2" border>
              <el-descriptions-item label="处理人">
                <div class="user-info" v-if="order.handler_name">
                  <el-avatar :size="24" :style="{ background: getAvatarColor(order.handler_name) }">
                    {{ getInitial(order.handler_name) }}
                  </el-avatar>
                  <span>{{ order.handler_name }}</span>
                </div>
                <span v-else class="text-gray">暂无</span>
              </el-descriptions-item>
              
              <!-- 故障工单显示完整的时间信息 -->
              <template v-if="order.maintenance_type === 3">
                <el-descriptions-item label="开始处理时间">
                  <span>{{ order.handle_time || order.started_at || '暂无' }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="完成时间">
                  <span>{{ order.complete_time || order.completed_at || '暂无' }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="关闭时间">
                  <span>{{ order.close_time || order.closed_at || '暂无' }}</span>
                </el-descriptions-item>
              </template>
              
              <!-- 维护工单只显示完成时间 -->
              <template v-else>
                <el-descriptions-item label="完成时间">
                  <span>{{ order.complete_time || order.completed_at || order.close_time || order.closed_at || '暂无' }}</span>
                </el-descriptions-item>
              </template>
            </el-descriptions>
            
            <div class="description-section" v-if="order.solution">
              <div class="section-label">解决方案</div>
              <div class="description-box success">{{ order.solution }}</div>
            </div>
            
            <div class="description-section" v-if="order.handle_memo">
              <div class="section-label">处理备注</div>
              <div class="description-box">{{ order.handle_memo }}</div>
            </div>
          </el-card>

          <!-- 操作卡片 -->
          <el-card class="wod-card">
            <template #header>
              <span class="card-title">操作</span>
            </template>
            
            <div class="wod-actions-panel">
              <template v-if="order.status === 'PENDING' && canHandle">
                <el-alert type="warning" :closable="false" show-icon>
                  <template #title>该工单待处理，请点击下方按钮接单</template>
                </el-alert>
                <el-button type="primary" size="large" :icon="Tools" @click="startProcess">
                  接单处理
                </el-button>
              </template>
              
              <template v-else-if="order.status === 'PROCESSING' && canHandle">
                <el-alert type="info" :closable="false" show-icon>
                  <template #title>该工单正在处理中，处理完成后请点击下方按钮</template>
                </el-alert>
                <el-button type="success" size="large" :icon="CircleCheck" @click="showCompleteDialog = true">
                  完成修复
                </el-button>
              </template>
              
              <template v-else-if="order.status === 'COMPLETED' && canConfirm">
                <el-alert type="success" :closable="false" show-icon>
                  <template #title>该工单已修复完成，请确认后关闭</template>
                </el-alert>
                <el-button type="success" size="large" plain :icon="Finished" @click="confirmOrder">
                  确认关闭
                </el-button>
              </template>
              
              <template v-else-if="order.status === 'CLOSED'">
                <el-alert type="info" :closable="false" show-icon>
                  <template #title>该工单已关闭</template>
                </el-alert>
              </template>
              
              <template v-else>
                <el-alert type="info" :closable="false" show-icon>
                  <template #title>当前状态无可用操作</template>
                </el-alert>
              </template>
            </div>
          </el-card>

          <!-- 状态流转记录 -->
          <el-card class="wod-card">
            <template #header>
              <span class="card-title">{{ order.maintenance_type === 3 ? '状态流转记录' : '维护记录' }}</span>
            </template>
            
            <el-timeline>
              <el-timeline-item
                :timestamp="order.maintenance_type === 3 ? '上报工单' : '添加维护记录'"
                :type="'primary'"
                placement="top">
                <p>{{ order.reported_at }}</p>
                <p class="timeline-desc">{{ order.maintenance_type === 3 ? '上报人' : '添加人' }}：{{ order.reporter_name }}</p>
              </el-timeline-item>
              
              <!-- 故障工单显示完整时间线 -->
              <template v-if="order.maintenance_type === 3">
                <el-timeline-item
                  v-if="order.status !== 'PENDING'"
                  timestamp="开始处理"
                  :type="order.status === 'PROCESSING' ? 'primary' : 'success'"
                  :hollow="order.status === 'PROCESSING'"
                  placement="top">
                  <p>{{ order.handle_time || order.started_at || '-' }}</p>
                  <p class="timeline-desc">处理人：{{ order.handler_name || '-' }}</p>
                </el-timeline-item>
                
                <el-timeline-item
                  v-if="order.status === 'COMPLETED' || order.status === 'CLOSED'"
                  timestamp="已完成"
                  :type="order.status === 'CLOSED' ? 'success' : 'primary'"
                  :hollow="order.status === 'COMPLETED'"
                  placement="top">
                  <p>{{ order.complete_time || order.completed_at || '-' }}</p>
                  <p class="timeline-desc" v-if="order.handle_memo">备注：{{ order.handle_memo }}</p>
                </el-timeline-item>
                
                <el-timeline-item
                  v-if="order.status === 'CLOSED'"
                  timestamp="已关闭"
                  type="success"
                  placement="top">
                  <p>{{ order.close_time || order.closed_at || '-' }}</p>
                  <p class="timeline-desc">上报人确认关闭</p>
                </el-timeline-item>
              </template>
              
              <!-- 维护工单显示简化时间线 -->
              <template v-else>
                <el-timeline-item
                  v-if="order.status !== 'PENDING'"
                  timestamp="已完成"
                  type="success"
                  placement="top">
                  <p>{{ order.complete_time || order.completed_at || order.close_time || order.closed_at || '-' }}</p>
                  <p class="timeline-desc" v-if="order.handle_memo">备注：{{ order.handle_memo }}</p>
                  <p class="timeline-desc">处理人：{{ order.handler_name || '-' }}</p>
                </el-timeline-item>
              </template>
            </el-timeline>
          </el-card>
        </div>

        <el-dialog v-model="showCompleteDialog" title="完成修复" width="500px" destroy-on-close>
          <el-form :model="completeForm" label-width="80px">
            <el-form-item label="处理备注">
              <el-input 
                v-model="completeForm.memo" 
                type="textarea" 
                :rows="4"
                placeholder="请填写处理情况..." />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="showCompleteDialog = false">取消</el-button>
            <el-button type="primary" @click="submitComplete">确认完成</el-button>
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
import { 
  Tickets, ArrowLeft, HomeFilled, Tools, CircleCheck, Finished
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const { goHome } = useNavigation()
const { user, isSxsAdmin, isDepartAdmin, isTeacher } = useAuth()

const orderId = route.params.id
const { loading, get: fetchOrder } = useApi(`/work-orders/center/${orderId}/`, { immediate: false })
const { post: updateOrderStatus } = useApi(`/work-orders/center/${orderId}/`, { immediate: false })

const order = ref(null)
const showCompleteDialog = ref(false)
const completeForm = ref({ memo: '' })

const canHandle = computed(() => {
  if (!user.value || !order.value) return false
  return isSxsAdmin.value || isDepartAdmin.value
})

const canConfirm = computed(() => {
  if (!user.value || !order.value) return false
  return order.value.reporter_id === user.value.id
})

const goBack = () => {
  router.push('/workorder-center')
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

const loadData = async () => {
  try {
    const response = await fetchOrder()
    
    if (response && response.success && response.data) {
      order.value = response.data.order || response.data
    }
  } catch (err) {
    showError('加载工单失败')
  }
}

const startProcess = async () => {
  try {
    const response = await updateOrderStatus({ status: 'processing' })
    if (response && response.success) {
      showSuccess('已接单，请尽快处理')
      loadData()
    }
  } catch (err) {
    showError('操作失败')
  }
}

const submitComplete = async () => {
  try {
    const response = await updateOrderStatus({ 
      status: 'completed',
      memo: completeForm.value.memo 
    })
    
    if (response && response.success) {
      showSuccess('已标记为完成，等待上报人确认')
      showCompleteDialog.value = false
      loadData()
    }
  } catch (err) {
    showError('操作失败')
  }
}

const confirmOrder = async () => {
  try {
    const response = await updateOrderStatus({ status: 'closed' })
    if (response && response.success) {
      showSuccess('工单已关闭')
      loadData()
    }
  } catch (err) {
    showError('操作失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.work-order-detail {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
}

.wod-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 32px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.wod-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.wod-title .el-icon {
  color: #e6a23c;
}

.wod-title h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.wod-actions {
  display: flex;
  gap: 12px;
}

.wod-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.wod-card {
  border-radius: 12px;
  overflow: visible;
}

.wod-card :deep(.el-card__header) {
  padding: 16px 20px;
  background: #fafbfc;
}

.wod-card :deep(.el-card__body) {
  padding: 24px;
  overflow: visible;
}

.card-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.order-number {
  font-family: 'Monaco', 'Menlo', monospace;
  color: #409eff;
  font-weight: 600;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.text-gray {
  color: #909399;
}

.description-section {
  margin-top: 20px;
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 12px;
}

.description-box {
  padding: 16px 20px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  min-height: 60px;
  word-break: break-all;
  border-left: 3px solid #dcdfe6;
}

.description-box.success {
  background: #f0f9eb;
  border-left-color: #67c23a;
  color: #529b2e;
}

.wod-actions-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
  padding: 20px;
  min-height: 120px;
}

.wod-actions-panel .el-alert {
  width: 100%;
  padding: 12px 16px;
}

.wod-actions-panel .el-button {
  min-width: 200px !important;
  height: 52px !important;
  font-size: 16px !important;
  padding: 14px 28px !important;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.wod-actions-panel .el-button .el-icon {
  margin-right: 8px;
  font-size: 18px;
}

.timeline-desc {
  font-size: 13px;
  color: #909399;
  margin-top: 6px;
}

@media (max-width: 768px) {
  .wod-header {
    flex-direction: column;
    gap: 16px;
    padding: 16px;
  }
  
  .wod-content {
    padding: 16px;
  }
}
</style>
