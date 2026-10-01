<!--
  自绘标题栏（桌面端专用）—— 窗口顶部只保留这一行

  结构（与 VS Code 一类桌面应用同构）：
    [Logo + 产品名] [文件 视图 帮助] ───────拖动区─────── [— □ ×]

  左边是身份与菜单（替代原生 Win32 菜单条），右边是窗口按钮，
  中间的空白整段是拖动区：按下交给系统拖动，双击切换最大化。
  菜单项的 ID 与 Rust 侧 menu.rs 完全一致，逻辑不重复实现。
-->
<template>
  <header class="lims-titlebar">
    <div class="lims-brand">
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <rect
          x="2"
          y="2"
          width="20"
          height="20"
          rx="5"
          fill="#1890ff"
        />
        <path
          d="M7 15.5V8.5h2.1v5.2h3.4v1.8H7Zm7.2 0V8.5h2.1v7h-2.1Z"
          fill="#ffffff"
        />
      </svg>
      <span class="lims-brand__title">实训室信息管理系统</span>
      <span
        v-if="environmentLabel"
        class="lims-brand__env"
      >{{ environmentLabel }}</span>
    </div>

    <!-- 应用内菜单：替代原生菜单条 -->
    <nav class="lims-menubar">
      <div
        v-for="(group, groupIndex) in menus"
        :key="group.label"
        class="lims-menu"
      >
        <button
          class="lims-menubtn"
          type="button"
          :class="{ 'is-open': openIndex === groupIndex }"
          :aria-expanded="openIndex === groupIndex ? 'true' : 'false'"
          @mousedown.stop
          @click.stop="toggleMenu(groupIndex)"
        >
          {{ group.label }}
        </button>

        <ul
          v-if="openIndex === groupIndex"
          class="lims-menu__panel"
          @mousedown.stop
          @click.stop
        >
          <template
            v-for="(item, index) in group.items"
            :key="index"
          >
            <li
              v-if="item.separator"
              class="lims-menu__sep"
              role="separator"
            />
            <li v-else>
              <button
                class="lims-menu__item"
                type="button"
                @click="runMenuItem(item)"
              >
                <span class="lims-menu__label">{{ item.label }}</span>
                <span
                  v-if="item.shortcut"
                  class="lims-menu__shortcut"
                >{{ item.shortcut }}</span>
              </button>
            </li>
          </template>
        </ul>
      </div>
    </nav>

    <div
      class="lims-drag"
      @mousedown.left="onDragStart"
      @dblclick="onToggleMaximize"
    />

    <div class="lims-actions">
      <button
        class="lims-winbtn"
        type="button"
        title="最小化"
        @click="onMinimize"
      >
        <svg
          width="10"
          height="10"
          viewBox="0 0 10 10"
          aria-hidden="true"
        >
          <path
            d="M0 5h10"
            stroke="currentColor"
            stroke-width="1"
          />
        </svg>
      </button>
      <button
        class="lims-winbtn"
        type="button"
        :title="isMaximized ? '向下还原' : '最大化'"
        @click="onToggleMaximize"
      >
        <svg
          v-if="!isMaximized"
          width="10"
          height="10"
          viewBox="0 0 10 10"
          aria-hidden="true"
        >
          <rect
            x="0.5"
            y="0.5"
            width="9"
            height="9"
            fill="none"
            stroke="currentColor"
          />
        </svg>
        <svg
          v-else
          width="10"
          height="10"
          viewBox="0 0 10 10"
          aria-hidden="true"
        >
          <rect
            x="0.5"
            y="2.5"
            width="7"
            height="7"
            fill="none"
            stroke="currentColor"
          />
          <path
            d="M2.5 2.5V0.5h7v7h-2"
            fill="none"
            stroke="currentColor"
          />
        </svg>
      </button>
      <button
        class="lims-winbtn lims-winbtn--close"
        type="button"
        title="关闭"
        @click="onClose"
      >
        <svg
          width="10"
          height="10"
          viewBox="0 0 10 10"
          aria-hidden="true"
        >
          <path
            d="M0 0l10 10M10 0L0 10"
            stroke="currentColor"
            stroke-width="1"
          />
        </svg>
      </button>
    </div>
  </header>
</template>

<script setup>
/**
 * 窗口能力全部走 Rust 自己的命令（shell_window / shell_menu / shell_sync），
 * 不依赖 @tauri-apps/api 包，也不需要在 capabilities 里放开窗口插件权限。
 */
import { onBeforeUnmount, onMounted, ref } from 'vue'

const isMaximized = ref(false)
const openIndex = ref(null)

/** 菜单 ID 与 menu.rs 的常量一一对应；action 则直接交给 shell_window */
const menus = [
  {
    label: '文件',
    items: [
      { id: 'lims.server-settings', label: '服务器设置…' },
      { separator: true },
      { action: 'close', label: '退出' }
    ]
  },
  {
    label: '视图',
    items: [
      { id: 'lims.reload', label: '重新加载', shortcut: 'Ctrl+R' },
      { action: 'toggle-fullscreen', label: '切换全屏', shortcut: 'F11' },
      { separator: true },
      { id: 'lims.devtools', label: '开发者工具', shortcut: 'F12' }
    ]
  },
  {
    label: '帮助',
    items: [{ id: 'lims.about', label: '关于 实训室信息管理系统' }]
  }
]

