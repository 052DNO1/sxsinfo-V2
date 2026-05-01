<template>
  <div class="app-container">
    <div class="header">
      <div style="display: flex; align-items: center; gap: 12px;">
        <svg
          width="36"
          height="36"
          viewBox="0 0 32 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <rect
            width="32"
            height="32"
            rx="8"
            fill="#1890FF"
          />
          <path
            d="M16 6L6 14H8V26H24V14H26L16 6Z"
            fill="white"
          />
          <rect
            x="13"
            y="18"
            width="6"
            height="8"
            fill="#1890FF"
          />
        </svg>
        <span style="font-size: 18px; color: #333; font-weight: bold;">
          <slot name="header">
            实训室信息管理系统
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
      <span>&copy; 2026 实训室信息管理系统</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BaseLayout',
}
</script>

<style scoped>
.footer {
  background-color: transparent !important;
  color: #999 !important;
  text-align: center;
  font-size: 12px;
  padding: 10px 0;
  width: 100% !important;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f7f8fa;
}

.content {
  flex: 1;
  padding-bottom: 50px;
}
</style>
