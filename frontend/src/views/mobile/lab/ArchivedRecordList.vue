<template>
  <div class="mobile-page">
    <van-nav-bar
      :title="listHeader"
      left-arrow
      @click-left="goBack"
    >
      <template #right>
        <van-icon
          name="home-o"
          size="20"
          @click="goHome"
        />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-skeleton
        v-if="loading"
        :row="5"
        animated
      />

      <van-empty
        v-else-if="error"
        :description="error"
      >
        <van-button
          size="small"
          type="primary"
          round
          @click="loadData"
        >
          重试
        </van-button>
      </van-empty>

      <template v-else>
        <div
          v-if="!selectedType"
          class="type-selection"
        >
          <div class="type-header">
            <div class="term-badge">
              <van-icon
                name="certificate"
                size="14"
              />
              <span>{{ listHeader }}</span>
            </div>
            <p class="type-tip">
              请选择要查看的记录类型
            </p>
          </div>

          <div class="type-grid">
            <div
              class="type-card"
              @click="selectType('usage')"
            >
              <div class="type-icon usage">
                <van-icon
                  name="description"
                  size="24"
                />
              </div>
              <div class="type-info">
                <span class="type-name">使用记录</span>
                <span class="type-count">{{ stats.record_count || 0 }} 条</span>
              </div>
              <van-icon
                name="arrow"
                color="#C0C4CC"
                size="14"
              />
            </div>

            <div
              class="type-card"
              @click="selectType('maintain')"
            >
              <div class="type-icon maintain">
                <van-icon
                  name="setting-o"
                  size="24"
                />
              </div>
              <div class="type-info">
                <span class="type-name">维护记录</span>
                <span class="type-count">{{ stats.maintain_count || 0 }} 条</span>
              </div>
              <van-icon
                name="arrow"
                color="#C0C4CC"
                size="14"
              />
            </div>

            <div
              class="type-card"
              @click="selectType('fault')"
            >
              <div class="type-icon fault">
                <van-icon
                  name="warning-o"
                  size="24"
                />
              </div>
              <div class="type-info">
                <span class="type-name">故障记录</span>
                <span class="type-count">{{ stats.equipment_maintenance_count || 0 }} 条</span>
              </div>
              <van-icon
                name="arrow"
                color="#C0C4CC"
                size="14"
              />
            </div>

            <div
              class="type-card"
              @click="selectType('class')"
            >
              <div class="type-icon class">
                <van-icon
                  name="calendar-o"
                  size="24"
                />
              </div>
              <div class="type-info">
                <span class="type-name">课表记录</span>
                <span class="type-count">{{ stats.class_count || 0 }} 条</span>
              </div>
              <van-icon
                name="arrow"
                color="#C0C4CC"
                size="14"
              />
            </div>

            <div
              class="type-card"
              @click="selectType('lab_info')"
            >
              <div class="type-icon lab">
                <van-icon
                  name="cluster-o"
                  size="24"
                />
              </div>
              <div class="type-info">
                <span class="type-name">实训室信息</span>
                <span class="type-count">{{ stats.lab_count || 0 }} 条</span>
              </div>
              <van-icon
                name="arrow"
                color="#C0C4CC"
                size="14"
              />
            </div>

            <div
              class="type-card"
              @click="selectType('device_info')"
            >
              <div class="type-icon device">
                <van-icon
                  name="desktop-o"
                  size="24"
                />
              </div>
              <div class="type-info">
                <span class="type-name">设备信息</span>
                <span class="type-count">{{ stats.device_count || 0 }} 条</span>
              </div>
              <van-icon
                name="arrow"
                color="#C0C4CC"
                size="14"
              />
            </div>

            <div
              class="type-card"
              @click="selectType('user_info')"
            >
              <div class="type-icon user">
                <van-icon
                  name="friends-o"
                  size="24"
                />
              </div>
              <div class="type-info">
                <span class="type-name">用户信息</span>
                <span class="type-count">{{ stats.user_count || 0 }} 条</span>
              </div>
              <van-icon
                name="arrow"
                color="#C0C4CC"
                size="14"
              />
            </div>
          </div>
        </div>

        <div
          v-else
          class="list-container"
        >
          <van-empty
            v-if="objectList.length === 0"
            description="暂无记录"
          />

          <van-cell-group
            v-else
            inset
          >
            <van-cell
              v-for="(item, index) in objectList"
              :key="index"
              is-link
              @click="viewDetail(item)"
            >
              <template #title>
                <div class="record-title">
                  {{ item.title }}
                </div>
              </template>
              <template #label>
                <div class="record-info">
                  <span
                    v-if="item.sxsname"
                    class="info-item"
                  >{{ item.sxsname }}</span>
                  <span
                    v-if="item.date"
                    class="info-item"
                  >{{ item.date }}</span>
                </div>
              </template>
              <template #value>
                <van-tag
                  :type="getTypeColor(selectedType)"
                  size="small"
                >
                  {{ getTypeName(selectedType) }}
                </van-tag>
              </template>
            </van-cell>
          </van-cell-group>
        </div>

        <Pagination
          v-if="isPaginated && totalPages > 1"
          :show="isPaginated && totalPages > 1"
          :current-page="currentPage"
          :page-size="pageSize"
          :total-count="totalCount"
          @current-change="handlePageChange"
        />
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/core/api/client'
import { useNavigation } from '@/core/utils/routeDecision'
import Pagination from '@/views/mobile/components/Pagination.vue'

