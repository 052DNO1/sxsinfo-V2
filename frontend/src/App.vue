<template>
  <router-view :key="$route.fullPath" />

  <!-- 服务器不可达时接管界面（原生实现，PC/移动端构建共用） -->
  <ConnectionGuard />
</template>

<script>
import ConnectionGuard from '@/components/ConnectionGuard.vue'

export default {
  name: 'App',
  components: {
    ConnectionGuard
  }
}
</script>

<style>
body { margin: 0; padding: 0; }
</style>
