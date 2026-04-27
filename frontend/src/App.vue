<template>
  <router-view :key="$route.fullPath" />
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
body { margin: 0; padding: 0; }
</style>
