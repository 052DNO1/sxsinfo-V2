<template>
  <MobileLayout>
    <div class="mobile-page">
      <van-nav-bar
        title="学期归档"
        left-arrow
        @click-left="goBack"
      >
        <template #right>
          <van-icon
            name="home-o"
            size="20"
            color="#4F6EF7"
            @click="goHome"
          />
        </template>
      </van-nav-bar>

      <div class="page-content">
        <div
          v-if="currentTerm"
          class="archive-hero animate-fade-in-up"
        >
          <div
            class="current-term-card"
            :class="{ archived: currentTerm.is_archived }"
          >
            <div
              class="card-badge"
              :class="currentTerm.is_archived ? 'archived' : 'current'"
            >
              {{ currentTerm.is_archived ? '已归档' : '当前学期' }}
            </div>
            <h3>{{ currentTerm.name }}</h3>
            <p>{{ currentTerm.start_date }} ~ {{ currentTerm.end_date }}</p>
          </div>
        </div>
        <div
          v-else
          class="empty-current animate-fade-in-up"
        >
          <van-icon
            name="warning-o"
            size="24"
            color="#FF9500"
          />
          <span>未设置当前学期</span>
        </div>

        <div
          v-if="currentTermStats"
          class="stats-section animate-fade-in-up animate-delay-1"
        >
          <div class="section-label">
            <span>📊</span> 学期数据统计
          </div>
          <div class="stats-grid">
            <div class="stat-card">
              <van-icon
                name="cluster-o"
                size="20"
                color="#07C160"
              />
              <div class="stat-info">
                <span class="stat-value">{{ currentTermStats.lab_count || 0 }}</span>
                <span class="stat-label">实训室</span>
              </div>
            </div>
            <div class="stat-card">
              <van-icon
                name="desktop-o"
                size="20"
                color="#5AC8FA"
              />
              <div class="stat-info">
                <span class="stat-value">{{ currentTermStats.device_count || 0 }}</span>
                <span class="stat-label">设备</span>
              </div>
            </div>
            <div class="stat-card">
              <van-icon
                name="friends-o"
                size="20"
                color="#4F6EF7"
              />
              <div class="stat-info">
                <span class="stat-value">{{ currentTermStats.user_count || 0 }}</span>
                <span class="stat-label">用户</span>
              </div>
            </div>
            <div class="stat-card">
              <van-icon
                name="description"
                size="20"
                color="#9B59B6"
              />
              <div class="stat-info">
                <span class="stat-value">{{ currentTermStats.record_count || 0 }}</span>
                <span class="stat-label">使用记录</span>
              </div>
            </div>
            <div class="stat-card">
              <van-icon
                name="calendar-o"
                size="20"
                color="#FF9500"
              />
              <div class="stat-info">
                <span class="stat-value">{{ currentTermStats.class_count || 0 }}</span>
                <span class="stat-label">课表记录</span>
              </div>
            </div>
            <div class="stat-card">
              <van-icon
                name="setting-o"
                size="20"
                color="#FF3B30"
              />
              <div class="stat-info">
                <span class="stat-value">{{ currentTermStats.maintain_count || 0 }}</span>
                <span class="stat-label">维护记录</span>
              </div>
            </div>
          </div>
        </div>

        <div
          v-if="termList.length > 0"
          class="info-section animate-fade-in-up animate-delay-2"
        >
          <div class="section-label">
            <span>📦</span> 历史学期
          </div>
          <div class="term-list">
            <div
              v-for="item in termList"
              :key="item.id"
              class="term-card"
              :class="{ archived: item.is_archived }"
            >
              <div class="term-name">
                {{ item.name || item.termname }}
              </div>
              <div class="term-date">
                {{ item.start_date }} ~ {{ item.end_date }}
              </div>
              <span
                v-if="item.is_archived"
                class="status-tag success"
              >已归档</span>
            </div>
          </div>
        </div>

        <template v-if="!currentTerm?.is_archived && canArchive">
          <div class="archive-section animate-fade-in-up animate-delay-3">
            <div class="section-label">
              <span>⚙️</span> 选择归档数据类型
            </div>
            <p class="section-desc">
              归档后数据会从业务表物理删除，仅保留在归档表中
            </p>

            <div class="options-list">
              <div
                class="option-card"
                :class="{ selected: archiveTypes.lab_info }"
                @click="toggleArchiveType('lab_info')"
              >
                <div class="option-checkbox">
                  <van-checkbox
                    :model-value="archiveTypes.lab_info"
                    shape="square"
                  />
                </div>
                <div class="option-icon lab">
                  <van-icon
                    name="cluster-o"
                    size="22"
                  />
                </div>
                <div class="option-info">
                  <span class="option-title">实训室信息</span>
                  <span class="option-count">
                    实训室{{ currentTermStats?.lab_count || 0 }} / 设备{{ currentTermStats?.device_count || 0 }}
                  </span>
                  <span class="option-count">
                    使用记录{{ currentTermStats?.record_count || 0 }} / 课表{{ currentTermStats?.class_count || 0 }}
                  </span>
                  <span class="option-count">
                    维护{{ currentTermStats?.maintain_count || 0 }} / 故障{{ currentTermStats?.equipment_maintenance_count || 0 }}
                  </span>
                </div>
              </div>

              <div
                class="option-card"
                :class="{ selected: archiveTypes.device_info }"
                @click="toggleArchiveType('device_info')"
              >
                <div class="option-checkbox">
                  <van-checkbox
                    :model-value="archiveTypes.device_info"
                    shape="square"
                  />
                </div>
                <div class="option-icon device">
                  <van-icon
                    name="desktop-o"
                    size="22"
                  />
                </div>
                <div class="option-info">
                  <span class="option-title">设备信息</span>
                  <span class="option-count">{{ currentTermStats?.device_count || 0 }} 台设备</span>
                </div>
              </div>

              <div
                class="option-card"
                :class="{ selected: archiveTypes.user_info }"
                @click="toggleArchiveType('user_info')"
              >
                <div class="option-checkbox">
                  <van-checkbox
                    :model-value="archiveTypes.user_info"
                    shape="square"
                  />
                </div>
                <div class="option-icon user">
                  <van-icon
                    name="friends-o"
                    size="22"
                  />
                </div>
                <div class="option-info">
                  <span class="option-title">用户信息</span>
                  <span class="option-count">{{ currentTermStats?.user_count || 0 }} 个用户（仅复制，不删除）</span>
                </div>
              </div>
            </div>

            <div
              v-if="departments.length > 0"
              class="dept-section"
            >
              <div class="section-label">
                <span>🏢</span> 按部门筛选（可选）
              </div>
              <van-field
                v-model="selectedDepartmentName"
                is-link
                readonly
                placeholder="选择部门"
                @click="showDeptPicker = true"
              />
              <van-popup
                v-model:show="showDeptPicker"
                position="bottom"
                round
              >
                <van-picker
                  :columns="departmentColumns"
                  @confirm="handleDeptConfirm"
                  @cancel="showDeptPicker = false"
                />
              </van-popup>
            </div>

            <div class="action-buttons">
              <van-button
                type="danger"
                size="large"
                :loading="loading"
                :disabled="!hasSelectedTypes"
                round
                @click="handleArchive"
              >
                <template #icon>
                  <van-icon name="lock" />
                </template>
                确认归档当前学期
              </van-button>
            </div>
          </div>

          <div class="tips-section animate-fade-in-up animate-delay-4">
            <div class="tips-header">
              <van-icon
                name="warning-o"
                size="16"
              /> 重要提示
            </div>
            <ul class="tips-list">
              <li>实训室归档会同时归档设备、使用记录、课表、工单</li>
              <li>归档后数据会从业务表物理删除，仅保留在归档表</li>
              <li>用户信息归档仅复制数据，不删除用户</li>
              <li>归档操作不可逆，请谨慎操作</li>
            </ul>
          </div>
        </template>

        <div
          v-else-if="currentTerm?.is_archived"
          class="archived-notice animate-fade-in-up"
        >
          <van-icon
            name="lock"
            size="48"
            color="#909399"
          />
          <h4>当前学期已归档</h4>
          <p>归档后的数据只能查看，不能修改。如需修改请联系超级管理员。</p>
          <van-button
            type="primary"
            size="small"
            @click="router.push('/archived-terms')"
          >
            查看归档记录
          </van-button>
        </div>

        <div
          v-if="canArchive && !currentTerm?.is_archived"
          class="quick-actions animate-fade-in-up animate-delay-2"
        >
          <div
            class="action-card primary"
            @click="router.push('/archived-terms')"
          >
            <van-icon
              name="search"
              size="20"
            /><span>查看归档记录</span>
          </div>
        </div>
      </div>
    </div>
  </MobileLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/core/api/client'
