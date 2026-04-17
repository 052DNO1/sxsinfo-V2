<!--
  App.vue - 应用根组件
  
  这是整个 Vue 应用的根组件，所有页面都在这里渲染。
  
  主要功能：
  1. <router-view /> - 路由出口，根据当前 URL 显示对应页面
  2. <GlobalTermReminder /> - 全局学期提醒组件
  
  对于新手：
  - 每个 Vue 应用只有一个根组件
  - router-view 是路由占位符，会显示当前路由对应的组件
-->

<template>
  <router-view />
  <GlobalTermReminder />
</template>

<script>
import GlobalTermReminder from '@/views/mobile/components/GlobalTermReminder.vue'

export default {
  name: 'App',
  components: {
    GlobalTermReminder
  }
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
}
</style>
