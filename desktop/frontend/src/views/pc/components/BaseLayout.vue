<!--
  页面基础布局

  桌面端改动（VS Code 风格）：
  - **去掉顶部 header**：Logo 与产品名已经在窗口标题栏上，页面里再来一行是重复的，
    而且这一行会把内容整体下压，"顶部只保留一行"就无从谈起；
  - **去掉 footer 版权条**：底部位置让给状态栏（当前用户 / 数据量 / 翻页），
    版权信息在「帮助 → 关于」里；
  - 内容区不再包一层大卡片，直接铺满，由内页自己决定分区。

  这些元素只在桌面端移除：Web 构建用的是 frontend/ 那份同名文件，不受影响。
-->
<template>
  <div class="app-container">
    <div class="content">
      <slot name="content">
        内容
      </slot>
    </div>
    <GlobalTermReminder />
  </div>
</template>

<script>
import GlobalTermReminder from './GlobalTermReminder.vue'
import { safeConfirm, safeAlert } from '@/core/utils/errorHandler'

export default {
  name: 'BaseLayout',
  components: { GlobalTermReminder },
  setup() {
    return {
      safeConfirm,
      safeAlert
    }
  }
}
</script>

<style scoped>
/* 只做纵向排布：不锁 height、不裁内容。
   之前写的 height:100% + overflow:hidden 会把表单类页面（自带 .page-container
   横向 flex、.panel-main 固定最小高度）裁成 0 高度，表现为"点开菜单全白"。 */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.content {
  flex: 1 1 auto;
}
</style>
