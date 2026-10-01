<template>
  <div :class="shellClass">
    <!-- 桌面端：自绘标题栏（替代系统标题栏 + 原生菜单条）。
         若同一份代码在浏览器里构建，isDesktopShell 为 false，仍按普通网页渲染。 -->
    <TitleBar v-if="isDesktopShell" />

    <div class="lims-shell__body">
      <!-- 刻意不用 <transition> 包 router-view：
           路由过渡 + mode="out-in" 在组件根节点为多根时会卡住不卸载，
           是"切页白屏"和"上一页残留"的典型来源；桌面端切页本来就快，不需要这层动画。 -->
      <router-view :key="$route.fullPath" />
    </div>

    <!-- 服务器不可达时接管界面（原生实现，PC/移动端构建共用） -->
    <ConnectionGuard />

    <!-- 底部状态栏：当前用户 / 连接状态 / 列表条数与翻页（桌面端专用） -->
    <StatusBar v-if="isDesktopShell" />

    <!-- 全局搜索面板（Ctrl/Cmd + K）：桌面端专用 -->
    <GlobalSearchPalette v-if="isDesktopShell" />
  </div>
</template>

<script>
import ConnectionGuard from '@/components/ConnectionGuard.vue'
import GlobalSearchPalette from '@/components/desktop/GlobalSearchPalette.vue'
import StatusBar from '@/components/desktop/StatusBar.vue'
import TitleBar from '@/components/desktop/TitleBar.vue'
import { isDesktop } from '@/core/config/runtime'
import { useHotkeys } from '@/core/shell/useHotkeys'

export default {
  name: 'App',
  components: {
    ConnectionGuard,
    GlobalSearchPalette,
    StatusBar,
    TitleBar
  },
  setup() {
    // 桌面端全局快捷键：Ctrl/Cmd+K 唤出全局搜索，Ctrl/Cmd+R 只刷新当前表格（不整页刷新）
    useHotkeys()
  },
  data() {
    return {
      isDesktopShell: isDesktop()
    }
  },
  computed: {
    shellClass() {
      // 桌面端用 flex 外壳（标题栏 + 内容区）；Web 端保持原样，不引入额外布局
      return this.isDesktopShell ? 'lims-shell' : 'lims-web'
    }
  }
}
</script>

<style>
body { margin: 0; padding: 0; }
</style>
