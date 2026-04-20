<template>
  <MobileLayout>
    <div class="mobile-page">
      <van-nav-bar title="工作台" left-arrow @click-left="goBack">
        <template #right>
          <van-icon name="bell" size="20" color="#4F6EF7" @click="router.push('/messages')" />
        </template>
      </van-nav-bar>

    <div class="page-content">
      <van-skeleton v-if="loading" :row="8" animated />

      <template v-else>
        <!-- 用户信息区 - 新版简洁设计 -->
        <div class="welcome-card animate-fade-in-up">
          <div class="welcome-greeting-tag">嗨你好</div>
          <h1 class="welcome-username">{{ currentUser?.nickname || currentUser?.username || '用户' }}</h1>
          <p class="welcome-message">欢迎回来，祝您工作顺利！</p>
          <div class="welcome-meta">
            <span class="meta-item">
              <van-icon name="calendar-o" size="14" />
              {{ todayDate }}
            </span>
            <span class="meta-divider">|</span>
            <span class="meta-item">
              <van-icon name="label-o" size="14" />
              {{ currentTerm || '2026' }}
            </span>
          </div>
        </div>

        <!-- 权限快捷操作 -->
        <div class="quick-actions animate-fade-in-up animate-delay-1">
          <h3 class="section-title">快捷操作</h3>
          
          <!-- 系统管理员 -->
          <van-grid :column-num="4" :border="false" icon-size="24" v-if="currentUser?.is_superuser">
            <van-grid-item icon="friends-o" text="用户管理" to="/userlist/1" icon-color="#4F6EF7" />
            <van-grid-item icon="description" text="操作日志" to="/operation-log" icon-color="#5AC8FA" />
          </van-grid>

          <!-- 超级管理员(非系统) -->
          <van-grid :column-num="4" :border="false" icon-size="24" v-else-if="currentUser?.is_super_admin && !currentUser?.is_superuser">
            <van-grid-item icon="calendar-o" text="学期管理" to="/term" icon-color="#5AC8FA" />
            <van-grid-item icon="hotel-o" text="查看分院信息" to="/deptlist" icon-color="#07C160" />
            <van-grid-item icon="friends-o" text="查看分院管理员" to="/userlist/4" icon-color="#4F6EF7" />
          </van-grid>

          <!-- 分院管理员 -->
          <van-grid :column-num="4" :border="false" icon-size="24" v-else-if="(currentUser?.is_departadmin) && !currentUser?.is_superuser">
            <van-grid-item icon="friends-o" text="用户管理" to="/userlist/1" icon-color="#4F6EF7" />
            <van-grid-item icon="cluster-o" text="全部实验室" to="/listsxs" icon-color="#07C160" />
          </van-grid>

          <!-- 实训室管理员 -->
          <van-grid :column-num="4" :border="false" icon-size="24" v-else-if="currentUser?.is_sxsadmin && !currentUser?.is_superuser && !currentUser?.is_departadmin">
            <van-grid-item icon="cluster-o" text="我的实训室" to="/listsxs" icon-color="#07C160" />
            <van-grid-item icon="orders-o" text="工单中心" to="/maintain-list" icon-color="#FF3B30" />
          </van-grid>

          <!-- 教师/普通用户 -->
          <van-grid :column-num="4" :border="false" icon-size="24" v-else-if="currentUser?.is_teacher || (!currentUser?.is_superuser && !currentUser?.is_super_admin && !currentUser?.is_departadmin && !currentUser?.is_sxsadmin)">
            <van-grid-item icon="edit" text="添加记录" to="/add-record" icon-color="#5AC8FA" />
            <van-grid-item icon="orders-o" text="工单中心" to="/maintain-list" icon-color="#FF3B30" />
          </van-grid>

        
        </div>

        <!-- 教师数据统计 -->
        <div class="stats-grid animate-fade-in-up animate-delay-2" v-if="isTeacherUser">
          <div class="stat-card stat-card--primary" @click="router.push('/record-list')">
            <div class="stat-icon stat-icon--blue"><van-icon name="notes-o" size="22" /></div>
            <div class="stat-info"><div class="stat-num">{{ teacherStats.total_records || 0 }}</div><div class="stat-label">本学期使用记录</div></div>
          </div>
          <div class="stat-card stat-card--success">
            <div class="stat-icon stat-icon--green"><van-icon name="calendar-o" size="22" /></div>
            <div class="stat-info"><div class="stat-num">{{ teacherStats.month_records || 0 }}</div><div class="stat-label">本月使用记录</div></div>
          </div>
          <div class="stat-card stat-card--danger">
            <div class="stat-icon stat-icon--red"><van-icon name="cluster-o" size="22" /></div>
            <div class="stat-info"><div class="stat-num">{{ teacherStats.used_laboratories || 0 }}</div><div class="stat-label">使用实训室数</div></div>
          </div>
        </div>

        <!-- 其他角色统计（原逻辑） -->
        <div class="stats-grid animate-fade-in-up animate-delay-2" v-else>
          <div class="stat-card stat-card--primary" @click="router.push('/listsxs')">
            <div class="stat-icon stat-icon--blue"><van-icon name="home-o" size="22" /></div>
            <div class="stat-info"><div class="stat-num">{{ stats.total_laboratories || 0 }}</div><div class="stat-label">实训室总数</div></div>
          </div>
          <div class="stat-card stat-card--success" @click="router.push('/userlist/1')">
            <div class="stat-icon stat-icon--green"><van-icon name="friends-o" size="22" /></div>
            <div class="stat-info"><div class="stat-num">{{ stats.total_users || 0 }}</div><div class="stat-label">注册用户</div></div>
          </div>
          <div class="stat-card stat-card--danger" @click="router.push('/maintain-list')">
            <div class="stat-icon stat-icon--red"><van-icon name="warning-o" size="22" /></div>
            <div class="stat-info"><div class="stat-num">{{ stats.pending_orders || 0 }}</div><div class="stat-label">待处理工单</div></div>
          </div>
        </div>

        <div class="announcement-section animate-fade-in-up animate-delay-3">
          <div class="section-header">
            <div class="section-header-left">
              <div class="section-icon">
                <van-icon name="volume-o" size="18" />
              </div>
              <h3 class="section-title">系统公告</h3>
              <span class="announcement-count" v-if="announcements.length">{{ announcements.length }}</span>
            </div>
            <div class="section-more" @click="router.push('/messages')">
              <span>查看全部</span>
              <van-icon name="arrow" size="12" />
            </div>
          </div>
          
          <div class="announcement-list">
            <van-empty v-if="!announcements.length" description="暂无公告" image-size="60" />
            <div v-else class="announcement-timeline">
              <div
                v-for="(item, index) in announcements.slice(0, 3)"
                :key="index"
                class="timeline-item"
                @click="viewAnnouncement(item)"
              >
                <div class="timeline-dot-wrapper">
                  <div class="timeline-dot" :class="'dot-' + (item.type || 'info')"></div>
                  <div class="timeline-line" v-if="index < Math.min(announcements.length, 3) - 1"></div>
                </div>
                
                <div class="timeline-content">
                  <div class="content-top">
                    <span class="tag-badge" :class="'tag-' + (item.type || 'info')">
                      {{ getTypeText(item.type) }}
                    </span>
                    <span class="time-text">{{ formatAnnouncementTime(item.created_at || item.time) }}</span>
                  </div>
                  <h4 class="content-title">{{ item.title || item.content }}</h4>
                  <p class="content-desc">{{ item.content || item.description | truncate(50) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    </div>
  </MobileLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNavigation } from '@/core/utils/routeDecision'
import { useAuth } from '@/core/hooks'
import MobileLayout from '@/views/mobile/components/MobileLayout.vue'
import api from '@/core/api/client'

const router = useRouter()
const { goBack, goHome } = useNavigation()
const { user: currentUser, logout } = useAuth()

const loading = ref(true)
const stats = ref({})
const teacherStats = ref({})
const announcements = ref([])
const currentTerm = ref('')

const isTeacherUser = computed(() => {
  const u = currentUser.value
  return u?.is_teacher || (!u?.is_superuser && !u?.is_super_admin && !u?.is_departadmin && !u?.is_sxsadmin)
})

const userRoleText = computed(() => {
  const u = currentUser.value
  if (!u) return '未登录'
  if (u.is_superuser) return '系统管理员'
  if (u.is_super_admin) return '超级管理员'
  if (u.is_departadmin) return '分院管理员'
  if (u.is_sxsadmin) return '实训室管理员'
  if (u.is_teacher) return '教师'
  return '普通用户'
})

const todayDate = computed(() => {
  const date = new Date()
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return `${date.getFullYear()} ${String(date.getMonth() + 1).padStart(2, '0')} ${String(date.getDate()).padStart(2, '0')} ${weekdays[date.getDay()]}`
})

const getTypeText = (type) => {
  const typeMap = {
    'urgent': '紧急',
    'important': '重要',
    'notice': '通知',
    'maintenance': '维护',
    'info': '公告'
  }
  return typeMap[type] || '公告'
}

const formatAnnouncementTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

const viewAnnouncement = (item) => {
  router.push('/messages')
}

onMounted(async () => {
  try {
    const res = await api.get('statistics/dashboard/')
    if (res?.data) {
      stats.value = res.data.stats || {}
      announcements.value = res.data.announcements || res.data.notices || []
      currentTerm.value = res.data.current_semester?.name || '2026'
    }
    
    if (isTeacherUser.value) {
      try {
        const teacherRes = await api.get('statistics/teacher/')
        if (teacherRes?.data) {
          teacherStats.value = teacherRes.data.stats || {}
        }
      } catch (e) {
        console.error('获取教师统计数据失败', e)
      }
    }
  } finally { loading.value = false }
})
</script>

<style scoped>
.welcome-card {
  background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
  border-radius: 16px;
  padding: 24px 20px;
  margin: 16px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.1);
}

