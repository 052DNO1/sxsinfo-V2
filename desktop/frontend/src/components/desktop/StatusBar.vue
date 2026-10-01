<!--
  底部状态栏（桌面端专用）

  VS Code / Linear 这类桌面应用的信息分区惯例：
  窗口上下各只有一条细栏，上面的条放"身份与全局操作"，下面的条放"上下文与状态"。
  于是侧边栏里的用户卡片、页脚版权、分页控件都有了下沉的地方：
  - 左：当前用户 + 角色 + 连接状态（延迟）
  - 右：当前列表名、条数区间、已选条数、翻页按钮

  数据来源：
  - 用户/角色/列表上下文 → core/shell/statusStore.js（响应式单例）
  - 连接状态 → core/config/connection.js 的 useConnection()（请求层已经在维护，不重复探测）
-->
<template>
  <footer class="lims-statusbar">
    <div class="lims-statusbar__group">
      <span
        class="lims-statusbar__item lims-statusbar__user"
        :title="userTitle"
      >
        <span
          class="lims-statusbar__dot"
          :class="online ? 'is-online' : 'is-offline'"
        />
        <span class="lims-statusbar__strong">{{ user?.nickname || '未登录' }}</span>
        <span v-if="user?.roleText">{{ user.roleText }}</span>
      </span>

      <span class="lims-statusbar__sep">|</span>

      <span class="lims-statusbar__item lims-statusbar__muted">{{ table ? '' : '就绪' }}</span>

      <span
        class="lims-statusbar__item"
        :title="serverTitle"
      >
        <span v-if="isChecking">正在检测服务器…</span>
        <span v-else-if="online">已连接<template v-if="latencyMs"> · {{ latencyMs }} ms</template></span>
        <span v-else class="lims-statusbar__warn">服务器未连接</span>
      </span>
    </div>

    <div class="lims-statusbar__group lims-statusbar__group--right">
      <template v-if="table">
        <span class="lims-statusbar__item lims-statusbar__muted">{{ table.label || '列表' }}</span>
        <span class="lims-statusbar__item lims-statusbar__strong">共 {{ dataCount }} 条数据</span>
        <span class="lims-statusbar__item lims-statusbar__muted">{{ rangeText }}</span>
        <span
          v-if="table.selectedCount > 0"
          class="lims-statusbar__item lims-statusbar__strong"
        >
          已选 {{ table.selectedCount }} 项
        </span>
        <span
          v-if="showPager"
          class="lims-statusbar__pager"
        >
          <button
            class="lims-statusbar__btn"
            type="button"
            title="上一页（PageUp）"
            :disabled="!table.canPrev"
            @click="requestPage(-1)"
          >
            <svg width="10" height="10" viewBox="0 0 10 10" aria-hidden="true">
              <path d="M6.5 1L2.5 5l4 4" fill="none" stroke="currentColor" stroke-width="1.3" />
            </svg>
          </button>
          <button
            class="lims-statusbar__btn"
            type="button"
            title="下一页（PageDown）"
            :disabled="!table.canNext"
            @click="requestPage(1)"
          >
            <svg width="10" height="10" viewBox="0 0 10 10" aria-hidden="true">
              <path d="M3.5 1l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.3" />
            </svg>
          </button>
        </span>
      </template>
      <span
        v-if="!table"
        class="lims-statusbar__item lims-statusbar__muted"
      />
    </div>
  </footer>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted } from 'vue'
import { useConnection } from '@/core/config/connection'
import { requestPage, useShellStatus } from '@/core/shell/statusStore'

const state = useShellStatus()
const { isOnline, isChecking, latencyMs, lastError } = useConnection()

const user = computed(() => state.user)
const table = computed(() => state.table)

const online = computed(() => isOnline.value === true)
// 只有"列表有分页"时才显示翻页按钮（共 1 页就没什么可翻的）
const showPager = computed(() => Boolean(table.value && table.value.pages > 1))

/** 总条数：优先取服务端总数，取不到就用当前页加载数 */
const dataCount = computed(() => {
  const t = table.value
  if (!t) return 0
  return t.total || t.loaded || 0
})

/** 当前页区间，如 1–20（总条数单独展示，这里不重复"共"字） */
const rangeText = computed(() => {
  const t = table.value
  if (!t || !t.total) return ''
  const from = (t.page - 1) * t.pageSize + 1
  const to = Math.min(t.page * t.pageSize, t.total)
  return `${from}–${to}`
})

const userTitle = computed(() => {
  const u = state.user
  if (!u) return '未登录'
  return [u.nickname, u.roleText].filter(Boolean).join(' · ')
})

const serverTitle = computed(() => {
  const base = state.connection?.baseUrl || ''
  if (isChecking.value) return `正在检测 ${base}`
  if (online.value) return `已连接：${base}`
  return `未连接：${base}${lastError.value ? '（' + lastError.value + '）' : ''}`
})

/** PageUp / PageDown 翻页：状态栏能力的键盘对应，符合"高信息密度 + 键盘优先" */
function onKeydown(event) {
  if (!showPager.value) return
  const target = event.target
  const tag = (target?.tagName || '').toLowerCase()
  // 输入框里 PageUp/PageDown 应该保持原生行为
  if (tag === 'input' || tag === 'textarea' || target?.isContentEditable) return
  if (event.key === 'PageUp') {
    requestPage(-1)
    event.preventDefault()
  } else if (event.key === 'PageDown') {
    requestPage(1)
    event.preventDefault()
  }
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
.lims-statusbar {
  flex: 0 0 auto;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 0 10px;
  background: var(--lims-statusbar-bg);
  border-top: 1px solid var(--lims-titlebar-border);
  color: var(--lims-statusbar-fg);
  font-size: 12px;
  line-height: 24px;
  user-select: none;
}

.lims-statusbar__group {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.lims-statusbar__group--right {
  justify-content: flex-end;
}

.lims-statusbar__item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
  opacity: 0.92;
}

.lims-statusbar__user {
  gap: 6px;
}

.lims-statusbar__muted {
  opacity: 0.6;
}

.lims-statusbar__strong {
  font-weight: 600;
}

.lims-statusbar__warn {
  color: #e0a400;
}

.lims-statusbar__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #8a8a8a;
}

.lims-statusbar__dot.is-online {
  background: #2ea043;
}

.lims-statusbar__dot.is-offline {
  background: #cd3131;
}

.lims-statusbar__pager {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.lims-statusbar__btn {
  width: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 3px;
  background: transparent;
  color: inherit;
  cursor: default;
}

.lims-statusbar__btn:hover:not(:disabled) {
  background: var(--lims-titlebar-hover);
}

.lims-statusbar__btn:disabled {
  opacity: 0.3;
}
</style>
