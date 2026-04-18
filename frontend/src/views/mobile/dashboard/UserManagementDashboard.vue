<template>
  <!-- 移动端直接显示内容 -->
  <div class="mobile-user-management-page mobile-layout">
    <van-nav-bar
      title="用户管理"
      left-arrow
      @click-left="handleBack"
      class="mobile-nav-bar"
    />

    <div class="mobile-content-wrapper">
      <div class="mobile-function-list">
        <a href="#" class="mobile-function-item" @click.prevent="navigateTo('/userlist/1')">
          <div class="mobile-function-icon">
            <van-icon name="user-circle-o" size="20" color="#1989fa" />
          </div>
          <div class="mobile-function-content">
            <span class="mobile-function-text">查看教师信息</span>
            <span class="mobile-function-label">管理所有教师账户信息</span>
          </div>
          <van-icon name="arrow" class="mobile-function-arrow" />
        </a>

        <a href="#" class="mobile-function-item" @click.prevent="navigateTo('/userlist/2')">
          <div class="mobile-function-icon">
            <van-icon name="manager-o" size="20" color="#7232dd" />
          </div>
          <div class="mobile-function-content">
            <span class="mobile-function-text">查看实训室管理员</span>
            <span class="mobile-function-label">管理实训室管理员账户</span>
          </div>
          <van-icon name="arrow" class="mobile-function-arrow" />
        </a>

        <a 
          v-if="user?.is_superuser || user?.is_departadmin"
          href="#" 
          class="mobile-function-item" 
          @click.prevent="navigateTo('/adduser/1')"
        >
          <div class="mobile-function-icon">
            <van-icon name="add-o" size="20" color="#07c160" />
          </div>
          <div class="mobile-function-content">
            <span class="mobile-function-text">添加用户</span>
            <span class="mobile-function-label">创建新的用户账户</span>
          </div>
          <van-icon name="arrow" class="mobile-function-arrow" />
        </a>

        <a 
          v-if="user?.is_superuser || user?.is_departadmin"
          href="#" 
          class="mobile-function-item" 
          @click.prevent="navigateTo('/import-user')"
        >
          <div class="mobile-function-icon">
            <van-icon name="add-square" size="20" color="#ff976a" />
          </div>
          <div class="mobile-function-content">
            <span class="mobile-function-text">导入用户</span>
            <span class="mobile-function-label">从Excel文件批量导入用户</span>
          </div>
          <van-icon name="arrow" class="mobile-function-arrow" />
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, onUnmounted } from 'vue'
import { useUser } from '@/composables/useCommon'
import { useMobile } from '@/composables/useMobile'

export default {
  name: 'MobileUserManagementDashboard',
  setup() {
    const { user } = useUser()
    const { handleBack, navigateTo, initMobileSetup } = useMobile()
    
    let cleanup = null
    onMounted(() => {
      cleanup = initMobileSetup()
    })
    
    onUnmounted(() => {
      if (cleanup) cleanup()
    })

    return {
      user,
      handleBack,
      navigateTo
    }
  }
}
</script>

<style scoped>
/* mobile.css 已在 main.js 中统一导入 */

.mobile-user-management-page {
  min-height: 100vh;
  background: #f7f8fa;
  display: flex;
  flex-direction: column;
}

.mobile-content-wrapper {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.mobile-content-wrapper .mobile-function-list {
  margin-top: 0;
}
</style>
