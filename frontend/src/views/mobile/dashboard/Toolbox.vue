<template>
  <MobileLayout>
    <div class="mobile-page">
      <van-nav-bar title="工具箱" />

    <div class="page-content">
      <div class="toolbox-section animate-fade-in-up">
        <h3 class="section-title">常用功能</h3>
        <div class="toolbox-grid">
          <div class="tool-card" v-for="(tool, index) in allTools" :key="index" @click="handleToolClick(tool)">
            <div class="tool-icon" :style="{ background: tool.bgColor }">
              <van-icon :name="tool.icon" :size="24" :color="tool.iconColor" />
            </div>
            <span class="tool-label">{{ tool.label }}</span>
          </div>
        </div>
      </div>
    </div>
    </div>
  </MobileLayout>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/core/hooks'
import { showDialog } from 'vant'
import MobileLayout from '@/views/mobile/components/MobileLayout.vue'

const router = useRouter()
const { user: currentUser, logout } = useAuth()

const handleToolClick = (tool) => {
  if (tool.action === 'logout') {
    showDialog({
      title: '提示',
      message: '确定要退出登录吗？',
      showCancelButton: true,
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      confirmButtonColor: '#FF3B30'
    }).then(async () => {
      await logout()
      router.push('/login')
    }).catch(() => {})
  } else {
    router.push(tool.path)
  }
}

const allTools = computed(() => {
  const tools = []

  if (currentUser.value?.is_superuser) {
    tools.push(
      { icon: 'friends-o', label: '用户管理', path: '/userlist/1', bgColor: '#EEF2FF', iconColor: '#4F6EF7' },
      { icon: 'description', label: '操作日志', path: '/operation-log', bgColor: '#EBF7FD', iconColor: '#5AC8FA' }
    )
  } else if (currentUser.value?.is_super_admin) {
    tools.push(
      { icon: 'calendar-o', label: '学期管理', path: '/term', bgColor: '#EBF7FD', iconColor: '#5AC8FA' },
      { icon: 'box-o', label: '归档学期', path: '/archive-term', bgColor: '#F3E8FF', iconColor: '#9B59B6' },
      { icon: 'clock-o', label: '查看归档记录', path: '/archived-terms', bgColor: '#FFF5E6', iconColor: '#FF9500' },
      { icon: 'hotel-o', label: '查看分院信息', path: '/deptlist', bgColor: '#E8F8EE', iconColor: '#07C160' },
      { icon: 'friends-o', label: '查看分院管理员', path: '/userlist/4', bgColor: '#EEF2FF', iconColor: '#4F6EF7' }
    )
    tools.push(
      { icon: 'revoke', label: '退出登陆', action: 'logout', bgColor: '#FFEBE9', iconColor: '#FF3B30' }
    )
  } else if (currentUser.value?.is_departadmin) {
    tools.push(
      { icon: 'friends-o', label: '用户管理', path: '/userlist/1', bgColor: '#EEF2FF', iconColor: '#4F6EF7' },
      { icon: 'cluster-o', label: '全部实训室', path: '/listsxs', bgColor: '#E8F8EE', iconColor: '#07C160' },
      { icon: 'notes-o', label: '使用记录', path: '/record-list', bgColor: '#F3E8FF', iconColor: '#9B59B6' },
      { icon: 'setting-o', label: '维护记录', path: '/maintain-list', bgColor: '#FFF5E6', iconColor: '#FF9500' },
      { icon: 'warning-o', label: '故障记录', path: '/maintain-list?type=fault', bgColor: '#FFEBE9', iconColor: '#FF3B30' },
      { icon: 'desktop-o', label: '全部设备', path: '/device-list', bgColor: '#EBF7FD', iconColor: '#5AC8FA' },
      { icon: 'calendar-o', label: '课程表', path: '/classlist', bgColor: '#E8FAF0', iconColor: '#1ABC9C' }
    )
  } else if (currentUser.value?.is_sxsadmin) {
    tools.push(
      { icon: 'cluster-o', label: '实训室管理', path: '/listsxs', bgColor: '#E8F8EE', iconColor: '#07C160' },
      { icon: 'notes-o', label: '查看使用记录', path: '/record-list', bgColor: '#F3E8FF', iconColor: '#9B59B6' },
      { icon: 'setting-o', label: '查看维护记录', path: '/maintain-list', bgColor: '#FFF5E6', iconColor: '#FF9500' },
      { icon: 'warning-o', label: '查看故障记录', path: '/maintain-list?type=fault', bgColor: '#FFEBE9', iconColor: '#FF3B30' },
      { icon: 'calendar-o', label: '查看课表', path: '/classlist', bgColor: '#E8FAF0', iconColor: '#1ABC9C' },
      { icon: 'desktop-o', label: '查看全部设备', path: '/device-list', bgColor: '#EBF7FD', iconColor: '#5AC8FA' },
      { icon: 'edit', label: '添加记录', path: '/add-record', bgColor: '#EBF7FD', iconColor: '#5AC8FA' },
      { icon: 'warning-o', label: '故障上报', path: '/report-maintenance', bgColor: '#FFF5E6', iconColor: '#FF9500' },
      { icon: 'orders-o', label: '工单中心', path: '/maintain-list', bgColor: '#FFEBE9', iconColor: '#FF3B30' }
    )
  } else if (currentUser.value?.is_teacher) {
    tools.push(
      { icon: 'calendar-o', label: '课程表', path: '/classlist', bgColor: '#E8FAF0', iconColor: '#1ABC9C' },
      { icon: 'cluster-o', label: '实训室', path: '/listsxs', bgColor: '#E8F8EE', iconColor: '#07C160' },
      { icon: 'notes-o', label: '使用记录', path: '/record-list', bgColor: '#F3E8FF', iconColor: '#9B59B6' },
      { icon: 'edit', label: '添加记录', path: '/add-record', bgColor: '#EBF7FD', iconColor: '#5AC8FA' },
      { icon: 'warning-o', label: '故障上报', path: '/report-maintenance', bgColor: '#FFF5E6', iconColor: '#FF9500' },
      { icon: 'orders-o', label: '工单中心', path: '/maintain-list', bgColor: '#FFEBE9', iconColor: '#FF3B30' }
    )
  }

  return tools
})
</script>

<style scoped>
.toolbox-section {
  margin-bottom: 20px;
}

.section-title {
  margin: 0 0 12px;
  padding: 0 16px;
  font-size: 16px;
  font-weight: 600;
  color: var(--mobile-text-primary);
}

.toolbox-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  padding: 0 16px;
}

.tool-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  background: var(--mobile-card);
  border-radius: var(--mobile-radius-lg);
  box-shadow: var(--mobile-shadow-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tool-card:active {
  transform: scale(0.95);
  box-shadow: var(--mobile-shadow-md);
}

.tool-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--mobile-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
}

.tool-card:active .tool-icon {
  transform: scale(0.9);
}

.tool-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--mobile-text-secondary);
  text-align: center;
  line-height: 1.3;
}
</style>