.welcome-greeting-tag {
  display: inline-block;
  font-size: 13px;
  font-weight: 600;
  color: #4F6EF7;
  background: rgba(255, 255, 255, 0.9);
  padding: 4px 12px;
  border-radius: 20px;
  margin-bottom: 12px;
}

.welcome-username {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  letter-spacing: -0.02em;
}

.welcome-message {
  margin: 0 0 16px;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.welcome-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #999;
  font-size: 13px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-divider {
  opacity: 0.3;
}

.section-title { margin:0 0 12px; font-size:16px;font-weight:600;color:var(--mobile-text-primary);display:flex;align-items:center;justify-content:space-between;padding:0 4px; }

.stat-card { display:flex!important; align-items:center; gap:14px; padding:18px 16px!important; text-align:left!important; }
.stat-icon { width:48px;height:48px;border-radius:var(--mobile-radius-md);display:flex;align-items:center;justify-content:center;flex-shrink:0; }
.stat-icon--blue{background:linear-gradient(135deg,#EEF2FF 0%,#E0E7FF 100%);color:#4F6EF7;}
.stat-icon--green{background:linear-gradient(135deg,#E8F8EE 0%,#D1F2E0 100%);color:#07C160;}
.stat-icon--orange{background:linear-gradient(135deg,#FFF5E6 0%,#FFE8CC 100%);color:#FF9500;}
.stat-icon--red{background:linear-gradient(135deg,#FFEBE9 0%,#FFD6D1 100%);color:#FF3B30;}
.stat-info{flex:1;}
.stat-info .stat-num{font-size:24px;font-weight:700;line-height:1.2;margin-bottom:2px;}
.stat-info .stat-label{font-size:13px;color:var(--mobile-text-secondary);}
.stat-card--primary .stat-num{color:#4F6EF7;} .stat-card--success .stat-num{color:#07C160;} .stat-card--danger .stat-num{color:#FF3B30;}

.announcement-section {
  padding: 0 16px 24px;
  background: linear-gradient(180deg, #FAFBFF 0%, #FFFFFF 100%);
  border-radius: 16px;
  margin: 0;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding: 4px 0;
}

.section-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #4F6EF7 0%, #6B8AFF 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.25);
}

.section-title {
  margin: 0 !important;
  font-size: 17px !important;
  font-weight: 700 !important;
  color: #1a1a2e !important;
  letter-spacing: -0.01em;
}

.announcement-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  color: white;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
}

.section-more {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #4F6EF7;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(79, 110, 247, 0.08);
}

.section-more:active {
  transform: scale(0.95);
  background: rgba(79, 110, 247, 0.15);
}

.announcement-list {
  margin-top: 0;
}

.announcement-timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;
  padding-left: 8px;
}

.timeline-item {
  display: flex;
  gap: 14px;
  padding: 16px;
  background: white;
  border-radius: 14px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: hidden;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #4F6EF7 0%, #6B8AFF 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.timeline-item:active {
  transform: scale(0.98) translateY(-2px);
  box-shadow: 0 8px 24px rgba(79, 110, 247, 0.15);
  border-color: rgba(79, 110, 247, 0.2);
}

.timeline-item:active::before {
  opacity: 1;
}

.timeline-dot-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  padding-top: 4px;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  position: relative;
  z-index: 2;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.dot-urgent {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  animation: pulse-urgent 2s infinite;
}

.dot-important {
  background: linear-gradient(135deg, #FFA94D 0%, #FFC078 100%);
}

.dot-notice,
.dot-info {
  background: linear-gradient(135deg, #4F6EF7 0%, #6B8AFF 100%);
}

.dot-maintenance {
  background: linear-gradient(135deg, #51CF66 0%, #69DB7C 100%);
}

@keyframes pulse-urgent {
  0%, 100% { 
    box-shadow: 0 2px 8px rgba(255, 107, 107, 0.4);
    transform: scale(1); 
  }
  50% { 
    box-shadow: 0 4px 16px rgba(255, 107, 107, 0.6);
    transform: scale(1.1); 
  }
}

.timeline-line {
  width: 2px;
  flex: 1;
  min-height: 20px;
  margin-top: 8px;
  background: linear-gradient(180deg, #E8ECF4 0%, transparent 100%);
  border-radius: 1px;
}

.timeline-content {
  flex: 1;
  min-width: 0;
}

.content-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  gap: 8px;
}

.tag-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
  flex-shrink: 0;
}

.tag-urgent {
  background: linear-gradient(135deg, #FFF0F0 0%, #FFE5E5 100%);
  color: #FF6B6B;
  border: 1px solid rgba(255, 107, 107, 0.2);
}

.tag-important {
  background: linear-gradient(135deg, #FFF8E6 0%, #FFF0D9 100%);
  color: #F59E0B;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.tag-notice,
.tag-info {
  background: linear-gradient(135deg, #EEF2FF 0%, #E8EDFF 100%);
  color: #4F6EF7;
  border: 1px solid rgba(79, 110, 247, 0.2);
}

.tag-maintenance {
  background: linear-gradient(135deg, #E8F9EE 0%, #DDF5E8 100%);
  color: #51CF66;
  border: 1px solid rgba(81, 207, 102, 0.2);
}

.time-text {
  font-size: 12px;
  color: #909399;
  font-weight: 400;
  flex-shrink: 0;
}

.content-title {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  transition: color 0.2s ease;
}

.timeline-item:active .content-title {
  color: #4F6EF7;
}

.content-desc {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
</style>