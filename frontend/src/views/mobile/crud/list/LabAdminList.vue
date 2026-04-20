<template>
  <div class="mobile-page">
    <van-nav-bar title="管理员列表" left-arrow @click-left="goBack">
      <template #right>
        <van-icon name="home-o" size="20" color="#4F6EF7" @click="goHome" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <div class="page-header" v-if="admins.length > 0">
        <h2>管理员</h2>
        <p>共 {{ admins.length }} 位管理员</p>
      </div>

      <div v-if="!loading && admins.length === 0" class="empty-state">
        <div class="empty-state-icon">🛡️</div>
        <h3>暂无管理员</h3>
      </div>

      <div v-else class="list-container animate-fade-in-up">
        <div 
          v-for="(admin, index) in admins" 
          :key="admin.id"
          class="list-card admin-card"
          :style="{ animationDelay: `${index * 0.06}s` }"
          @click="handleItemClick(admin)"
        >
          <div class="admin-avatar-ring">
            <span>{{ (admin.name || admin.username).charAt(0).toUpperCase() }}</span>
          </div>
          <div class="list-card-content">
            <div class="list-card-header">
              <span class="list-card-title">{{ admin.name || admin.username }}</span>
              <span class="status-badge primary">{{ admin.role || '管理员' }}</span>
            </div>
            <div class="list-card-subtitle">
              <van-icon name="user-o" size="12" /> {{ admin.username }}
            </div>
          </div>
          <van-icon name="arrow" color="#C5C9D0" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { userService } from '@/core/services/BaseService'
import { useNavigation } from '@/core/utils/routeDecision'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()

const loading = ref(false)
const admins = ref([])

const loadData = async () => {
  if (loading.value) return
  loading.value = true
  try {
    const response = await userService.list({ role__gt: 0 })
    
    if (response) {
      const list = response.list || response.data?.list || []
      admins.value = list.map(item => ({
        id: item.id,
        username: item.username,
        name: item.nickname || item.username,
        role: item.role_name || '',
        avatar: ''
      }))
    }
  } catch (err) {
    console.error('Load admins error:', err)
  } finally {
    loading.value = false
  }
}

const handleItemClick = (admin) => {
  router.push(`/edit-user/${admin.id}`)
}

const goBack = () => router.go(-1)

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.list-container { padding: 0 16px; }

.admin-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: var(--mobile-card);
  border-radius: var(--mobile-radius-lg);
  margin-bottom: 10px;
  box-shadow: var(--mobile-shadow-sm);
  transition: all 0.25s ease;
  cursor: pointer;
}

.admin-card:active { transform: scale(0.98); box-shadow: var(--mobile-shadow-md); }

.admin-avatar-ring {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--mobile-gradient-hero);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.admin-avatar-ring span {
  font-size: 18px;
  font-weight: 700;
  color: white;
}

.list-card-content { flex: 1; min-width: 0; }

.list-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 4px;
}

.list-card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--mobile-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-card-subtitle {
  font-size: 12px;
  color: var(--mobile-text-hint);
  display: flex;
  align-items: center;
  gap: 4px;
}

.list-card-subtitle .van-icon { margin-right: 2px; }
</style>