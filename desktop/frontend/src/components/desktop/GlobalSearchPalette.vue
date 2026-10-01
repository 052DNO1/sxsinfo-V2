<!--
  全局搜索面板（Ctrl/Cmd + K）—— 参考 VS Code / Linear 的命令面板

  交互契约：
  - 打开：全局快捷键（core/shell/useHotkeys.js 派发 lims:global-search）
          或任意位置派发 lims:open-search（侧边栏搜索框点击即用这个）
  - 关闭：Esc、点遮罩、选中结果并跳转后自动关闭
  - 输入：300ms 防抖
  - 键盘：↑/↓ 选中、Enter 跳转、Esc 关闭
  - 数据源优先级：
      ① props.search / window.__LIMS_SEARCH__ 提供的远端函数（接后端搜索接口）
      ② 内置的模块索引（本工程的主要功能入口，离线可用）

  设计取舍：面板本身不引入任何请求库，也不改 core/api——
  远端搜索通过"注入一个函数"的方式接入，谁用谁传。
-->
<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="palette-mask"
      @mousedown.self="close"
    >
      <div
        class="palette"
        role="dialog"
        aria-modal="true"
        aria-label="全局搜索"
      >
        <div class="palette__search">
          <el-icon class="palette__icon">
            <Search />
          </el-icon>
          <input
            ref="inputRef"
            v-model="keyword"
            class="palette__input"
            type="text"
            placeholder="搜索功能、分院、实训室、工单…"
            spellcheck="false"
            @keydown.down.prevent="move(1)"
            @keydown.up.prevent="move(-1)"
            @keydown.enter.prevent="confirm"
            @keydown.esc.prevent="close"
          >
          <span
            v-if="loading"
            class="palette__hint"
          >搜索中…</span>
          <span
            v-else
            class="palette__hint"
          >{{ results.length }} 项</span>
        </div>

        <div class="palette__body">
          <div
            v-if="!results.length"
            class="palette__empty"
          >
            {{ keyword ? '没有匹配结果' : '输入关键词开始搜索' }}
          </div>

          <ul
            v-else
            class="palette__list"
          >
            <li
              v-for="(item, index) in results"
              :key="item.id || item.path || index"
              class="palette__item"
              :class="{ 'is-active': index === activeIndex }"
              @mouseenter="activeIndex = index"
              @click="choose(item)"
            >
              <el-icon class="palette__item-icon">
                <component :is="item.icon || Document" />
              </el-icon>
              <div class="palette__item-text">
                <span class="palette__item-title">{{ item.title }}</span>
                <span
                  v-if="item.subtitle"
                  class="palette__item-sub"
                >{{ item.subtitle }}</span>
              </div>
              <span
                v-if="item.group"
                class="palette__item-group"
              >{{ item.group }}</span>
            </li>
          </ul>
        </div>

        <div class="palette__footer">
          <span><kbd>↑</kbd><kbd>↓</kbd> 选择</span>
          <span><kbd>Enter</kbd> 打开</span>
          <span><kbd>Esc</kbd> 关闭</span>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Document, Search } from '@element-plus/icons-vue'
import { EVENT_GLOBAL_SEARCH } from '@/core/shell/useHotkeys'

/** 侧边栏搜索框点击时派发这个事件即可唤出面板 */
const EVENT_OPEN_SEARCH = 'lims:open-search'

const props = defineProps({
  /** 远端搜索：async (keyword) => Array<{id,title,subtitle,path,group,icon}> */
  search: { type: Function, default: null },
  /** 防抖毫秒 */
  debounce: { type: Number, default: 300 }
})

const router = useRouter()
const visible = ref(false)
const keyword = ref('')
const results = ref([])
const activeIndex = ref(0)
const loading = ref(false)
const inputRef = ref(null)

/**
 * 内置模块索引（离线可用）
 * 路径取自工程真实路由：core/router/index.js
 */
const MODULES = [
  { id: 'home', title: '首页', subtitle: '数据总览', path: '/', group: '导航', icon: 'HomeFilled' },
  { id: 'term', title: '学期管理', path: '/term', group: '主要工作', icon: 'Calendar' },
  { id: 'archive-term', title: '归档学期', path: '/archive-term', group: '主要工作', icon: 'Box' },
  { id: 'archived-terms', title: '查看归档记录', path: '/archived-terms', group: '主要工作', icon: 'Collection' },
  { id: 'deptlist', title: '分院信息', path: '/deptlist', group: '主要工作', icon: 'OfficeBuilding' },
  { id: 'lab-mgmt', title: '实训室与资源管理', path: '/lab-resource-management', group: '主要工作', icon: 'OfficeBuilding' },
  { id: 'userlist', title: '用户管理', path: '/userlist', group: '用户操作', icon: 'User' },
  { id: 'workorder', title: '工单中心', path: '/workorder-center', group: '主要工作', icon: 'Tickets' },
  { id: 'stats', title: '数据中心', path: '/comprehensive-stats', group: '主要工作', icon: 'DataLine' },
  { id: 'teaching', title: '个人教学中心', path: '/personal-teaching', group: '主要工作', icon: 'Reading' },
  { id: 'operation-log', title: '操作日志', path: '/operation-log', group: '系统', icon: 'Document' },
  { id: 'backup', title: '数据备份与恢复', path: '/backup-manage', group: '系统', icon: 'Download' },
  { id: 'change-pwd', title: '修改密码', path: '/change-password', group: '用户操作', icon: 'Lock' },
  { id: 'update-user', title: '修改用户信息', path: '/update-user', group: '用户操作', icon: 'User' },
  { id: 'server', title: '服务器设置', subtitle: '配置后端地址', path: '/server-settings', group: '系统', icon: 'Setting' }
]

