<template>
  <div class="mobile-page">
    <van-nav-bar title="记录详情" left-arrow @click-left="goBack">
      <template #right><van-icon name="home-o" size="20" color="#4F6EF7" @click="goHome" /></template>
    </van-nav-bar>

    <div class="page-content">
      <van-skeleton v-if="loading" :row="5" animated />

      <template v-else-if="record">
        <div class="detail-hero animate-fade-in-up">
          <div class="detail-hero-icon" style="background: var(--mobile-gradient-ocean)">
            <van-icon name="notes-o" size="24" />
          </div>
          <div class="detail-hero-info">
            <h2>{{ record.laboratory_name || record.sxsname || '使用记录' }}</h2>
            <p>{{ record.usage_date || record.sxsdate || '' }} · {{ record.time_slot || record.sxsstart || '' }}</p>
          </div>
          <span class="status-badge" :class="record.device_status === 'NORMAL' ? 'success' : 'danger'">{{ getStatusText(record.device_status) }}</span>
        </div>

        <div class="info-section animate-fade-in-up animate-delay-1">
          <div class="section-label"><span>👤</span> 使用人信息</div>
          <div class="info-card">
            <div class="info-row"><span class="info-label">使用人</span><span class="info-value">{{ record.user_name || record.teacher_name || record.username || '-' }}</span></div>
            <div class="info-row"><span class="info-label">人数</span><span class="info-value bold">{{ record.student_count || record.sxspersoncount || '-' }} 人</span></div>
          </div>
        </div>

        <div class="info-section animate-fade-in-up animate-delay-2" v-if="record.class_name || record.course_name">
          <div class="section-label"><span>📚</span> 课程/班级信息</div>
          <div class="info-card">
            <div class="info-row" v-if="record.class_name"><span class="info-label">班级</span><span class="info-value">{{ record.class_name }}</span></div>
            <div class="info-row" v-if="record.course_name"><span class="info-label">课程名称</span><span class="info-value">{{ record.course_name }}</span></div>
            <div class="info-row" v-if="record.weeks"><span class="info-label">周次</span><span class="info-value">{{ record.weeks }}</span></div>
          </div>
        </div>

        <div class="info-section animate-fade-in-up animate-delay-3" v-if="record.content || record.sxsdesc">
          <div class="section-label"><span>📝</span> 实训内容</div>
          <div class="info-card content-card">{{ record.content || record.sxsdesc }}</div>
        </div>

        <div class="info-section" v-if="record.note">
          <div class="section-label"><span>💬</span> 备注</div>
          <div class="info-card content-card note-card">{{ record.note }}</div>
        </div>

        <div class="info-section" v-if="record.created_at">
          <div class="section-label"><span>🕐</span> 系统信息</div>
          <div class="info-card meta-card">
            <div class="info-row"><span class="info-label">创建时间</span><span class="info-value hint">{{ formatDate(record.created_at) }}</span></div>
          </div>
        </div>

        <div class="form-actions">
          <van-button type="primary" block round size="large" icon="edit" @click="handleEdit">编辑记录</van-button>
        </div>
      </template>

      <div v-else class="empty-state">
        <div class="empty-state-icon">📄</div>
        <h3>记录不存在</h3>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/core/utils/routeDecision'
import { recordService } from '@/core/services/BaseService'
import { showError } from '@/core/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()

const loading = ref(false)
const record = ref(null)

const formatDate = (dateStr) => dateStr ? dateStr.substring(0, 16).replace('T', ' ') : ''

const getStatusText = (status) => ({ NORMAL: '正常', FAULTY: '异常/故障' })[status] || status || '正常'

const loadData = async () => {
  loading.value = true
  try {
    const response = await recordService.get(route.params.id)
    if (response) record.value = response.data || response
  } catch (err) { showError('加载记录失败') }
  finally { loading.value = false }
}

const handleEdit = () => router.push(`/edit-record/${record.value?.id}`)
const goBack = () => router.go(-1)

onMounted(() => loadData())
</script>

<style scoped>
.detail-hero {
  display: flex; align-items: center; gap: 14px;
  padding: 24px 16px;
  background: var(--mobile-primary-bg);
  margin: -12px -16px 16px;
}

.detail-hero-icon {
  width: 52px; height: 52px; border-radius: var(--mobile-radius-md);
  display: flex; align-items: center; justify-content: center;
  color: white; flex-shrink: 0;
}

.detail-hero-info h2 { margin: 0 0 4px; font-size: 17px; font-weight: 700; color: var(--mobile-text-primary); }
.detail-hero-info p { margin: 0; font-size: 13px; color: var(--mobile-text-hint); }

.info-section { margin-bottom: 8px; }
.section-label { display: flex; align-items: center; gap: 8px; padding: 10px 16px 6px; font-size: 13px; font-weight: 600; color: var(--mobile-text-secondary); }
.section-label span { font-size: 16px; }

.info-card {
  background: var(--mobile-card);
  border-radius: var(--mobile-radius-lg);
  box-shadow: var(--mobile-shadow-sm);
  overflow: hidden;
}

.info-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
}
.info-row:not(:last-child) { border-bottom: 1px solid var(--mobile-border); }

.info-label { font-size: 13px; color: var(--mobile-text-hint); }
.info-value { font-size: 14px; font-weight: 500; color: var(--mobile-text-primary); }
.info-value.bold { font-weight: 600; font-size: 15px; }
.info-value.hint { color: var(--mobile-text-hint); }

.content-card { padding: 16px !important; line-height: 1.7; font-size: 14px; color: var(--mobile-text-secondary); }
.note-card { background: linear-gradient(135deg, #FFFBE8 0%, #FFF9E1 100%); border-color: #FFE082; }
.meta-card .info-row:last-child { border-bottom: none; }
</style>