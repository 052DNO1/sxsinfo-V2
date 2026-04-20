<template>
  <div class="mobile-tab-bar" :class="{ 'safe-area': hasSafeArea }">
    <div class="tab-bar-container">
      <div
        v-for="tab in tabs"
        :key="tab.path"
        class="tab-item"
        :class="{ active: currentPath === tab.path }"
        @click="handleTabClick(tab.path)"
      >
        <div class="tab-icon-wrapper">
          <van-icon :name="currentPath === tab.path ? tab.activeIcon : tab.icon" :size="24" />
          <span v-if="tab.badge" class="tab-badge">{{ tab.badge }}</span>
        </div>
        <span class="tab-label">{{ tab.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const hasSafeArea = computed(() => {
  return window?.cssSupports?.('padding-bottom', 'env(safe-area-inset-bottom)') || true
})

const tabs = [
  {
    path: '/',
    label: '首页',
    icon: 'home-o',
    activeIcon: 'home',
    badge: 0
  },
  {
    path: '/toolbox',
    label: '工具箱',
    icon: 'apps-o',
    activeIcon: 'apps',
    badge: 0
  },
  {
    path: '/profile',
    label: '我的',
    icon: 'user-o',
    activeIcon: 'user',
    badge: 0
  }
]

const currentPath = computed(() => {
  const path = route.path
  if (path === '/' || path.startsWith('/?')) return '/'
  if (path === '/toolbox') return '/toolbox'
  if (path === '/profile' || path.startsWith('/edit-profile') || path === '/change-password') return '/profile'
  return null
})

const handleTabClick = (path) => {
  if (route.path !== path) {
    router.push(path)
  }
}
</script>

<style scoped>
.mobile-tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 999;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(232, 236, 241, 0.8);
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.06);
}

.mobile-tab-bar.safe-area {
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.tab-bar-container {
  display: flex;
  align-items: center;
  justify-content: space-around;
  height: 56px;
  padding: 0 8px;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  flex: 1;
  height: 100%;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  -webkit-tap-highlight-color: transparent;
}

.tab-item:active {
  transform: scale(0.92);
}

.tab-icon-wrapper {
  position: relative;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.tab-item.active .tab-icon-wrapper {
  transform: translateY(-2px);
}

.tab-item .van-icon {
  color: #9CA3AF;
  transition: all 0.3s ease;
}

.tab-item.active .van-icon {
  color: #4F6EF7;
  filter: drop-shadow(0 2px 8px rgba(79, 110, 247, 0.3));
}

.tab-badge {
  position: absolute;
  top: -4px;
  right: -8px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: #FF3B30;
  color: white;
  font-size: 10px;
  font-weight: 600;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
}

.tab-label {
  font-size: 10px;
  font-weight: 500;
  color: #9CA3AF;
  transition: all 0.3s ease;
  letter-spacing: 0.02em;
}

.tab-item.active .tab-label {
  color: #4F6EF7;
  font-weight: 600;
}
</style>
