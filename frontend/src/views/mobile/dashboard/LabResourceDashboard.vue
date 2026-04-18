<template>
  <!-- 移动端直接显示内容 -->
  <div class="mobile-dashboard-page mobile-layout">
    <van-nav-bar
      title="实训室与资源管理"
      left-arrow
      @click-left="handleBack"
      class="mobile-nav-bar"
    />

    <div class="mobile-content-wrapper">
      <van-cell-group inset>
        <!-- 超级管理员和分院管理员：查看分院所有实训室 -->
        <van-cell
          v-if="user?.is_superuser || user?.is_departadmin"
          label="分配管理员及查看全部实训室"
          is-link
          @click="navigateTo('/listsxs/4')"
          class="mobile-function-item"
        >
          <template #title>
            <div style="display: flex; align-items: center;">
              <van-icon name="shop-o" size="24px" color="#1989fa" style="margin-right: 12px;" />
              <span>全部实训室</span>
            </div>
          </template>
        </van-cell>

        <!-- 实训室管理员：查看自己管理的实训室 -->
        <van-cell
          v-if="user?.is_sxsadmin && !user?.is_superuser && !user?.is_departadmin"
          label="查看和管理我负责的实训室，查看使用和维护记录"
          is-link
          @click="navigateTo('/listsxs/2')"
          class="mobile-function-item"
        >
          <template #title>
            <div style="display: flex; align-items: center;">
              <van-icon name="shop-o" size="24px" color="#1989fa" style="margin-right: 12px;" />
              <span>我管理的实训室</span>
            </div>
          </template>
        </van-cell>

        <!-- 超级管理员和分院管理员：添加实训室 -->
        <van-cell
          v-if="user?.is_superuser || user?.is_departadmin"
          label="创建新的实训室"
          is-link
          @click="navigateTo('/addsxs')"
          class="mobile-function-item"
        >
          <template #title>
            <div style="display: flex; align-items: center;">
              <van-icon name="add-o" size="24px" color="#07c160" style="margin-right: 12px;" />
              <span>添加实训室</span>
            </div>
          </template>
        </van-cell>

        <!-- 批量导入课表：所有有权限的用户 -->
        <van-cell
          v-if="user?.is_superuser || user?.is_departadmin || user?.is_sxsadmin"
          label="从Excel文件导入课表"
          is-link
          @click="navigateTo('/import')"
          class="mobile-function-item"
        >
          <template #title>
            <div style="display: flex; align-items: center;">
              <van-icon name="upload" size="24px" color="#ff976a" style="margin-right: 12px;" />
              <span>批量导入课表</span>
            </div>
          </template>
        </van-cell>

        <!-- 添加维护记录：实训室管理员 -->
        <van-cell
          v-if="user?.is_sxsadmin && !user?.is_superuser && !user?.is_departadmin"
          label="为管理的实训室添加维护记录"
          is-link
          @click="navigateTo('/add?sxsid=0')"
          class="mobile-function-item"
        >
          <template #title>
            <div style="display: flex; align-items: center;">
              <van-icon name="setting-o" size="24px" color="#07c160" style="margin-right: 12px;" />
              <span>添加维护记录</span>
            </div>
          </template>
        </van-cell>
      </van-cell-group>
    </div>
  </div>
</template>

<script>
import { onMounted, onUnmounted } from 'vue'
import { useUser } from '@/composables/useCommon'
import { useMobile } from '@/composables/useMobile'

export default {
  name: 'MobileLabResourceDashboard',
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
</style>