import { useAuth } from '@/core/hooks'
import { useNavigation } from '@/core/utils/routeDecision'
import { showSuccess, showError, showConfirm } from '@/core/utils/errorHandler'
import MobileLayout from '@/views/mobile/components/MobileLayout.vue'

const router = useRouter()
const { goHome } = useNavigation()
const { user } = useAuth()

const loading = ref(false)
const currentTerm = ref(null)
const currentTermStats = ref(null)
const termList = ref([])
const departments = ref([])
const selectedDepartmentId = ref(null)
const selectedDepartmentName = ref('')
const showDeptPicker = ref(false)

const archiveTypes = ref({
  lab_info: true,
  device_info: false,
  user_info: false
})

const canArchive = computed(() => user.value?.is_super_admin)

const hasSelectedTypes = computed(() => {
  return Object.values(archiveTypes.value).some(v => v)
})

const departmentColumns = computed(() => {
  return [
    { text: '全部部门', value: null },
    ...departments.value.map(d => ({ text: d.name, value: d.id }))
  ]
})

const toggleArchiveType = (type) => {
  archiveTypes.value[type] = !archiveTypes.value[type]
}

const handleDeptConfirm = ({ selectedOptions }) => {
  selectedDepartmentId.value = selectedOptions[0].value
  selectedDepartmentName.value = selectedOptions[0].text
  showDeptPicker.value = false
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (selectedDepartmentId.value) {
      params.department_id = selectedDepartmentId.value
    }
    const response = await api.get('/semesters/archive_overview/', params)

    if (response && response.success) {
      const data = response.data || response
      currentTerm.value = data.current_semester
      if (data.current_semester && data.current_semester.stats) {
        currentTermStats.value = data.current_semester.stats
      } else {
        currentTermStats.value = null
      }
      termList.value = data.archived_semesters || []
      departments.value = data.departments || []
    }
  } catch (e) {
    showError('加载失败')
  } finally {
    loading.value = false
  }
}

