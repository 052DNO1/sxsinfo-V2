<template>
  <div class="app-wrapper">
    <router-view />
    <GlobalTermReminder />
    <AIFloatBall v-if="!isMobile" />
    <MobileTabBar v-if="isMobile && showTabBar" />
  </div>
</template>

<script>
import { defineAsyncComponent, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import MobileTabBar from '@/views/mobile/components/MobileTabBar.vue'

function checkIsMobile() {
  if (typeof window === 'undefined') return false
  return window.location.hash.includes('#/mobile') ||
         window.location.pathname.includes('/mobile') ||
         (window.navigator.userAgent && /Mobile|Android|iPhone/i.test(navigator.userAgent))
}

const isMobileEnv = ref(checkIsMobile())

const GlobalTermReminder = defineAsyncComponent(() => {
  return isMobileEnv.value
    ? import('@/views/mobile/components/GlobalTermReminder.vue')
    : import('@/views/pc/components/GlobalTermReminder.vue')
})

const AIFloatBall = defineAsyncComponent(() =>
  import('@/components/AIFloatBall.vue')
)

export default {
  name: 'App',
  components: { GlobalTermReminder, AIFloatBall, MobileTabBar },
  setup() {
    const route = useRoute()
    const isMobile = isMobileEnv
    const showTabBar = computed(() => {
      const hiddenPaths = ['/login', '/change-password']
      return !hiddenPaths.includes(route.path)
    })
    return { isMobile, showTabBar }
  }
}
</script>

<style>
body { margin: 0; padding: 0; }

.app-wrapper {
  min-height: 100vh;
  position: relative;
}
</style>
