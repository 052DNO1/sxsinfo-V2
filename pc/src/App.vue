<!--
  App.vue - 应用根组�?
  
  这是整个 Vue 应用的根组件，所有页面都在这里渲染�?
  
  主要功能�?
  1. <router-view /> - 路由出口，根据当�?URL 显示对应页面
  2. <GlobalTermReminder /> - 全局学期提醒组件
  
  对于新手�?
  - 每个 Vue 应用只有一个根组件
  - router-view 是路由占位符，会显示当前路由对应的组�?
-->

<template>
  <!-- 路由出口：显示当前路由对应的页面组件 -->
  <router-view />
  
  <!-- 全局学期提醒组件：提醒用户设置当前学�?-->
  <GlobalTermReminder />
  
  <!-- AI智能助手悬浮球：全局显示 -->
  <AIFloatBall />
</template>

<script>
import GlobalTermReminder from '@/views/pc/components/GlobalTermReminder.vue'
import AIFloatBall from '@/components/AIFloatBall.vue'

export default {
  name: 'App',
  components: {
    GlobalTermReminder,
    AIFloatBall
  }
}
</script>

<style>
/* 全局样式：重置默认边�?*/
body {
  margin: 0;
  padding: 0;
}
</style>
