<!-- 页面基础布局 -->
<template>
  <div class="app-container">
    <div class="header">
      <div style="display: flex; align-items: center; gap: 12px;">
        <svg width="36" height="36" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="32" height="32" rx="8" fill="#1890FF"/>
          <path d="M16 6L6 14H8V26H24V14H26L16 6Z" fill="white"/>
          <rect x="13" y="18" width="6" height="8" fill="#1890FF"/>
        </svg>
        <span style="font-size: 20px; color: #333; font-weight: bold; letter-spacing: 1px;">
          <slot name="header">
          智慧实训室平台V2
          </slot>
        </span>
      </div>
    </div>
    <div class="content">
      <slot name="content">
        内容
      </slot>
    </div>
    <div class="footer">
      <span>&copy; 2026 实训室使用信息管理系 | 版权所有憨憨学生</span>
    </div>
  </div>
</template>

<script>
import { safeConfirm, safeAlert } from '@/core/utils/errorHandler'

export default {
  name: 'BaseLayout',
  setup() {
    return {
      safeConfirm,
      safeAlert
    }
  }
}
</script>

<style scoped>
/* 覆盖全局 footer 样式，适配新版设计 */
.footer {
  background-color: transparent !important;
  color: #999 !important;
  text-align: center;
  font-size: 12px;
  padding: 10px 0;
  width: 100% !important;
  margin: 0 !important;
  box-shadow: none !important;
  border-radius: 0 !important;
}

/* 确保容器全屏 */
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.content {
  flex: 1;
}
</style>
