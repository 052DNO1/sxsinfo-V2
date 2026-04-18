<template>
  <!-- 移动端直接显示内容 -->
  <div class="mobile-dashboard-page mobile-layout">
    <van-nav-bar
      title="个人教学中心"
      left-arrow
      @click-left="handleBack"
      class="mobile-nav-bar"
    />

    <div class="mobile-content-wrapper">
      <van-cell-group inset>
        <van-cell
          label="查看我的实训室使用记录"
          is-link
          @click="navigateTo(`/listuserrecord/${userId}`)"
          class="mobile-function-item"
        >
          <template #title>
            <div style="display: flex; align-items: center;">
              <van-icon name="records" size="24px" color="#1989fa" style="margin-right: 12px;" />
              <span>我的实训室记录</span>
            </div>
          </template>
        </van-cell>

        <van-cell
          label="记录新的实训室使用"
          is-link
          @click="navigateTo('/add-record')"
          class="mobile-function-item"
        >
          <template #title>
            <div style="display: flex; align-items: center;">
              <van-icon name="add-o" size="24px" color="#07c160" style="margin-right: 12px;" />
              <span>添加实训记录</span>
            </div>
          </template>
        </van-cell>
      </van-cell-group>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, onUnmounted } from 'vue'
import { useUser } from '@/composables/useCommon'
import { useMobile } from '@/composables/useMobile'

export default {
  name: 'MobilePersonalTeachingDashboard',
  setup() {
    const { user } = useUser()
    const userId = computed(() => user.value?.id || '')
    const { handleBack, navigateTo, initMobileSetup } = useMobile()
    
    let cleanup = null
    onMounted(() => {
      cleanup = initMobileSetup()
    })
    
    onUnmounted(() => {
      if (cleanup) cleanup()
    })

    return {
      userId,
      handleBack,
      navigateTo
    }
  }
}
</script>


