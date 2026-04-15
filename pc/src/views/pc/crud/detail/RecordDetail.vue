<template>
  <Index class="pc-layout">
    <template #rightcontent>
      <div class="detail-container">
        <div class="detail-header">
          <div class="header-left">
            <el-button :icon="Back" @click="goBack" circle />
            <div class="header-info">
              <h2>{{ title }}</h2>
              <p>{{ subtitle }}</p>
            </div>
          </div>
          <div class="header-right">
            <el-tag :type="statusTag.type" size="large">{{ statusTag.text }}</el-tag>
          </div>
        </div>

        <div class="detail-content" v-loading="loading">
          <el-card class="info-card" shadow="never">
            <template #header>
              <div class="card-header">
                <el-icon><InfoFilled /></el-icon>
                <span>基本信息</span>
              </div>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item
                v-for="field in basicFields"
                :key="field.label"
                :label="field.label"
              >
                <template v-if="field.type === 'status'">
                  <el-tag :type="getStatusType(detailData[field.prop])">
                    {{ field.options?.[detailData[field.prop]] || detailData[field.prop] || '-' }}
                  </el-tag>
                </template>
                <template v-else-if="field.type === 'date'">
                  {{ formatDate(detailData[field.prop]) }}
                </template>
                <template v-else-if="field.type === 'datetime'">
                  {{ formatDateTime(detailData[field.prop]) }}
                </template>
                <template v-else>
                  {{ detailData[field.prop] || '-' }}
                </template>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-card class="info-card" shadow="never" v-if="contentField">
            <template #header>
              <div class="card-header">
                <el-icon><Document /></el-icon>
                <span>{{ contentField.label }}</span>
              </div>
            </template>
            <div class="content-text">
              {{ detailData[contentField.prop] || '暂无内容' }}
            </div>
          </el-card>

          <el-card class="info-card" shadow="never" v-if="extraFields.length > 0">
            <template #header>
              <div class="card-header">
                <el-icon><MoreFilled /></el-icon>
                <span>附加信息</span>
              </div>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item
                v-for="field in extraFields"
                :key="field.label"
                :label="field.label"
              >
                {{ detailData[field.prop] || '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </div>
      </div>
    </template>
  </Index>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Index from '@/views/pc/dashboard/Index.vue'
import { useApi } from '@/core/hooks'
import { Back, InfoFilled, Document, MoreFilled } from '@element-plus/icons-vue'
import { showError } from '@/core/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const api = useApi('', { immediate: false })

const loading = ref(true)
const detailData = ref({})

const recordType = computed(() => {
  const type = route.params.type
  if (type === 'workorder') return 'workorder'
  if (type === 'maintain' || type === 'maintenance_record') return 'maintain'
  return 'usage'
})

const title = computed(() => {
  const titles = {
    usage: '使用记录详情',
    maintain: '维护记录详情',
    workorder: '故障工单详情'
  }
  return titles[recordType.value]
})

const subtitle = computed(() => {
  return detailData.value.order_number || detailData.value.laboratory_name || detailData.value.title || ''
})

const statusTag = computed(() => {
  const data = detailData.value
  if (recordType.value === 'workorder') {
    const statusMap = {
      'PENDING': { type: 'warning', text: '待处理' },
      'PROCESSING': { type: 'primary', text: '处理中' },
      'COMPLETED': { type: 'success', text: '已完成' },
      'CLOSED': { type: 'info', text: '已关闭' }
    }
    return statusMap[data.status] || { type: 'info', text: data.status || '未知' }
  }
  if (recordType.value === 'maintain') {
    const statusMap = {
      'maintained': { type: 'success', text: '已维护' },
      'pending': { type: 'warning', text: '待维护' },
      'processing': { type: 'primary', text: '维护中' }
    }
    return statusMap[data.status] || { type: 'info', text: data.status_display || data.status || '未知' }
  }
  return { type: 'success', text: '正常' }
})

const basicFields = computed(() => {
  const fields = {
    usage: [
      { label: '实训室', prop: 'laboratory_name' },
      { label: '使用日期', prop: 'usage_date', type: 'date' },
      { label: '节次', prop: 'time_slot' },
      { label: '课时', prop: 'class_hours' },
      { label: '教师', prop: 'teacher_name' },
      { label: '班级', prop: 'class_name' },
      { label: '学生人数', prop: 'student_count' },
      { label: '学期', prop: 'semester_name' }
    ],
    maintain: [
      { label: '工单编号', prop: 'order_number' },
      { label: '工单类型', prop: 'order_type_display' },
      { label: '实训室', prop: 'laboratory_name' },
      { label: '维护人', prop: 'maintainer_name' },
      { label: '状态', prop: 'status', type: 'status', options: { 'maintained': '已维护', 'pending': '待维护', 'processing': '维护中' } },
      { label: '维护时间', prop: 'maintenance_time', type: 'datetime' },
      { label: '学期', prop: 'semester_name' }
    ],
    workorder: [
      { label: '工单标题', prop: 'title' },
      { label: '实训室', prop: 'laboratory_name' },
      { label: '设备', prop: 'equipment_name' },
      { label: '维护类型', prop: 'maintenance_type_display' },
      { label: '优先级', prop: 'priority' },
      { label: '上报人', prop: 'reporter_name' },
      { label: '处理人', prop: 'handler_name' },
      { label: '上报时间', prop: 'reported_at', type: 'datetime' },
      { label: '完成时间', prop: 'completed_at', type: 'datetime' }
    ]
  }
  return fields[recordType.value] || []
})

const contentField = computed(() => {
  const fields = {
    usage: { label: '实训内容', prop: 'content' },
    maintain: { label: '维护内容', prop: 'content' },
    workorder: { label: '问题描述', prop: 'description' }
  }
  return fields[recordType.value]
})

const extraFields = computed(() => {
  if (recordType.value === 'workorder') {
    return [
      { label: '解决方案', prop: 'solution' },
      { label: '处理备注', prop: 'handle_note' },
      { label: '评分', prop: 'rating' },
      { label: '反馈', prop: 'feedback' }
    ]
  }
  return [
    { label: '备注', prop: 'note' },
    { label: '创建时间', prop: 'created_at' }
  ]
})

const apiUrls = {
  usage: '/records/',
  maintain: '/work-orders/records/',
  workorder: '/work-orders/'
}

const loadData = async () => {
  loading.value = true
  try {
    const id = route.params.id
    if (!id) {
      showError('缺少记录ID')
      return
    }
    
    const url = apiUrls[recordType.value] || apiUrls.usage
    const response = await api.get({}, { url: `${url}${id}/` })
    
    if (response) {
      detailData.value = response.data || response
    }
  } catch (err) {
    showError('加载详情失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const formatDate = (date) => {
  if (!date) return '-'
  return date.split('T')[0]
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return datetime.replace('T', ' ').split('.')[0]
}

const getStatusType = (status) => {
  const typeMap = {
    'NORMAL': 'success',
    'MAINTENANCE': 'warning',
    'DAMAGED': 'danger'
  }
  return typeMap[status] || 'info'
}

onMounted(loadData)
</script>

<style scoped>
.detail-container {
  padding: 0;
  max-width: 1200px;
  margin: 0 auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: #fff;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-info h2 {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.header-info p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.content-text {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #606266;
  padding: 8px 0;
}

:deep(.el-descriptions__label) {
  width: 120px;
  font-weight: 500;
}

:deep(.el-descriptions__content) {
  word-break: break-all;
}
</style>