const route = useRoute()
const router = useRouter()
const { goHome } = useNavigation()

const loading = ref(false)
const error = ref('')
const objectList = ref([])
const listHeader = ref('归档记录')
const stats = ref({})
const isPaginated = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const pageSize = ref(10)

const selectedType = computed(() => route.query.type || null)

const getTypeName = (type) => {
  const typeMap = {
    'usage': '使用',
    'maintain': '维护',
    'fault': '故障',
    'class': '课表',
    'lab_info': '实训室',
    'device_info': '设备',
    'user_info': '用户'
  }
  return typeMap[type] || '记录'
}

const getTypeColor = (type) => {
  const colorMap = {
    'usage': 'primary',
    'maintain': 'success',
    'fault': 'danger',
    'class': 'warning',
    'lab_info': 'info',
    'device_info': 'default',
    'user_info': 'primary'
  }
  return colorMap[type] || 'default'
}

const selectType = (type) => {
  router.push({
    query: { ...route.query, type, page: 1 }
  })
}

const loadData = async () => {
  loading.value = true
  error.value = ''

  try {
    const id = route.params.id
    const type = route.query.type
    const page = route.query.page || 1

    const params = { page }
    if (type) {
      params.type = type
    }

    const response = await api.get(`/schedules/archived/${id}/`, params)

    if (response) {
      listHeader.value = response.semester_name || '归档记录'

      if (response.mode === 'dashboard' || !type) {
        stats.value = response.stats || {}
        objectList.value = []
        isPaginated.value = false
      } else {
        stats.value = {}
        isPaginated.value = response.total_pages > 1
        currentPage.value = response.page || 1
        totalPages.value = response.total_pages || 1
        totalCount.value = response.total || 0
        pageSize.value = response.page_size || 10

        if (response.list && Array.isArray(response.list)) {
          objectList.value = response.list.map((row, idx) => {
            const baseItem = {
              type: type,
              id: row.id || idx,
              sxsname: row.laboratory_name || row.lab_name || '',
              content: row.description || row.content || '',
              title: row.title || row.class_name || row.course_name || row.name || row.nickname || row.content || '暂无标题'
            }

            if (type === 'usage') {
              return {
                ...baseItem,
                date: row.usage_date || '',
                className: row.class_name || '',
                teacherName: row.teacher_name || row.operator || '',
                timeSlot: row.time_slot || ''
              }
            } else if (type === 'maintain' || type === 'fault') {
              return {
                ...baseItem,
                date: row.reported_at || row.completed_at || '',
                orderNumber: row.order_number || '',
                reporterName: row.reporter_name || '',
                handlerName: row.handler_name || '',
                status: row.status || row.status_display || '',
                priority: row.priority || ''
              }
            } else if (type === 'class') {
              return {
                ...baseItem,
                date: row.schedule_date || row.usage_date || '',
                courseName: row.course_name || '',
                teacherName: row.teacher_name || row.operator || ''
              }
            } else if (type === 'lab_info') {
              return {
                ...baseItem,
                deptName: row.department_name || '',
                location: row.location || ''
              }
            } else if (type === 'device_info') {
              return {
                ...baseItem,
                deviceCode: row.device_code || '',
                deviceType: row.device_type || ''
              }
            } else if (type === 'user_info') {
              return {
                ...baseItem,
                username: row.username || '',
                role: row.role || ''
              }
            }

            return baseItem
          })
        } else {
          objectList.value = []
        }
      }
    } else {
      error.value = '加载失败'
      objectList.value = []
    }
  } catch (err) {
    error.value = '加载失败'
    objectList.value = []
    console.error('Load data error:', err)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  router.push({
    query: { ...route.query, page }
  })
}

const viewDetail = (item) => {
  console.log('View detail:', item)
}

const goBack = () => router.go(-1)

watch(() => route.query, () => {
  loadData()
}, { immediate: false })

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.mobile-page {
  min-height: 100vh;
  background: #f7f8fa;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  padding-bottom: 100px;
}

.type-selection {
  padding: 0;
}

.type-header {
  text-align: center;
  padding: 20px 16px;
  margin-bottom: 12px;
}

.term-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: linear-gradient(135deg, #909399 0%, #7A7D83 100%);
  color: white;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
}

.type-tip {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.type-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 16px;
}

.type-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
  cursor: pointer;
}

.type-card:active {
  transform: scale(0.98);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.type-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.type-icon.usage { background: #F3E8FF; color: #9B59B6; }
.type-icon.maintain { background: #E8F8EE; color: #07C160; }
.type-icon.fault { background: #FFEBE9; color: #FF3B30; }
.type-icon.class { background: #FFF5E6; color: #FF9500; }
.type-icon.lab { background: #EBF7FD; color: #5AC8FA; }
.type-icon.device { background: #EEF2FF; color: #4F6EF7; }
.type-icon.user { background: #FFF0F0; color: #FF6B6B; }

.type-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.type-name {
  font-size: 15px;
  font-weight: 600;
  color: #303233;
}

.type-count {
  font-size: 12px;
  color: #909399;
}

.list-container {
  min-height: 300px;
}

.record-title {
  font-size: 15px;
  font-weight: 500;
  color: #323233;
}

.record-info {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 6px;
}

.info-item {
  font-size: 12px;
  color: #969799;
}

:deep(.pagination-wrapper) {
  margin-bottom: 60px;
}
</style>