/** 当前使用的搜索函数：props > window 注入 > 内置索引 */
const searchFn = computed(() => props.search || (typeof window !== 'undefined' ? window.__LIMS_SEARCH__ : null))

function localSearch(text) {
  const q = text.trim().toLowerCase()
  if (!q) {
    // 空关键词给"最近/常用"的默认列表，比空白更友好
    return MODULES.slice(0, 8).map((item) => ({ ...item, group: item.group || '导航' }))
  }
  return MODULES.filter(
    (item) => item.title.toLowerCase().includes(q) || (item.subtitle || '').toLowerCase().includes(q) || item.path.includes(q)
  )
}

let timer = null

async function runSearch(text) {
  const remote = searchFn.value
  if (typeof remote !== 'function') {
    results.value = localSearch(text)
    activeIndex.value = 0
    return
  }

  loading.value = true
  try {
    const list = await remote(text)
    results.value = Array.isArray(list) ? list : []
  } catch (error) {
    // 远端失败时退回内置索引，保证面板永远有反馈（不弹错误、不白屏）
    console.warn('[palette] 远端搜索失败，回退内置索引:', error)
    results.value = localSearch(text)
  } finally {
    loading.value = false
    activeIndex.value = 0
  }
}

/** 300ms 防抖 */
watch(keyword, (text) => {
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => runSearch(text), props.debounce)
})

function move(delta) {
  if (!results.value.length) return
  const next = (activeIndex.value + delta + results.value.length) % results.value.length
  activeIndex.value = next
}

function confirm() {
  const item = results.value[activeIndex.value]
  if (item) choose(item)
}

function choose(item) {
  if (!item) return
  close()
  if (typeof item.action === 'function') {
    item.action(item)
    return
  }
  if (item.path) {
    router.push(item.path).catch(() => {})
  }
}

function open() {
  visible.value = true
  keyword.value = ''
  results.value = localSearch('')
  activeIndex.value = 0
  nextTick(() => inputRef.value?.focus())
}

function close() {
  visible.value = false
  if (timer) clearTimeout(timer)
}

function onGlobalSearch() {
  if (visible.value) close()
  else open()
}

onMounted(() => {
  window.addEventListener(EVENT_GLOBAL_SEARCH, onGlobalSearch)
  window.addEventListener(EVENT_OPEN_SEARCH, open)
})

onBeforeUnmount(() => {
  window.removeEventListener(EVENT_GLOBAL_SEARCH, onGlobalSearch)
  window.removeEventListener(EVENT_OPEN_SEARCH, open)
  if (timer) clearTimeout(timer)
})

defineExpose({ open, close })
</script>

<style scoped>
.palette-mask {
  position: fixed;
  inset: 0;
  z-index: 6000;
  background: rgba(15, 23, 42, 0.35);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 12vh;
}

.palette {
  width: 560px;
  max-width: 92vw;
  background: var(--el-bg-color, #ffffff);
  border: 1px solid var(--el-border-color, #e5e7eb);
  border-radius: 8px;
  box-shadow: 0 16px 48px rgba(15, 23, 42, 0.24);
  overflow: hidden;
}

.palette__search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  height: 44px;
  border-bottom: 1px solid var(--el-border-color-lighter, #f3f4f6);
}

.palette__icon {
  color: var(--el-text-color-secondary, #6b7280);
  font-size: 16px;
}

.palette__input {
  flex: 1;
  height: 100%;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--el-text-color-regular, #333333);
  font-family: inherit;
  font-size: 14px;
}

.palette__hint {
  font-size: 12px;
  color: var(--el-text-color-placeholder, #9ca3af);
}

.palette__body {
  max-height: 46vh;
  overflow-y: auto;
}

.palette__empty {
  padding: 28px 0;
  text-align: center;
  font-size: 13px;
  color: var(--el-text-color-placeholder, #9ca3af);
}

.palette__list {
  margin: 0;
  padding: 4px;
  list-style: none;
}

.palette__item {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 40px;
  padding: 0 8px;
  border-radius: 6px;
  cursor: default;
}

.palette__item.is-active {
  background: var(--el-color-primary-light-9, #ecf5ff);
}

.palette__item-icon {
  color: var(--el-text-color-secondary, #6b7280);
  font-size: 15px;
}

.palette__item.is-active .palette__item-icon {
  color: var(--el-color-primary, #1890ff);
}

.palette__item-text {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.palette__item-title {
  font-size: 13px;
  color: var(--el-text-color-primary, #1f2937);
  white-space: nowrap;
}

.palette__item-sub {
  font-size: 12px;
  color: var(--el-text-color-placeholder, #9ca3af);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.palette__item-group {
  font-size: 11px;
  color: var(--el-text-color-placeholder, #9ca3af);
}

.palette__footer {
  display: flex;
  gap: 16px;
  padding: 8px 12px;
  border-top: 1px solid var(--el-border-color-lighter, #f3f4f6);
  background: var(--el-fill-color-light, #f5f6f8);
  font-size: 11.5px;
  color: var(--el-text-color-secondary, #6b7280);
}

.palette__footer kbd {
  display: inline-block;
  min-width: 16px;
  margin-right: 3px;
  padding: 0 4px;
  border: 1px solid var(--el-border-color, #e5e7eb);
  border-bottom-width: 2px;
  border-radius: 3px;
  background: #ffffff;
  font-family: inherit;
  font-size: 11px;
  text-align: center;
}
</style>