const handleArchive = async () => {
  if (!hasSelectedTypes.value) {
    await showConfirm('请至少选择一种要归档的数据类型')
    return
  }

  const confirmed = await showConfirm('确定要归档选中的数据类型吗？此操作不可逆！')
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
    await showError(err.message || '归档失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => router.go(-1)

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.archive-hero { padding: 16px; margin-bottom: 12px; }
.current-term-card {
  background: var(--mobile-gradient-success);
  border-radius: var(--mobile-radius-lg);
  padding: 24px 20px;
  position: relative;
  overflow: hidden;
}
.current-term-card::after {
  content:''; position:absolute; top:-30%; right:-15%;
  width:120px;height:120px;border-radius:50%;background:rgba(255,255,255,0.1);
}
.current-term-card.archived {
  background: var(--mobile-gradient-info);
}
.card-badge {
  display:inline-block;padding:3px 10px;border-radius:var(--mobile-radius-full);
  font-size:11px;font-weight:600;color:white;background:rgba(255,255,255,0.25);margin-bottom:10px;
}
.current-term-card h3 { margin:0 0 6px; font-size:18px; font-weight:700; color:white; }
.current-term-card p { margin:0; font-size:13px; color:rgba(255,255,255,0.85); }
.empty-current { display:flex;align-items:center;gap:10px;padding:20px;background:#FFF5E6;border-radius:var(--mobile-radius-lg);font-size:14px;color:#FF9500;font-weight:500; margin: 16px; }

.stats-section { margin-bottom: 16px; }
.section-label { display:flex;align-items:center;gap:8px;padding:10px 16px 6px;font-size:13px;font-weight:600;color:var(--mobile-text-secondary); }
.section-label span { font-size:16px; }

.stats-grid { display:grid;grid-template-columns:repeat(2, 1fr);gap:8px;padding:0 16px; }
.stat-card {
  display:flex;align-items:center;gap:10px;
  padding:12px 14px;background:var(--mobile-card);border-radius:var(--mobile-radius-md);
  box-shadow:var(--mobile-shadow-sm);
}
.stat-info { display:flex;flex-direction:column; }
.stat-value { font-size:18px;font-weight:700;color:var(--mobile-text-primary);line-height:1.2; }
.stat-label { font-size:11px;color:var(--mobile-text-hint); }

.info-section { margin-bottom: 8px; }
.term-list { display:flex;flex-direction:column;gap:8px;padding:0 16px; }
.term-card {
  display:flex;align-items:center;justify-content:space-between;gap:12px;
  padding:14px 16px;background:var(--mobile-card);border-radius:var(--mobile-radius-md);
  box-shadow:var(--mobile-shadow-sm);border-left:3px solid transparent;
}
.term-card.archived { border-left-color: #07C160; opacity: 0.85; }
.term-name { font-size:14px;font-weight:600;color:var(--mobile-text-primary); }
.term-date { font-size:11px;color:var(--mobile-text-hint);flex:1; }
.status-tag { padding:3px 10px;border-radius:var(--mobile-radius-full);font-size:11px;font-weight:600; }
.status-tag.success { background:var(--mobile-success-bg);color:var(--mobile-success); }

.archive-section { margin-top: 16px; }
.section-desc { font-size:12px;color:var(--mobile-text-hint);margin:0 16px 12px; }

.options-list { display:flex;flex-direction:column;gap:10px;padding:0 16px; }
.option-card {
  display:flex;align-items:flex-start;gap:12px;
  padding:14px;background:var(--mobile-card);border-radius:var(--mobile-radius-md);
  box-shadow:var(--mobile-shadow-sm);border:2px solid transparent;
  cursor:pointer;transition:all 0.2s ease;
}
.option-card.selected { border-color:var(--mobile-primary);background:var(--mobile-primary-bg); }
.option-checkbox { padding-top:2px; }
.option-icon {
  width:44px;height:44px;border-radius:var(--mobile-radius-md);
  display:flex;align-items:center;justify-content:center;flex-shrink:0;
}
.option-icon.lab { background:#E8F8EE;color:#07C160; }
.option-icon.device { background:#EBF7FD;color:#5AC8FA; }
.option-icon.user { background:#EEF2FF;color:#4F6EF7; }
.option-info { display:flex;flex-direction:column;gap:2px;flex:1; }
.option-title { font-size:14px;font-weight:600;color:var(--mobile-text-primary); }
.option-count { font-size:11px;color:var(--mobile-text-hint); }

.dept-section { margin-top:16px;padding:0 16px; }
.dept-section .section-label { padding:0 0 6px; }

.action-buttons { padding:16px;margin-top:16px; }
.action-buttons .van-button { width:100%; }

.tips-section {
  margin:0 16px 16px;padding:14px;background:#FFF5E6;
  border-radius:var(--mobile-radius-md);border:1px solid #FFE4C4;
}
.tips-header { display:flex;align-items:center;gap:6px;font-size:13px;font-weight:600;color:#FF9500;margin-bottom:8px; }
.tips-list { margin:0;padding-left:18px;font-size:12px;color:#606266;line-height:1.8; }
.tips-list li { margin-bottom:4px; }

.quick-actions { display:grid;grid-template-columns:1fr;gap:10px;padding:0 16px;margin-top:8px; }
.action-card {
  display:flex;align-items:center;justify-content:center;gap:8px;
  padding:14px 12px;border-radius:var(--mobile-radius-md);font-size:13px;font-weight:600;
  cursor:pointer;transition:all 0.2s ease;
}
.action-card.primary { background:var(--mobile-primary-bg);color:var(--mobile-primary); }
.action-card:active { transform:scale(0.97); }

.archived-notice {
  display:flex;flex-direction:column;align-items:center;
  padding:40px 20px;text-align:center;margin:16px;
  background:var(--mobile-card);border-radius:var(--mobile-radius-lg);
  box-shadow:var(--mobile-shadow-sm);
}
.archived-notice h4 { margin:16px 0 8px;font-size:16px;color:var(--mobile-text-primary); }
.archived-notice p { margin:0 0 16px;font-size:13px;color:var(--mobile-text-hint); }
</style>
