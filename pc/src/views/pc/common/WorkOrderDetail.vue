<!-- 工单详情页面 -->
<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="work-order-detail" v-loading="loading">
        <div class="wod-header">
          <div class="wod-title">
            <el-icon :size="28"><Tickets /></el-icon>
            <h2>工单详情</h2>
          </div>
          <div class="wod-actions">
            <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
            <el-button :icon="HomeFilled" @click="goHome">首页</el-button>
          </div>
        </div>

        <div class="wod-content" v-if="order">
          <el-card class="wod-card">
            <template #header>
              <div class="card-header">
                <el-tag :type="getTagType(order.status)" size="large">
                  {{ getStatusLabel(order.status) }}
                </el-tag>
                <span class="order-id">工单编号·{{ order.id }}</span>
              </div>
            </template>

            <div class="wod-info">
              <div class="info-row">
                <div class="info-item">
                  <label>实训室名称</label>
                  <span>{{ order.laboratory_name || order.sxsname }}</span>
                </div>
                <div class="info-item">
                  <label>门牌号</label>
                  <span>{{ order.room_number || order.sxsno }}</span>
                </div>
              </div>
              <div class="info-row">
                <div class="info-item">
                  <label>上报人</label> 
                  <span>{{ order.requester_name || order.maintainrequester_name }}</span>
                </div>
                <div class="info-item">
                  <label>上报时间</label>
                  <span>{{ order.created_at || order.maintainrequestdate }}</span>
                </div>
              </div>
              <div class="info-row full">
                <div class="info-item">
                  <label>故障内容</label>
                  <div class="content-box">{{ order.content || order.maintainrecordcontent }}</div>
                </div>
              </div>
            </div>
          </el-card>

          <el-card class="wod-card" v-if="order.status !== 'pending'">
            <template #header>
              <span class="card-title">处理信息</span>
            </template>
            <div class="wod-info">
              <div class="info-row">
                <div class="info-item">
                  <label>处理人</label>
                  <span>{{ order.handler_name || '暂无' }}</span>
                </div>
                <div class="info-item">
                  <label>接单时间</label>
                  <span>{{ order.handle_time || '暂无' }}</span>
                </div>
              </div>
              <div class="info-row">
                <div class="info-item">
                  <label>完成时间</label>
                  <span>{{ order.complete_time || '暂无' }}</span>
                </div>
                <div class="info-item">
                  <label>关闭时间</label>
                  <span>{{ order.close_time || '暂无' }}</span>
                </div>
              </div>
              <div class="info-row full" v-if="order.solution || order.handle_memo">
                <div class="info-item">
                  <label>处理备注</label>
                  <div class="content-box">{{ order.solution || order.handle_memo }}</div>
                </div>
              </div>
            </div>
          </el-card>

          <el-card class="wod-card" v-if="!isFromFaultList">
            <template #header>
              <span class="card-title">操作</span>
            </template>
            <div class="wod-actions-panel">
              <template v-if="order.status === 'pending' && canHandle">
                <el-alert type="warning" :closable="false" show-icon>
                  <template #title>该工单待处理，请点击下方按钮接单</template>
                </el-alert>
                <el-button type="primary" size="large" :icon="Tools" @click="startProcess">
                  接单处理
                </el-button>
              </template>
              
              <template v-else-if="order.status === 'processing' && canHandle">
                <el-alert type="info" :closable="false" show-icon>
                  <template #title>该工单正在处理中，处理完成后请点击下方按钮</template>
                </el-alert>
                <el-button type="success" size="large" :icon="CircleCheck" @click="showCompleteDialog = true">
                  完成修复
                </el-button>
              </template>
              
              <template v-else-if="order.status === 'completed' && canConfirm">
                <el-alert type="success" :closable="false" show-icon>
                  <template #title>该工单已修复完成，请确认后关闭</template>
                </el-alert>
                <el-button type="success" size="large" plain :icon="Finished" @click="confirmOrder">
                  确认关闭
                </el-button>
              </template>
              
              <template v-else-if="order.status === 'closed'">
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

          <el-card class="wod-card">
            <template #header>
              <span class="card-title">状态流转记录</span>
            </template>
            <el-timeline>
              <el-timeline-item
                timestamp="待处理"
                :type="order.status !== 'pending' ? 'success' : 'primary'"
                :hollow="order.status === 'pending'">
                <p>{{ order.created_at || order.maintainrequestdate }}</p>
                <p class="timeline-desc">上报人：{{ order.requester_name || order.maintainrequester_name }}</p>
              </el-timeline-item>
              <el-timeline-item
                v-if="order.status !== 'pending'"
                timestamp="处理中"
                :type="order.status !== 'processing' ? 'success' : 'primary'"
                :hollow="order.status === 'processing'">
                <p>{{ order.handle_time || '-' }}</p>
                <p class="timeline-desc">处理人：{{ order.handler_name || '-' }}</p>
              </el-timeline-item>
              <el-timeline-item
                v-if="order.status === 'completed' || order.status === 'closed'"
                timestamp="已完成"
                :type="order.status === 'closed' ? 'success' : 'primary'"
                :hollow="order.status === 'completed'">
                <p>{{ order.complete_time || '-' }}</p>
                <p class="timeline-desc" v-if="order.solution || order.handle_memo">备注：{{ order.solution || order.handle_memo }}</p>
              </el-timeline-item>
              <el-timeline-item
                v-if="order.status === 'closed'"
                timestamp="已关闭"
                type="success">
                <p>{{ order.close_time || '-' }}</p>
                <p class="timeline-desc">上报人确认关闭</p>
              </el-timeline-item>
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
const { loading, get: fetchOrder } = useApi(`/work-orders/${orderId}/`, { immediate: false })
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
  return order.value.requester === user.value.id || order.value.maintainrequester === user.value.id
})

const isFromFaultList = computed(() => {
  return route.query.from === 'fault-list'
})

const goBack = () => {
  if (route.query.from === 'fault-list') {
    router.back()
  } else {
    router.push('/workorder-center')
  }
}

const getStatusLabel = (status) => {
  const labels = {
    'pending': '待处理',
    'processing': '处理中',
    'completed': '已完成',
    'closed': '已关闭'
  }
  return labels[status] || status
}

const getTagType = (status) => {
  const types = {
    'pending': 'warning',
    'processing': 'primary',
    'completed': 'success',
    'closed': 'info'
  }
  return types[status] || 'info'
}

const loadData = async () => {
  try {
    const response = await fetchOrder()
    if (response) {
      order.value = response.order || response
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-id {
  font-size: 14px;
  color: #909399;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.wod-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
}

.info-row.full {
  grid-template-columns: 1fr;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
}

.info-item label {
  font-size: 14px;
  color: #909399;
  flex-shrink: 0;
}

.info-item span {
  font-size: 15px;
  color: #303133;
  word-break: break-all;
}

.content-box {
  padding: 14px 18px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  min-height: 60px;
  word-break: break-all;
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
  
  .info-row {
    grid-template-columns: 1fr;
  }
}
</style>