// 环境标签：构建时注入就用，没注入则不显示（避免生产环境误标）
const environmentLabel = import.meta.env?.VITE_APP_ENV_LABEL || ''

function bridge() {
  return (
    (window.__TAURI__ && window.__TAURI__.core) ||
    window.__TAURI_INTERNALS__ ||
    null
  )
}

function invoke(command, args) {
  const api = bridge()
  if (!api || typeof api.invoke !== 'function') return Promise.resolve(null)
  return api.invoke(command, args).catch((error) => {
    console.warn('[titlebar] 调用失败:', command, error)
    return null
  })
}

function toggleMenu(index) {
  openIndex.value = openIndex.value === index ? null : index
}

function onDragStart() {
  openIndex.value = null
  invoke('shell_window', { action: 'start-drag' })
}

function onMinimize() {
  openIndex.value = null
  invoke('shell_window', { action: 'minimize' })
}

function onToggleMaximize() {
  openIndex.value = null
  invoke('shell_window', { action: 'toggle-maximize' }).then(syncWindowState)
}

function onClose() {
  invoke('shell_window', { action: 'close' })
}

function runMenuItem(item) {
  openIndex.value = null
  if (item.id) {
    invoke('shell_menu', { id: item.id })
    return
  }
  if (item.action) {
    invoke('shell_window', { action: item.action }).then(syncWindowState)
  }
}

function applyMaximized(value) {
  isMaximized.value = value
  document.documentElement.classList.toggle('lims-maximized', value)
}

function syncWindowState() {
  return invoke('shell_sync').then((state) => {
    if (state && typeof state === 'object') {
      applyMaximized(state.maximized === true)
    }
  })
}

let unlistenState = null
let unlistenTheme = null
let onDocumentMouseDown = null

onMounted(async () => {
  await syncWindowState()

  const api = bridge()
  if (api && typeof api.event?.listen === 'function') {
    unlistenState = await api.event.listen('lims:window-state', (event) => {
      const payload = event?.payload
      if (payload && typeof payload === 'object') {
        applyMaximized(payload.maximized === true)
      }
    })

    // 跟随系统暗色：Element Plus 的暗色变量挂在 html.dark 上
    unlistenTheme = await api.event.listen('lims:theme', (event) => {
      const theme = String(event?.payload || 'light')
      document.documentElement.classList.toggle('dark', theme === 'dark')
    })
  }

  onDocumentMouseDown = () => {
    openIndex.value = null
  }
  document.addEventListener('mousedown', onDocumentMouseDown)
})

onBeforeUnmount(() => {
  if (typeof unlistenState === 'function') unlistenState()
  if (typeof unlistenTheme === 'function') unlistenTheme()
  if (onDocumentMouseDown) document.removeEventListener('mousedown', onDocumentMouseDown)
})
</script>

<style scoped>
.lims-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 0 0 auto;
  padding-right: 4px;
}

.lims-brand__title {
  font-size: 12.5px;
  font-weight: 600;
  white-space: nowrap;
}

.lims-brand__env {
  padding: 0 5px;
  border-radius: 3px;
  background: #fff1b8;
  color: #874d00;
  font-size: 11px;
  line-height: 15px;
}

/* 菜单条紧跟 Logo：与原生应用一致，左侧是"身份 + 菜单" */
.lims-menubar {
  display: flex;
  align-items: center;
  gap: 1px;
  flex: 0 0 auto;
}

.lims-menu {
  position: relative;
}

.lims-menubtn {
  height: 22px;
  padding: 0 8px;
  border: 0;
  border-radius: 3px;
  background: transparent;
  color: inherit;
  font-family: inherit;
  font-size: 12.5px;
  cursor: default;
  transition: background var(--lims-duration-fast) var(--lims-ease);
}

.lims-menubtn:hover,
.lims-menubtn.is-open {
  background: var(--lims-titlebar-hover);
}

.lims-menu__panel {
  position: absolute;
  top: calc(var(--lims-titlebar-height) - 12px);
  left: 0;
  min-width: 210px;
  margin: 0;
  padding: 4px 0;
  list-style: none;
  background: var(--lims-titlebar-bg);
  border: 1px solid var(--lims-titlebar-border);
  border-radius: 4px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.16);
  z-index: 4000;
}

.lims-menu__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  width: 100%;
  height: 26px;
  padding: 0 12px;
  border: 0;
  background: transparent;
  color: var(--lims-titlebar-fg);
  font-family: inherit;
  font-size: 12.5px;
  text-align: left;
  cursor: default;
}

.lims-menu__item:hover {
  background: #0067c0;
  color: #ffffff;
}

.lims-menu__shortcut {
  opacity: 0.55;
  font-size: 11.5px;
}

.lims-menu__item:hover .lims-menu__shortcut {
  opacity: 0.8;
}

.lims-menu__sep {
  height: 1px;
  margin: 4px 0;
  background: var(--lims-titlebar-border);
}

.lims-drag {
  flex: 1 1 auto;
  height: 100%;
  min-width: 32px;
}

.lims-actions {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
}
</style>
