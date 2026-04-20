<template>
  <div class="mobile-layout">
    <slot />
    <MobileTabBar />
  </div>
</template>

<script setup>
import MobileTabBar from './MobileTabBar.vue'
</script>

<style scoped>
.mobile-layout {
  min-height: 100vh;
  background: var(--mobile-bg, #F2F3F7);
  position: relative;
}
</style>
