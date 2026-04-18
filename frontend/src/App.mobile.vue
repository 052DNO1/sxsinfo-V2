<template>
  <div class="mobile-app">
    <router-view />
  </div>
</template>

<script setup>
</script>

<style scoped>
.mobile-app {
  min-height: 100vh;
  background: var(--bg-primary, #f2f3f5);
}
</style>
