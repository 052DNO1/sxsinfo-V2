<template>
  <MobileLayout>
    <div class="mobile-page">
      <van-nav-bar title="操作日志" left-arrow @click-left="goBack">
        <template #right><van-icon name="home-o" size="20" color="#4F6EF7" @click="goHome" /></template>
      </van-nav-bar>

      <div class="page-content">
        <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
          <div class="stats-row">
            <div class="stat-item">
              <div class="stat-value">{{ stats.total_count || 0 }}</div>
              <div class="stat-label">总操作数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value highlight">{{ stats.today_count || 0 }}</div>
              <div class="stat-label">今日操作</div>
            </div>
            <div class="stat-item">
              <div class="stat-value success">{{ stats.week_count || 0 }}</div>
              <div class="stat-label">近7天</div>
            </div>
          </div>

          <van-cell-group inset title="筛选">
            <van-field
              v-model="filters.search"
              placeholder="搜索操作描述/操作人"
              left-icon="search"
              clearable
              @clear="loadLogList"
              @keyup.enter="loadLogList"
            />
            <van-field
              v-model="filters.module"
              is-link
              readonly
              label="模块"
              placeholder="全部模块"
              @click="showModulePicker = true"
            />
          </van-cell-group>

          <van-list
            v-model:loading="loading"
            :finished="finished"
            finished-text="没有更多了"
            @load="loadLogList"
          >
            <van-cell-group inset title="日志列表">
              <van-cell
                v-for="log in logList"
                :key="log.id"
                :label="formatTime(log.created_at)"
                clickable
                @click="showDetail(log)"
              >
                <template #title>
                  <van-tag :type="getModuleTagType(log.module)" size="small">{{ log.module_display }}</van-tag>
                  <span class="log-title">{{ log.operation_type_display }}</span>
                </template>
                <template #value>
                  <span class="operator">{{ log.operator_username || '系统' }}</span>
                </template>
                <template #label>
                  <div class="log-desc">{{ log.description || '-' }}</div>
                  <div class="log-target" v-if="log.target_name">目标: {{ log.target_name }}</div>
                </template>
              </van-cell>
            </van-cell-group>
          </van-list>

          <van-empty v-if="!loading && logList.length === 0" description="暂无操作日志" />
        </van-pull-refresh>
      </div>

      <van-popup v-model:show="showModulePicker" position="bottom" round>
        <van-picker
          title="选择模块"
          :columns="moduleOptions"
          @confirm="onModuleConfirm"
          @cancel="showModulePicker = false"
        />
      </van-popup>

      <van-popup v-model:show="detailVisible" position="bottom" round style="max-height: 70vh;">
        <div class="detail-popup" v-if="currentLog">
          <div class="detail-header">
            <h3>操作日志详情</h3>
          </div>
          <van-cell-group inset>
            <van-cell title="操作时间" :value="formatTime(currentLog.created_at)" />
            <van-cell title="操作人" :value="currentLog.operator_username || '系统'" />
            <van-cell title="模块">
              <template #value>
                <van-tag :type="getModuleTagType(currentLog.module)" size="small">{{ currentLog.module_display }}</van-tag>
              </template>
            </van-cell>
            <van-cell title="操作类型" :value="currentLog.operation_type_display" />
            <van-cell title="目标对象" :value="currentLog.target_name || '-'" />
            <van-cell title="IP地址" :value="currentLog.ip_address || '-'" />
            <van-cell title="操作描述" :value="currentLog.description || '-'" />
          </van-cell-group>
          <div class="detail-json" v-if="currentLog.detail">
            <div class="json-label">详细信息</div>
            <pre>{{ JSON.stringify(currentLog.detail, null, 2) }}</pre>
          </div>
        </div>
      </van-popup>
    </div>
  </MobileLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNavigation } from '@/core/utils/routeDecision'
import { useApi } from '@/core/hooks'
import MobileLayout from '@/views/mobile/components/MobileLayout.vue'

const router = useRouter()
const { goBack, goHome } = useNavigation()
const { get } = useApi()

const refreshing = ref(false)
const loading = ref(false)
const finished = ref(false)
const showModulePicker = ref(false)
const detailVisible = ref(false)

const stats = ref({ total_count: 0, today_count: 0, week_count: 0 })
const filters = reactive({ search: '', module: '' })
const logList = ref([])
const currentLog = ref(null)

const moduleOptions = [
  { text: '全部模块', value: '' },
  { text: '用户管理', value: 'user' },
  { text: '设备管理', value: 'equipment' },
  { text: '课表管理', value: 'schedule' },
  { text: '部门管理', value: 'department' },
  { text: '实训室管理', value: 'laboratory' },
  { text: '系统设置', value: 'system' }
]

const getModuleTagType = (module) => {
  const typeMap = {
    'user': 'primary',
    'equipment': 'success',
    'schedule': 'warning',
    'department': '',
    'laboratory': 'success',
    'system': 'danger',
    'cache_config': 'info',
    'backup': 'info'
  }
  return typeMap[module] || 'default'
}

const formatTime = (datetime) => {
  if (!datetime) return '-'
  const date = new Date(datetime)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const loadStats = async () => {
  try {
    const res = await get({}, { url: '/operation-logs/stats/' })
    if (res?.data) stats.value = res.data
  } catch (e) {
    console.error('加载统计失败:', e)
  }
}

const loadLogList = async () => {
  loading.value = true
  try {
    const params = { page: 1, page_size: 20 }
    if (filters.search) params.search = filters.search
    if (filters.module) params.module = filters.module

    const res = await get({}, { url: '/operation-logs/', params })
    if (res?.data) {
      logList.value = res.data.list || []
      finished.value = true
    }
  } catch (e) {
    console.error('加载日志失败:', e)
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const onRefresh = async () => {
  await loadStats()
  await loadLogList()
}

const onModuleConfirm = ({ selectedValues }) => {
  filters.module = selectedValues[0]
  showModulePicker.value = false
  loadLogList()
}

const showDetail = async (log) => {
  try {
    const res = await get({}, { url: `/operation-logs/${log.id}/` })
    if (res?.data) {
      currentLog.value = res.data
      detailVisible.value = true
    }
  } catch (e) {
    console.error('获取详情失败:', e)
  }
}

onMounted(() => {
  loadStats()
  loadLogList()
})
</script>

<style scoped>
.mobile-page { min-height: 100vh; background: #f7f8fa; }
.page-content { padding: 12px; padding-bottom: 60px; }

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}
.stat-item {
  background: #fff;
  border-radius: 8px;
  padding: 12px 8px;
  text-align: center;
}
.stat-value { font-size: 20px; font-weight: 600; color: #323233; }
.stat-value.highlight { color: #1989fa; }
.stat-value.success { color: #07c160; }
.stat-label { font-size: 12px; color: #969799; margin-top: 4px; }

.log-title { margin-left: 8px; font-weight: 500; }
.operator { font-size: 12px; color: #969799; }
.log-desc { font-size: 12px; color: #646266; margin-top: 4px; }
.log-target { font-size: 11px; color: #969799; margin-top: 2px; }

.detail-popup { padding: 16px; }
.detail-header { text-align: center; padding-bottom: 12px; border-bottom: 1px solid #eee; margin-bottom: 12px; }
.detail-header h3 { margin: 0; font-size: 16px; }
.detail-json { margin-top: 12px; padding: 12px; background: #f7f8fa; border-radius: 8px; }
.json-label { font-size: 13px; font-weight: 500; margin-bottom: 8px; }
.detail-json pre { margin: 0; font-size: 11px; white-space: pre-wrap; word-break: break-all; }
</style>
